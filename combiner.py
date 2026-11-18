import tracker
tracker.track( "combiner" )

import sys

cur_key = ""
cur_tip = 0.0
cur_total = 0.0

# Loop through each line of input
for line in sys.stdin:
    # Extract error code and quantity
    parts = line.strip().split( '\t' )

    if len( parts ) != 2:
        print( f"Invalid input - {line}", file=sys.stderr )
        continue

    key, value = parts

    tip, total = value.split( '|' )
    
    # If more of the same key
    if key == cur_key:
        # Increase quantity
        cur_tip += float( tip ) # Add to count
        cur_total += float( total )
    
    # If a new key
    else:
        # Make sure it is a code
        if cur_key != "":
            print( f"{cur_key}\t{cur_tip}|{cur_total}" )
            
        # Reset current
        cur_key = key
        cur_tip = float( tip )
        cur_total = float( total )

# Print final code
if cur_key !="":
    print( f"{cur_key}\t{cur_tip}|{cur_total}" )