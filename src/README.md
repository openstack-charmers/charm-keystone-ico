# Overview

This subordinate charm provides an IBM CLoud Orchestrator integration with
OpenStack Keystone.

# Usage

With the OpenStack neutron-api charm:

    juju deploy keystone
    juju deploy keystone-ico
    juju add-relation keystone keystone-ico
