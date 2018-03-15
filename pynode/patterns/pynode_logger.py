import logging
from manager import Manager


class LogSocketHandler(logging.Handler):

    __instance = None

    @staticmethod
    def get_instance():
        if LogSocketHandler.__instance is None:
            LogSocketHandler()
        return LogSocketHandler.__instance

    def __init__(self):
        if LogSocketHandler.__instance is None:
            LogSocketHandler.__instance = self
        logging.basicConfig(level=logging.INFO,
                            format='(%(threadName)-10s) %(levelname)s: %(message)s')
        logging.Handler.__init__(self, level=logging.INFO)

    def emit(self, record):
        if Manager.get_instance().web_socket_enable == 'True':
            from webapi.web_socket_listener import WebSocket
            socket = WebSocket.get_instance()
            socket.update_log_record(record)


