import socket
from typing import Dict, Any
import os

import kubernetes.client

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

        self._config = kubernetes.client.Configuration()
        self._config.host = cfg.get("host", "https://kubernetes.default.svc")
        self._config.api_key_prefix["authorization"] = "Bearer"
        self._config.ssl_ca_cert = cfg.get("ca_file")
        self._config.verify_ssl = cfg.get("verify_ssl", True)

        self._config.api_key["authorization"] = cfg.get("api_key")
        if not self._config.api_key["authorization"]:
            if not os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/token"):
                raise ValueError("missing api_key")
            with open("/var/run/secrets/kubernetes.io/serviceaccount/token", "r") as tokenfile:
                self._config.api_key["authorization"] = tokenfile.readline()
            self._config.ssl_ca_cert = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"

        self._nodename = socket.gethostname()

        self._led_state = cfg.get("led_state", "blinking")
        self._led_interval = float(cfg.get("led_interval", 0.5))

        interval = cfg.get("interval", {})
        self._add_update_cache("pods", int(interval.get("interval", 30)), self._update_pods)

    @property
    def pods(self) -> Dict[str, int]: return self._get_cache("pods")

    @property
    def scheduled_pods(self) -> int: return self.pods["scheduled"]

    @property
    def started_pods(self) -> int: return self.pods["started"]

    @property
    def ready_pods(self) -> int: return self.pods["ready"]

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

    def _update(self):
        if not self.led:
            return
        led = self.parent.get_led(self.led)
        if not led:
            self._log.error("Could not find LED %s", self.led)
            return
        if self.ready_pods < self.scheduled_pods or self.started_pods < self.scheduled_pods:
            led.set_state(self._led_state, interval=self._led_interval)

    def _show(self, display: Display):
        display.write_line("Scheduled: {:2d}".format(self.scheduled_pods))
        display.write_line("Started:   {:2d} ({:2d})".format(self.started_pods, self.ready_pods))