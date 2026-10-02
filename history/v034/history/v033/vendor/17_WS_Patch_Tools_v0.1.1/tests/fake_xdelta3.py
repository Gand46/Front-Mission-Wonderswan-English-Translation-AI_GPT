#!/usr/bin/env python3
import sys,shutil
args=sys.argv[1:]
if '-V' in args:
    print('xdelta3 3.2.0 fake-selftest'); raise SystemExit
if '-e' in args:
    # xdelta3 -e -s SOURCE TARGET PATCH
    shutil.copyfile(args[-2],args[-1]); raise SystemExit
if '-d' in args:
    # xdelta3 -d -s SOURCE PATCH OUTPUT
    shutil.copyfile(args[-2],args[-1]); raise SystemExit
raise SystemExit(2)
