import socket
from typing import Dict, Tuple, Any
import os

import kubernetes.client

from pyscreen.display import Display
from pyscreen.plugin import Plugin, Author
from pyscreen.menu import Menu


def get_kubeconfig(cfg: Dict[str, Any]) -> kubernetes.client.Configuration:
    config = kubernetes.client.Configuration()
    config.host = cfg.get("host", "https://kubernetes.default.svc")
    config.api_key_prefix["authorization"] = cfg.get("api_key_prefix", "Bearer")
    config.ssl_ca_cert = cfg.get("ca_file")
    config.verify_ssl = cfg.get("verify_ssl", True)

    config.api_key["authorization"] = cfg.get("api_key")
    if not config.api_key["authorization"]:
        if not os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/token"):
            raise ValueError("missing api_key")
        with open("/var/run/secrets/kubernetes.io/serviceaccount/token", "r") as tokenfile:
            config.api_key["authorization"] = tokenfile.readline()
        config.ssl_ca_cert = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"

    return config


def get_kubenode(config: kubernetes.client.Configuration) -> Tuple[str, str]:
    podname = os.environ.get("POD_NAME")
    namespace = os.environ.get("POD_NAMESPACE")
    if not podname or not namespace:
        hostname = socket.gethostname()
        ipaddr = socket.gethostbyname(hostname)
        return (hostname, ipaddr)

    with kubernetes.client.ApiClient(config) as api_client:
        v1 = kubernetes.client.CoreV1Api(api_client)
        ret = v1.read_namespaced_pod(name=podname, namespace=namespace)
        if not ret:
            return ("UNKNOWN", "127.0.0.1")
        return (ret.spec.node_name, ret.status.host_ip)


class Kubernetes(Plugin):
    def __init__(self):
        displays = {}
        menus = {"pods": PodsMenu, "kubenet": KubernetesNetMenu}
        gpios = {}

        super().__init__("Kubernetes", "1.0.0",
                         Author("g0dsCookie", "g0dscookie@cookieprojects.de"),
                         displays=displays, menus=menus, gpios=gpios)


class PodsMenu(Menu):
    def __init__(self, cfg: Dict[str, Any]):
        super().__init__(name="PODS", cfg=cfg)
        self._config = get_kubeconfig(cfg=cfg)
        self._led_state = cfg.get("led_state", "blinking")
        self._led_interval = float(cfg.get("led_interval", 0.5))

        interval = cfg.get("interval", {})
        self._add_update_cache("pods", int(interval.get("pods", 30)), self._update_pods)
        self._add_update_cache("nodename", int(interval.get("nodename", 120)), self._update_nodename, force=True)

    @property
    def pods(self) -> Dict[str, int]: return self._get_cache("pods")

    @property
    def scheduled_pods(self) -> int: return self.pods["scheduled"]

    @property
    def started_pods(self) -> int: return self.pods["started"]

    @property
    def ready_pods(self) -> int: return self.pods["ready"]

    @property
    def nodename(self) -> str: return self._get_cache("nodename")[0]

    def _update_nodename(self): return get_kubenode(self._config)

    def _update_pods(self):
        with kubernetes.client.ApiClient(self._config) as api_client:
            v1 = kubernetes.client.CoreV1Api(api_client)
            ret = v1.list_pod_for_all_namespaces(watch=False)
            started, ready, scheduled = 0, 0, 0
            for pod in ret.items:
                if not pod.spec.node_name == self.nodename:
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


class KubernetesNetMenu(Menu):
    def __init__(self, cfg: Dict[str, Any]):
        super().__init__(name="NET", cfg=cfg)
        self._config = get_kubeconfig(cfg=cfg)
        
        interval = cfg.get("interval", {})
        self._add_update_cache("nodename", int(interval.get("nodename", 120)), self._update_nodename, force=True)

    @property
    def nodename(self) -> str: return self._get_cache("nodename")[0]

    @property
    def ipaddress(self) -> str: return self._get_cache("nodename")[1]

    def _update_nodename(self): return get_kubenode(self._config)

    def _show(self, display: Display):
        display.write_line(self.nodename)
        display.write_line(self.ipaddress)