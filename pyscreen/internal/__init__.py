from ..plugin import Author, Plugin

from .ssd1306 import SSD1306

from .netmenu import NetMenu
from .cpumenu import CPUMenu

from .led import LED
from .button import Button


class Internal(Plugin):
    def __init__(self):
        displays = {"ssd1306": SSD1306}
        menus = {"network": NetMenu, "net": NetMenu,
                 "cpu": CPUMenu, "cpumem": CPUMenu}
        gpios = {"led": LED, "button": Button}
        
        super().__init__("internal", "1.0.0",
                         Author("g0dsCookie", "g0dscookie@cookieprojects.de"),
                         displays=displays, menus=menus, gpios=gpios)