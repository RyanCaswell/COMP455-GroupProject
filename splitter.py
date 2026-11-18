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

parser.add_argument(
    "--combiner",
    action="store_true",
    help="Use a combiner for each mapper"
)

args = parser.parse_args()

mapper_count = args.mappers
output_batch = 5000
input_batch = 500
reducer_dict = args.dict
use_combiner = args.combiner

# Start Sorter
if reducer_dict:
    sorter = None

    # Start Reducer
    reducer = subprocess.Popen(
        [sys.executable, "reducer.py", "--dict"],
        stdin=subprocess.PIPE,
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

# Mapper to Combiner links
local_pipe = []

if use_combiner:
    for _ in range( mapper_count ):
        local_sorter = subprocess.Popen(
            [sys.executable, "sorter.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )

        combiner = subprocess.Popen(
            [sys.executable, "combiner.py"],
            stdin=local_sorter.stdout,
            stdout=subprocess.PIPE,
            text=True
        )

        local_sorter.stdout.close()

        local_pipe.append( ( local_sorter, combiner ) )

write_lock = threading.Lock()

# Read mapper's output
def forward_output( index, mapper ):
    batch = []

    # Select mapper output target (combiner or reducer)
    if use_combiner:
        local_sorter, combiner = local_pipe[ index ]
        target = local_sorter.stdin
    else:
        target = reducer.stdin if reducer_dict else sorter.stdin

    # Connect mapper output
    for line in mapper.stdout:
        batch.append( line )

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

    # Local combiner
    if use_combiner:
        local_sorter.stdin.close()

        target = reducer.stdin if reducer_dict else sorter.stdin
        
        batch = []

        for line in combiner.stdout:
            batch.append( line )

            if len( batch ) >= output_batch:
                with write_lock: # TODO: Needed?
                    target.write( "".join( batch ) )
                    target.flush()
                batch.clear()

        if batch:
            with write_lock: # TODO: Needed?
                target.write( "".join( batch ) )
                target.flush()

        combiner.stdout.close()

        local_sorter.wait()
        combiner.wait()

    # Remote reducer
    else:
        if not reducer_dict:
            with write_lock:
                target.flush()

threads = [
    threading.Thread( target=forward_output, args=( i, mapper ) )
    for i, mapper in enumerate( mappers )
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
    sorter.wait()
else:
    reducer.stdin.close()

reducer.wait()