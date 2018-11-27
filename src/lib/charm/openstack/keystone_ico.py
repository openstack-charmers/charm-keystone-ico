#!/usr/bin/env python
import subprocess

import charmhelpers.core.hookenv as hookenv
from charmhelpers.core.hookenv import (
    config,
    log,
    status_set,
    is_leader,
    leader_get,
    leader_set,
)
import charms_openstack.charm

from charmhelpers.contrib.openstack.utils import (
    CompareOpenStackReleases,
    os_release,
)


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

