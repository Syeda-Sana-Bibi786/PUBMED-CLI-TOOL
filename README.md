
## Demo
https://github.com/user-attachments/assets/526a29a8-7b99-4254-9192-6a077b4ee2c8

# PUBMED CLI - get-papers-list
A python CLI tool to fetch PubMed research papers and extract details like PubmedID,Title,Publication Date,Non-academic Author(s),Company Affiliation(s) & Corresponding Author Email (if available) into a CSV file.
## Project Structure
PUBMED/
|__ .venv #virtual environment
|__ pyproject.toml #poetry config and dependencies
|__ README.md #project Documentation
|__PUBMED/
|  |__ __init__.py #Makes PUBMED a python package
|  |
package
|  |__ __main__.py #Main CLI code and logic

All logic lives in __main__.py:
-CLI parsing with argparse
-PubMed API Search using eUtils
-Author name,affiliation , and email extraction
-Non-academic filtering
-CSV export
## Features
-Search for PubMed papers using a keyword
-Filters out academic authors
-Extract author names,affiliations and corresponding emails (if available)
-Save results to CSV
-Debug mode to inspect fetched data
## Installation
This project uses [Poetry](https://python-poetry.org/) for dependency management and packaging.
-Can install using the command in terminal: pip install poetry
-Then type this:
poetry install
## Requirements
-python 3.10 or higher
-Poetry ([Installation guide](https://python-poetry.org/docs/#installation))
## Installation Steps
Clone the repository and install dependencies:
in terminal
git clone
https://github.com/Syeda-Sana-Bibi786/pubmed-cli.git
cd pubmed-cli
poetry install
## To Execute The Program
-In terminal type:
poetry run get-papers-list --query "covid vaccine" --file covidvac.csv --debug
## CLI Flags:
--query   (required) : Search term to query PubMed
--file    (optional) : Output CSV filename (default: output.csv)
--debug   (optional) : Show internal debug info
Example:
poetry run get-papers-list --query "AI in medicine" --file ai_results.csv --debug
## CSV Output Format:
PubMedID, Title, Publication Date, Author, Affiliation, Corresponding Author Email
## Filtering Logic:
Filters out academic authors based on these keywords:
"university", "college", "institute", "school", "hospital", "center", "centre"
# Error Handling:
- Handles blank queries
- Detects API request failures (timeouts, 500s)
- Handles XML parsing issues
- Skips over broken/missing data
# Typed Python:
- Fully type-annotated using Python’s `typing` module
- Types used: List, Dict, Optional, etc.
- You can check it with:
  poetry add --dev mypy
  poetry run mypy PUBMED/
# Libraries Used:
- requests         : For HTTP calls to PubMed
- beautifulsoup4   : For XML parsing
- lxml             : Fast XML backend for BeautifulSoup
- csv, re, argparse: Built-in Python modules
- Poetry           : For managing dependencies and packaging
