import socket
from typing import Dict, Any

from ..display import Display
from ..menu import Menu


class NetMenu(Menu):
    def __init__(self, cfg: Dict[str, Any] = None) -> None:
        cfg = cfg or {}
        super().__init__(name="NETWORK", cfg=cfg)
        
        self._fqdn = bool(cfg.get("fqdn", False))
        
        interval = cfg.get("interval", {})
        self._add_update_cache("hostname", int(interval.get("hostname", 60)), self._update_hostname)
        self._add_update_cache("ipaddress", int(interval.get("ipaddress", 60)), self._update_ipaddress)
        
    @property
    def hostname(self) -> str: return self._get_cache("hostname")
    
    @property
    def ipaddress(self) -> str: return self._get_cache("ipaddress")
    
    def _update_hostname(self):
        return socket.getfqdn() if self._fqdn else socket.gethostname()
    
    def _update_ipaddress(self):
        return socket.gethostbyname(socket.gethostname())
    
    def _update(self, display: Display):
        display.write_line(self.hostname)
        display.write_line(self.ipaddress)