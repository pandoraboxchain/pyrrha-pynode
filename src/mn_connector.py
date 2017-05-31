from concurrent import futures
import time

from api.masternode_worker_pb2 import *
from api.masternode_worker_pb2_grpc import *


_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class MNConnector:
    """Provices methods that implement functionality for masternode worker endpoint"""

    def __init__(self, servicer: WorkerServicer):
        self.servicer = servicer
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        add_WorkerServicer_to_server(
            self.servicer, self.server)

    def serve(self, port='[::]:50051'):
        self.server.add_insecure_port(port)
        self.server.start()
        print("Listening for incoming masternode connections on %s" % port)
        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            self.server.stop(0)
