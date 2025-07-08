# -*- coding: utf-8 -*-

import pdb
from datetime import date
from datetime import datetime, timedelta
import os 
import glob
import shutil
import threading
import subprocess
from time import sleep
import locale
import zipfile
locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
import sys
from wx_decomp import *

# Add o diretorio das bibliotecas da WX
sys.path.insert(1, sys.path[0] + "/libs/")
from wx_opweek import ElecData
from wx_opweek import getLastSaturday

base='DADGNL.RV1'
ent='DADGNL.RV2'
out='DADGNL.teste'
comenta_dadgnl_v1(base,ent,out)
pdb.set_trace()
