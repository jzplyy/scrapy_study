from pathlib import Path
import sys
import os

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
PRIVATE_KEY_PATH = os.path.join(BASE_DIR, 'private_key.pem')

from .utils import *
from .mail import *

