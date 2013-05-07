import sys, os, bottle

sys.path=[os.getcwd()] + sys.path
os.chdir(os.path.dirname(__file__))

import microreader

application = bottle.default_app()

