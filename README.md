# GreyNSights

*The grey area between privacy and utility* 

GreyNSights is a Framework for Privacy-Preserving Data Analysis. Currently with support only for Pandas. The framework allows analysts to remotely query a dataset such that the dataset remains at source and private to data analyst. The package offers flexbility to the analyst by ensuring that they can use the same pandas syntax for analyzing and transforming datasets , but cannot view the indiviual rows. GreyNSights also offers flexibility to query several datasets together and get aggregate statistics. 

The three major principles behind the library:

* No raw data is exposed only aggregates 
* The aggregates or analysis does not leak any information about individual rows 
* Pandas capabilities to transform and process datasets is still preserved


## Installation 

1. Clone the repository 

   ``` https://github.com/kamathhrishi/GreyNSights.git ```

2. Install the required packages 

   ``` pip install requirements.txt ```

3. Install the library from source 

   ``` python3 setup.py install ```
