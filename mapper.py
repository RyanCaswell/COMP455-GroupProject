import tracker
tracker.track( "mapper" )

import sys
import os
from datetime import datetime

MAPPER_ENCODE = os.environ.get( "MAPPER_ENCODE", "True" ) == "True"

AIRPORT_NAMES = {
        1: "Newark Airport",
        132: "JFK Airport",
        138: "LaGuardia Airport",
    }

BUCKETS = [
            "Night (00-06)",
            "Morning (06-12)",
            "Afternoon (12-18)",
            "Evening (18-24)"
        ]

def get_airport( depart, arrive ):
    # Check if an airport
    departing = depart in AIRPORT_NAMES
    arriving = arrive in AIRPORT_NAMES
    
    if MAPPER_ENCODE:
        depart = AIRPORT_NAMES.get( depart ) if departing else None
        arrive = AIRPORT_NAMES.get( arrive ) if arriving else None
    else:
        depart = depart if departing else None
        arrive = arrive if arriving else None

    if departing and arriving:
        return f"B|{depart}|{arrive}"
        
    if departing:
        return f"D|{depart}"

    if arriving:
        return f"A|{arrive}"

    return f"N|None"

def get_value( tip, total ):
    return f"{tip}|{total}"

# Read input, one line at a time
for line in sys.stdin:
    try:
        data = line.strip().split( "," )

        # Quality checks
        if len( data ) != 5:
            print( f"Error reading CSV - {len( data )} index, should be 5", file=sys.stderr )
            continue

        depart = int( data[1] )
        arrive = int( data[2] )

        date = data[0]
        total = data[4]
        tip = data[3]

        hour = int( date[11:13] ) // 6

        if MAPPER_ENCODE:
            hour = BUCKETS[hour]

        airport = get_airport( depart, arrive )
        value = get_value( tip, total )

        if value:
            print( f"{airport}\t{value}" )
            print( f"T|{hour}\t{value}" )

    except ( TypeError, ValueError ) as e:
        print( f"Error reading CSV - {e}", file=sys.stderr )