import argparse

import requests
import dateparser
from sitecrawl import crawl

exclude_paths = [
    '/some_admin_url/',
    '/some_secret_url/',
]


def crawl_site(url, depth=1, no_pound=False, no_get=False, no_validate_ct=False, max_crawl=0, verbose=False):
    """ USe site crawler to crawl the website """

    crawl.base_url = crawl.truncate_last_slash(url)
    crawl.no_pound = no_pound
    crawl.no_get = no_get
    crawl.no_validate_ct = no_validate_ct
    crawl.max_crawl = max_crawl
    crawl.verbose = verbose

    print('* Crawling:', crawl.base_url)
    print('* Depth:', depth)
    print('* Max crawl:', max_crawl)
    print('* No pound:', no_pound)
    print('* No get:', no_get)
    print('* No validate content type:', no_validate_ct)
    print('* Verbose:', verbose)

    crawl.deep_crawl(depth=depth)


def get_last_modified(url):
    """ Get last modified date of a URL """

    header = requests.head(
        url,
        headers=crawl.crawling_headers,
        timeout=crawl.crawling_timeout
    ).headers

    if 'Last-Modified' in header:
        dt = dateparser.parse(header['Last-Modified'])
        if dt:
            return dt.strftime("%Y-%m-%d")

    return None


def write_sitemap(sitemap_path, verbose=False):
    """ Write sitemap to XML file """

    f = open(sitemap_path, "w")
    f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
    f.write("<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n")

    for url in crawl.get_internal_urls():
        # Skip URLs matching excluded paths
        skipped = False
        for exclude_path in exclude_paths:
            if exclude_path in url:
                skipped = True
                break

        # Move to next item if URL is excluded
        if skipped:
            continue

        if verbose:
            print('* Adding URL to sitemap:', url)

        # Get last modified date
        last_modified = get_last_modified(url) or ''

        # Add URL to sitemap
        f.writelines([
            "<url>\n",
            "<loc>" + url + "</loc>\n",
            "<lastmod>" + last_modified + "</lastmod>\n" if last_modified else "",
            "</url>\n"
        ])

    f.write("</urlset>\n")
    f.close()


def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", type=str,
                        help="URL to crawl", required=True)
    parser.add_argument("-s", "--sitemap", type=str,
                        help="XML sitemap destination path", required=True)
    parser.add_argument("-d", "--depth", type=int,
                        help="Depth of the crawl", default=1)
    parser.add_argument("-p", "--no_pound",
                        action='store_true', help="Discard local anchors")
    parser.add_argument("-g", "--no_get", action='store_true',
                        help="Discard GET parameters")
    parser.add_argument("-c", "--no_validate_ct", action='store_true',
                        help="Accept non text/html content types")
    parser.add_argument("-m", "--max", type=int,
                        help="Max number of internal URLs to return (allows to limit crawling of a large website)", default=0)
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="Verbose mode")
    args = parser.parse_args()

    # Crawl the site
    crawl_site(args.url, args.depth, args.no_pound,
               args.no_get, args.no_validate_ct, args.max, args.verbose)

    # Write sitemap
    write_sitemap(args.sitemap, args.verbose)


if __name__ == '__main__':
    main()
