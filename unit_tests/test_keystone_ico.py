
import mock

import reactive.keystone_ico_handlers as handlers

import charms_openstack.test_utils as test_utils


class TestRegisteredHooks(test_utils.TestRegisteredHooks):

    def test_registered_hooks(self):
        # test that the hooks actually registered the relation expressions that
        # are meaningful for this interface: this is to handle regressions.
        # The keys are the function names that the hook attaches to.
        hook_set = {
            'when': {
                'configure_keystone_middleware':
                    ('endpoint.keystone-middleware.connected',
                     'ico.installed', ),
                'install_packages':
                    ('endpoint.keystone-middleware.new-release', )

            },
            'when_not': {
                'install_packages': ('ico.installed', ),
                'remove_ico_filter':
                    ('endpoint.keystone-middleware.connected', ),
            },
        }
        # test that the hooks were registered via the
        # reactive.keystone_ico_handler
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

    def _patch_endpoint_from_flag(self):
        self.patch_object(handlers, 'endpoint_from_flag',
                          name='endpoint_from_flag',
                          new=mock.MagicMock())

    def _patch_release_compare(self, release):
        self.patch_object(handlers, 'CompareOpenStackReleases',
                          name='CompareOpenStackReleases',
                          new=mock.MagicMock())
        self.CompareOpenStackReleases.return_value = release

    def test_install_packages_successfull(self):
        self._patch_endpoint_from_flag()
        self._patch_release_compare('pike')
        the_charm = self._patch_provide_charm_instance()
        self.patch_object(handlers, 'set_flag')
        handlers.install_packages()
        the_charm.install.assert_called_once_with()
        self.set_flag.assert_called_once_with('ico.installed')

    def test_not_supported_version(self):
        keystone_release = 'rocky'
        self._patch_endpoint_from_flag()
        self.endpoint_from_flag().release_version.return_value = \
            keystone_release
        self._patch_release_compare(keystone_release)
        self.patch_object(handlers, 'set_flag')
        self.patch_object(handlers, 'status_set')
        handlers.install_packages()
        self.set_flag.assert_not_called()
        self.status_set.assert_called_with(
            'blocked',
            'rocky release of keystone software is not supported')

    def test_configure_keystone_middleware(self):
        the_charm = self._patch_provide_charm_instance()
        self._patch_endpoint_from_flag()
        handlers.configure_keystone_middleware()
        the_charm.get_ico_token.assert_called_once()
        the_charm.render_keystone_paste_ini.assert_called_once()
