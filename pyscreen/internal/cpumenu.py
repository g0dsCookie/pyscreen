from typing import Dict, Any

import psutil

from ..display import Display
from ..menu import Menu


class CPUMenu(Menu):
    def __init__(self, cfg: Dict[str, Any]) -> None:
        cfg = cfg or {}
        super().__init__(name="CPU / MEM", cfg=cfg)
        
        interval = cfg.get("interval", {})
        self._add_update_cache("cpu", int(interval.get("cpu", 1)), self._update_cpu)
        self._add_update_cache("memory", int(interval.get("mem", 1)), self._update_vmem)
        
    @property
    def cpu(self) -> float: return self._get_cache("cpu")
    
    @property
    def memory(self) -> float: return self._get_cache("memory")
    
    def _update_cpu(self): return psutil.cpu_percent()
    
    def _update_vmem(self): return psutil.virtual_memory().percent
    
    def _update(self, display: Display):
        display.write_line("CPU: {:3.0}f %".format(self.cpu))
        display.write_line("MEM: {:3.1}f %".format(self.memory))