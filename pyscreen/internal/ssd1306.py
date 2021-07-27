from typing import Dict, Any

from board import SCL, SDA
import busio
import adafruit_ssd1306

from ..display import Display


class SSD1306(Display):
    def __init__(self, cfg: Dict[str, Any] = None) -> None:
        super().__init__(cfg)
        
    def _init(self):
        self._i2c = busio.I2C(SCL, SDA)
        self._display = adafruit_ssd1306.SSD1306_I2C(self.width, self.height,
                                                     self._i2c)
        self._display.rotate(self.rotation)
        self._display.fill(0)

    def _poweroff(self): self._display.poweroff()
    
    def _poweron(self): self._display.poweron()

    def _show(self):
        self._display.image(self._image)
        self._display.show()