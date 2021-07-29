import logging
from sys import displayhook
import time
from typing import List, Dict, Any, Union

import RPi.GPIO as RPI_GPIO

from yaml import load as load_yaml
try:
    from yaml import CLoader as YAMLLoader
except ImportError:
    from yaml import Loader as YAMLLoader

from .pluginparent import PluginParent
from .display import Display
from .menu import Menu
from .gpio import GPIO, GPIOType


class PyScreen:
    def __init__(self, cfg: Dict[str, Any]):
        self._log = logging.getLogger(self.__class__.__name__)

        mycfg = cfg.get("pyscreen", {})
        self._loop_interval = float(mycfg.get("interval", 0.1))
        self._standby = float(mycfg.get("standby", 120))
        
        self._selected_menu = 0
        
        # load plugins
        self._plugins = PluginParent(cfg.get("plugins", {}))
        self._plugins.load_plugins()
        
        self._display = self._load_display(cfg.get("display", {}))
        self._menus: List[Menu] = list(self._load_menus(cfg.get("menus", [])))
        self._gpios: Dict[str, GPIO] = dict(self._load_gpios(cfg.get("gpios", [])))

    @property
    def menu(self) -> Menu: return self._menus[self._selected_menu]

    def _load_display(self, cfg: Dict[str, Any]) -> Display:
        typ = cfg.get("type")
        if not typ:
            raise ValueError("Missing type option for display")
        display = self._plugins.get_display(typ)
        if not display:
            raise ValueError("Display %s not found")
        display = display(cfg)
        display.init()
        return display

    def _load_menus(self, cfg: List[Dict[str, Any]]) -> List[Menu]:
        i = 0
        for menu in cfg:
            name = menu.get("name")
            if not name:
                raise ValueError("Missing name option for Menu %d" % i)
            m = self._plugins.get_menu(name)
            if not m:
                raise ValueError("Menu %s not found for %d" % (name, i))
            m = m(menu)
            i += 1
            yield m
            
    def _load_gpios(self, cfg: List[Dict[str, Any]]) -> List[GPIO]:
        i = 0
        for gpio in cfg:
            typ = gpio.get("type")
            if not typ:
                raise ValueError("Missing type option for GPIO %d" % i)
            g = self._plugins.get_gpio(typ)
            if not g:
                raise ValueError("GPIO %s not found for GPIO %d" % (typ, i))
            g: GPIO = g(gpio)
            if g.type == GPIOType.INPUT:
                g.parent = self
            g.init()
            i += 1
            yield g.name, g

    def next_menu(self):
        self._selected_menu += 1
        if self._selected_menu >= len(self._menus):
            self._selected_menu = 0
        self._log.debug("New selected menu %d", self._selected_menu)
            
    def previous_menu(self):
        self._selected_menu -= 1
        if self._selected_menu < 0:
            self._selected_menu = len(self._menus) - 1
        self._log.debug("New selected menu %d", self._selected_menu)

    def main(self):
        last_menu_update = 0
        last_input = time.time()
        standby = False
        while True:
            cur = time.time()

            for name, gpio in self._gpios.items():
                if gpio.type != GPIOType.INPUT:
                    continue
                if gpio.update():
                    last_input = time.time()
                    last_menu_update = 0
                    if standby:
                        self._display.poweron()
                        standby = False

            if not standby and self._standby > 0 and (cur - last_input) >= self._standby:
                self._display.poweroff()
                standby = True

            for menu in self._menus:
                menu.update()

            if not standby and (cur - last_menu_update) >= self.menu.interval:
                self.menu.show(self._display)
                last_menu_update = cur

            time.sleep(self._loop_interval)


def parse_config(file: str) -> Dict[str, Any]:
    with open(file, "r") as yaml_file:
        return load_yaml(yaml_file, Loader=YAMLLoader)


def main():
    cfg = parse_config("pyscreen.yml")
    logging.basicConfig(
        format="%(asctime)-15s %(name)s [%(levelname)s]: %(message)s",
        level=cfg.get("pyscreen", {}).get("loglevel", "INFO")
    )
    
    RPI_GPIO.setmode(RPI_GPIO.BCM)
    
    screen = PyScreen(cfg)
    screen.main()


if __name__ == '__main__':
    main()