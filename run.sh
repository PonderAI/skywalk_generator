#!/bin/bash

samples=$1

Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
sleep 3

## python3 src/1_generate_cases.py $samples
## python3 src/2_run_cases.py
## python3 src/3_postprocess_cfd_data.py