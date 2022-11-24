import dataclasses
import logging
from configparser import ConfigParser, RawConfigParser


@dataclasses.dataclass
class Configuration:
    formatter_string: str = '%(asctime)s - %(threadName)s : {%(name)s:%(lineno)d} : %(levelname)s : %(message)s'

    def __post_init__(self):
        self.__str__ = self.__repr__
        self.logger = logging.getLogger(__file__)

    def load_config_ini(self):
        for key in self.__annotations__:
            self.logger.warning(f'{key}')
            config_ini = RawConfigParser(inline_comment_prefixes='#')
            config_ini.read('config.ini')

            setattr(self,key,self.get_value(key,config_ini.get('top',key)))

    def get_value(self,key:str,value:str):
        self.logger.warning(type(getattr(self,key)).__name__)
        match type(getattr(self,key)).__name__:
            case str:
                return str(value)
            
