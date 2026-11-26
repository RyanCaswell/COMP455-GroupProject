import tracker
import time
import json
import os
import urllib.request

from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col,concat,hour,lit,sum as spark_sum,when



metrics_tracker = tracker.track("pyspark")

INPUT_PATH = Path("data/yellow_tripdata_2026-01.parquet")

AIRPORT_NAMES = {
    1: "Newark Airport",
    132: "JFK Airport",
    138: "LaGuardia Airport",
}

BUCKETS = [
    "Night (00-06)",
    "Morning (06-12)",
    "Afternoon (12-18)",
    "Evening (18-24)",
]

start_time = time.time()



# MAPPER 
def location_name(location):
    expression = None

    for code, name in AIRPORT_NAMES.items():
        if expression is None:
            expression = when(location == code, lit(name))
        else:
            expression = expression.when(location == code, lit(name))

    return expression
def airport_key(depart, arrive):
    depart_name = location_name(depart)
    arrive_name = location_name(arrive)

    return (
        when(
            depart_name.isNotNull() & arrive_name.isNotNull(),
            concat(lit("B|"), depart_name, lit("|"), arrive_name)
        )
        .when(
            depart_name.isNotNull(),
            concat(lit("D|"), depart_name)
        )
        .when(
            arrive_name.isNotNull(),
            concat(lit("A|"), arrive_name)
        )
        .otherwise(lit("N|None"))
    )
def time_key(pickup_hour):
    expression = when(pickup_hour < 6, lit(BUCKETS[0]))

    for index, label in enumerate(BUCKETS[1:-1], start=1):
        expression = expression.when(
            pickup_hour < (index + 1) * 6,
            lit(label)
        )

    return concat(
        lit("T|"),
        expression.otherwise(lit(BUCKETS[-1]))
    )


#  Metrics
def get_spark_input_bytes(spark):
    endpoint = (
        f"{spark.sparkContext.uiWebUrl}/api/v1/applications/"
        f"{spark.sparkContext.applicationId}/stages"
    )
    with urllib.request.urlopen(endpoint, timeout=5) as response:
        stages = json.loads(response.read())
    latest_stages = {}
    for stage in stages:
        stage_id = stage["stageId"]
        if (
            stage_id not in latest_stages
            or stage["attemptId"] > latest_stages[stage_id]["attemptId"]
        ):
            latest_stages[stage_id] = stage
    input_bytes = sum(
        stage.get("inputBytes", 0)
        for stage in latest_stages.values()
    )

    input_records = sum(
        stage.get("inputRecords", 0)
        for stage in latest_stages.values()
    )
    return input_bytes, input_records

spark = (
    SparkSession.builder
    .appName("AirportTipRate")
    .master("local[*]")
    .getOrCreate()
)

data = spark.read.parquet(str(INPUT_PATH))

trips = data.select(
    col("PULocationID").alias("depart"),
    col("DOLocationID").alias("arrive"),
    hour(col("tpep_pickup_datetime")).alias("hour"),
    col("tip_amount").alias("tip"),
    col("total_amount").alias("total")
)


# mapper functions
airport_mapping = trips.select(
    airport_key(col("depart"), col("arrive")).alias("key"),
    "tip",
    "total"
)

time_mapping = trips.select(
    time_key(col("hour")).alias("key"),
    "tip",
    "total"
)

mapped = airport_mapping.unionByName(time_mapping)



# Reducer
reduced = mapped.groupBy("key").agg(
    spark_sum("tip").alias("tip"),
    spark_sum("total").alias("total")
)

results = sorted(
    reduced.collect(),
    key=lambda row: row["key"]
)


# Results

output_bytes = 0

for row in results:
    average = row["tip"] / row["total"]
    line = f"{row['key']},{average:.1%}\n"
    output_bytes += len(line.encode("utf-8"))
    print(line, end="")


def record_summary(bytes_in, bytes_out, start, end):
    path = Path("metrics_summary_final.csv")
    seconds = end - start
    run_name = os.environ.get("RUN_NAME", "pyspark")
    row = (
        f"{run_name},pyspark,1,{bytes_in},{bytes_out},"
        f"{start},{end},{seconds:.3f},0.0,{seconds:.1f}"
    )

    if path.exists():
        text = path.read_text()
        newline = "\r\n" if "\r\n" in text else "\n"
        lines = [line for line in text.splitlines() if line.split(",", 1)[0] != run_name]
    else:
        newline = "\n"
        lines = ["run,stage,procs,bytes_in,bytes_out,start,end,seconds,t_start,t_end"]

    lines.append(row)
    path.write_text(newline.join(lines) + newline)


# Benchmark 

input_bytes, input_records = get_spark_input_bytes(spark)

metrics_tracker["add_input"](input_bytes)

spark.stop()

end_time = time.time()
execution_time = end_time - start_time
record_summary(input_bytes, output_bytes, start_time, end_time)


# Print Out

print("\n========== SPARK BENCHMARK ==========")

print(
    f"Data entering Spark: "
    f"{input_bytes:,} bytes ({input_records:,} records)"
)

print(f"Execution time: {execution_time:.4f} seconds")

print("=====================================")
