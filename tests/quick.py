from cltoolkit import Wordlist
from pyclts import CLTS
import sys
from cltoolkit.util import *

sys.path.append(cltoolkit_test_path("repos", "carvalhopurus"))
sys.path.append(cltoolkit_test_path("repos", "wangbcd"))

clts = CLTS(cltoolkit_test_path("repos", "clts"))
wl2 = Wordlist.from_lexibank(["carvalhopurus", "wangbcd"])
