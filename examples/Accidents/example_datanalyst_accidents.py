from GreyNsights.analyst import DataWorker, DataSource, Pointer, Command, Analyst
from GreyNsights.frameworks import framework
import numpy as np

frameworks = framework()

pandas = frameworks.pandas

identity = Analyst("Alice", port=65441, host="127.0.0.1")

worker = DataWorker(port=65443, host="127.0.0.1")
dataset = DataSource(identity, worker, "Sample Data")

a = dataset.get_config()
print(a)

a = a.approve().init_pointer()


df = pandas.DataFrame(a)

# 31.019322070944433
# 31.083416873168627
# 2850

# 31.011228070175438
# 30.0
# 2850


p = 3

p = dataset.send(p).chain

# print(df["TMC"].sum())

print(df["TMC"])

# top 5 rows
# print(df["TMC"].sum().get())
# top 50 rows


# last 5 rows
print(df.tail())
# last 50 rows
df.tail(50)

print(df.describe().get())

print("TMC sum: ", df["TMC"].sum().get())
print("TMC std: ", df["TMC"].std().get())
print("Severity mean: ", df["Severity"].mean().get())
print("Severity mean: ", df["Severity"].mean().get())

# print(df["TMC"])

# print(df["TMC"].mean())
# no of rows in dataframe
# print(len(df))
# Shape of Dataframe
df.shape

print("COLUMNS: ", df.columns)
print("SHAPE: ", df.shape)

df.columns = [
    "ID",
    "Source",
    "TMC",
    "Severity",
    "Start_Time",
    "End_Time",
    "Start_Lat",
    "Start_Lng",
    "End_Lat",
    "End_Lng",
    "Distance_mi",
    "Description",
    "Number",
    "Street",
    "Side",
    "City",
    "County",
    "State",
    "Zipcode",
    "Country",
    "Timezone",
    "Airport_Code",
    "Weather_Timestamp",
    "Temperature_F",
    "Wind_Chill_F",
    "Humidity_%",
    "Pressure_in",
    "Visibility_mi",
    "Wind_Direction",
    "Wind_Speed_mph",
    "Precipitation_in",
    "Weather_Condition",
    "Amenity",
    "Bump",
    "Crossing",
    "Give_Way",
    "Junction",
    "No_Exit",
    "Railway",
    "Roundabout",
    "Station",
    "Stop",
    "Traffic_Calming",
    "Traffic_Signal",
    "Turning_Loop",
    "Sunrise_Sunset",
    "Civil_Twilight",
    "Nautical_Twilight",
    "Astronomical_Twilight",
]

df = df[
    [
        "ID",
        "Source",
        "TMC",
        "Severity",
        "Start_Time",
        "End_Time",
        "Start_Lat",
        "Start_Lng",
        "End_Lat",
        "End_Lng",
    ]
]


df.dtypes


df["Somecol"] = (df["TMC"] + df["Severity"] / 10) / 2
(df["TMC"] + df["Severity"])

df["LOL"] = df["TMC"]


df["Somecol"] = df["TMC"] + df["Severity"]

(df["TMC"] + df["Severity"] / 10) / 2

df["TMC"] > 2

(df["Severity"] > 8) | (df["TMC"] > 200)

df[df["TMC"] > 200]

df[(df["Severity"] > 8) | (df["TMC"] > 200)]

And_df = df[(df["TMC"] > 200)]
# Multiple conditions: OR
Or_df = df[(df["Severity"] > 8) | (df["TMC"] > 200)]

df["Somecol"] = df["TMC"]


def somefunc(x):
    return x + 2


somefunc_pt = dataset.send(somefunc)


df["Somecol"] = df["TMC"].apply(somefunc_pt)


from math import cos, sin, asin, sqrt, pi


def haversine_distance(lat1, lon1, lat2, lon2):
    # Haversine distance formula taken from Michael Dunn's StackOverflow post:
    # https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points

    x_1 = pi / 180 * lat1
    y_1 = pi / 180 * lon1
    x_2 = pi / 180 * lat2
    y_2 = pi / 180 * lon2

    dlon = y_2 - y_1
    dlat = x_2 - x_1
    a = sin(dlat / 2) ** 2 + cos(x_1) * cos(x_2) * sin(dlon / 2) ** 2

    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers

    return c * r


haversine_distance_pt = dataset.send(haversine_distance)


def lol1(x):

    return haversine_distance_pt(
        x["Start_Lat"], x["Start_Lng"], x["End_Lat"], x["End_Lng"]
    )


lol_pt = dataset.send(lol1)

df["hDistance"] = df.apply(
    lol_pt,
    axis=1,
)


# Single condition
df_dis_gt_2 = df[df["hDistance"] > 2]
# Multiple conditions: AND
And_df = df[(df["hDistance"] > 8) & (df["TMC"] > 200)]
# Multiple conditions: OR
Or_df = df[(df["hDistance"] > 8) | (df["TMC"] > 200)]
# Multiple conditions: NOT
Not_df = df[~((df["hDistance"] > 8) | (df["TMC"] > 200))]
