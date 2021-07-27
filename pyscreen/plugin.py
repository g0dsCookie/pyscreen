import abc
from typing import Union, Dict, Tuple, List

from packaging import version

from .display import Display
from .menu import Menu
from .gpio import GPIO


class Author:
    def __init__(self, name: str, email: str):
        self._name = name
        self._email = email

    @property
    def name(self) -> str: return self._name

    @property
    def email(self) -> str: return self._email

    def __str__(self) -> str: return "%s <%s>" % (self.name, self.email)


class Plugin(abc.ABC):
    def __init__(self, name: str, plugin_version: Union[str, version.Version],
                 author: Author, displays: Dict[str, Display] = None,
                 menus: Dict[str, Menu] = None, gpios: Dict[str, GPIO] = None):
        self._name = name
        
        if isinstance(plugin_version, version.Version):
            self._version = plugin_version
        else:
            self._version = version.parse(plugin_version)

        if not isinstance(author, Author):
            raise TypeError("author is not an instance of %t" % Author)
        self._author = author
        
        self._displays: Dict[str, Display] = displays or {}
        self._menus: Dict[str, Menu] = menus or {}
        self._gpios: Dict[str, GPIO] = gpios or {}
        
    @property
    def name(self) -> str: return self._name
    
    @property
    def version(self) -> version.Version: return self._version
    
    @property
    def author(self) -> Author: return self._author
    
    @property
    def displays(self) -> Dict[str, Display]: return self._displays

    @property
    def menus(self) -> Dict[str, Menu]: return self._menus
    
    @property
    def gpios(self) -> Dict[str, GPIO]: return self._gpios            