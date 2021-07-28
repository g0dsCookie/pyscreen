import logging
from pathlib import Path
import re
import importlib.util
import inspect
import os

from typing import Dict, List, Any

from .display import Display
from .menu import Menu
from .gpio import GPIO
from .plugin import Plugin


class PluginParent:
    def __init__(self, cfg: Dict[str, Any]):
        self._log = logging.getLogger(self.__class__.__name__)
        self._folders: List[str] = cfg.get("folders", [Path.joinpath(Path.home(), ".local", "lib", "pyscreen")])
        self._plugins: Dict[str, Plugin] = {}

    @property
    def log(self) -> logging.Logger: return self._log
    
    @property
    def plugin_folders(self) -> List[str]: return self._folders
    
    @property
    def plugins(self) -> List[Plugin]: return self._plugins.values()
    
    @property
    def displays(self) -> Dict[str, Display]: return {n.lower(): d for p in self.plugins for n, d in p.displays.items()}
    
    @property
    def menus(self) -> Dict[str, Menu]: return {n.lower(): m for p in self.plugins for n, m in p.menus.items()}
    
    @property
    def gpios(self) -> Dict[str, GPIO]: return {n.lower(): g for p in self.plugins for n, g in p.gpios.items()}
    
    def get_display(self, name: str) -> Display: return self.displays.get(name.lower())
    
    def get_menu(self, name: str) -> Menu: return self.menus.get(name.lower())
    
    def get_gpio(self, name: str) -> GPIO: return self.gpios.get(name.lower())
    
    def _load_internal(self):
        from pyscreen.internal import Internal
        p = Internal()
        self._plugins[p.name.lower()] = p
        self._log.debug("Loaded %s from %s [%s]", p.name, p.author, p.version)
        
    def _load_external(self, dirpath: str):
        search = re.compile(r"\.py$", re.IGNORECASE)
        files = filter(lambda f: (not f.startswith("__") and search.search(f)),
                       os.listdir(dirpath))
        for file in files:
            name = os.path.splitext(os.path.basename(file))[0]
            modname = "pyscreen.plugins.%s" % name
            spec = importlib.util.spec_from_file_location(modname, os.path.join(dirpath, file))
            if not spec:
                self._log.error("Failed to load plugin from %s", file)
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            for m in dir(mod):
                if m.startswith("__") or m.endswith("__"):
                    continue
                attr = getattr(mod, m)
                if not inspect.isclass(attr) or not issubclass(attr, Plugin) or attr == Plugin:
                    continue
                p: Plugin = attr()
                self._plugins[p.name.lower()] = p
                self._log.info("Loaded %s from %s [%s]", p.name, p.author,
                               p.version)
            
    def load_plugins(self):
        self._load_internal()
        for d in self.plugin_folders:
            if not os.path.exists(d) or not os.path.isdir(d):
                continue
            self._load_external(d)