#!/bin/bash

g++ -fPIC -shared -o \
src/libgeometry/libgeom.so \
src/libgeometry/fakeglm.cpp \
src/libgeometry/libgeom.cpp \
-Ofast


# g++ -fPIC -shared -o src/process_verts.so src/process_verts.cpp -lGL -ldl