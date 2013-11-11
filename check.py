import logging
import requests
from requests.exceptions import TooManyRedirects, SSLError, ConnectionError
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger('urlchecker')
logger.setLevel(logging.DEBUG)

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)s - %(message)s')

sh.setFormatter(formatter)

logger.addHandler(sh)

checked_urls = []

def absolute_urls(url, deepth=1, extract_id=None, extract_class=None, internal_urls=[], verify_cert=True):
    """ check for absolute internal urls
    """

    logger.debug('process "%s"', url)
    
    try:
        r = requests.get(url, verify=verify_cert)
    except TooManyRedirects:
        logger.error('Redirect loop detected at "%s"', url)
        return
    except SSLError as e:
        logger.warn('SSLError at "%s": %s', url, e)
        return absolute_urls(url, deepth, extract_id, extract_class, internal_urls, verify_cert=False)
    except ConnectionError as e:
        logger.error('ConnectionError at "%s": %s', url, e)
        return

    if r.status_code != 200:
        logger.error('[%d] Error loading page "%s"', r.status_code, url)

    if not 'text/html' in r.headers['content-type']:
        logger.debug('skip non-html file: %s at "%s"', r.headers['content-type'], url)
        return

    bs = BeautifulSoup(r.text)

    if extract_id is not None:
        bs = bs.find(attrs={'id': extract_id})
    elif extract_class is not None:
        bs = bs.find(attrs={'class': extract_class})

    links = []

    if bs is None:
        logger.debug('Empty page content, check extract_id/extract_class: "%s"', url)
        return

    for a in bs.findAll('a'):
        if not a.has_attr('href'):
            logger.error('Invalid link: "%s" at "%s"', a, url)
            continue

        href = a['href']
        if href in checked_urls:
            continue

        if href.startswith('mailto'):
            logger.debug('mail link found: %s at "%s"', href, url)
            continue

        if href.startswith('http'):
            h = href[href.find('//')+2:]
            if h[:h.find('/')] in internal_urls:
                logger.warn('internal absolute url found: "%s" at "%s"', href, url)
                links.append(href)
                
        else:
            links.append(urljoin(url, href))

    if deepth <= 0:
        return

    for link in links:
        absolute_urls(link, deepth-1, extract_id, extract_class,
                      internal_urls, verify_cert)

