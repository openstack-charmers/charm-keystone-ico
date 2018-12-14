#!/usr/bin/env python
import subprocess
import configparser
from charmhelpers.core.hookenv import (
    config,
    log,
    status_set,
    is_leader,
    leader_get,
    leader_set,
)
import charms_openstack.charm


class KeystoneICOCharm(charms_openstack.charm.OpenStackCharm):

    # Internal name of charm
    service_name = name = 'keystone-ico'

    # First release supported
    release = 'queens'

    # List of packages to install for this charm
    packages = ['']

    def install(self):
        log('Starting Keystone ICO installation')
        subprocess.check_call(['dpkg', '-i', 'keystone-ico_1_amd64.deb'])
        status_set('active', 'Unit is ready')

    def uninstall(self):
        log('Starting Keystone ICO removal')
        subprocess.check_call(['dpkg', '-r', 'keystone-ico'])

    def get_ico_token(self):
        log('Setting token configuration')
        if config('token-secret'):
            token = config('token-secret')
        else:
            if is_leader():
                if not leader_get('token'):
                    token = subprocess.check_output(
                        ['dd if=/dev/urandom bs=16 count=1 '
                         '2>/dev/null | base64'],
                        shell=True).strip()
                else:
                    token = leader_get('token')
                leader_set({'token': token})
            else:
                token = leader_get('token')
        return token

    def setup_simple_token_filter(self):
        keystone_paste_file = '/etc/keystone/keystone-paste.ini'
        filter_config = configparser.ConfigParser()
        filter_config.read(keystone_paste_file)
        filter_config['filter:simpletoken'] = {}
        filter_factory_config = 'keystone.middleware.simpletoken:' \
                                'SimpleTokenAuthentication.factory'
        filter_config['filter:simpletoken']['paste.filter_factory'] = \
            filter_factory_config

        for section in ['pipeline:public_api',
                        'pipeline:admin_api',
                        'pipeline:api_v3']:
            if 'simpletoken' not in filter_config[section]['pipeline']:
                pipeline = filter_config[section]['pipeline'].split(' ')
                # The filter must come after the json_body
                filter_index = pipeline.index('json_body') + 1

                pipeline.insert(filter_index, 'simpletoken')
                filter_config[section]['pipeline'] = " ".join(pipeline)

        with open(keystone_paste_file, 'w') as configfile:
            filter_config.write(configfile)

    def remove_simple_token_filter(self):
        keystone_paste_file = '/etc/keystone/keystone-paste.ini'
        filter_config = configparser.ConfigParser()
        filter_config.read(keystone_paste_file)

        if 'filter:simpletoken' in filter_config:
            del filter_config['filter:simpletoken']

        for section in ['pipeline:public_api',
                        'pipeline:admin_api',
                        'pipeline:api_v3']:
            if 'simpletoken' in filter_config[section]['pipeline']:
                pipeline = filter_config[section]['pipeline'].split(' ')
                pipeline.remove('simpletoken')
                filter_config[section]['pipeline'] = " ".join(pipeline)
        with open(keystone_paste_file, 'w') as configfile:
            filter_config.write(configfile)
