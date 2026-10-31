import pandas as pd

df = pd.read_json( "metrics.json", lines=True )

stages = df.groupby( [ "run", "stage" ] ).agg(
    procs=( "stage", "size" ),
    bytes_in =( "bytes_in", "sum" ),
    bytes_out=( "bytes_out", "sum" ),
    start=( "start", "min" ),
    end=( "end", "max" ),
).reset_index()

stages["seconds"] = (stages["end"] - stages["start"] ).round( 3 )
runStart = stages.groupby( "run" )["start"].transform( "min" )
stages["t_start"] = ( stages["start"] - runStart ).round( 1 )
stages["t_end"] = ( stages["end"] - runStart ).round( 1 )
stages = stages.sort_values( [ "run", "start" ] )

print( stages[ [ "run", "stage", "procs", "bytes_in", "bytes_out", "seconds", "t_start", "t_end" ] ].to_string( index=False ) )

print()
for run, group in stages.groupby( "run" ):
    elapsed = group["end"].max() - group["start"].min()
    traffic = group[ group["stage"] != "reducer" ][ "bytes_out"].sum()
    print( f"{run} - elapsed: {elapsed:.3f} seconds, total traffic: {traffic} bytes" )