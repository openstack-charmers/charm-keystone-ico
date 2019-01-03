#!/usr/bin/env python
import subprocess
import os
import charms_openstack.charm
from charmhelpers.core.hookenv import (
    config,
    log,
    status_set,
    is_leader,
    leader_get,
    leader_set,
    resource_get
)
from charmhelpers.core.templating import render

KEYSTONE_DIR = '/etc/keystone'
KEYSTONE_PASTE_INI = KEYSTONE_DIR + '/keystone-paste.ini'
KEYSTONE_PASTE_INI_TEMPLATE = 'keystone-paste.ini.j2'


class KeystoneICOCharm(charms_openstack.charm.OpenStackCharm):

    # Internal name of charm
    service_name = name = 'keystone-ico'

    # First release supported
    release = 'ocata'

    # List of packages to install for this charm
    packages = ['']

    def install(self):
        log('Starting Keystone ICO installation')
        ico_package = resource_get('package')
        if ico_package:
            subprocess.check_call(['dpkg', '-i', ico_package])
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
                        shell=True).strip().decode("utf-8")
                else:
                    token = leader_get('token')
                leader_set({'token': token})
            else:
                token = leader_get('token')
        return token

    def render_keystone_paste_ini(self, enabled):
        '''Render keystone-paste.ini
        '''
        if os.path.exists(KEYSTONE_PASTE_INI):
            os.remove(KEYSTONE_PASTE_INI)
        render(source=KEYSTONE_PASTE_INI_TEMPLATE,
               target=KEYSTONE_PASTE_INI,
               owner='root',
               group='root',
               perms=0o644,
               context={'ico_enabled': enabled})
