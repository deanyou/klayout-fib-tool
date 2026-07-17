"""Registry for FIB drawing plugin instances and activation state."""


class FibPluginRegistry:
    """Own plugin instances behind a small, testable interface."""

    def __init__(self, modes=("cut", "connect", "probe")):
        self._plugins = {mode: None for mode in modes}
        self._active_plugin = None

    @property
    def active_plugin(self):
        return self._active_plugin

    def register(self, mode, plugin):
        if mode not in self._plugins:
            raise ValueError("Unknown plugin mode: %s" % mode)
        self._plugins[mode] = plugin
        return plugin

    def get(self, mode):
        return self._plugins.get(mode)

    def modes(self):
        return tuple(self._plugins)

    def values(self):
        return tuple(self._plugins.values())

    def activate(self, plugin):
        self._active_plugin = plugin
        return plugin

    def deactivate(self, plugin):
        if self._active_plugin is not plugin:
            return False
        self._active_plugin = None
        return True
