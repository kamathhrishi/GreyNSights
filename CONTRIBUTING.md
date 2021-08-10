# Contributing

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
