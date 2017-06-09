#!/usr/local/bin/python3

import sys
import logging
import codecs
import csv


from .zuorarecord import ZuoraAccountRecord, ZuoraContactRecord, createZObjects, updateZObjects, CreateZObjectFailureException


def createAccounts(zuora, accounts):
    createZObjects(zuora, accounts)

    updateAccounts = [account for account in accounts if account.success]
    for account in updateAccounts:
        if account.row['Status'] == 'Active':
            account.activate()
    updateZObjects(zuora, updateAccounts)


def splitAccountContact(row):
    account = {}
    contact = {}
    isNewAccountStart = False
    for fieldName, value in row.items():
        if fieldName == 'Account.IsNewAccountStart':
            isNewAccountStart = True
        elif fieldName.startswith('Account.'):
            fieldName = fieldName[len('Account.'):]
            account[fieldName] = value
        elif fieldName.startswith('Contact.'):
            fieldName = fieldName[len('Contact.'):]
            contact[fieldName] = value

    return (isNewAccountStart, account, contact)


def load_accounts(zuora, csvReader):

    logger = logging.getLogger("loader")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("loader.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger.info("Account load started")


    accounts = []
    rowNumber = 0;
    while True:
        try:
            rowNumber += 1
            row = csvReader.__next__()
            isNewAccountStart, accountRow, contactRow = splitAccountContact(row)
            if isNewAccountStart:
                account = ZuoraAccountRecord(zuora, accountRow, rowNumber)
                accounts.append(account)

            account.addContact(contactRow, rowNumber)
        except csv.Error as err:
            logger.error("csv.Error {} at row #{}".format(str(err), str(rowNumber)))
        except StopIteration:
            break
        except CreateZObjectFailureException:
            break

    logger.info("Lines read={}".format(str(rowNumber)))
    logger.info("Accounts read={}".format(str(len(accounts))))

    createAccounts(zuora, accounts)
    for account in accounts:
        for error in account.getErrors():
            logger.error(';'.join(['row#'+str(account.getRowNumber()), account.getRow()['Name'], str(error)]))
        for contact in account.getContacts():
            for error in contact.getErrors():
                logger.error(';'.join(['row#'+str(contact.getRowNumber()), contact.getRow()['WorkEmail'], str(error)]))

    logger.info("Account load completed")

