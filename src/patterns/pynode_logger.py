import logging


class LogSocketHandler(logging.Handler):

    __instance = None
    logger = None

    @staticmethod
    def get_instance():
        if LogSocketHandler.__instance is None:
            LogSocketHandler()
        return LogSocketHandler.__instance

    def __init__(self):
        if LogSocketHandler.__instance is None:
            LogSocketHandler.__instance = self
        logging.Handler.__init__(self, level=logging.INFO)

    def emit(self, record):
        from webapi.web_socket_listener import WebSocket
        socket = WebSocket.get_instance()
        socket.update_log_record(record)


