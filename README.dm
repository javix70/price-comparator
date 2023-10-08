# Supermarket Price Comparator for Valdivia, Chile

This Python project aims to scrape supermarket data from the city of Valdivia in Chile and compare prices. It's a great starting point for anyone looking to understand data extraction and web scraping using Scrapy and Django.

## Project Overview

1. **Objective**: Extract and compare supermarket product prices in Valdivia, Chile.
2. **Main Tools**: Scrapy (for web scraping) and Django (for backend operations).

## Getting Started

### Prerequisites

Before you start, make sure you have the following dependencies installed:

```python
pip install virtualenv scrapy django
```

> Note: There are some additional dependencies mentioned (like `scrapy-splash`, `requests`, and docker commands related to `splash`). These are not used currently and can be skipped unless needed for future enhancements.

### Setting up the Environment

1. **Activate the virtual environment**:
   
```python
source venv/bin/activate
```

2. **Django database setup**:

```python
python manage.py makemigrations
python manage.py migrate
```

### Running the Scraper

Navigate to the `supermarket` directory from the root of the project and execute the spider named `lider`:

```python
cd supermarket
scrapy crawl lider
```

### Debugging Tips

1. **Using Scrapy Shell**:
   
```python
scrapy shell <url>
```

2. **Using Python Debugger (pdb)**:

Insert the following line of code at the location where you want to set a breakpoint:

```python
import pdb; pdb.set_trace()
```

### Utilities

- **Pretty-print output**:
  
```python
from pprint import pprint
pprint(response.body)
```

- **List and filter public methods**:

```python
public_methods = [method for method in dir(HtmlResponse) if not method.startswith('_')]
```

- **Get documentation for Python functions**:

```python
help([])
help(type([]))
```