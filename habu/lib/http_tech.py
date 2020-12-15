import json
import logging
import os
import os.path
#import pwd
from pathlib import Path

import regex as re
import requests
import requests_cache
from bs4 import BeautifulSoup

DATADIR = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '../data')))

def http_tech(url, cache=True, verbose=False):

    if verbose:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    if cache:
        homedir = Path(os.path.expanduser('~'))
        requests_cache.install_cache(str(homedir / '.habu_requests_cache'), expire_after=3600)

    try:
        r = requests.get(url, verify=False)
    except Exception as e:
        logging.error(e)
        return False

    with (DATADIR / 'apps-habu.json').open() as f:
        data = json.load(f)

    apps = data['apps']
    categories = data['categories']

    content = r.text
    soup = BeautifulSoup(content, "lxml")
    tech = {}

    # convertir los strings a listas, para que siempre los valores sean listas
    for app in apps:
        for field in ['url', 'html', 'env', 'script', 'implies', 'excludes']:

            if field in apps[app]:
                if not isinstance(apps[app][field], list):
                    apps[app][field] = [apps[app][field]]

    content = r.text
    soup = BeautifulSoup(content, "lxml")
    tech = {}

    for app in apps:

        for cookie, value in apps[app].get('cookies', {}).items():
            if cookie in r.cookies:
                if not value or value == r.cookies[cookie]:
                    print(app)

        version_group = False

        for header in apps[app].get('headers', []):
            if header in r.headers:

                header_regex = apps[app]['headers'][header].split('\;')[0]

                if '\;version:\\' in apps[app]['headers'][header]:
                    version_group = apps[app]['headers'][header].split('\;version:\\')[1]

                try:
                    match = re.search(header_regex, r.headers[header], flags=re.IGNORECASE)
                except Exception:
                    continue

                if match or not header_regex:

                    logging.info("{app} detected by {header} HTTP header = {header_content}".format(app=app, header=header, header_content=r.headers[header]))
                    if app not in tech:
                        tech[app] = apps[app]

                    if version_group and version_group.isdigit():
                        try:
                            version = match.group(int(version_group))
                            if version:
                                tech[app]['version'] = version
                        except IndexError:
                            pass


        for key in ['script', 'html']:

            version_group = False

            for item in apps[app].get(key, []):

                item_regex = item.split('\;')[0]

                if '\;version:\\' in item:
                    version_group = item.split('\;version:\\')[1]

                try:
                    match = re.search(item_regex, r.text, flags=re.IGNORECASE & re.MULTILINE)
                except Exception:
                    continue

                if match:
                    logging.info("{app} detected by HTML body with regex {regex}".format(app=app, regex=item_regex))
                    if app not in tech:
                        tech[app] = apps[app]

                    if version_group and version_group.isdigit():
                        try:
                            version = match.group(int(version_group))
                            if version:
                                tech[app]['version'] = version
                        except IndexError:
                            pass

        for url_regex in apps[app].get('url', []):
            try:
                match = re.search(url_regex, url, flags=re.IGNORECASE & re.MULTILINE)
            except Exception:
                continue

            if match:
                logging.info("{app} detected by URL with regex {regex}".format(app=app, regex=url_regex))
                if app not in tech:
                    tech[app] = apps[app]

        for meta in apps[app].get('meta', []):

            version_group = False

            for tag in soup.find_all("meta", attrs={'name': meta}):
                meta_regex = apps[app]['meta'][meta]

                if '\;version:\\' in meta_regex:
                    version_group = meta_regex.split('\;version:\\')[1]

                meta_regex = meta_regex.split('\;')[0]

                try:
                    match = re.search(meta_regex, tag['content'], flags=re.IGNORECASE)
                except Exception:
                    continue

                if match:
                    logging.info("{app} detected by meta {meta} tag with regex {regex}".format(app=app, meta=meta, regex=meta_regex))

                    if app not in tech:
                        tech[app] = apps[app]

                    if version_group and version_group.isdigit():
                        try:
                            version = match.group(int(version_group))
                            if version:
                                tech[app]['version'] = version
                        except IndexError:
                            pass

    for t in list(tech.keys()):
        for imply in tech[t].get('implies', []):
            imply = imply.split('\\;')[0]
            logging.info("{imply} detected because implied by {t}".format(imply=imply, t=t))
            tech[imply] = apps[imply]

    for t in list(tech.keys()):
        try:
            tech[t]['category'] = categories[tech[t]['cats'][0]]['name']
        except KeyError:
            pass

    for t in list(tech.keys()):
        for exclude in tech[t].get('excludes', []):
            logging.info("removing {exlude} because its excluded by {t}".format(exlude=exclude, t=t))
            try:
                del(tech[t])
            except KeyError:
                pass

    response = {}

    for t in sorted(tech):
        response[t] = {'categories':[]}
        if 'version' in tech[t]:
            response[t]['version'] = tech[t]['version']
        for category in tech[t]['cats']:
            response[t]['categories'].append(categories[str(category)]['name'])

    return response

if __name__ == '__main__':
    print(json.dumps(get_tech('https://woocommerce.com', verbose=True, cache=True), indent=4))

