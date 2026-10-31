# COMP 455 Group Project

## Dataset Link

https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

## Ideas

* Look at tipping based on airport useage
  * What locations are airports? (taxi_zone_loopup.csv)
  * Total airport fees range from 1.75 to 26.75 Why does negative airport fee exist?
  * Should provides lop sided relation to text combiner
  * Does the pickup date effect how much they are tipped? (Do we tip more during busier days like holidays etc.)
  * compare time and space complexitys of python based MapReduced vs PySparks


* Where should we clean data? Multiple points?
  * Ingest?
  * Beginning of mapper?
  * End of mapper?
  * Reducer?

* Multiple datasets?
  * Just create loop in ingest, with a list of datasets?
    * Create list from what datasets are in data folder?
