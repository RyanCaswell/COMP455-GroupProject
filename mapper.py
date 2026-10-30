import sys
import json

# Read input, one line at a time
for line in sys.stdin:
    try:
        record = json.loads( line )

        airport_fee = record["Airport_fee"]
        tip = record["tip_amount"]

        print( f"{airport_fee}\t{tip}")
    except ( json.JSONDecodeError, KeyError, TypeError ):
        print( f"Error reading JSON", file=sys.stderr )