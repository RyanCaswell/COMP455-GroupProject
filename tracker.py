import atexit
import json
import os
import sys
import time
from pathlib import Path

LOG_PATH = Path( "metrics.json" )

RUN_NAME = os.environ.get( "RUN_NAME", "default" )

class Counter:
    # Initilize class
    def __init__( self, stream ):
        self.stream = stream
        self.bytes = 0

    # When iterating over
    def __iter__( self ):
        for line in self.stream:
            self._count( line )
            yield line

    def __getattr__( self, name):
        return getattr( self.stream, name )

    # Count bytes in stream
    def _count( self, text ):
        self.bytes += len( text.encode( "utf-8" ) )
        if os.linesep == "\r\n":
            self.bytes += text.count( "\n" )

    # Count and forward
    def write( self, text ):
        self._count( text )
        return self.stream.write( text )

    # Read and forward
    def read( self, *args ):
        text = self.stream.read( *args )
        self._count( text )
        return text

    # Readline and forward
    def readline( self, *args ):
        line = self.stream.readline( *args )
        self._count( line )
        return line

def track( stage: str ):
    # Start timers
    start = time.perf_counter()
    startWall = time.time()

    # Create counter for input and output
    stdin = sys.stdin = Counter( sys.stdin )
    stdout = sys.stdout = Counter( sys.stdout )

    def save():
        record = {
            "run": RUN_NAME,
            "stage": stage,
            "bytes_in": stdin.bytes,
            "bytes_out": stdout.bytes,
            "seconds": round( time.perf_counter() - start, 3 ),
            "start": startWall,
            "end": time.time(),
        }

        with LOG_PATH.open( "a" ) as file:
            file.write( json.dumps( record ) + "\n" )

    atexit.register( save )