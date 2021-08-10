import numpy as np
from analyst import Analyst, Command, DataSource, DataWorker, Pointer
from frameworks import framework

frameworks = framework()

pandas = frameworks.pandas

identity = Analyst("Alice", port=65442, host="127.0.0.1")
worker = DataWorker(port=65441, host="127.0.0.1")
dataset = DataSource(identity, worker, "Sample Data").init_pointer()

dataset["Number of times pregnant"].mean()
dataset["Number of times pregnant"].mean()
# dataset.fillna(0)

# print(dataset[dataset.isnull()].sum().get())


"""
print(dataset.columns)

print(dataset["Number of times pregnant"].sum().get())
print(
    dataset["Plasma glucose concentration a 2 hours in an oral glucose tolerance test"]
    .sum()
    .get()
)

dataset = dataset[
    [
        "Diastolic blood pressure (mm Hg)",
        "2-Hour serum insulin (mu U/ml)",
        "Body mass index (weight in kg/(height in m)^2)",
        "Age (years)",
        " Diabetes pedigree function",
    ]
]

print(dataset.describe().get())


columns = dataset.columns


print("\n")
print("SUM")
print("\n")

"""
"""for col in columns:

    print(col + " : ", dataset[col].sum().get())"""

"""
print("\n")
print("STD")
print("\n")
"""

"""for col in columns:

    print(col + " : ", dataset[col].std().get())"""

"""
print("\n")
print("MEAN")
print("\n")
"""

"""for col in columns:

    print(col + " : ", dataset[col].mean().get())"""

"""
dataset["Randomfeature1"] = (
    dataset["Age (years)"] + dataset[" Diabetes pedigree function"]
) / 2
print((dataset["Randomfeature1"] / 2).mean().get())

df_select = dataset["Age (years)"] > 30
dataset["Randomfeature2"] = dataset[df_select]["Age (years)"]
dataset["Randomfeature3"] = dataset[df_select]["2-Hour serum insulin (mu U/ml)"]
dataset["Randomfeature4"] = dataset[df_select][
    "Body mass index (weight in kg/(height in m)^2)"
]
dataset["Randomfeature5"] = dataset[df_select][" Diabetes pedigree function"]

df_select = (dataset["Age (years)"] > 30) & (
    dataset["2-Hour serum insulin (mu U/ml)"] > 4.0
)

dataset["Randomfeature2"] = dataset[df_select]["Age (years)"]
dataset["Randomfeature3"] = dataset[df_select]["2-Hour serum insulin (mu U/ml)"]
dataset["Randomfeature4"] = dataset[df_select][
    "Body mass index (weight in kg/(height in m)^2)"
]
dataset["Randomfeature5"] = dataset[df_select][" Diabetes pedigree function"]

print(dataset["Randomfeature2"].sum().get())
print(dataset["Randomfeature3"].sum().get())
print(dataset["Randomfeature4"].sum().get())
print(dataset["Randomfeature5"].sum().get())
"""
