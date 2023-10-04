# The propose for this project is to scrapy all supermarket from valdivia city on Chile and comparator de prices.

# The first step is to extract the products for each supermarket, for this we use the scrapy library and the xpath for each supermarket.

# prerequisites
```python
  install virtualenv
  install scrapy
  install django
  install scrapy-splash  # NOT USED
  install requests # NOT USED
  docker pull scrapinghub/splash1 # NOT USED
  database postgresql
```


# active the virtualenv
```python
  source venv/bin/activate
```


# Execute the spider
```python
  scrapy crawl lider
```

# for debug
```python
   scrapy shell <url>

# Or you can use the pdb library
import pdb; pdb.set_trace() into the parse method in the spider


# Utilities for me

# Pretty print output
import pprint
pprint.pprint(response.body)

# Get and Filter public_methods
public_methods = [method for method in dir(HtmlResponse) if not method.startswith('_')]


# execute the docker container , NOT USED
```python
  sudo docker pull scrapinghub/splash
  sudo docker run -it -p 8050:8050 --rm scrapinghub/splash # Acts as a daemon
```