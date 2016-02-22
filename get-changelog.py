#!/usr/bin/env python
# coding: utf-8
#
# usage:
#
# chmod +x get_changelog.py
# ./get-changelog [PATH_OF_GIT_PROJECT] [TMP_FILE]
#
import re
import sys
import os
import datetime

out = "cd " + sys.argv[1] + " && git log --format='* %at - %cn <%ce>%n-%h - %s%n' --first-parent > " + sys.argv[2]
os.system(str(out))

with open(sys.argv[2], 'r') as f:
        line = re.sub(r'([0-9]{10})', lambda x: datetime.datetime.fromtimestamp(int(x.group(1))).strftime('%a %b %d %Y'), f.read())

with open(sys.argv[2], 'w') as f:
        f.write(line)
