#!/usr/bin/python3

import sys
import re
import numpy as np


params = dict()
for fname in sys.argv[2:]:
    new_fname = re.sub(r'(.csv)', '', fname)
    params[new_fname] = np.loadtxt(fname, comments='%', delimiter=',')
    np.savez(sys.argv[1], **params)
