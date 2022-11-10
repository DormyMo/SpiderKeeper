#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from SpiderKeeper.run import main

main()
