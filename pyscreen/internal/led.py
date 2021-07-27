from typing import Dict, Any

import RPi.GPIO as RPI_GPIO

from ..gpio import GPIO, GPIOType


class LED(GPIO):
    def __init__(self, cfg: Dict[str, Any]):
        super().__init__(GPIOType.OUTPUT, cfg)

    def on(self): RPI_GPIO.output(self.pin, RPI_GPIO.HIGH)

    def off(self): RPI_GPIO.output(self.pin, RPI_GPIO.LOW)