import ipfsapi
import os
import requests
import time
import math
import logging
import sys

from integration.ipfs_service import IpfsAbstract


class IpfsConnector(IpfsAbstract):

    connector = None
    data_dir = None
    chunk_size = 4096

    logger = logging.getLogger("IpfsConnector")

    def connect(self, server='localhost', port=5001, data_dir='../tmp'):
        self.connector = ipfsapi.connect(server, port)
        if data_dir not in os.getcwd():
            os.chdir(data_dir)
        return self.connector

    # new version for data downloader implementation
    def download_file(self, file_address: str):
        try:
            # for downloading use https getaway
            host_remote = 'https://gateway.ipfs.io/ipfs/'
            with open(file_address, "wb") as f:
                self.logger.info("Search IPFS for data : " + file_address)
                start = time.time()
                try:
                    return self.connector.get(file_address)
                    #response = requests.get(host_remote + file_address, stream=True, timeout=120)
                except Exception as ex:
                    if isinstance(ex.args, tuple):
                        str_exception = ex.args[0].args[0]
                        if 'Read timed out' in str(str_exception):
                            self.logger.info('Get file by getaway timed out try get by ipfs API')
                            return self.connector.get(file_address)
                # for getting data vs ipfs https comment sting below
                response = requests.get(host_remote + file_address, stream=True, timeout=120)
                total_length = response.headers.get('content-length')

                if total_length is None:  # no content length header
                    f.write(response.content)
                else:
                    total_iterations = math.ceil(int(total_length) / self.chunk_size)
                    if total_iterations > 1:
                        self.print_progress_bar(0,
                                                total_iterations,
                                                prefix='Download:',
                                                suffix='Complete',
                                                length=50)
                    current_iteration = 0
                    for data in response.iter_content(chunk_size=self.chunk_size):
                        f.write(data)
                        current_iteration = current_iteration + 1
                        self.print_progress_bar(current_iteration,
                                                total_iterations,
                                                prefix='Download:',
                                                suffix='Complete',
                                                length=50)
                    end = time.time()
                    elapse = end - start
                    self.logger.info("File size                        : " + str(total_length))
                    self.logger.info("Operation complete success. time : " + str(elapse))
        except Exception as ex:
            self.logger.info("Operation exception.")
            self.logger.info(ex.args)
        return f

# old download impl by sync library
#    def download_file(self, file_address: str):
#        return self.connector.get(file_address)

    def upload_file(self, file_name: str):
        return self.connector.add(file_name)['Hash']

    # -------------------------------------
    # Print iterations progress
    # -------------------------------------
    def print_progress_bar(self, iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        message = '\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix)
        # simple solution working correctly only on unix like systems
        # self.logger.info(message)
        sys.stdout.write(message)
        sys.stdout.flush()
        # Print New Line on Complete
        if iteration == total:
            sys.stdout.write('\r\n')
            sys.stdout.flush()
