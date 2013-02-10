import os
import sys
if sys.version_info.major < 3:
    import urlparse
if sys.version_info.major >= 3:
    import urllib.parse as urlparse

import argparse
import requests
from bs4 import BeautifulSoup

urls = []
history = []
dir = '.'
timeout = 3
max_depth = 1
max_url = 500
verbose = False

def download(url, request=None):
    '''Download the URL.
    If the request is already available, direct write content to file.
    '''
    
    print('> ' + url)
    try:
        if not request:
            request = requests.get(url, timeout=timeout)

        with open(path_for(url), 'wb') as f:
            f.write(request.content)

    except Exception as e:
        if verbose:
            print(e)


def path_for(url):
    '''Path of the PDF file for the url'''
    
    url = urlparse.urlparse(url)
    name = url.path.split('/')[-1]
    if not name.endswith('.pdf'):
        name += '.pdf'

    return os.path.join(dir, name)

def crawl(url, depth=0):
    '''Crawl the URL. If it is a link to a PDF file, save the file to disk.'''
    
    depth += 1
    u = urlparse.urlparse(url)
    if u.path.endswith('.pdf'):
        download(url)

    else:
        try:
            r = requests.get(url, timeout=timeout)
            if 'html' in r.headers['Content-Type']:
                if verbose:
                    print('.' * depth + url)

                soup = BeautifulSoup(r.text)
                new_urls = (urlparse.urljoin(url, link.get('href'))
                            for link in soup.find_all('a'))
                urls.extend((url, depth)
                            for url in new_urls
                            if url not in history)

            if 'pdf' in r.headers['Content-Type']:
                # the request actually returns a PDF file
                # write the content of the request directly to disk
                download(url, r)

        except Exception as e:
            if verbose:
                print(e)

def main():
    parser = argparse.ArgumentParser(description=
        '''crawl the start url and pages linked to it,
        and download all pdf(s) found''')
    parser.add_argument('start_url', help='start url')
    parser.add_argument('-d', '--directory', default='.',
                        help='download directory, default current directory')
    parser.add_argument('-md', '--max_depth', type=int, default=1,
                        help='''max depth of the urls tree, set to 1 will only
                        download pdf(s) in the start url''')
    parser.add_argument('-m', '--max_url', type=int, default=500,
                        help='max numbers of urls in the history, default 500')
    parser.add_argument('-t', '--timeout', type=float, default=3,
                        help='timeout for a connection, default 3 seconds')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='print more detail output')

    args = parser.parse_args()
    global max_depth
    global max_url
    global verbose
    global dir
    global timeout

    dir = args.directory
    if not os.path.exists(dir):
        os.makedirs(dir)

    max_depth = args.max_depth
    max_url = args.max_url
    timeout = args.timeout
    verbose = args.verbose

    urls.append((args.start_url, 0))

    print('start crawling...')
    while urls and len(history) < max_url:
        url, depth = urls.pop()
        if url in history or depth > max_depth:
            continue
        else:
            history.append(url)
            crawl(url, depth)

if __name__ == '__main__':
    main()
