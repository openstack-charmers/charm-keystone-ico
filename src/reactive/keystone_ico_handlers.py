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

import charms.reactive as reactive

from charms_openstack.charm import (
    provide_charm_instance,
    use_defaults,
)
import charm.openstack.keystone_ico as ico  # noqa

use_defaults('update-status')


@reactive.when_not('ico.installed')
def install_ico():
    with provide_charm_instance() as charm_class:
        charm_class.install()
    reactive.set_state('ico.installed')


@reactive.when('keystone-middleware.connected')
@reactive.when('ico.installed')
def configure_keystone_principal(principle):

    with provide_charm_instance() as charm_class:
        charm_class.setup_simple_token_filter()
        principle.configure_principal(service_name=charm_class.name,
                                      simple_token_secret=charm_class.get_ico_token(),
                                      methods="external,password,token,oauth1",
                                      external="keystone.auth.plugins.external.Domain",
                                      simple_token_header="SimpleToken")


@reactive.when('keystone-middleware.departing')
def remove_ico_filter():
    with provide_charm_instance() as charm_class:
        charm_class.uninstall()
        charm_class.remove_simple_token_filter()
