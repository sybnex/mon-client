#!/usr/bin/env python3
# -*- coding: utf-8 -*-

if __name__ == '__main__':
    try:
        import os
        import sys
        import yaml
        import psutil
        import pprint
        import datetime
        import platform
        import warnings
        import elasticsearch
    except Exception as x:
        print("ERROR:", x)
        sys.exit(1)
    else:
        print("INFO: tests are all good")
        sys.exit(0)
