import tracker
tracker.track( "reducer" )

import sys

def print_output( key, total, count ):
    average = total / count
    print( f"{key},{average:.1%}|{count}" )

cur_key = ""
cur_sum = 0.0
cur_count = 0

# Loop through each line of input
for line in sys.stdin:
    # Extract error code and quantity
    key, value = line.strip().split( '\t' )

    pct, count = value.strip().split( '|' )
    
    # If more of the same key
    if key == cur_key:
        # Increase quantity
        cur_count += int( count ) # Add to count
        cur_sum += float( pct )
    
    # If a new key
    else:
        # Make sure it is a code
        if cur_key != "":
            print_output( cur_key, cur_sum, cur_count )
            
        # Reset current
        cur_key = key
        cur_count = int( count )
        cur_sum = float( pct )

# Print final code
if cur_key !="":
    print_output( cur_key, cur_sum, cur_count )