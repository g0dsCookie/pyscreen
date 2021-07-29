import time
from typing import Callable, Dict, List, Union, Any

import RPi.GPIO as RPI_GPIO

from ..gpio import GPIO, GPIOType


class Button(GPIO):
    def __init__(self, cfg: Dict[str, Any]):
        super().__init__(GPIOType.INPUT, cfg)
        self._down = cfg.get("down", "falling").lower()
        self._up = cfg.get("up", "rising").lower()
        self._bouncetime = int(cfg.get("bouncetime", 0))

        if self._up not in ["falling", "rising"]:
            raise ValueError("unknown definition for up: %s", self._up)
        if self._down not in ["falling", "rising"]:
            raise ValueError("unknown definition for down: %s", self._down)

        if self._down == "rising" and self._up == "rising":
            raise ValueError("up and down cannot be both rising")
        if self._down == "falling" and self._up == "falling":
            raise ValueError("up and down cannot be both falling")

        self._available_actions: Dict[str, Callable] = {
            "next_scene": lambda: self._parent.next_menu(),
            "previous_scene": lambda: self._parent.previous_menu(),
            "reset_led": lambda: self._parent.reset_led(),
        }
        self._actions: List[Dict[str, Union[str, int]]] = []
        for action in cfg.get("actions", []):
            name = action.get("action")
            if not name:
                raise ValueError("missing name on action")
            if not name in self._available_actions:
                raise ValueError("undefined action %s" % name)
            min = int(action.get("min", 0))
            max = int(action.get("max", 0))
            self._actions.append({"action": name, "min": min, "max": max})

        self._down_time = 0
        self._up_time = 0

    def _callback(self, channel):
        state = RPI_GPIO.input(channel)
        if state:
            if self._up == "rising":
                self._up_time = time.time()
                self._log.debug("detected button up")
            if self._down == "rising":
                self._down_time = time.time()
                self._log.debug("detected button down")
        else:
            if self._up == "falling":
                self._up_time = time.time()
                self._log.debug("detected button up")
            if self._down == "falling":
                self._down_time = time.time()
                self._log.debug("detected button down")

    def _post_init(self):
        RPI_GPIO.add_event_detect(self.pin, RPI_GPIO.BOTH, callback=self._callback, bouncetime=self._bouncetime)

    def _update(self) -> bool:
        if not self._down_time or not self._up_time:
            return self._down_time > 0 or self._up_time > 0
        dt, ut = self._down_time, self._up_time
        self._down_time, self._up_time = 0, 0

        pressed = ut - dt
        self._log.debug(pressed)
        for action in self._actions:
            min, max = action["min"], action["max"]
            if pressed < min or (max > 0 and pressed > max):
                continue
            self._available_actions[action["action"]]()
            return True
        return False