#!/bin/bash

python -m grpc_tools.protoc -Iprotobuf --python_out=src/api --grpc_python_out=src/api protobuf/masternode_worker.proto
