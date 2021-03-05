# GreyNSights

*The grey area between privacy and utility* 

<a href="https://kamathhrishi.github.io/Private_pandas.md/">Introductory Blogpost</a>

<p style="text-align:justify">GreyNSights is a Framework for Privacy-Preserving Data Analysis. Currently with support only for Pandas. The framework allows analysts to remotely query a dataset such that the dataset remains at source and private to data analyst. The package offers flexbility to the analyst by ensuring that they can use the same pandas syntax for analyzing and transforming datasets , but cannot view the indiviual rows. GreyNSights also offers flexibility to query several parties together and get aggregate statistics without revealing individual counts of parties. </p>

The three major principles behind the library:

* <b>No raw data is exposed only aggregates</b>

  The analyst can query and transform the dataset however they would want to , but can only get the aggregate results back. 

* <b>The aggregates or analysis does not leak any information about individual rows</b>

   The aggregate results are differentially private securing data rows from differencing attacks. 

* <b>Pandas capabilities to transform and process datasets is still preserved</b>

  The analyst might have to add a few lines of code for initializing the setup with dataowner , but they would essentially use the same pandas syntax ensuring   
  anybody who already knows pandas could use without having to learn anything more. 



## Usage 

1. <a href="https://github.com/kamathhrishi/GreyNSights/tree/main/examples/Accidents">Accidents example</a> provides examples of how range of queries could be performed and how datasets could be transformed using GreyNSights 
2. <a href="https://github.com/kamathhrishi/GreyNSights/tree/main/examples/Multi%20Party">Federated Analyticals</a> example which shows how you could analyze datasets of several parties together. This is only restricted to linear queries such as sum, average , std and counts. 


## Installation 

1. Clone the repository 

   ``` https://github.com/kamathhrishi/GreyNSights.git ```

2. Install the required packages 

   ``` pip install requirements.txt ```

3. Install the library from source 

   ``` python3 setup.py install ```
