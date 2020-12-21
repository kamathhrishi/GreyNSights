from analyst import DataWorker, DataSource, Pointer, Command, Analyst
from session import framework

"""
# Framework Test
e = framework()

identity = Analyst("Alice", port=65441, host="127.0.0.1")
b = DataWorker(port=65441, host="127.0.0.1")
a = DataSource(identity, b, "Sample Data").init_pointer()


pandas = e.pandas

df = pandas.DataFrame(a)

"""

# Pandas Test
e = framework()

identity = Analyst("Alice", port=65441, host="127.0.0.1")
b = DataWorker(port=65441, host="127.0.0.1")
a = DataSource(identity, b, "Sample Data").init_pointer()

pandas = e.pandas
# matplotlib = e.matplotlib

df = pandas.DataFrame(a)

# plt = matplotlib.pyplot

# plt.plot(a["area"],a["population"]).get()

# plt.hist(a["area"]).get()

# plt.hist(a["population"]).get()

# print(a['area'])
# a.head().get()

ht = df
print(ht.sum(axis=1).get())

ht = df["area"]
ht = ht.unique().get()

kt = df.std()

print(kt + kt)

# print(pt.unique())

print(kt + kt)
print(kt - kt)

# print(pt * pt)
# print(pt / pt)
print(ht[0:1])
