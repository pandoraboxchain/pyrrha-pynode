from concurrent import futures
import time
import math
import grpc

from api.masternode_pb2 import *
from api.masternode_pb2_grpc import *


_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class MNConnector(WorkerServiceServicer):
    """Provices methods that implement functionality for masternode worker endpoint"""

    def __init__(self):
        self.db = route_guide_resources.read_route_guide_database()
        pass

    @staticmethod
    def serve():
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        add_WorkerServiceServicer_to_server(
            MasternodeSerivceServicer(), server)
        server.add_insecure_port('[::]:50051')
        server.start()
        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            server.stop(0)
