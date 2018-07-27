[![Codacy Badge](https://api.codacy.com/project/badge/Grade/a1b8a914ff5f48de9f15f944391b51a1)](https://www.codacy.com/app/dr-orlovsky/pyrrha-pynode?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=pandoraboxchain/pyrrha-pynode&amp;utm_campaign=Badge_Grade)
[![Build Status](https://travis-ci.org/pandoraboxchain/pyrrha-pynode.svg?branch=master)](https://travis-ci.org/pandoraboxchain/pyrrha-pynode)
# Pyrrha Python Node

Experimental node implementation for Pyrrha version of Pandora Boxchain providing computations using AI kernels on hardware
from providers. Current version is have rebuilded architecture

* Python 3.6+ support

## Quickstart

At the moment, the node has a basic startup configuration, to work with actual consensus contracts
from the main branch of the repository.
Base pynode configuration file are located in pynode/core/config folder and contains basic settings for
providing node launch.

On first launch
    easy_install --upgrade pip
    pip install -r requirements.txt

Knowing install problems
* problem with web3 install (Failed building wheel for cytoolz)
    - solution :
```sh    
    sudo apt-get install python3.6-dev
    sudo python3.6 -m pip install cytoolz
    sudo python3.6 -m pip install -r requirements.txt
```
* after pip installs package success and getting error on launch
"ModuleNotFoundError: No module named 'Crypto'"
    - solution :
```sh
pip uninstall crypto
pip uninstall pycrypto
```
and install it again
```sh
pip install crypto
pip install pycryptodome==3.6.1
```

* On Windows sometimes web3 cant import Crypto.Random
    - solution :
    Check for crypto package name and if its 'crypto' rename it to 'Crypto'

## IPFS problems

* The local ipfs daemon does not host a locally added file
   - solution :
   restart local daemon or ipfs node server

* IPFS The problem with ipfs with the unloading and accessibility of large files > 10MB
   - on adding big file significantly increases the time through which it will be available
   - any ideas are welcome

An easier way to use a docker

## Simple launch
Command for simple launch   
```sh
python pynode.py -p<password from local vault>
```   
After simple console launching in terminal will be printed launch information based on configs and launch settings
for example:
```sh
   Configuration file path      : ..\pynode\core\config\pynode.ini
   Config reading success
   Pynode production launch
   Node launch mode             : 0
   Ethereum use                 : remote
   Ethereum host                : http://rinkeby.pandora.network:8545
   Worker node account owner    : 0x08eCFDAc62152BebFCD4C217aE7e377a8A2cAdc6
   Primary contracts addresses
   Pandora main contract        : 0x9f301cfd1217fd60e4244a12b1edffe458e8b9bd
   Worker node contract         : 0x6ac66706c9eF0b2A6eD6B471fb2d086d0C7BC055
   IPFS configuration
   IPFS use                     : pandora
   IPFS host                    : http://ipfs.pandora.network
   IPFS port                    : 5001
   IPFS file storage            : tmp
   Web socket enable            : False
   ABI folder path              : ../pyrrha-consensus/build/contracts/
``` 
and pynode perform launch in current console thread.

-- pynode ver 0.1.2, pynode-core ver 0.1.2
- update batches logic
- refactor filter events
- refactor kernel and dataset parsers

-- pynode ver 0.1.1, pynode-core ver 0.1.1
- update web3 py to 4.2.1 version for pynode and tools
- improve security and transaction methods
- documents up to date

-- pynode ver 0.1.0-alpha, pynode-core ver 0.1.0-alpha
- make installer for core module (current version is 0.1.0-alpha)

-- ver 0.1.1
- at current version account logic are updated (Always satisfied but not mandatory) see more in logs

### Local tests launching
All tests is based in folder test and can be launched by 
```sh
python launcher_test.py
```

## Use Docker
Current pynode version support creating Docker images.
When your double check yor launch settings its possible to create Docker image
from project folder execute
```sh
docker-compose build 
``` 
and for launch container 
```sh
docker-compose up
```   
In current time launch command for docker is 
   CMD ["python",  "./pynode.py", "-p","<your_vault_password>", "-c", "core/config/pynode.ini", "-i", "pandora", "-e", "remote", "-a", "../abi/"]
which are duplicate default settings, your can config pynode as your needed and rebuild container with 
your launch parameters
   
   
   
Current remote deployment for testing and PoC

======== KERNEL  =========
  - KERNEL for training 
    - 0xC59C2f5e9e5e38bcf55CDfaB6450155967a1a65F
    - ipfs address : QmRRRboNgF2169kTGozNPF6VmYSZWbrwbfoo9Fag5JZqLi (model)
 
  - KERNEL for prediction
    - 0x2e1bc6cDca93c6C22C4A067C317177f5EF412E10
    - ipfs address : QmRRRboNgF2169kTGozNPF6VmYSZWbrwbfoo9Fag5JZqLi (model)
    - ipfs address : QmRuocz82HetMMmLAFBuBGxNmpeUCCCpQqhSreYRMD6vBL (weights)
   
======== DATASET =========
  - DATASET for training
    - 0x6a9d4A8BB2aa5B5BafA7a5e04234410829688F60
    - ipfs address : QmeZ5Ra4NsSVqTv5T6jiDKM7yDVKPmwDH94Sfuyy3Knd1d 
      - "train_x":"QmQNWiv1s7rhoUrfELCtK65VZGbTE79Bfa3kkoeFf7aVQA"
      - "train_y":"QmT3keTG7fXrPRZApjwVWvZDamLC5LeyvQLou4rSJLJJEj"

  - DATASET for predict (one batch)
    - 0x2632103cfD39Bdd1A9f170f26A0295dbaFeeBb85
    - ipfs address : QmfLq32vssJ8RmcT49cFtUmFm3Rw2MozWhkTRRFyKbobX8
        - batch ipfs address : QmYhL15VowVXhUPms1VhTcmeVBjxWZhNEQ5kpdo5kBoPYY
  
  - DATASET fro predict (two batches)
    - 0x0dbE74b60c588DFc3b6aeB973e78B4748e499979
    - ipfs address : QmRqqir1e2BL91vRmCfuQQcbTRHgU6jJKNXGFb7pvQxGgW
        - batch ipfs address : QmYhL15VowVXhUPms1VhTcmeVBjxWZhNEQ5kpdo5kBoPYY
        - batch ipfs address : QmWFKhJK4fuE2ixnyysRVnRk4WAcvGVpHPpvsUTNn4zKLW
  