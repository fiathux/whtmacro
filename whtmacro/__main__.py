# -*- coding: utf-8 -*-

import sys
import os

if not __package__:
  path = os.path.join(os.path.dirname(__file__), os.pardir)
  sys.path.insert(0, path)

from whtmacro import main

main()
