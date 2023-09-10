#!/bin/bash

g++ -fPIC -shared -o src/libgeometry/libgeom.so src/libgeometry/libgeom.cpp
# g++ -fPIC -shared -o src/process_verts.so src/process_verts.cpp -lGL -ldl