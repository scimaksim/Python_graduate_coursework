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