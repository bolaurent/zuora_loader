#!/usr/local/bin/python3

# To use Charles Proxy:
#
# In shell:
#REQUESTS_CA_BUNDLE=/Users/bo/charles-ssl-proxying-certificate.pem
#export REQUESTS_CA_BUNDLE


import logging
import pdb
import csv
from dateutil.parser import parse


from .zuorarecord import ZuoraSubscriptionRecord, createSubscriptions




def splitSubscriptionRow(row):
    orderType = None
    subscription = {}
    ratePlan = {}
    charge = {}
    tier = {}
    for key, value in row.items():

        if key == 'OrderType':
            orderType = value

        elif key.startswith('Subscription.'):
            key = key[len('Subscription.'):]
            subscription[key] = value

        elif key in set(['ContractEffectiveDate', 'CustomerAcceptanceDate', 'ServiceActivationDate']):
            subscription[key] = value

        elif key.startswith('RatePlan.'):
            key = key[len('RatePlan.'):]
            ratePlan[key] = value

        elif key.startswith('Charge.'):
            key = key[len('Charge.'):]
            charge[key] = value

        elif key.startswith('Tier.'):
            key = key[len('Tier.'):]

            if 'Tier.Tier' in row:
                tier[key] = value
            else:
                # Tier.Price has to go on the RatePlanCharge, because we are not using tiered pricing
                charge[key] = value

    if 'CustomerAcceptanceDate' not in subscription:
        subscription['CustomerAcceptanceDate'] = subscription['ContractEffectiveDate']

    if 'ServiceActivationDate' not in subscription:
        subscription['ServiceActivationDate'] = subscription['CustomerAcceptanceDate']

        # avoid zuora error 'Subscription ContractEffectiveDate should not be greater than ServiceActivationDate'
        if parse(subscription['CustomerAcceptanceDate']) < parse(subscription['ContractEffectiveDate']):
            subscription['ContractEffectiveDate'] = subscription['CustomerAcceptanceDate']

    return (orderType, subscription, ratePlan, charge, tier)



def load_subscriptions(zuora, csvReader):
    logger = logging.getLogger("loader")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("loader.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger.info("Subscription load started")


    subscriptions = []
    rowNumber = 0;
    while True:
        try:
            rowNumber += 1
            row = csvReader.__next__()
            (orderType, subscriptionRow, ratePlanRow, chargeRow, tierRow) = splitSubscriptionRow(row)
            if orderType == 'Create Subscription':
                subscription = ZuoraSubscriptionRecord(zuora, subscriptionRow, rowNumber)
                subscriptions.append(subscription)

            subscription.addRatePlan(ratePlanRow, chargeRow, tierRow, rowNumber)
        except csv.Error as err:
            logger.error("csv.Error {} at row #{}".format(str(err), str(rowNumber)))
        except StopIteration:
            break

    logger.info("Lines read={}".format(str(rowNumber)))
    logger.info("Subscriptions read={}".format(str(len(subscriptions))))

    createSubscriptions(zuora, subscriptions)

    for subscription in subscriptions:
        subscription.logErrors()


    logger.info("Subscription load completed")

