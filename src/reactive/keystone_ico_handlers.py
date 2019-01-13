# Copyright 2018 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from charms.reactive import endpoint_from_flag
from charms.reactive import when, when_not
from charms.reactive import clear_flag, set_flag

from charms_openstack.charm import provide_charm_instance
from charmhelpers.contrib.openstack.utils import CompareOpenStackReleases
import charm.openstack.keystone_ico as ico  # noqa
from charmhelpers.core.hookenv import status_set, config


@when_not('ico.installed')
@when('endpoint.keystone-middleware.new-release')
def install_packages():
    principal_keystone = \
        endpoint_from_flag('endpoint.keystone-middleware.new-release')
    release = principal_keystone.release_version()
    if release and CompareOpenStackReleases(release) >= "rocky":
        status_set('blocked',
                   '{} release of keystone software '
                   'is not supported'.format(release))
    else:
        with provide_charm_instance() as charm_class:
            charm_class.install()
        set_flag('ico.installed')


@when('endpoint.keystone-middleware.connected',
      'ico.installed')
def configure_keystone_middleware():
    with provide_charm_instance() as charm_class:
        charm_class.render_keystone_paste_ini(True)
        middleware_configuration = {
            "authentication": {
                "simple_token_header": "SimpleToken",
                "simple_token_secret": charm_class.get_ico_token()
            },
            "auth": {
                "methods": "external,password,token,oauth1",
                "password": "keystone.auth.plugins.password.Password",
                "token": "keystone.auth.plugins.token.Token",
                "oauth1": "keystone.auth.plugins.oauth1.OAuth"
            }
        }
        if config('multi-tenancy'):
            middleware_configuration['auth'].update(
                {"external": "keystone.auth.plugins.external.Domain"
                 })
        principal_keystone = \
            endpoint_from_flag('endpoint.keystone-middleware.connected')

        principal_keystone.configure_principal(
            middleware_name=charm_class.service_name,
            configuration=middleware_configuration)


@when_not('endpoint.keystone-middleware.connected')
def remove_ico_filter():
    with provide_charm_instance() as charm_class:
        charm_class.uninstall()
        charm_class.render_keystone_paste_ini(False)
    clear_flag('ico.installed')
    clear_flag('endpoint.keystone-middleware.departed')
