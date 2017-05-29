from .singleton import Singleton

from .mn_connector import *
from .processor import *
from .verificator import Verificator

from api.masternode_worker_pb2 import *


VER_MAJOR = 0
VER_MINOR = 1
VER_PATCH = 0
AGENT_NAME = 'neurowrk'

TASKS_LIMIT = 3


class BusyError (Exception):
    pass


class Broker (WorkerServicer):

    def __init__(self):
        # Set up masternode connections
        self.mn_connector = MNConnector(self)

        self.processors = []
        self.tasks = {}
        self.verificator = Verificator()

    def run(self):
        self.mn_connector.serve()

    def spawn_processor(self) -> Processor:
        if len(self.processors) >= TASKS_LIMIT:
            raise BusyError
        processor = Processor(self)
        self.processors += processor
        return processor

    #
    # Masternode-Worker RPC implementation
    #

    def ping(self, request, context):
        return VersionInfo(major=VER_MAJOR, minor=VER_MINOR, patch=VER_PATCH, agent=AGENT_NAME)

    def suggest_peers(self, request, context):
        # TODO: Implement
        # Current response: I don't know anybody else :)
        return PeersList()

    def cognite_batch(self, request: CognitionRequest, context) -> CognitionResponse:
        # Verifying integrity, validity and legality
        if not self.verificator.verify_masternode(request.pub_key, request.message):
            return CognitionResponse(
                accepted=False,
                payload=DeclinedTask(reason=DeclineReason.UNVERIFIED, message="Masternode didn't pass verification")
            )
        if not self.verificator.verify_neurocontract(request.contract_address):
            return CognitionResponse(
                accepted=False,
                payload=DeclinedTask(reason=DeclineReason.UNVERIFIED, message="Contract didn't pass verification")
            )

        task_id, time_est = None, None
        decline_reason = None
        # Run batch processor
        try:
            processor = self.spawn_processor()
            task_id, time_est = processor.cognite_batch(
                request.arch_address, request.model_address, request.data_address
            )
            self.tasks[task_id] = processor
        except BusyError:
            decline_reason = DeclinedTask(reason=DeclineReason.BUSY, message="Too many active tasks already")
        except IPFSError as ipfs:
            decline_reason = DeclinedTask(reason=DeclineReason.IPFS_ERROR, message=ipfs.message)
        except ModelInconsistencyError:
            decline_reason = DeclinedTask(reason=DeclineReason.BROKEN_MODEL, message="Model file is broken")
        except DataInconsistencyError:
            decline_reason = DeclinedTask(reason=DeclineReason.BROKEN_DATA, message="Data file is broken")
        except Exception as ex:
            decline_reason = DeclinedTask(reason=DeclineReason.INTERNAL_ERROR,
                                          message="Internal exception of type %s" % type(ex))
        except:
            decline_reason = DeclinedTask(reason=DeclineReason.INTERNAL_ERROR, message="Unknown internal error")
        finally:
            if decline_reason is not None:
                return CognitionResponse(accepted=False, payload=decline_reason)

        return CognitionResponse(accepted=True, payload=AcceptedTask(task_id=task_id, time_estimage=time_est))

    def batch_status(self, request, context) -> BatchStatus:
        processor = self.tasks[request.task_id]
        if processor is not None:
            return BatchStatus(active=True, time_estimate=processor.get_time_estimate())
        else:
            return BatchStatus(active=False, time_estimate=0)
