import tracker
tracker.track( "all-in-one" )

from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, col
import time

start_time = time.time()

spark = SparkSession.builder \
    .appName("AirportFee") \
    .master("local[*]") \
    .getOrCreate()

df = spark.read.parquet("data/yellow_tripdata_2026-01.parquet")
starting = df.count()

# about 1 million records have null airport fee. This data is collected from the taxis computers automatically. Null and zero do not mean the same thing!
# I think we should just keep this sperate since is so many values
#df = df.filter(
#    col("Airport_fee").isNotNull() &
#    col("tip_amount").isNotNull()
#)
#cleaned = df.count()
#dropped = starting - cleaned
#print(f"Original records: {starting}")
#print(f"Remaining records: {cleaned}")
#print(f"Dropped records: {dropped}")


#this is conceptually the same as MapReduce. Spark processes the records and organizes them by AirPortFee
#It them groups records by the same fee ammount and adds the tips
# Map	groupBy("Airport_fee")
# Reduce	sum("tip_amount")
# groupby and sum are high level operations but spark distibues them actuamtically
results = df.groupBy("Airport_fee") \
    .agg(sum("tip_amount").alias("total_tip"))

results.show()

spark.stop()

end_time = time.time()

print(f"\n Spark execution time: {end_time - start_time:.4f} seconds")