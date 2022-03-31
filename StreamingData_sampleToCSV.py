#Script for pyspark streaming example
#Start spark instance via pyspark in your terminal (command if on Windows)

#Read in some data to sample from
import pandas as pd
neuralgia = pd.read_csv("data/neuralgia.csv")

#Now a for loop to sample a few rows and output them to a data set
#Put a pause in as well
import numpy as np
import time

for i in range(0,10):
    #randomly sample 5 rows
    temp = neuralgia.loc[np.random.randint(neuralgia.shape[0], size = 5)]
    # create a new column that grabs the current local time
    temp["timestamp"] = [time.strftime("%H:%M:%S", time.localtime())]*5
    # write to a .csv file, each file will be uniquely named
    temp.to_csv("csvfiles/neuralgia" + str(i) + ".csv", index = False, header = False)
    # will produce 1 file, wait 10 seconds, produce another, etc. until we get 10 files total
    time.sleep(25)
    
    
    
#Commands for reading the stream, procesing, and outputting
from pyspark.sql.types import StructType
# set up schema correspodning to our data
myschema = StructType().add("Treatment", "string").add("Sex", "string").add("Age", "integer").add("Duration", "integer").add("Pain", "string").add("timestamp", "timestamp")
df = spark.readStream.schema(myschema).csv(r"C:\Users\mnikiforov\Documents\GitHub\ST590_Analysis_of_Big_Data\csvfiles")
agg = df.groupBy("Sex").avg("Duration")
myquery = agg.writeStream.outputMode("complete").format("console").start()
    

    
    
#Commands for reading the stream, procesing, and outputting
#Now including windowing
from pyspark.sql.types import StructType
# import windowing function
from pyspark.sql.functions import window

myschema = StructType().add("Treatment", "string").add("Sex", "string").add("Age", "integer").add("Duration", "integer").add("Pain", "string").add("timestamp", "timestamp")

df = spark.readStream.schema(myschema).csv("C:\\repos\\ST-554\\03-StreamingData\csvfiles")

agg = df.groupBy(
    window(df.timestamp,"1 minute", "1 minute"),
    "Sex").avg("Duration")

windowquery = agg.writeStream.outputMode("update").format("console").start()
        
    
#Commands for joining a stream with a static data frame
from pyspark.sql.types import StructType

#First read in a static dataframe
staticDF = spark.read.csv('C:\Users\mnikiforov\Documents\GitHub\ST590_Analysis_of_Big_Data\data\impressions.csv', 
                         schema = StructType().add('adId', "integer").add('impressionTime', 'timestamp'))

#Now set up the stream to take in data from the .csv

df = spark.readStream.schema(
    StructType().add('adId', "integer").add('clickTime', 'timestamp')
).csv(r"C:\Users\mnikiforov\Documents\GitHub\ST590_Analysis_of_Big_Data\csvfiles")

joinquery = staticDF.join(df, "adId", "inner").writeStream.outputMode("append").format("console").start()