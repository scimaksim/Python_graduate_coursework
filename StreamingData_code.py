import pandas as pd
air_data = pd.read_csv("data/AirQualityUCI.csv", sep = ";", decimal = ",")
air_data
air_data.info()


air_data = pd.read_excel("data/AirQualityUCI.xlsx")

air_data


air_data.info()

type(air_data.Time[0])


a = pd.to_datetime(["04-01-2022 10:00"], dayfirst=True)

a

b = pd.to_datetime(["04-01-2022 11:00"])

a-b

b.day

b.hour


air_data = pd.read_excel("data/AirQualityUCI.xlsx", parse_dates = [["Date", "Time"]])

air_data.info()


air_data = air_data.rename(columns = {'CO(GT)': 'co_gt'})

air_data


for i in range(air_data.shape[0]):

    if air_data.iloc[i].co_gt > 8:

        print("High CO Concentration at " + str(air_data.Date_Time[i]))


for i in range(air_data.shape[0]):

    temp = air_data.iloc[i]

    dt = temp.Date_Time

    value = temp.co_gt

    if value > 8:

        print("High CO Concentration at " + str(dt))

        with open('logs/COHigh.txt', 'a') as f:

            f.write(str(dt) + "," + str(value) + "\n")

    elif value < 0:

        print("Invalid CO Concentration at " + str(dt))

        with open('logs/COInvalid.txt', 'a') as f:

            f.write(str(dt) + "," + str(value) + "\n")


missing = 0

for i in range(air_data.shape[0]):

    temp = air_data.iloc[i]

    dt = temp.Date_Time

    value = temp.co_gt

    if value > 8:

        print("High CO Concentration at " + str(dt))

        with open('logs/COHigh.txt', 'a') as f:

            f.write(str(dt) + "," + str(value) + "\n")

        missing = 0

    elif value < 0:

        print("Invalid CO Concentration at " + str(dt))

        with open('logs/COInvalid.txt', 'a') as f:

            f.write(str(dt) + "," + str(value) + "\n")

        if value == -200:

            missing += 1

        if missing == 6:

            #Send email code

    else:

        missing = 0



import pandas as pd

import numpy as np

np.random.seed(10)

impressions = pd.DataFrame({

  'adId': range(500),

  'clickTime': (pd.to_datetime('2022-01-01') + pd.to_timedelta(np.random.rand(500), unit = "D")).sort_values()

})

clicks = impressions.iloc[np.random.randint(size = 30, low = 0, high = 499)].sort_index()

clicks.clickTime = clicks.clickTime + pd.to_timedelta(np.random.rand(30)/100, unit = "D")


impressions


clicks


pd.merge(left = impressions, right = clicks, on = "adId", how = 'right')


def update_mean(new_data, old_mean, count):

    return old_mean + (1/count)*(new_data-old_mean)


import numpy as np

import pandas as pd

air_data = pd.read_excel("data/AirQualityUCI.xlsx", parse_dates = [["Date", "Time"]])

air_data = air_data.rename(columns = {'CO(GT)': 'co_gt'})

air_data = air_data.loc[air_data.co_gt != -200].reset_index()

air_data


o_mean = 0

n = 1

means = []

for i in range(air_data.shape[0]):

    means.append(update_mean(air_data.co_gt[i], old_mean = o_mean, count = n))

    o_mean = means[i]

    n += 1


pd.DataFrame(zip(air_data.co_gt, means), columns = ["Data", "Means"])


def update_var(new_data, old_var, old_mean, count):

    return ((count-2)/(count-1))*old_var + (new_data - old_mean)**2/count


n = 3

means = [air_data.co_gt[0], air_data.co_gt[0:2].mean()]

variances = [np.nan, air_data.co_gt[0:2].var()]

o_mean = means[1]

o_var = variances[1]



for i in range(2, air_data.shape[0]):

    means.append(update_mean(air_data.co_gt[i], old_mean = o_mean, count = n))

    variances.append(update_var(air_data.co_gt[i], old_var = o_var, old_mean = o_mean, count = n))

    o_mean = means[i]

    o_var = variances[i]

    n += 1


print(air_data.co_gt[0:5].var(), air_data.co_gt.var())

pd.DataFrame(zip(air_data.co_gt, means, np.sqrt(np.array(variances)), np.array(variances)),

  columns = ["Data", "Means", "SDs", "Vars"])


my_values = []

rolling_means = [np.nan, np.nan]

window = 3

for i in range(air_data.shape[0]):

    my_values.append(air_data.co_gt[i])

    if i < window-1:

        continue

    rolling_means.append(np.mean(my_values))

    my_values = my_values[1:]




pd.DataFrame(zip(air_data.rolling(3).co_gt.mean(), rolling_means), columns = ["pandas", "us"])


air_data.rolling(3).co_gt.std()










df = spark \

    .readStream \

    .format("kafka") \

    .option("kafka.bootstrap.servers", "localhost:9092") \

    .option("subscribe", "topic_name") \

    .load()


df = spark \

    .readStream \

    .format("rate") \

    .option("rowsPerSecond", 1) \

    .load()


# Read all the csv files written atomically in a directory

userSchema = StructType().add("name", "string").add("age", "integer")

csvDF = spark \

    .readStream \

    .option("sep", ";") \

    .schema(userSchema) \

    .csv("/path/to/directory")



df.groupBy(

  window(df.timestamp, "1 minute", "30 seconds"), #2nd arg is window size, 3rd update time

  other_grouping_var

  ).aggregation()


df \

  .withWatermark("timestamp", "20 seconds") \ #accept data 20 seconds past the close of the window

  .groupBy(

    window(df.timestamp, "1 minute", "30 seconds"), #2nd arg is window size, 3rd update time

    other_grouping_var

  ) \

  .aggregation()


streamDF1.join(streamDF2, "col_id")   # inner join on common column col_id


# Define watermarks

impressionsWithWatermark = impressions \

  .selectExpr("adId AS impressionAdId", "impressionTime") \

  .withWatermark("impressionTime", "10 seconds ")   # max 10 seconds late


clicksWithWatermark = clicks \

  .selectExpr("adId AS clickAdId", "clickTime") \

  .withWatermark("clickTime", "20 seconds")        # max 20 seconds late


from pyspark.sql.functions import expr


# Left outer join with time range conditions

impressionsWithWatermark.join(

  clicksWithWatermark,

  expr("""

    clickAdId = impressionAdId AND

    clickTime >= impressionTime AND

    clickTime <= impressionTime + interval 1 hour

    """),

  "leftOuter"

)


streamingDF.join(staticDF, "column", "inner")

