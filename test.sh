#!/bin/bash
python3 -m pytest test/test_rsa.py -W ignore::DeprecationWarning
