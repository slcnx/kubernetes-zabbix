import dataclasses
import logging
import threading
import time


@dataclasses.dataclass
class TimedThread(threading.Thread):
    stop_thread = False
    restart_thread = False
    daemon = True

    exit_flag:threading.Event
    resource: str
    daemon_object: str
    daemon_method: str

    delay_first_run: bool = False
    delay_first_run_seconds: int=60
    cycle_interval_seconds:int = 30
    def __post_init__(self)->None:
        self.logger = logging.getLogger(__file__)
        threading.Thread.__init__(self, target=self.run)

    def stop(self) -> None:
        self.logger.warning(f'OK: thread {self.resource} is stopping')
        self.stop_thread = True
        self.exit_flag.set()

    def run(self) ->None:
        # 延迟启动
        if self.delay_first_run:
            self.logger.warning(f'{self.resouce} -> {self.daemon_method} | 延迟{self.delay_first_run_seconds}s开始运行 [运行周期 {self.cycle_interval_seconds}s]')
            time.sleep(self.delay_first_run_seconds)

            try:
                self._run(first_run=True)
            except Exception as e:
                self.logger.exception(e)


        # 非延迟启动
        while not self.exit_flag.wait(self.cycle_interval_seconds):
            try:
                self._run(first_run=True)
            except Exception as e:
                self.logger.exception(e)
                self.logger.error(f'循环运行失败 {self.resource}.{self.daemon_method} [周期 {self.cycle_interval_seconds}]\n {self.cycle_interval_seconds}s后重试...')
                time.sleep(self.cycle_interval_seconds)
        self.logger.warning(f'timed线程终止 {self.resource}.{self.daemon_method} ')


    def _run(self,first_run:bool=False)->None:
        if first_run:
            self.logger.debug(f'首次运行timed线程 {self.resource}.{self.daemon_method} [周期 {self.cycle_interval_seconds}] ')
        else:
            self.logger.debug(f'循环运行timed线程 {self.resource}.{self.daemon_method} [周期 {self.cycle_interval_seconds}] ')
        getattr(self.daemon_object,self.daemon_method)(self.resource)
        self.logger.debug(f'运行timed线程完成 {self.resource}.{self.daemon_method} [周期 {self.cycle_interval_seconds}] ')



