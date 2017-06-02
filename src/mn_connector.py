from concurrent import futures
from collections import namedtuple
import time

from neuromwapi.messages import *
from neuromwapi.services import *


MWAPIConfig = namedtuple('MWAPIConfig', 'host port max_conns')

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class MNConnector:
    """Provices methods that implement functionality for masternode worker endpoint (MWAPI)"""

    def __init__(self, servicer: WorkerServicer, config: MWAPIConfig):
        self.config = config
        self.servicer = servicer
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.config.max_conns))
        add_WorkerServicer_to_server(
            self.servicer, self.server)

    def serve(self):
        addr = '%s:%d' % (self.config.host, self.config.port)
        self.server.add_insecure_port(addr)
        self.server.start()
        print("Listening for incoming masternode connections on %s" % addr)
        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            self.server.stop(0)
