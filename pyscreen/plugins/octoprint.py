import logging
from typing import Dict, Tuple, Any
import requests
import urllib.parse

from pyscreen.plugin import Plugin, Author
from pyscreen.menu import Menu
from pyscreen.display import Display


class Octoprint(Plugin):
    def __init__(self):
        displays = {}
        menus = {"octopi_connection": ConnectionStatus}
        gpios = {}

        super().__init__("Octoprint", "1.0.0",
                         Author("g0dsCookie", "g0dscookie@cookieprojects.de"),
                         displays=displays, menus=menus, gpios=gpios)


class OctoprintMenu(Menu):
    def __init__(self, name: str, cfg: Dict[str, Any],
                 connection_status: bool = False, printer_status: bool = False):
        super().__init__(name=name, cfg=cfg)
        self._url = cfg.get("url")
        self._token = cfg.get("token")

        if connection_status:
            self._add_update_cache("connection", 5, self._status)
        if printer_status:
            self._add_update_cache("printer", 2, self._printer)

    @property
    def connection(self) -> str: return self._get_cache("connection")

    @property
    def temperature(self) -> Dict[str, Any]: return self._get_cache("printer")[0]

    @property
    def state(self) -> Dict[str, Any]: return self._get_cache("printer")[1]

    def _get(self, path: str) -> Dict[str, Any]:
        hdr = {"X-Api-Key": self._token}
        url = urllib.parse.urljoin(self._url, path)
        r = requests.get(url, headers=hdr)
        try:
            data = r.json()
        except ValueError:
            data = {}
        if r.status_code != 200 or "error" in data:
            self._log.error("GET failed on %s: %d | %s", url, r.status_code,
                            data.get("error", "no error msg provided"))
        return data

    def _status(self) -> str:
        return self._get("/api/connection").get("current", {}).get("state", "API_ERROR")

    def _printer(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        data = self._get("/api/printer")
        temp = data.get("temperature", {})
        state = data.get("state", {})
        return (temp, state)

class ConnectionStatus(OctoprintMenu):
    def __init__(self, cfg: Dict[str, Any]):
        super().__init__(name="OCTOPI STATUS", cfg=cfg,
                         connection_status=True, printer_status=True)

    def _show(self, display: Display):
        bed = self.temperature.get("bed", {})
        tool = self.temperature.get("tool0", {})
        display.write_line("Status: %s" % self.connection)
        display.write_line("{:2.1f}/{:2.0f} | {:3.1f}/{:3.0f}".format(
            bed.get("actual", -1), bed.get("target", -1),
            tool.get("actual", -1), tool.get("target", -1))
        )