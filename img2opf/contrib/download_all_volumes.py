import argparse
import os
from urllib.request import urlopen
from bs4 import BeautifulSoup
from tqdm import tqdm


def page_length(path):
    with open(path) as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    pg_len = []
    for a in soup.find_all('a'):
        o = a['href'].split('%')

        code = o[1].split('C')[-1]
        pg = o[2].split('C')[-1]
        ln = o[-1].split('C')[-1]
        pg_len.append((code, pg, ln))

    return pg_len


def download_all_volumes(path):
    work = path.split('/')[-1].split('.')[0]
    for code, vol, ln in page_length(path):
        vol_dir = 'data/{}/vol-{}'.format(work, vol)
        if not os.path.exists(vol_dir):
             os.makedirs(vol_dir)
        print('[INFO]  Volume-{} downloading....'.format(vol))
        for pg in tqdm(range(1, int(ln)+1)):
            url = 'https://www.tbrc.org/browser/ImageService?work=W22084&igroup={}&image={}&first=1&last={}&fetchimg=yes'.format(code, pg, ln)
            with open(vol_dir + '/page-{0:03d}.png'.format(pg), 'wb') as f:
                f.write(urlopen(url).read())


if __name__ == "__main__":
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--html", type=str, help="directory path containing all the images")
    args = ap.parse_args()

    download_all_volumes(args.html)
