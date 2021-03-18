import argparse
import logging
import requests
import time
import os
import csv
from bs4 import BeautifulSoup
from functools import wraps
import pickle
import re

def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as err:
                    msg = "%s, Retrying in %d seconds..." % (str(err), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)
        return f_retry  # true decorator
    return deco_retry


@retry(Exception, tries=40, delay=5, backoff=2, logger=logging.getLogger('retry'))
def get_request_with_retry(url, header):
    return requests.get(url).content


# Get all review urls of all given hotels
def parse_review_urls_of_hotel(base_url, pagination_urls, header):
    # Initialize the list for the resulting urls
    review_urls = list()
    print("base_url",base_url, pagination_urls)
    for pagination_url in pagination_urls:
        # Retrieve url content of the hotel pagination url
        content = get_request_with_retry(pagination_url, header)
        #print(content)
        # Define parser
        soup = BeautifulSoup(content, 'html.parser')
        
        # Get all review containers of the current page
        hotel_review_containers = soup.find('div', attrs={'data-test-target': 'reviews-tab'})
        #print(hotel_review_containers)
        # Retrieve each review url of the current hotel pagination page
        for hotel_review_container in hotel_review_containers:
            #print(hotel_review_container)
            if hotel_review_container.has_attr('class'):
                if len(hotel_review_container['class']) == 2:
                    a = hotel_review_container.find('q')
                    review_urls.append(a.text)

    return review_urls

# Main
if __name__ == '__main__':
    # Setup commandline handler
    parser = argparse.ArgumentParser(description='scrape the reviews of a whole city on tripadvisor' , usage='python tripadvisor-scrapper 294265 d302294 Pan_Pacific_Singapore-Singapore')
    parser.add_argument('id', help='the geolocation id of the city')
    parser.add_argument('hotelid', help='the id of the hotel')
    parser.add_argument('name', help='the name of the city')
    parser.add_argument('--pickle', choices=['load', 'store'], help='[load] store a scraped reviews list as pickle for later parsing,[load] load a scraped reviews list for parsing')
    parser.add_argument('--filename', help='the filename of the pickle file placed in pickle directory')
    args = parser.parse_args()

    # Setup logger
    session_timestamp = time.strftime('%Y%m%d-%H%M%S')
    logging.basicConfig(filename='./logs/' + session_timestamp + '-' + args.name.lower() + '.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logging.getLogger().addHandler(logging.StreamHandler())

    # Define user agent
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:47.0) Gecko/20100101 Firefox/47.0'}

    # Define base urls of TripAdvisor
    BASE_URL = 'http://www.tripadvisor.com.sg/'
    HOTEL_DEFAULT_URL = 'Hotel_Review-g' + args.id + '-d'+ args.hotelid+'-Reviews-'+ args.name + '.html'

    # Parse all needed urls
    if not args.pickle or args.pickle == 'store':
        logger.info('STARTED: Scraping of ' + args.name + ' review urls. Build tree "city-pagination-urls--city-hotel-urls--hotel-pagination-urls--hotel-review-urls".')
        reviews = parse_review_urls_of_hotel(BASE_URL, [BASE_URL+HOTEL_DEFAULT_URL], headers)

        #logger.info("reviews" +  str(reviews))
    
    outfile = './data/'+args.name
    with open(outfile,'w') as f:
        f.write(str(reviews))
    
    logger.info('Written reviews to '+outfile)
