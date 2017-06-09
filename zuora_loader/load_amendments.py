#!/usr/local/bin/python3

# To use Charles Proxy:
#
# In shell:
#REQUESTS_CA_BUNDLE=/Users/bo/charles-ssl-proxying-certificate.pem
#export REQUESTS_CA_BUNDLE


import logging
import pdb
import csv



from .zuorarecord import ZuoraAmendmentRecord, createZObjects, distributeResponses, CreateZObjectFailureException



def splitAmendmentRow(row):
    amendment = {}
    subscription = {}
    ratePlan = {}
    charge = {}
    tier = {}
    for key, value in row.items():
        if key.startswith('Amendment.'):
            key = key[len('Amendment.'):]
            amendment[key] = value

        elif key.startswith('Subscription.'):
            key = key[len('Subscription.'):]
            subscription[key] = value

        elif key in set(['ContractEffectiveDate','OrderType']):
            amendment[key] = value

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

    return (amendment, subscription, ratePlan, charge, tier)


def load_amendements(zuora, csvReader):
    logger = logging.getLogger("loader")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("loader.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger.info("Amendments load started")


    rowNumber = 0;
    while True:
        try:
            rowNumber += 1
            row = csvReader.__next__()
            (amendmentRow, subscriptionRow, ratePlanRow, chargeRow, tierRow) = splitAmendmentRow(row)
            if amendmentRow['OrderType'] == 'NewProduct':
                amendment = ZuoraAmendmentRecord(zuora, amendmentRow, subscriptionRow, rowNumber)
                amendment.setRatePlan(ratePlanRow, chargeRow, tierRow, rowNumber)
                amendRequest = amendment.getAmendRequest()
                results = zuora.amend(amendRequest)
                if not results[0]['Success']:
                    logger.error(result)

            else:
                logger.error("Unsupported OrderType {} at row #{}".format(orderType, str(rowNumber)))
        except csv.Error as err:
            logger.error("csv.Error {} at row #{}".format(str(err), str(rowNumber)))
        except StopIteration:
            break

        bar.update(rowNumber)

    logger.info("Lines read={}".format(str(rowNumber)))
    logger.info("Amendments load completed")

