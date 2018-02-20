import threading
from abc import ABCMeta, abstractmethod
from jsonrpc import dispatcher
from jsonrpc.manager import JSONRPCResponseManager
from werkzeug.wrappers import Request, Response
from wsgiref.simple_server import make_server

from test.core.base_test_core import BaseCoreConfiguration


class BaseTestListener(threading.Thread):
    __metaclass__ = ABCMeta

    server = None
    configuration = None

    def __init__(self, host: str, configuration: BaseCoreConfiguration):
        host = host.replace('http://', '')
        host, port = host.split(':')
        self.server = make_server(host, int(port), self.application)
        self.configuration = configuration

    def stop(self):
        self.server.shutdown()

    def launch(self):
        self.server.serve_forever()

    @Request.application
    def application(self, request):
        dispatcher["eth_syncing"] = self.eth_syncing
        dispatcher["eth_call"] = self.eth_call
        dispatcher["eth_newFilter"] = self.eth_new_filter
        dispatcher["eth_getFilterChanges"] = self.eth_get_filter_changes

        dispatcher["eth_accounts"] = self.eth_accounts
        dispatcher["eth_estimateGas"] = self.eth_estimate_gas
        dispatcher["eth_blockNumber"] = self.eth_block_number
        dispatcher["eth_getBlockByNumber"] = self.eth_get_block_by_number
        dispatcher["eth_sendTransaction"] = self.eth_send_transaction

        response = JSONRPCResponseManager.handle(request.data, dispatcher)
        return Response(response.json, mimetype='application/json')

    @abstractmethod
    def eth_syncing(self):
        result = self.configuration.get_core_syncing_state()
        print("syncing : " + str(result))
        return result

    @abstractmethod
    def eth_call(self, params: dict, latest: str):
        result = self.configuration.eth_call(params, latest)
        print("call : " + str(result))
        return result

    @abstractmethod
    def eth_new_filter(self, args: dict, **kwargs):
        result = self.configuration.eth_new_filter(args, **kwargs)
        print("eth_new_filter : " + str(result))
        return result

    @abstractmethod
    def eth_get_filter_changes(self, *args, **kwargs):
        result = self.configuration.eth_get_filter_changes(*args, **kwargs)
        print("eth_get_filter_changes : " + str(result))
        return result

    @abstractmethod
    def eth_accounts(self, *args, **kwargs):
        result = self.configuration.eth_get_accounts(*args, **kwargs)
        print("eth_accounts : " + str(result))
        return result

    @abstractmethod
    def eth_estimate_gas(self, params: dict, **kwargs):
        result = self.configuration.eth_estimate_gas(params, **kwargs)
        print("eth_estimate_gas : " + str(result))
        return result

    @abstractmethod
    def eth_block_number(self, *args, **kwargs):
        result = self.configuration.eth_block_number(args, **kwargs)
        print("eth_block_number : " + str(result))
        return result

    @abstractmethod
    def eth_get_block_by_number(self, *args, **kwargs):
        result = self.configuration.eth_get_block_by_number(args, **kwargs)
        print("eth_get_block_by_number : " + str(result))
        return result

    @abstractmethod
    def eth_send_transaction(self, params: dict, **kwargs):
        result = self.configuration.eth_send_transaction(params, **kwargs)
        print("eth_send_transaction : " + str(result))
        return result


