import tracker
tracker.track( "mapper" )

import sys
import os

from encode import BUCKETS, AIRPORT_NAMES

MAPPER_ENCODE = os.environ.get( "MAPPER_ENCODE", "True" ) == "True"

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

        # Quality - Ensure there are 5 values
        if len( data ) != 5:
            print( f"Error reading CSV - {len( data )} index, should be 5", file=sys.stderr )
            continue

        total = data[4]
        tip = data[3]

        # Quality - Ensure payments are not negative
        if total <= 0 or tip < 0 or tip > total:
            print( f"Invalid payment - Total: {total} Tip: {tip}", file=sys.stderr )
            continue

        date = data[0]
        hour = int( date[11:13] ) // 6

        if hour not in [ 0, 1, 2, 3 ]:
            print( f"Invalid hour - {hour}", file=sys.stderr )
            hour = None

        if MAPPER_ENCODE:
            hour = BUCKETS[hour]

        depart = int( data[1] )
        arrive = int( data[2] )

        if not arrive or arrive > 265 or arrive < 1:
            print( f"Invalid locationID - {arrive}", file=sys.stderr )
            continue

        if not depart or depart > 265 or arrive < 1:
            print( f"Invalid locationID - {depart}", file=sys.stderr )
            continue

        airport = get_airport( depart, arrive )
        value = get_value( tip, total )

        if airport:
            print( f"{airport}\t{tip}|{total}" )
        if hour:
            print( f"T|{hour}\t{tip}|{total}" )

    except ( TypeError, ValueError ) as e:
        print( f"Error reading CSV - {e}", file=sys.stderr )