# ANITA VISUALISATION DASHBAORD

## Getting started
Most packages used are native python3 (datetime, json etc.)
Other packages needed:
- plotly
- dash
- pandas
- numpy

Packages used in other parts of this project:
- bs4
- importlib
- pycountry
- requests
- zipfile

**Requirements.txt**
In the main folder (folder above this one) you can find the requirements txt file. 
This file consists of all the packages used. If this is installed, it will work as well. I don't know if i'm
using all of these packages, seems that a lot are installed dependencies for other packages (such as pandas)'

## Launch the dashboard
1. open terminal
2. Change directory (cd) to visualisation/dash
3. enter `python app.py`
4. The tool should be  launched

## Data
**Demonstation data** \
The data currently used is a CSV (is easier), these can be found in the /dash/data folder.

**Use other data**\
If you want to export JSON into CSV files you can use a jupyter notebook called `json_to_csv.ipynb`
You'll need to have `jupyter` (jupyter notebook) installed for this, or another IDE that can read this file.

# Extra
## How to install requirements.txt file
- open terminal
- cd to the right folder, where the requirement.txt file is
- Exit the current venv (if you are using one)
    - `$ conda deactivate`
- Create a new one
    - `$ conda create -n name_environment`
- Activate venv
    - `$ conda activate name_environment`
- Install packages requirements.txt
    - `(name_environment)$ pip install -r requirements.txt`


 

