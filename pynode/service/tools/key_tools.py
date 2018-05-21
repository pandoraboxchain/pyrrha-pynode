import os
import logging
from pathlib import Path
from hashlib import md5
from base64 import b64decode
from Crypto.Cipher import AES


class KeyTools:

    BLOCK_SIZE = 16  # Bytes
    pad = None
    unpad = None

    logger = None

    vault_path = None
    vault_folder = 'vault'
    vault_name = 'worker_node_key.pri'

    def __init__(self):
        self.logger = logging.getLogger("Key Tool")
        self.pad = lambda s: s + (self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE) * \
                         chr(self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE)
        self.unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    def check_vault(self):
        vault_folder = Path(os.getcwd()+'/'+self.vault_folder)
        if os.path.exists(vault_folder) is False:
            os.makedirs(vault_folder)
        vault_file = Path(str(vault_folder)+'/'+self.vault_name)
        if os.path.isfile(vault_file) is False:
            open(vault_file, 'a').close()
            self.vault_path = vault_file
            return False
        if os.path.getsize(vault_file) is 0:
            self.vault_path = vault_file
            return False
        self.vault_path = vault_file
        return True

    def obtain_key(self, vault_password: str) -> str:
        try:
            vault_password = md5(vault_password.encode('utf8')).hexdigest()
            vault_file = open(self.vault_path, "rb")
            enc = b64decode(vault_file.read())
            iv = enc[:16]
            cipher = AES.new(vault_password.encode('utf8'), AES.MODE_CBC, iv)
            result = self.unpad(cipher.decrypt(enc[16:])).decode('utf8')
        except Exception as ex:
            self.logger.info('Wrong password. Exception due key obtaining.')
            self.logger.info(ex.args)
            return None
        return result


