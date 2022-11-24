import dataclasses
import threading
from typing import Optional, Callable, Any, Iterable, Mapping
import logging



@dataclasses.dataclass
class WatcherThread(threading.Thread):
    stop_thread= False
    restart_thread = False
    daemon = False
    exit_flag: threading.Event
    resource: str
    daemon_object: str
    daemon_method: str
    def __post_init__(self)->None:
        self.logger = logging.getLogger(__file__)
        threading.Thread.__init__(self, target=self.run)

    def stop(self) -> None:
        self.logger.warn(f'OK: thread {self.resource} is stopping')
        self.stop_thread = True

    def run(self) -> None:
        self.logger.warning(f'[start thread|watch {self.resource} -> {self.daemon_method}')

        try:
            getattr(self.daemon_object, self.daemon_method)(self.resource)
        except Exception as e:
            self.logger.error(e)
            self.restart_thread = True


