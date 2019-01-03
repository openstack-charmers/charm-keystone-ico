# Overview

This subordinate charm provides an IBM CLoud Orchestrator integration with
OpenStack Keystone.


# Usage

This charm deploy a keystone Middleware, so it relies on keystone charm:

    juju deploy keystone
    juju deploy keystone-ico
    juju add-relation keystone keystone-ico

#Limitation

The use of this charm is limited to Openstack Ocata release