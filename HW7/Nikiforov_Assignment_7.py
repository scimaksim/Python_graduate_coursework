####################################
# Assignment 7
# Maksim Nikiforov
# ST590 - April, 2022
####################################

####################################
############# Task 1 ###############
####################################

######### Reading a stream #########

# Import necessary libraries and initiate Spark session
import pandas as pd
import numpy as np
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

# Create an input stream from the rate format using 1 row per second
input_stream = spark \
          .readStream \
          .format("rate") \
          .option("rowsPerSecond", 1) \
          .load()

######### Transform/aggregation step #########

# Import the window() function
from pyspark.sql.functions import window

# Add a watermark that relies on the timestamp column 
# and uses a five second watermark.
# Use it with .groupBy() to create windows that
# are 30 seconds long with no overlap (i.e. tumbling windows).
# Sum the values within that window using the .sum() aggregation

windowed_stream = input_stream \
           .withWatermark("timestamp", "5 seconds") \
           .groupBy(window(input_stream.timestamp, "30 seconds")) \
           .sum()

######### Writing the stream #########

# Write the stream to memory.
# Use the "memory" output format, the "update" outputMode, and
# make the trigger based on a processingTime of 20 seconds
myquery = windowed_stream \
            .writeStream.outputMode("update") \
            .format("memory") \
            .trigger(processingTime = "20 seconds") \
            .queryName("myquery") \
            .start()

# Code to view output in the pyspark console
spark.sql("SELECT * FROM myquery") \
        .coalesce(1) \
        .write \
        .format("json") \
        .option("header", "false") \
        .save(r"C:\Users\mnikiforov\Documents\GitHub\ST590_Analysis_of_Big_Data\HW7\myquery_results")

####################################
############# Task 2 ###############
####################################

# Repeat task 1 but allow for overlapping windows. Have the windows overlap by 15 seconds.
# Add an additional "10 seconds" argument to groupBy() and window() operations.
windowed_stream_sliding = input_stream \
           .withWatermark("timestamp", "5 seconds") \
           .groupBy(window(input_stream.timestamp, "30 seconds", "15 seconds")) \
           .sum()

# Write the new sliding window stream to memory.
myquery_sliding = windowed_stream_sliding \
            .writeStream.outputMode("update") \
            .format("memory") \
            .trigger(processingTime = "20 seconds") \
            .queryName("myquery_sliding") \
            .start()

# Code to view output in the pyspark console
spark.sql("SELECT * FROM myquery_sliding") \
        .coalesce(1) \
        .write \
        .format("json") \
        .option("header", "false") \
        .save(r"C:\Users\mnikiforov\Documents\GitHub\ST590_Analysis_of_Big_Data\HW7\myquery_sliding_results")

####################################
############# Task 3 ###############
####################################

##### Setup for creating files #####

# Import required libraries for importing data (pandas),
# invoking 10-second delay after writing to files (time),
# and creating directories when they do not yet exist (os)
import pandas as ps
import time
import os

# Read in the all_accelerometer_data_pids_13.csv file (relative directory)
accelerometer_data = ps.read_csv('HW7/all_accelerometer_data_pids_13.csv')

# Create two data frames, one for person SA0297’s data and one for person PC6771’s data.
SA0297_data = accelerometer_data[accelerometer_data.pid == "SA0297"]
PC6771_data = accelerometer_data[accelerometer_data.pid == "PC6771"]

# Create new directories to store .CSV files
os.makedirs('HW7/SA0297_data', exist_ok=True)
os.makedirs('HW7/PC6771_data', exist_ok=True)

# Set up a for loop to write 500 values at a time for
# SA0297 to a .csv file in a folder for that person’s data.
# Begin loop at first row, stop when we reach the end of our CSV file,
# increment by 500 for slicing purposes
for i in range(0, len(SA0297_data), 500):
    # Starting index for slicing using .iloc[]
    start_index = i
    # End index (increment of 500)
    end_index = i + 500
    # Slice 500 rows at a time, sequentially
    temp = SA0297_data.iloc[start_index:end_index]
    # Write to a .CSV file (uniquely named) within the new directory
    temp.to_csv("HW7/SA0297_data/SA0297_" \
    + str(i) + ".csv", index = False, header = False)
    
# The loop should then delay for 10 seconds after writing to the files.
time.sleep(10)

#  Similarly output values for PC6771 to another folder.
# Begin loop at first row, stop when we reach the end of our CSV file,
# increment by 500 for slicing purposes
for i in range(0, len(PC6771_data), 500):
    # Starting index for slicing using .iloc[]
    start_index = i
    # End index (increment of 500)
    end_index = i + 500
    # Slice 500 rows at a time, sequentially
    temp = PC6771_data.iloc[start_index:end_index]
    # Write to a .CSV file (uniquely named)
    temp.to_csv("HW7/PC6771_data/PC6771_" \
    + str(i) + ".csv", index = False, header = False)
# The loop should then delay for 10 seconds after writing to the files.
time.sleep(10)

##### Reading a stream #####
from pyspark.sql.types import StructType

# Setup the schema (read all in as strings) for SA0297
SA0297_schema = StructType() \
                  .add("time", "string") \
                  .add("pid", "string") \
                  .add("x", "string") \
                  .add("y", "string") \
                  .add("z", "string")

# Setup the schema (read all in as strings) for PC6771
PC6771_schema = StructType() \
                  .add("time", "string") \
                  .add("pid", "string") \
                  .add("x", "string") \
                  .add("y", "string") \
                  .add("z", "string")


# Create an input stream from the csv folder for SA0297
SA0297_df = spark.readStream.schema(SA0297_schema).csv("HW7/SA0297_data")

# Create an input stream from the csv folder for PC6771
PC6771_df = spark.readStream.schema(PC6771_schema).csv("HW7/PC6771_data")

##### Transform/aggregation step #####
# Import functions to find square root 
from pyspark.sql.functions import col, sqrt

transform_SA0297 = SA0297_df \
                      .select("time", "pid", col("x").cast("double"), col("y").cast("double"), col("z").cast("double")) \
                      .select("time", "pid", sqrt(col("x")**2 + col("y")**2 + col("z")**2) \
                      .alias("mag"))

transform_PC6771 = PC6771_df \
                      .select("time", "pid", col("x").cast("double"), col("y").cast("double"), col("z").cast("double")) \
                      .select("time", "pid", sqrt(col("x")**2 + col("y")**2 + col("z")**2) \
                      .alias("mag"))


##### Writing the stream #####

# Create new directories to store .CSV files
os.makedirs('HW7/SA0297_write', exist_ok=True)
os.makedirs('HW7/PC6771_write', exist_ok=True)

# Write the files
SA0297_stream = transform_SA0297 \
                   .writeStream.outputMode("append") \
                   .format("csv") \
                   .option("path", "HW7/SA0297_write") \
                   .option("checkpointlocation", "HW7/SA0297_write") \
                   .start()

PC6771_stream = transform_PC6771 \
                   .writeStream.outputMode("append") \
                   .format("csv") \
                   .option("path", "HW7/PC6771_write") \
                   .option("checkpointlocation", "HW7/PC6771_write") \
                   .start()


# Use PySpark to read in all "part" files
allfiles = spark.read.option("header","false").csv("HW7/SA0297_write/part-*.csv")

# Output as CSV file
allfiles \
.coalesce(1) \
.write.format("csv") \
.option("header", "false") \
.save("HW7/SA0297_write/single_csv_file")


# Use PySpark to read in all "part" files
allfiles = spark.read.option("header","false").csv("HW7/PC6771_write/part-*.csv")

# Output as CSV file
allfiles \
.coalesce(1) \
.write.format("csv") \
.option("header", "false") \
.save("HW7/PC6771_write/single_csv_file")
