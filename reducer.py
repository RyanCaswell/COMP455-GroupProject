import tracker
tracker.track( "reducer" )

import sys
import os

MAPPER_ENCODE = os.environ.get( "MAPPER_ENCODE", "True" ) == "True"

AIRPORT_NAMES = {
        "1": "Newark Airport",
        "132": "JFK Airport",
        "138": "LaGuardia Airport",
    }

BUCKETS = [
            "Night (00-06)",
            "Morning (06-12)",
            "Afternoon (12-18)",
            "Evening (18-24)"
        ]

def print_output( key, tip, total ):
    average = tip / total

    if not MAPPER_ENCODE:
        parts = key.split("|")
        code = parts[0]

        if code == "T":
            key = f"T|{BUCKETS[int( parts[1] )]}"

        elif code == "N":
            key = "N|None"

        elif code == "B":
            depart = AIRPORT_NAMES.get( parts[1] )
            arrive = AIRPORT_NAMES.get( parts[2] )
            key = f"B|{depart}|{arrive}"

        elif code == "A" or code == "D":
            key = f"{code}|{AIRPORT_NAMES.get( parts[1] )}"

        else:
            raise ValueError( f"Unexpected key format: {key!r}" )
    
    print( f"{key},{average:.1%}" )

cur_key = ""
cur_tip = 0.0
cur_total = 0.0

# Loop through each line of input
for line in sys.stdin:
    # Extract error code and quantity
    key, value = line.strip().split( '\t' )

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
            print_output( cur_key, cur_tip, cur_total )
            
        # Reset current
        cur_key = key
        cur_tip = float( tip )
        cur_total = float( total )

# Print final code
if cur_key !="":
    print_output( cur_key, cur_tip, cur_total )