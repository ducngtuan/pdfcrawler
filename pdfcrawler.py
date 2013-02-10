import os
import sys
if sys.version_info.major == 2:
    import urlparse
if sys.version_info.major == 3:
    import urllib.parse as urlparse

import argparse
import requests
from bs4 import BeautifulSoup

urls = []
history = []
dir = '.'
timeout = 3
max_deep = 1
max_url = 500
verbose = False

def download(url, request=None):
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
    url = urlparse.urlparse(url)
    name = url.path.split('/')[-1]
    if not name.endswith('.pdf'):
        name += '.pdf'

    return os.path.join(dir, name)

def crawl(url, deep=0):
    deep += 1
    u = urlparse.urlparse(url)
    if u.path.endswith('.pdf'):
        download(url)

    else:
        try:
            r = requests.get(url, timeout=timeout)
            if 'html' in r.headers['Content-Type']:
                if verbose:
                    print('.' * deep + url)

                soup = BeautifulSoup(r.text)
                new_urls = (urlparse.urljoin(url, link.get('href'))
                            for link in soup.find_all('a'))
                urls.extend((url, deep)
                            for url in new_urls
                            if url not in history)

            if 'pdf' in r.headers['Content-Type']:
                # download link to pdf file that does not contain '.pdf'
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
    parser.add_argument('-md', '--max_deep', type=int, default=1,
                        help='''max deep of urls tree, set to 0 will only
                        download pdf(s) in the start url''')
    parser.add_argument('-m', '--max_url', type=int, default=500,
                        help='max numbers of urls, default 500')
    parser.add_argument('-t', '--timeout', type=float, default=3,
                        help='timeout for a connection, default 3 seconds')
    parser.add_argument('-v', '--verbose', help='print more detail output',
                        action='store_true')

    args = parser.parse_args()
    global max_deep
    global max_url
    global verbose
    global dir
    global timeout

    dir = args.directory
    if not os.path.exists(dir):
        os.makedirs(dir)

    max_deep = args.max_deep
    max_url = args.max_url
    timeout = args.timeout
    verbose = args.verbose

    urls.append((args.start_url, 0))

    print('start crawling...')
    while urls and len(history) < max_url:
        url, deep = urls.pop()
        if url in history or deep > max_deep:
            continue
        else:
            history.append(url)
            crawl(url, deep)

if __name__ == '__main__':
    main()
