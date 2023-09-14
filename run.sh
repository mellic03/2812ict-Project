#!/bin/bash


./buildcpp.sh
source venv/bin/activate
python3 src/main.py USE_CPP
