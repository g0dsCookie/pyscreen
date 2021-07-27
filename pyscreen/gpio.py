import abc
from enum import Enum
import logging
from typing import Dict, Any

import RPi.GPIO as RPI_GPIO


class GPIOType(Enum):
    INPUT = 1
    OUTPUT = 2


class GPIO(abc.ABC):
    def __init__(self, typ: GPIOType, cfg: Dict[str, Any]):
        self._name = cfg.get("name")
        if not self.name:
            raise ValueError("Missing name option")
        self._log = logging.getLogger(self.__class__.__name__).getChild(self.name)
        
        self._pin = int(cfg.get("pin", 0))
        if not self.pin:
            raise ValueError("Missing pin option for %s" % self.name)
        
        self._type: GPIOType = typ
        self._parent = None
        
    @property
    def name(self) -> str: return self._name
    
    @property
    def type(self) -> GPIOType: return self._type
    
    @property
    def pin(self) -> int: return self._pin

    @property
    def parent(self): return self._parent
    
    @parent.setter
    def parent(self, val): self._parent = val
    
    def _pre_init(self): pass
    def _post_init(self): pass
    def _update(self) -> bool: return False
        
    def init(self):
        self._pre_init()
        if self._type == GPIOType.INPUT:
            RPI_GPIO.setup(self.pin, RPI_GPIO.IN)
        elif self._type == GPIOType.OUTPUT:
            RPI_GPIO.setup(self.pin, RPI_GPIO.OUT)
        else:
            raise ValueError("Unknown value for GPIOType")
        self._post_init()
        
    def update(self) -> bool: return self._update()