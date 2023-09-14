#!/bin/bash

g++ -fPIC -shared -o \
shared_libs/geometry/libgeom.so \
shared_libs/geometry/fakeglm.cpp \
shared_libs/geometry/libgeometry.cpp \
-Ofast

mv shared_libs/geometry/libgeom.so src/libgeometry/libgeom.so
