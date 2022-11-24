import dataclasses
import logging
import signal
import sys
import threading
from pprint import pformat

from config import Configuration
from timedthread import TimedThread
from watcherthread import WatcherThread
from kubernetes import client, watch
from kubernetes.client import ApiClient, CoreV1Api, AppsV1Api,EventsV1Api
from kubernetes import config as kube_config

@dataclasses
class CheckDaemon:
    manage_threads: list[WatcherThread|TimedThread]
    discovery_interval: int
    api_zabbix_interval: int = 60
    rate_limit_seconds: int = 30
    data_resend_interval: int = 30
    exit_flag: threading.Event = threading.Event()

    kube_config.load_kube_config()
    api_client:ApiClient = kube_config.new_client_from_config()

    # Kubernetes API
    core_v1:CoreV1Api = client.CoreV1Api(api_client)
    apps_v1:AppsV1Api = client.AppsV1Api(api_client)
    extensions_v1:EventsV1Api = client.EventsV1Api(api_client)

    # config
    config: Configuration
    resources: list[str]
    def __post_init__(self) -> None:
        self.logger = logging.getLogger(__file__)

    def run(self) -> None:
        self.start_data_threads()

    def handler(self,signum):
        if signum in [signal.SIGTERM]:
            self.logger.info(f'处理信号{signum}, 3s停止')
            self.exit_flag.set()
            for thread in self.manage_threads:
                thread.join(timeout=3)
            self.logger.info('All threads exited... exit check_kubernetesd')
            sys.exit(0)

    def start_data_threads(self) -> None:
        thread: WatcherThread|TimedThread

        thread = TimedThread("pods", self.data_resend_interval, self.exit_flag,
                             daemon_object=self, daemon_method='watch_data')
        self.manage_threads.append(thread)
        thread.start()

    def watch_data(self,resource: str) ->None:
        while True:
            w = watch.Watch()
            for obj in w.stream(self.core_v1.list_service_for_all_namespaces, **{"timeout_seconds": 30 }):
                self.watch_event_handler(resource, obj)

            self.logger.debug(f"获取数据完成 >>>{resource}<<<, 重启")

    def watch_event_handler(self, resource: str, event: dict) -> None:
        obj = event['object'].to_dict()
        event_type = event['type']
        name = obj['metadata']['name']
        namespace = str(obj['metadata']['namespace'])

        self.logger.warning(f"{event_type} [{resource}]: {namespace}/{name} : >>>{pformat(obj, indent=2)}<<<")