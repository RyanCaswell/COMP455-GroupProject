import sys
import subprocess
import threading
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "-m", "--mappers",
    type=int,
    default=4,
    help="Number of mappers (default=4)"
)

parser.add_argument(
    "--dict",
    action="store_true",
    help="Use dictionary-based reducer"
)

args = parser.parse_args()

mapper_count = args.mappers
output_batch = 5000
input_batch = 500
reducer_dict = args.dict

# Start Sorter
if reducer_dict:
    sorter = None

    # Start Reducer
    reducer = subprocess.Popen(
        [sys.executable, "reducerDict.py"],
        stdin=sorter.stdout,
        text=True
    )

else:
    sorter = subprocess.Popen(
        [sys.executable, "sorter.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )

    # Start Reducer
    reducer = subprocess.Popen(
        [sys.executable, "reducer.py"],
        stdin=sorter.stdout,
        text=True
    )

sorter.stdout.close()

# Start Mappers
mappers = [
    subprocess.Popen(
        [sys.executable, "mapper.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    for _ in range( mapper_count )
]

write_lock = threading.Lock()

# Read mapper's output
def forward_output( mapper ):
    batch = []

    # Iterate over mapper output
    for line in mapper.stdout:
        batch.append( line )

        # Set where to send mapper output
        target = reducer.stdin if reducer_dict else sorter.stdin

        # If enough records, flush to output
        if len( batch ) >= output_batch:
            with write_lock:
                target.write( "".join( batch ) )
                target.flush()
            batch.clear()

    # Final flush of any remaining
    if batch:
        with write_lock:
            target.write( "".join( batch ) )
            target.flush()

    mapper.stdout.close()

threads = [
    threading.Thread( target=forward_output, args=( mapper, ) )
    for mapper in mappers
]

for thread in threads:
    thread.start()

# Send batches to mappers
batches = [ [] for _ in range( mapper_count ) ]

for i, line in enumerate(sys.stdin):
    mapper_index = i % mapper_count
    batches[mapper_index].append( line )

    if len( batches[mapper_index] ) >= input_batch:
        mappers[mapper_index].stdin.write(
            "".join(batches[mapper_index])
        )
        mappers[mapper_index].stdin.flush()
        batches[mapper_index].clear()

# Send final to mappers
for i, batch in enumerate( batches ):
    if batch:
        mappers[i].stdin.write("".join( batch ) )
        mappers[i].stdin.flush()

# Close mapper inputs
for mapper in mappers:
    mapper.stdin.close()

# Wait for all mappers
for mapper in mappers:
    mapper.wait()

# Wait for output forwarding
for thread in threads:
    thread.join()

# Close sorter input
if sorter:
    sorter.stdin.close()

# Wait for sorter and reducer
if sorter:
    sorter.wait()

reducer.wait()