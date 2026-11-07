import tracker
tracker.track( "mapper" )

import sys
import json
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
        record = json.loads( line )

        depart = record["PULocationID"]
        arrive = record["DOLocationID"]

        date = datetime.fromisoformat( record["tpep_pickup_datetime"] ) # Could be switched to index number
        total = record["total_amount"]
        tip = record["tip_amount"]

        hour = date.hour // 6

        if MAPPER_ENCODE:
            hour = BUCKETS[hour]

        airport = get_airport( depart, arrive )
        value = get_value( tip, total )

        if value:
            print(
                f"{airport}\t{value}\n"
                f"T|{hour}\t{value}"
            )

    except ( json.JSONDecodeError, KeyError, TypeError, ValueError ) as e:
        print( f"Error reading JSON - {e}", file=sys.stderr )