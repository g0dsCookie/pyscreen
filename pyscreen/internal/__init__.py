from ..plugin import Author, Plugin

from .ssd1306 import SSD1306
from .mainmenu import MainMenu
from .led import LED
from .button import Button


class Internal(Plugin):
    def __init__(self):
        displays = {"ssd1306": SSD1306}
        menus = {"main": MainMenu}
        gpios = {"led": LED, "button": Button}
        
        super().__init__("internal", "1.0.0",
                         Author("g0dsCookie", "g0dscookie@cookieprojects.de"),
                         displays=displays, menus=menus, gpios=gpios)