import abc
import logging
import time
from typing import Dict, Any, Union, Callable

from PIL.ImageDraw import ImageDraw

from .display import Display


class Menu(abc.ABC):
    def __init__(self, name: str = None, cfg: Dict[str, Any] = None) -> None:
        self._log = logging.getLogger(self.__class__.__name__)

        self._name = name or self.__class__.__name__

        cfg = cfg or {}
        self._interval = int(cfg.get("interval", 5))
        self._update_cache: Dict[str, Dict[str, Union[float, Callable]]] = {}

        self._led: str = cfg.get("led")

    @property
    def name(self) -> str: return self._name

    @property
    def led(self) -> str: return self._led

    @property
    def log(self) -> logging.Logger: return self._log

    @property
    def interval(self) -> int: return self._interval

    def _update(self): pass

    def _show(self, display: Display): pass

    def _add_update_cache(self, name: str, interval: float, func: Callable):
        if name in self._update_cache:
            raise ValueError("%s already exists" % name)
        self._update_cache[name] = {
            "interval": interval,
            "last": 0,
            "cache": None,
            "func": func
        }
        self._log.debug("Added update cache task for %s", name)

    def _get_cache(self, name: str) -> Any:
        return self._update_cache.get(name)["cache"]

    def update(self):
        cur = time.time()
        for name, info in self._update_cache.items():
            interval, last_run, func = info["interval"], info["last"], info["func"]
            if (cur - last_run) < interval:
                continue
            self.log.debug("Updating cache for %s", name)
            info["cache"] = func()
            info["last"] = cur

    def show(self, display: Display):
        display.clear()
        display.write_line("<~- {:^13s} -~>".format(self.name))
        self._show(display)
        display.show()