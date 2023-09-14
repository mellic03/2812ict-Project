#!/bin/bash

#  -fPIC -shared -o 

g++ -fPIC -shared -o src/client/libclient.so \
shared_libs/netcode/common/ng_common.cpp \
shared_libs/netcode/client/ng_client.cpp \
shared_libs/netcode/server/ng_server.cpp \
shared_libs/netcode/client/main.cpp -Ofast



g++ \
shared_libs/netcode/common/ng_common.cpp \
shared_libs/netcode/client/ng_client.cpp \
shared_libs/netcode/server/ng_server.cpp \
shared_libs/netcode/server/main.cpp -g -o faceserver

