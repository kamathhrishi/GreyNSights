import pydp as dp  # our privacy library
from pydp.algorithms.laplacian import (
    BoundedSum,
    BoundedMean,
    Count,
    Max,
    Min,
    Percentile,
    Median,
)
import pandas as pd
import numpy as np
import numpy


class DPReporter:
    def __init__(self, privacybudget, epsilon):

        self.privacybudget = privacybudget
        self.epsilon = epsilon

    def query(self, cmd, data):

        queries = {
            "count": self.Count,
            "mean": self.Mean,
            "sum": self.Sum,
            "percentile": self.Percetile,
            "max": self.Max,
            "min": self.Min,
            "median": self.Mean,
        }

        return queries[cmd](data)

    def Count(self, data):

        dtype = None

        if isinstance(data[0], numpy.float64):

            dtype = "float"

        elif isinstance(data[0], numpy.int64):

            dtype = "int"

        x = Count(epsilon=self.epsilon, dtype=dtype)
        self.privacybudget -= self.epsilon
        if self.privacybudget < 0:
            raise Exception
        print("Privacy Budget", self.privacybudget)
        return x.quick_result(list(data))

    def Mean(self, data):

        dtype = None

        if isinstance(data[0], numpy.float64):

            dtype = "float"

        elif isinstance(data[0], numpy.int64):

            dtype = "int"

        x = BoundedMean(self.epsilon, 0, int(max(data)), dtype=dtype)
        self.privacybudget -= self.epsilon
        if self.privacybudget < 0:
            raise Exception
        print("Privacy Budget", self.privacybudget)
        return x.quick_result(list(data))

    def Sum(self, data):

        print(data)

        dtype = None

        if isinstance(data.iloc[0], numpy.float64):

            dtype = "float"

        elif isinstance(data.iloc[0], numpy.int64):

            dtype = "int"

        elif isinstance(data.iloc[0], numpy.bool_):

            dtype = "int"
            data = data.astype(numpy.int64)

        print(int(max(data)))

        x = BoundedSum(self.epsilon, 0, int(max(data)), dtype=dtype)
        self.privacybudget -= self.epsilon
        if self.privacybudget < 0:
            raise Exception
        print("Privacy Budget", self.privacybudget)
        return x.quick_result(list(data))

    def Percetile(self, data):

        dtype = None

        if isinstance(data[0], numpy.float64):

            dtype = "float"

        elif isinstance(data[0], numpy.int64):

            dtype = "int"

        x = Percentile(epsilon=self.epsilon, dtype=dtype)
        self.privacybudget -= self.epsilon
        if self.privacybudget < 0:
            raise Exception
        print("Privacy Budget", self.privacybudget)
        return x.quick_result(list(data))

    def Max(self, data):

        dtype = None

        if isinstance(data[0], numpy.float64):

            dtype = "float"

        elif isinstance(data[0], numpy.int64):

            dtype = "int"

        x = Max(epsilon=self.epsilon, dtype=dtype)
        self.privacybudget -= self.epsilon
        if self.privacybudget < 0:
            raise Exception
        print("Privacy Budget", self.privacybudget)
        return x.quick_result(list(data))

    def Min(self, data):

        dtype = None

        if isinstance(data[0], numpy.float64):

            dtype = "float"

        elif isinstance(data[0], numpy.int64):

            dtype = "int"

        x = Min(epsilon=self.epsilon, dtype=dtype)
        self.privacybudget -= self.epsilon
        if self.privacybudget < 0:
            raise Exception
        print("Privacy Budget", self.privacybudget)
        return x.quick_result(list(data))

    def Median(self, data):

        dtype = None

        if isinstance(data[0], numpy.float64):

            dtype = "float"

        elif isinstance(data[0], numpy.int64):

            dtype = "int"

        x = Median(epsilon=self.epsilon, dtype=dtype)
        self.privacybudget -= self.epsilon
        if self.privacybudget < 0:
            raise Exception
        print("Privacy Budget", self.privacybudget)
        return x.quick_result(list(data))


"""reporter = DPReporter(0.1,0.4)

df2 = pd.DataFrame(np.random.randint(0,100000000,size=(100, 4)), columns=list('ABCD'))

print("SUM: ",df2["A"].sum())
print("DP SUM: ",reporter.query("sum", df2["A"]))
print(reporter.query("count", df2["A"]))
print("COUNT: ",df2["A"].count())
print(df2['A'].mean())
print(reporter.query("mean", df2["A"]))
# print(reporter.query("percentile", df2[df2["a"] > 2]["a"]))
#print(reporter.query("max", df2["A"]))
#print(reporter.query("min", df2["A"]))
print(df2['A'].median())
print(reporter.query("median", df2["A"]))"""
