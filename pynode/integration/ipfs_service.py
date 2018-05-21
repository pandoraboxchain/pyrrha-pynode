from abc import ABCMeta, abstractmethod


class IpfsAbstract(metaclass=ABCMeta):

    @abstractmethod
    def connect(self, server='localhost', port=5001, data_dir='../tmp'):
        pass

    @abstractmethod
    def download_file(self, file_address: str):
        pass

    @abstractmethod
    def upload_file(self, file_name: str):
        pass


class IpfsService(IpfsAbstract):

    def __init__(self, strategic: IpfsAbstract):
        self.strategy = strategic

    def connect(self, server='localhost', port=5001, data_dir='../tmp'):
        self.strategy.connect(server=server, port=port, data_dir=data_dir)

    def download_file(self, file_address: str):
        return self.strategy.download_file(file_address=file_address)

    def upload_file(self, file_name: str):
        return self.strategy.upload_file(file_name=file_name)


