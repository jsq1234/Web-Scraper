# Web Scraper 

## Installation 
    python -m venv venv
    pip install -r requirements.txt

## Working
Uses Selenium package to use the chrome driver to scrape the page and returns the list of project names plus their
details in a pandas dataframe. You can set the number of results to scrape by change N in the Scraper constructor. 
