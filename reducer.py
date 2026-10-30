import sys

cur_key = ""
cur_count = 0.0

# Loop through each line of input
for line in sys.stdin:
    # Extract error code and quantity
    key, value = line.strip().split( '\t' )
    
    # If more of the same key
    if key == cur_key:
        # Increase quantity
        cur_count = cur_count + float( value ) # Add to sum 
    
    # If a new key
    else:
        # Make sure it is a code
        if cur_key != "":
            print( f"{cur_key},{cur_count}" )
            
        # Reset current
        cur_key = key
        cur_count = float( value )

# Print final code
if cur_key !="":
    print( f"{cur_key},{cur_count}" )