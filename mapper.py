import tracker
tracker.track( "mapper" )

import sys
import json

airport_names = {
    1: "Newark Airport",
    132: "JFK Airport",
    138: "LaGuardia Airport",
}

def get_key( depart, arrive ):
    if depart and arrive:
        return f"B|{depart}|{arrive}"
        
    if depart:
        return f"D|{depart}"

    if arrive:
        return f"A|{arrive}"

    return f"X|None"

def get_value( tip, total ):
    if total <= 0:
        return None
    pct = tip / total
    return f"{pct}|1"

# Read input, one line at a time
for line in sys.stdin:
    try:
        record = json.loads( line )

        date = record["tpep_pickup_datetime"]
        depart = airport_names.get( record["PULocationID"] )
        arrive = airport_names.get( record["DOLocationID"] )
        total = record["total_amount"]
        tip = record["tip_amount"]

        key = get_key( depart, arrive )
        value = get_value( tip, total )

        if key and value:
            print( f"{key}\t{value}")

    except ( json.JSONDecodeError, KeyError, TypeError ):
        print( f"Error reading JSON", file=sys.stderr )