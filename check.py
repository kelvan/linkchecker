import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger('urlchecker')
logger.setLevel(logging.INFO)

def check_absolute(url, deepth=1, extract_id=None, extract_class=None, internal_urls=[]):
    """ check for absolute internal urls
    """
    checked_urls = []
    
    r = requests.get(url)
    if r.status_code != 200:
        logger.error('[%d] Error loading page "%s"', r.status_code, url)
    
    bs = BeautifulSoup(r.text)

    if extract_id is not None:
        bs = bs.find(attrs={'id': extract_id})

    for a in bs.findAll('a'):
        href = a['href']
        if href.startswith('http'):
            h = href[href.find('//')+2:]
            if h[:h.find('/')] in internal_urls:
                logger.warn('internal absolute url found: "%s"', href)

    return bs
