import sys
from operator import itemgetter



lines = list( sys.stdin )    # reads through the counter, one line at a time

# Sort, up to tab
lines.sort( key = lambda line: line.partition("\t")[0] ) # Does this help?

# Write to reducer
sys.stdout.write( "".join( lines ) )