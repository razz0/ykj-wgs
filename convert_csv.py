#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Coordinate transformer
"""
import argparse
import logging
from urllib.error import HTTPError

import pandas as pd
import requests
import time
from lxml import etree


logging.basicConfig(  # filename='classifier.log',
                    filemode='a',
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def post(url, data, retries=0, wait=1):
    """
    Send a post request to the given URL with the given data, expecting a JSON response.
    Throws a HTTPError if the request fails (after retries, if any) or if JSON
    parsing fails.

    `url` is the URL to send the request to.

    `data` is a dict containing the data to send to the URL.

    `retries` is the number of retries to attempt if the request fails. Optional.

    `wait` is the number of seconds to wait between retries. Optional, default is 1 second.
    Has no effect if `retries` is not set.
    """

    if retries < 0:
        raise ValueError('Invalid amount of retries: {}'.format(retries))
    if wait < 0:
        raise ValueError('Invalid retry wait time: {}'.format(wait))

    tries = retries + 1

    while tries:
        logger.debug('Sending request to {} with data: {}'.format(url, data))
        res = requests.post(url, data)
        try:
            res.raise_for_status()
            res = res.json()
        except (HTTPError, ValueError) as e:
            tries -= 1
            if tries:
                logger.warning('Received error ({}) from {} with request data: {}.'
                        .format(e, url, data))
                logger.warning('Waiting {} seconds before retrying'.format(wait))
                time.sleep(wait)
                continue
            elif retries:
                logger.warning('Error {}, out of retries.'.format(e))
            raise HTTPError('Error ({}) from {} with request data: {}.'.format(e, url, data))
        else:
            # Success
            logger.debug('Success, received: {}'.format(res))
            return res

if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="Coordinate transformer", fromfile_prefix_chars='@')
    argparser.add_argument("file", help="CSV file to read coords from")
    args = argparser.parse_args()


    coords = pd.read_csv(args.file, sep=",")


    for coord in coords.iterrows():
        name, y, x, note = coord[1][:4]

        data = dict(action_route='Coordinates',
                    targetSRS='EPSG:4258',
                    srs='NLSFI:ykj',
                    lat=y,
                    lon=x)

        res = post('https://hkp.maanmittauslaitos.fi/hkp/action', data)
        new_lat = res['lat']
        new_lon = res['lon']
        print('{name} - {note}:'.format(name=name, note=note))
        print('Latitude: %s' % new_lat)
        print('Longitude: %s' % new_lon)
        print()
