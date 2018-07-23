#!/usr/bin/env python
import subprocess

import charmhelpers.core.hookenv as hookenv
from charmhelpers.core.hookenv import (
    config,
    log,
    status_set,
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

        status_set('active', 'Unit is ready')

    def get_ico_conf(self):
        log('Setting keystone configuration')
        return config('token-secret')
