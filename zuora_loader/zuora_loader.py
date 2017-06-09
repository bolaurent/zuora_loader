#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import os
import codecs
import argparse
import json
import csv
import pdb

from .zuora import Zuora
from .load_accounts import load_accounts
from .load_subscriptions import load_subscriptions
from .load_amendments import load_amendements



#add correct version number here
__version__ = "0.0.1"


PROGRAMNAME = "zuora_loader"
VERSION = __version__
COPYRIGHT = ""



def main():
    logger = logging.getLogger("loader")
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(description='Load a csv file into Zuora instance')
    parser.add_argument('--sandbox', action="store_true", default=False)
    parser.add_argument("filename", help="file to load")
    parser.add_argument("object", help="zuora object to load")
    args = parser.parse_args()

    if args.sandbox:
        zuora_configfile = os.path.expanduser('~') + '/.zuora-sandbox-config.json'
    else:
        zuora_configfile = os.path.expanduser('~') + '/.zuora-production-config.json'

    with open(zuora_configfile, 'r') as f:
        zuora_config = json.load(f)

    zuora = Zuora(zuora_config)

    with codecs.open(args.filename, 'r', 'utf-8') as csvfile:
        csvReader = csv.DictReader(csvfile, delimiter=',')

        if args.object == 'account':
            load_accounts(zuora, csvReader)
        elif args.object == 'subscription':
            load_subscriptions(zuora, csvReader)
        elif args.object == 'amendment':
            load_amendments(zuora, csvReader)
        else:
            print('object {} is invalid'.format(args.object))
            exit(1)


if __name__ == "__main__":
    main()

