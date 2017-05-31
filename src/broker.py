import logging
import traceback

from mn_connector import *
from processor import *
from verificator import Verificator

from api.masternode_worker_pb2 import *


# TODO: Read version constants from build-specific configuration file
VER_MAJOR = 0
VER_MINOR = 1
VER_PATCH = 0
AGENT_NAME = 'neurowrk'

# TODO: Read constants from generic configuration file
TASKS_LIMIT = 3


class BusyError (Exception):
    pass


class Broker (WorkerServicer, ProcessorCallback):

    def __init__(self):
        # Set up masternode connections
        self.mn_connector = MNConnector(self)

        self.processors = []
        self.tasks = {}
        self.verificator = Verificator()

    def run(self):
        print("Starting masternode interface...")
        self.mn_connector.serve()
        print("Masternode interface started successfully")

    def spawn_processor(self) -> Processor:
        if len(self.processors) >= TASKS_LIMIT:
            logging.warning("Can't instantiate processor, number of tasks is to high")
            raise BusyError
        print("Instantiating processor...")
        processor = Processor(self)
        print("New processor instantiated successfully.")
        self.processors.append(processor)
        return processor

    #
    # Masternode-Worker RPC implementation
    #

    def ping(self, request, context):
        print("Got ping request from masternode.")
        return VersionInfo(major=VER_MAJOR, minor=VER_MINOR, patch=VER_PATCH, agent=AGENT_NAME)

    def suggest_peers(self, request, context):
        # TODO: Implement
        # Current response: I don't know anybody else :)
        return PeersList()

    def cognite_batch(self, request: CognitionRequest, context) -> CognitionResponse:
        print("Got cognite_batch request from masternode")
        # Verifying integrity, validity and legality
        if not self.verificator.verify_masternode(request.pub_key, request.signed_message):
            return CognitionResponse(
                accepted=False,
                decline_info=DeclinedTask(reason=DeclineReason.Value('UNVERIFIED'),
                                          message="Masternode didn't pass verification")
            )
        if not self.verificator.verify_neurocontract(request.contract_address):
            return CognitionResponse(
                accepted=False,
                decline_info=DeclinedTask(reason=DeclineReason.Value('UNVERIFIED'),
                                          message="Contract didn't pass verification")
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
            decline_reason = DeclinedTask(reason=DeclineReason.Value('BUSY'), message="Too many active tasks already")
        except IPFSError as ipfs:
            decline_reason = DeclinedTask(reason=DeclineReason.Value('IPFS_ERROR'), message=ipfs.message)
        except ModelInconsistencyError:
            decline_reason = DeclinedTask(reason=DeclineReason.Value('BROKEN_MODEL'), message="Model file is broken")
        except DataInconsistencyError:
            decline_reason = DeclinedTask(reason=DeclineReason.Value('BROKEN_DATA'), message="Data file is broken")
        except Exception as ex:
            traceback.print_exc()
            decline_reason = DeclinedTask(reason=DeclineReason.Value('INTERNAL_ERROR'),
                                          message="Internal exception of type %s" % type(ex))
        except:
            decline_reason = DeclinedTask(reason=DeclineReason.Value('INTERNAL_ERROR'), message="Unknown internal error")
        finally:
            if decline_reason is not None:
                logging.warning(decline_reason.message)
                return CognitionResponse(accepted=False, decline_info=decline_reason)

        return CognitionResponse(accepted=True, task_info=AcceptedTask(task_id=task_id, time_estimage=time_est))

    def batch_status(self, request, context) -> BatchStatus:
        processor = self.tasks[request.task_id]
        if processor is not None:
            return BatchStatus(active=True, time_estimate=processor.get_time_estimate())
        else:
            return BatchStatus(active=False, time_estimate=0)
