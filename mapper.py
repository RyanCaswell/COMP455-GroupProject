import tracker
tracker.track( "mapper" )

import sys
import json
from datetime import datetime

def get_airport( depart_code, arrive_code ):
    airport_names = {
        1: "Newark Airport",
        132: "JFK Airport",
        138: "LaGuardia Airport",
    }

    depart = airport_names.get( depart_code )
    arrive = airport_names.get( arrive_code )

    if depart and arrive:
        return f"B|{depart}|{arrive}"
        
    if depart:
        return f"D|{depart}"

    if arrive:
        return f"A|{arrive}"

    return f"N|None"

def get_value( tip, total ):
    if total <= 0:
        return None
    pct = tip / total
    return f"{pct}|1"

def get_hour( date ):
        buckets = [
            "Night (00-06)",
            "Morning (06-12)",
            "Afternoon (12-18)",
            "Evening (18-24)"
        ]

        return f"T|{buckets[date.hour // 6]}"


# Read input, one line at a time
for line in sys.stdin:
    try:
        record = json.loads( line )

        date = datetime.fromisoformat( record["tpep_pickup_datetime"] ) # Could be switched to 
        depart = record["PULocationID"]
        arrive = record["DOLocationID"]
        total = record["total_amount"]
        tip = record["tip_amount"]

        hour = get_hour( date )
        airport = get_airport( depart, arrive )
        value = get_value( tip, total )

        if airport and value:
            print( f"{airport}\t{value}")

        if hour and value:
            print( f"{hour}\t{value}")

    except ( json.JSONDecodeError, KeyError, TypeError, ValueError ) as e:
        print( f"Error reading JSON - {e}", file=sys.stderr )