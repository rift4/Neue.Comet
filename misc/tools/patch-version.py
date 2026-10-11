# Updates "?v=x" in files
#
# The fonts ship unversioned, so there is no version to stamp. The cache
# busters are now build timestamps (see build_version in defs.html) and the
# "?v=" query strings are stripped instead of rewritten, leaving the URL to
# be cached normally.
import os, sys, re
from os.path import dirname, basename, abspath, relpath, join as pjoin
sys.path.append(abspath(pjoin(dirname(__file__), 'tools')))
from common import BASEDIR

def updateCSSFile(filename):
  regex = re.compile(r'(url\("[^"]+?)v=[^"]*("\))')
  with open(filename, 'r') as f:
    s = f.read()
  s = regex.sub(lambda m: '%s%s' % (m.group(1), m.group(2)), s)
  with open(filename, 'w') as f:
    f.write(s)


def updateHTMLFile(filename):
  regex = re.compile(r'((?:href|src)="[^"]+?)v=[^"]*(")')
  with open(filename, 'r') as f:
    s = f.read()
  s = regex.sub(lambda m: '%s%s' % (m.group(1), m.group(2)), s)
  with open(filename, 'w') as f:
    f.write(s)

for fn in sys.argv[1:]:
  if fn.endswith(".css"):
    updateCSSFile(fn)
  elif fn.endswith(".html"):
    updateHTMLFile(fn)
  else:
    raise "Unexpected file type %r" % fn
