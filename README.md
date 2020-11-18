# ANITA SCRAPER
This scraper scrapes multiple marketplaces for different products and vendors and creates json files where all information is stored.

## Getting started

- Clone / download this github
- Use python + virtual environments (optional)
- install the following packages \
You can also use the `requirements.txt` file to install all packages into your conda env
    - bs4
    - importlib
    - pycountry
    - requests
    - zipfile
    - plotly
    - dash
    - pandas
    - numpy
    
**How to do:**
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

    
 
## Included markets
DarkNet:
- Agartha
- Apollon
- Berlusconi
- CannaHome
- Cannazon
- Darkmarket
- Drugs & Medicine
- Empire Market (only Vendor, no product or feedback due to lack of data)
- Silkroad 3
- Tochka



SurfaceWeb:
- directdrugs (only Product, no vendors on website)
- drugscenter (Only Product, no vendors on website)
- palmetto (Only product, no vendors on website)

## Format of the github

- anita_scraping_tool
    - anita \
    This folder contains all modules
        - Scraper.py \ 
        The scraper module
        - Importfile.py \
        The import scraper that contains the module that moves the files and structures them
        - Merge.py \
        The module that merges the files and exports the json files
        - MarketScraper (folder)
            - MarketIdentifier.py \
            The module that contains the identifier for the different markets
            - [market].py \
            A lot of differet scrapers per market.
        
    - main_notebook.ipynb \
    Contains the commands to use the modules. Used demonstration data
    - DATA_DEMONSTRATION_PURPOSES \
    This is the folder that contains the example data
        - input_phase_1 \
        contains some example data
        - output_phase_1 \
        Here the output of the main_notebook will be copied to
        - output_phase_3 \
        The output of Phase 3 will be copied to this folder
        - BACKUP_FOR_TRYING_AGAIN \
        Contains the content of the above 3 folders, for trying again
