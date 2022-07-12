'''
Basic Voynich stats
'''
# ==============================================================================
# Import
# ==============================================================================
import numpy as np
import pandas as pd

import sys
sys.path.insert(0, '../../voynpy')
from corpora import vms, vms1, vms2, plants1, fems, simp1, caesar

# ==============================================================================
# Collate and sort paragraph-starting tokens
# ==============================================================================