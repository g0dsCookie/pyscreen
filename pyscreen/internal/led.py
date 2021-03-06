from enum import Enum
import time
from typing import Dict, Any, Union

import RPi.GPIO as RPI_GPIO

from ..gpio import GPIO, GPIOType


class LEDState(Enum):
    on = 1
    off = 2
    blinking = 3


class LED(GPIO):
    def __init__(self, cfg: Dict[str, Any]):
        super().__init__(GPIOType.OUTPUT, cfg)

        try:
            self._init_state: LEDState = LEDState[cfg.get("state", "off")]
        except KeyError:
            self._log.error("unknown LED state for %s: %s", self.name, cfg.get("state"))
            self._init_state = LEDState.off

        self._state: LEDState = self._init_state
        self._last_blink: float = 0
        self._init_blink_interval: float = float(cfg.get("blink_interval", 0.1))
        self._blink_interval: float = self._init_blink_interval

    @property
    def state(self) -> LEDState: return self._state

    @property
    def blinking_interval(self) -> int: return self._blink_interval

    def _post_init(self):
        if self.state == LEDState.on:
            self.on()
        elif self.state == LEDState.off:
            self.off()
        elif self.state == LEDState.blinking:
            self.on()
            self._last_blink = time.time()

    def on(self): RPI_GPIO.output(self.pin, RPI_GPIO.HIGH)

    def off(self): RPI_GPIO.output(self.pin, RPI_GPIO.LOW)

    def reset(self):
        self._state = self._init_state
        self._blink_interval = self._init_blink_interval
        self._post_init()

    def set_state(self, state: Union[str, LEDState], interval: float = 0.1):
        if isinstance(state, str):
            try: state = LEDState[state]
            except KeyError:
                self._log.error("invalid state %s", state)
                return
        if not isinstance(state, LEDState):
            raise TypeError("state has invalid type")

        if interval <= 0.1:
            raise ValueError("interval has to be at least 0.1")
        self._state = state
        self._blink_interval = interval

    def _update(self) -> bool:
        if not self._state == LEDState.blinking:
            return False

        cur = time.time()
        if (cur - self._last_blink) < self._blink_interval:
            return False

        ledstate = RPI_GPIO.input(self.pin)
        RPI_GPIO.output(self.pin, not ledstate)
        self._last_blink = cur

        return False