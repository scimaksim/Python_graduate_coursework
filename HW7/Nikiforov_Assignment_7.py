####################################
# Assignment 7
# Maksim Nikiforov
# ST590 - April, 2022
####################################

#######################################################################################
####################################### Task 1 ########################################
#######################################################################################

######### Task 1 - Reading a stream #########

# Create an input stream using the "rate" format at a rate of 1 row per second.
# This outputs values with a timestamp. 
# The values start at 0 and increase by 1 each time.

input_stream = spark \
          .readStream \
          .format("rate") \
          .option("rowsPerSecond", 1) \
          .load()

######### Task 1 - Transform/aggregation step #########

# Import the window() function
from pyspark.sql.functions import window

# Add a watermark that relies on the "timestamp" column and uses a five second watermark.
# Use it with .groupBy() to create windows that are 
# 30 seconds long with no overlap (i.e. tumbling windows).
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
            .queryName("myquery_tumbling") \
            .start()

# Code to view output in the pyspark console
spark.sql("SELECT * FROM myquery_tumbling") \
        .coalesce(1) \
        .write \
        .format("json") \
        .option("header", "false") \
        .save("HW7/myquery_tumbling_results")


#######################################################################################
####################################### Task 2 ########################################
#######################################################################################

# Repeat task 1 but allow for overlapping windows. Have the windows overlap by 15 seconds.
# Add an additional "15 seconds" argument to groupBy() and window() operations.
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
        .save("HW7/myquery_sliding_results")


#######################################################################################
####################################### Task 3 ########################################
#######################################################################################

################ Setup for crating files ###############

# Import required libraries for importing data (pandas),
# invoking 10-second delay after writing to files (time),
# and creating directories when they do not yet exist (os)
import pandas as ps
import time
import os

# Read in the all_accelerometer_data_pids_13.csv file (directory is relative)
accelerometer_data = ps.read_csv('HW7/all_accelerometer_data_pids_13.csv')

# Filter to create two data frames, 
# one for person SA0297’s data and one for person PC6771’s data.
SA0297_df = accelerometer_data[accelerometer_data.pid == "SA0297"]
PC6771_df = accelerometer_data[accelerometer_data.pid == "PC6771"]

# Assign custom "name" attributes to our data frames, reference them
# to create new directories in the subsequent "for" loop
SA0297_df.name = "SA0297_df"
PC6771_df.name = "PC6771_df"

# Since .to_csv() does not create directories for us,
# manually create new directories to store .CSV files.
# Reference the custom ".name" attribute we created earlier
os.makedirs('HW7/SA0297_df_sliced', exist_ok=True)
os.makedirs('HW7/PC6771_df_sliced', exist_ok=True)

# Set up a for loop to write 500 values at a time to .CSV files for PID
# SA0297 and PC6771.
for df_name in [SA0297_df, PC6771_df]:
    # Begin loop at first row, increment by 500 for slicing,
    # stop when we reach the last record for each PID
    for i in range(0, len(df_name), 500):
        # Starting index for slicing using .iloc[]
        start_index = i
        # End index (increment of 500)
        end_index = i + 500
        # Slice 500 rows at a time, sequentially
        temp = df_name.iloc[start_index:end_index]
        # Write to a .CSV file (uniquely named) within the new directory
        temp.to_csv("HW7/" + df_name.name + "_sliced/" + df_name.name + "_" + str(i) + ".csv", index = False, header = False)
# The loop should then delay for 10 seconds after writing to the files.
time.sleep(10)

################### Reading a stream ####################

# Import StructType to help us set up schema
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
SA0297_input_stream = spark.readStream.schema(SA0297_schema).csv("HW7/SA0297_df_sliced")

# Create an input stream from the csv folder for PC6771
PC6771_input_stream = spark.readStream.schema(PC6771_schema).csv("HW7/PC6771_df_sliced")

##### Transform/aggregation step #####

# Import functions to find square root 
from pyspark.sql.functions import col, sqrt

# For both streams, transform x, y, and z coordinates into a magnitude.
# Cast the x, y, and z columns to type double and then apply the square and square root.
# Keep the "time" and "pid" columns, the new "mag" column, 
# and drop the original x, y, and z columns.
transform_SA0297 = SA0297_input_stream \
                      .select("time", "pid", col("x").cast("double"), col("y").cast("double"), col("z").cast("double")) \
                      .select("time", "pid", sqrt(col("x")**2 + col("y")**2 + col("z")**2) \
                      .alias("mag"))

transform_PC6771 = PC6771_input_stream \
                      .select("time", "pid", col("x").cast("double"), col("y").cast("double"), col("z").cast("double")) \
                      .select("time", "pid", sqrt(col("x")**2 + col("y")**2 + col("z")**2) \
                      .alias("mag"))


############################# Writing the stream ##############################

# Write out each stream out to its own .CSV file(s).

# Create new directories to store .CSV files
os.makedirs('HW7/SA0297_df_stream_write/checkpoint', exist_ok=True)
os.makedirs('HW7/PC6771_df_stream_write/checkpoint', exist_ok=True)

# Write the files
SA0297_stream = transform_SA0297 \
                   .writeStream.outputMode("append") \
                   .format("csv") \
                   .option("path", "HW7/SA0297_df_stream_write") \
                   .option("checkpointlocation", "HW7/SA0297_df_stream_write/checkpoint") \
                   .start()

PC6771_stream = transform_PC6771 \
                   .writeStream.outputMode("append") \
                   .format("csv") \
                   .option("path", "HW7/PC6771_df_stream_write") \
                   .option("checkpointlocation", "HW7/PC6771_df_stream_write/checkpoint") \
                   .start()

####################### Combine .CSV files into single_csv_file ###################

# Use PySpark to read in all "part" files
for df_name in [SA0297_df, PC6771_df]:
    allfiles = spark.read.option("header","false").csv("HW7/" + df_name.name + "_stream_write/" + "part-*.csv")
    # Output as CSV file
    allfiles \
    .coalesce(1) \
    .write.format("csv") \
    .option("header", "false") \
    .save("HW7/" + df_name.name + "_stream_write/single_csv_file")
    
    
#######################################################################################
################################## End of submission ##################################
#######################################################################################