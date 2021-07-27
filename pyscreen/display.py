import abc
import logging
from typing import Dict, Any

from PIL import Image, ImageDraw, ImageFont


class Display(abc.ABC):
    def __init__(self, cfg: Dict[str, Any] = None) -> None:
        cfg = cfg or {}
        self._width = int(cfg.get("width", 128))
        self._height = int(cfg.get("height", 32))
        self._rotation = int(cfg.get("rotation", 2))

        padding = cfg.get("padding", {})
        self._padding_top: int = padding.get("top", 2)
        self._padding_left: int = padding.get("left", 2)

        self._log = logging.getLogger(self.__class__.__name__)

        self._image: Image = None
        self._draw: ImageDraw = None

        font = cfg.get("font", {})
        if "name" not in font:
            self._font: ImageFont = ImageFont.load_default()
        else:
            self._font: ImageFont = ImageFont.truetype(font.get("name"), size=int(font.get("size", 10)))

        self._line = 0
        self._font_size = int(font.get("size", 10))

    @property
    def log(self) -> logging.Logger: return self._log

    @property
    def width(self) -> int: return self._width

    @property
    def height(self) -> int: return self._height

    @property
    def rotation(self) -> int: return self._rotation

    @property
    def padding_left(self) -> int: return self._padding_left

    @property
    def padding_top(self) -> int: return self._padding_top

    @abc.abstractmethod
    def _init(self): raise NotImplementedError()

    @abc.abstractmethod
    def _poweroff(self): raise NotImplementedError()

    @abc.abstractmethod
    def _poweron(self): raise NotImplementedError()

    @abc.abstractmethod
    def _show(self): raise NotImplementedError()

    def init(self):
        # initialize display
        self._init()
        
        # create image
        self._image = Image.new("1", (self.width, self.height))
        self._draw = ImageDraw.Draw(self._image)
        self.clear()

    def poweroff(self): return self._poweroff()

    def poweron(self): return self._poweron()

    def clear(self, show=False):
        self._draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        self._line = 0
        if show: self.show()

    def write_line(self, line: str):
        self._draw.text((self._padding_left, self._line + self._padding_top),
                        line, font=self._font, fill=255)
        self._line += self._font_size

    def show(self): return self._show()