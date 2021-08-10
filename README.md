# GreyNSights

*The grey area between privacy and utility*

<a href="https://kamathhrishi.github.io/MyWebsite/jekyll/update/2021/02/22/Privatepandas.html">Introductory Blogpost</a>

<p style="text-align:justify">GreyNSights is a Framework for Privacy-Preserving Data Analysis. Currently with support only for Pandas. The framework allows analysts to remotely query a dataset such that the dataset remains at source and private to data analyst. The package offers flexbility to the analyst by ensuring that they can use the same pandas syntax for analyzing and transforming datasets, but cannot view the indiviual rows. GreyNSights also offers flexibility to query several parties together and get aggregate statistics without revealing individual counts of parties. </p>

<h3>Not for production usage.</h3>
</br>

The three major principles behind the library:

* <b>No raw data is exposed only aggregates</b>

  The analyst can query and transform the dataset however they would want to, but can only get the aggregate results back.

* <b>The aggregates or analysis does not leak any information about individual rows</b>

   The aggregate results are differentially private securing data rows from differencing attacks.

* <b>Pandas capabilities to transform and process datasets is still preserved</b>

  The analyst might have to add a few lines of code for initializing the setup with dataowner, but they would essentially use the same pandas syntax ensuring
  anybody who already knows pandas could use without having to learn anything more.


## Installation

1. Clone the repository

   ``` https://github.com/kamathhrishi/GreyNSights.git ```

2. Install the required packages

   ``` pip install requirements.txt ```

3. Install the library from source

   ``` python3 setup.py install ```


## Workflow Diagram

<div style="text-align:center">
<img height="500px" widht="500px" src="https://github.com/kamathhrishi/GreyNSights/blob/main/images/Overall%20Diagram.png?raw=true"></img>
</div>

## Usage

Analysis using GreyNSights hosted remotely.

```python

#Initilization code of GreyNSights
import GreyNsights
from GreyNsights.analyst import DataWorker, DataSource, Pointer, Command, Analyst
from GreyNsights.frameworks import framework

identity = Analyst("Alice", port=65441, host="127.0.0.1")
worker = DataWorker(port=6544, host="127.0.0.1")
dataset = DataSource(identity,worker, "Sample Data")
config = dataset.get_config()

#Initialization Pointer
dataset_pt = config.approve().init_pointer()

#Analysis of dataset
df = pandas.DataFrame(dataset_pt)
df.columns
df.describe().get()
df['carrots_eaten'].mean().get()
df['carrots_eaten'].sum().get()
(df['carrots_eaten']>70).sum().get()
df['carrots_eaten'].max().get()
```

Analysis using Pandas

```python
dataset=pd.read_csv(<PATH>)

df = pandas.DataFrame(dataset)
df.columns
df.describe().get()
df['carrots_eaten'].mean()
df['carrots_eaten'].sum()
(df['carrots_eaten']>70).sum()
df['carrots_eaten'].max()
```

## Examples

1. <a href="https://github.com/kamathhrishi/GreyNSights/tree/main/examples/Accidents">Accidents example</a> provides examples of how range of queries could be performed and how datasets could be transformed using GreyNSights
2. <a href="https://github.com/kamathhrishi/GreyNSights/tree/main/examples/Multi%20Party">Federated Analytics</a> example which shows how you could analyze datasets of several parties together. This is only restricted to linear queries such as sum, average, std and counts.


## Contributing

There are several ways you could possibly contribute. I haven't put them as issues yet.
If you would be interested in contributing, write to me at kamathhrishi@gmail.com.
I will be putting up some issues soon which you can take up by commenting on the issue. 

Here are the steps you can follow to make feature changes and contribute:

1. Fork the repository 
2. Clone it locally using git command 
   ``` git clone https://github.com/{your username}/GreyNSights.git ```
3. Install requires packages (recommended to perform this in a seperate virtualenv or conda environment)

   ``` pip install requirements.txt ```
   
4. Install the package 

   ``` python3 setup.py install ```
   
5. Ensure tests are running by running pytest in the root of repository

   ``` pytest ```
   
6. Make the required changes 
7. Run precommit hook 
   ``` pre-commit run --all-files ```
9. Test if the changes are okay by running pytest again 
10. Add it to git, commit it and push it. 
11. Make a pull request to this repository
