import tracker
tracker.track( "sorter" )

import sys

lines = list( sys.stdin )    # reads through the counter, one line at a time
lines.sort()

for line in lines:
    sys.stdout.write( line )