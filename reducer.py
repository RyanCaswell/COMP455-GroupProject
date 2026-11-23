import tracker
tracker.track( "reducer" )

import sys
import os
import argparse

from encode import BUCKETS, AIRPORT_NAMES

parser = argparse.ArgumentParser()
parser.add_argument(
    "--dict",
    action="store_true",
    help="Use flag to start with an in-memory dictionary (input need not be sorted/ no sort stage)",
)
args = parser.parse_args()

MAPPER_ENCODE = os.environ.get( "MAPPER_ENCODE", "True" ) == "True"

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
            depart = AIRPORT_NAMES.get( int( parts[1] ) )
            arrive = AIRPORT_NAMES.get( int( parts[2] ) )
            key = f"B|{depart}|{arrive}"

        elif code == "A" or code == "D":
            key = f"{code}|{AIRPORT_NAMES.get( parts[1] )}"

        else:
            raise ValueError( f"Unexpected key format: {key!r}" )
    
    print( f"{key},{average:.1%}" )


def reduce_streaming():
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


def reduce_dict():
    results = {}

    # Loop through each line of input
    for line in sys.stdin:
        # Extract error code and quantity
        key, value = line.strip().split( '\t' )

        tip, total = value.split( '|' )

        if key not in results:
            results[key] = { "tip": 0.0, "total": 0.0 }

        results[key]["tip"] += float( tip )
        results[key]["total"]  += float( total )

    for key, value in results.items():
        print_output( key, value.get( "tip"), value.get( "total") )


if args.dict:
    reduce_dict()
else:
    reduce_streaming()