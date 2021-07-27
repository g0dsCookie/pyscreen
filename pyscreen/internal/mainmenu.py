import socket
from typing import Dict, Any

import psutil

from ..display import Display
from ..menu import Menu


class MainMenu(Menu):
    def __init__(self, cfg: Dict[str, Any] = None) -> None:
        cfg = cfg or {}
        super().__init__(cfg=cfg)
        
        self._fqdn = bool(cfg.get("fqdn", False))
        
        interval = cfg.get("interval", {})
        self._add_update_cache("hostname", int(interval.get("hostname", 60)), self._update_hostname)
        self._add_update_cache("ipaddress", int(interval.get("ipaddress", 60)), self._update_ipaddress)
        self._add_update_cache("cpu", int(interval.get("cpu", 1)), self._update_cpu)
        self._add_update_cache("memory", int(interval.get("mem", 1)), self._update_vmem)
        
    @property
    def hostname(self) -> str: return self._get_cache("hostname")
    
    @property
    def ipaddress(self) -> str: return self._get_cache("ipaddress")
    
    @property
    def cpu(self) -> float: return self._get_cache("cpu")
    
    @property
    def memory(self) -> float: return self._get_cache("memory")
        
    def _update_hostname(self):
        return socket.getfqdn() if self._fqdn else socket.gethostname()
    
    def _update_ipaddress(self):
        return socket.gethostbyname(socket.gethostname())
    
    def _update_cpu(self): return psutil.cpu_percent()
    
    def _update_vmem(self): return psutil.virtual_memory().percent
        
    def _update(self, display: Display):
        display.write_line(self.hostname)
        display.write_line(self.ipaddress)
        display.write_line("{:3.0f}% | {:3.1f}%".format(self.cpu, self.memory))