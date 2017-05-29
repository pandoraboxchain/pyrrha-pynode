from concurrent import futures
import time

from api.masternode_pb2 import *
from api.masternode_pb2_grpc import *

from .singleton import Singleton


_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class MasternodeRequestsServicer(WorkerServiceServicer):

    def CogniteBatch(self, request, context):
        pass


class MNConnector(Singleton):
    """Provices methods that implement functionality for masternode worker endpoint"""

    def __init__(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        add_WorkerServiceServicer_to_server(
            MasternodeRequestsServicer(), self.server)

    def serve(self, port='[::]:50051'):
        self.server.add_insecure_port(port)
        self.server.start()
        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            self.server.stop(0)
