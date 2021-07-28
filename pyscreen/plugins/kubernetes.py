import socket
from typing import Dict, Any

import kubernetes.client
import kubernetes.config

from pyscreen.display import Display
from pyscreen.plugin import Plugin, Author
from pyscreen.menu import Menu


class Kubernetes(Plugin):
    def __init__(self):
        displays = {}
        menus = {"pods": PodsMenu}
        gpios = {}

        super().__init__("Kubernetes", "1.0.0",
                         Author("g0dsCookie", "g0dscookie@cookieprojects.de"),
                         displays=displays, menus=menus, gpios=gpios)


class PodsMenu(Menu):
    def __init__(self, cfg: Dict[str, Any]) -> None:
        super().__init__(name="PODS", cfg=cfg)

        if not cfg.get("api_key"):
            kubernetes.config.load_kube_config()
            self._config = kubernetes.client.configuration
        else:
            self._config = kubernetes.client.Configuration()
            self._config.host = cfg.get("host", "https://localhost:6443")
            self._config.api_key_prefix["authorization"] = "Bearer"
            self._config.api_key["authorization"] = cfg.get("api_key")
            self._config.verify_ssl = cfg.get("verify_ssl", True)

        self._nodename = socket.gethostname()

        interval = cfg.get("interval", {})
        self._add_update_cache("pods", int(interval.get("interval", 30)), self._update_pods)

    @property
    def pods(self) -> Dict[str, int]: return self._get_cache("pods")

    def _update_pods(self):
        with kubernetes.client.ApiClient(self._config) as api_client:
            v1 = kubernetes.client.CoreV1Api(api_client)
            ret = v1.list_pod_for_all_namespaces(watch=False)
            started, ready, scheduled = 0, 0, 0
            for pod in ret.items:
                if not pod.spec.node_name == self._nodename:
                    continue
                scheduled += 1
                if pod.status.container_statuses[0].started:
                    started += 1
                if pod.status.container_statuses[0].ready:
                    ready += 1
            return {"started": started, "ready": ready, "scheduled": scheduled}

    def _update(self, display: Display):
        display.write_line("Scheduled: {:2d}".format(self.pods["scheduled"]))
        display.write_line("Started:   {:2d} ({:2d})".format(self.pods["started"], self.pods["ready"]))