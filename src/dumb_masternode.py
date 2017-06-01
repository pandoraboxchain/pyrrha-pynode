from api.masternode_worker_pb2 import *
from api.masternode_worker_pb2_grpc import *


def worker_ping(stub: WorkerStub) -> VersionInfo:
    print('Pinging worker...')
    resp = stub.ping(VersionInfo(major=0, minor=1, patch=0, agent='dumb_masternode'))
    print('Got version %d.%d.%d; masternode powered by %s' % (resp.major, resp.minor, resp.patch, resp.agent))
    return resp


def worker_cognite_batch(stub: WorkerStub) -> CognitionResponse:
    print('Sending batch of work for cognition...')
    # Keras1 VGG16 arch: QmZ4WTy97oAEmn89hbZCijKFsYrki5RPTHvXbYqJtAi9N6
    #              weights: QmfQ6qBGjHWb7K3oTYmUKxQytcYKyAZfDrLPXKMFhYiEAq
    # Keras2 VGG16 arch: QmNqqnk23MvQL8w5nbxaNYCnVNyYZdP7HxB8Td2QYdQh78
    #              weights:
    req = CognitionRequest(arch_address='QmNqqnk23MvQL8w5nbxaNYCnVNyYZdP7HxB8Td2QYdQh78', # VGG16 architecture
                           model_address='QmfQ6qBGjHWb7K3oTYmUKxQytcYKyAZfDrLPXKMFhYiEAq', # Pre-trained VGG16 model
                           data_address='QmNxi5m9oZekHcfddayPwKNmsFfBGAP39CZXSnjnC2yF6B', # 7 sample images
                           samples_count=1,
                           pub_key='',
                           signed_message='',
                           contract_address='')
    resp = stub.cognite_batch(req)
    if resp.accepted:
        print('Batch accepted, task id %s, estimated time %d' %
              (resp.task_info.task_id, resp.task_info.time_estimate))
    else:
        print('Batch rejection, reason #%d: %s' %
              (resp.decline_info.reason, resp.decline_info.message))
    return resp


def main(argv):
    print('Starting dumb masternode...')
    channel = grpc.insecure_channel('localhost:50051')
    stub = WorkerStub(channel)
    worker_ping(stub)
    worker_cognite_batch(stub)


if __name__ == "__main__":
    main(sys.argv)
