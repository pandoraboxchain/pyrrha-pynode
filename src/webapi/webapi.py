from collections import namedtuple
from abc import ABCMeta, abstractmethod

WebAPIConfig = namedtuple('WebAPIConfig', 'host port')


class Status:
    def __init__(self):
        pass


class WebAPIDelegate:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_status(self) -> Status:
        pass


class WebAPI:
    def __init__(self, config: WebAPIConfig, delegate):
        pass

    def run(self):
        pass
