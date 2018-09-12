[![Codacy Badge](https://api.codacy.com/project/badge/Grade/a1b8a914ff5f48de9f15f944391b51a1)](https://www.codacy.com/app/dr-orlovsky/pyrrha-pynode?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=pandoraboxchain/pyrrha-pynode&amp;utm_campaign=Badge_Grade)
[![Build Status](https://travis-ci.org/pandoraboxchain/pyrrha-pynode.svg?branch=master)](https://travis-ci.org/pandoraboxchain/pyrrha-pynode)
# Pyrrha Python Node

Python implementation of worker node for Pyrrha protocol for computations
using AI kernels using hardware from providers.
This version has:
* Rebuilt architecture
* Changed events listening logic.
* Python 3.6+ support

## Initial setup/update

```sh
    git clone --recurse-submodules https://github.com/pandoraboxchain/pyrrha-pynode.git
```

## Preparing for launch
This version works in a testnet Ethereum environment Rinkeby.
* Create Ethereum Rinkeby wallet by MetaMask 
* Send him at least 1ETH or get free ETH from Rinkeby faucet https://faucet.rinkeby.io/
* For next steps please provide your Rinkeby wallet address for white-listing procedure

## White-listing
To pass the procedure, please provide to us your Rinkeby wallet address by creating issue or email us to: <br/>
  korostelyov@pandoraboxchain.ai <br/>
  ukolova@pandoraboxchain.ai <br/>

## Quickstart
At the moment, the node has a basic startup configuration, to work with actual consensus contracts
from the main branch of the repository. 
Base pynode configuration file are located in pynode/core/config folder and contains basic settings for
providing node launch.

Before first launch
```sh
    pip install -r requirements.txt
```

## Worker Node contract creation
To start the node you need to create a working contract in a consensus environment.
After confirmation of the white-listing of your Rinkeby wallet address please use our internal tool
to create worker node contract and finish basic setup.
```sh
    cd tools
    python ./worker_tools.py -a <Your white-listed Rinkeby wallet address>
```
This tool will ask your for private key from your Rinkeby wallet and for local launch password.<br/>
It will create/overwrite pyrrha-pynode/vault/worker_node_key.pri file with your private key encrypted by provided password.<br/>
When tool finishes, contract address will be added to pyrrha-pynode/pynode/config/pynode.ini into the following field <br/>
[Contracts] <br/>
worker_node= 'worker node contract address'

## WARNING
To prevent data loss, please make a backup of
* Personal password for pynode launch
* pyrrha-pynode/vault/worker_node_key.pri file
* pyrrha-pynode/pynode/config/pynode.ini file

In case of loss, this data can not be restored!!!
 
## Simple launch
Command for simple launch   
```sh
    python pynode.py -p '<Personal password for pynode launch>'
```   
Launch information based on configs and initial settings will be printed to terminal
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
and pynode perform launch in current console thread. <br/>
If everything is done correctly the current node state and blocks listening process will be displayed.
```sh
    (Thread-2  ) INFO: Contract WorkerNode initial state is Idle
    (Thread-2  ) INFO: POLL_INTERVAL : 15 sleep_time : 14.5 block_number : 2975447
    (Thread-2  ) INFO: POLL_INTERVAL : 15 sleep_time : 14.5 block_number : 2975448
    (Thread-2  ) INFO: POLL_INTERVAL : 15 sleep_time : 14.5 block_number : 2975449
    (Thread-2  ) INFO: POLL_INTERVAL : 15 sleep_time : 14.5 block_number : 2975450
    ...
``` 
Node is running and in standby mode.

### Local tests launching
All tests is based in folder test and can be launched by 
```sh
    python launcher_test.py
```

### Use Docker 
Current pynode version support creating Docker images. <br/>
When your double check yor launch settings its possible to create Docker image by docker-compose
```sh 
    docker-compose build 
``` 
 and for launch container 
```sh 
    docker-compose up
```
In current time launch command for docker is <br/> 
```sh 
    CMD ["python", "./pynode.py", "-p","<your_vault_password>", "-c", "core/config/pynode.ini", "-i", "pandora", "-e", "remote", "-a", "../abi/"] 
```
which are duplicate default settings, your can config pynode as your needed and rebuild container with your launch parameters 
 
### Versions review
-- pynode ver 0.1.3, pynode-core ver 0.1.3
- improve job working mechanism
- improve filter events listener

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

 
### Knowing install problems
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
    pip install crypto
```
* On Windows sometimes web3 cant import Crypto.Random
    - solution :
    Check for crypto package name and if its 'crypto' rename it to 'Crypto'
* Sometimes pip unable to install keras and tensorflow.
    - in current version keras=2.0.8, tensorflow=1.3.0 are used. 
    - solution:
    Try to install it manually from console.
* The local ipfs daemon does not host a locally added file
   - solution :
   restart local daemon or ipfs node server

### Preloaded test data
======== KERNEL  =========
  - KERNEL for training on 48 epochs
    - contract: 0x0Cb9dBDe49be9040EAF2d200cDA874aF44bf7f29
  - KERNEL for training on 100 epochs
    - contract: 0x6b54fB95b48944f16b198706BEE7fdC6d0230Fe2
  - KERNEL for prediction
    - contract: 0x744cA86eD4A0ead226ABCAd6349FDbCfb82912c1
   
======== DATASET =========
  - DATASET for training on 48 epochs
    - contract: 0xfA80239654c087399D94B0FbFec2Cfb7280C16D9
  - DATASET for training on 100 epochs
    - contract: 0xcf18C44C1e41A47551A9c9f299ecB36E1F44083A
  - DATASET for predict (one batch with 100 items)
    - contract: 0x3f8542f22E715D8C840A7261aaa9323232EA8F63
  - DATASET for predict (one batch with 50 items)
    - contract: 0xc652aF842b37815D0B7FD8BEE15F28210Bf7e0DB
  - DATASET for predict (one batch with 10 items)
    - contract: 0x6Da1722bdDcfCB949087BaFA51f86ab6cAeB5413
  - DATASET for predict (two batches by 100 items)
    - contract: 0xE14D4e300DadD764687B906Eb8269304edFf9D28
  - DATASET for predict (three batches by 100 items)
    - contract: 0x69D3C2556EF35D59526C9Ab6814722Bde5A269C2
  
======== JOB EXAMPLES ========= <br/>
```sh
COGNITIVE JOB TRAIN_100
JOB_TYPE   : Training
KERNEL     : 0x6b54fB95b48944f16b198706BEE7fdC6d0230Fe2
DATASET    : 0xcf18C44C1e41A47551A9c9f299ecB36E1F44083A
```
```sh
COGNITIVE JOB PREDICT_100 
JOB_TYPE   : Prediction 
KERNEL     : 0x744cA86eD4A0ead226ABCAd6349FDbCfb82912c1
DATASET    : 0x3f8542f22E715D8C840A7261aaa9323232EA8F63
```