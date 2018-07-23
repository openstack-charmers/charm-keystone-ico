import mock

import reactive.keystone_ico_handlers as handlers

import charms_openstack.test_utils as test_utils


class TestRegisteredHooks(test_utils.TestRegisteredHooks):

    def test_hooks(self):
        # test that the hooks actually registered the relation expressions that
        # are meaningful for this interface: this is to handle regressions.
        # The keys are the function names that the hook attaches to.
        hook_set = {
            'when': {
                'configure_neutron_plugin': ('keystone-ico.connected', ),
            },
            'when_not': {
                'install_packages': ('ico.installed', ),
            },
        }
        # test that the hooks were registered via the
        # reactive.keystone_ico_handlers
        self.registered_hooks_test_helper(handlers, hook_set, [])


class TestHandlers(test_utils.PatchHelper):

    def _patch_provide_charm_instance(self):
        the_charm = mock.MagicMock()
        self.patch_object(handlers, 'provide_charm_instance',
                          name='provide_charm_instance',
                          new=mock.MagicMock())
        self.provide_charm_instance().__enter__.return_value = the_charm
        self.provide_charm_instance().__exit__.return_value = None
        return the_charm

    def test_install_packages(self):
        the_charm = self._patch_provide_charm_instance()
        self.patch_object(handlers.reactive, 'set_state')
        handlers.install_packages()
        the_charm.install.assert_called_once_with()
        calls = [mock.call('ico.installed')]
        self.set_state.assert_has_calls(calls)
