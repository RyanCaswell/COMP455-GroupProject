# COMP 455 Group Project

## Dataset Link

The page for the NYC Taxi & Limousine Commission datasets can be found here:
https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

Or a direct link to the dataset used in our testing:
https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-01.parquet

## Setup

We recommend using a Python virtual enviroment for running benchmarks. This can be setup and required packages added by running ```setup.ps1```.

## Requirements

* Python 3.14+
* PyArrow
* Pandas
* ipykernel
* PySpark

## Benchmarking

To run a small test benchmark, use ```test_Benchmark.py```.

To run a test of all mapReduce of benchmarks, use ```mapReduce_Benchmark.ps1```.

To run a full suite of benchmarks, use ```all_Benchmark.ps1```.

## Manual Run Examples

```ingester.py``` must be run at least once to create the input for manual runs.

### Basic Pipeline

```python mapper.py < data\log.txt | sorter.py | reducer.py```

### 4 Mapper, Reducer-side Join, Dictionary based Reducer

```splitter.py -mappers 4 --reducer-join --dict < data\log.txt```
