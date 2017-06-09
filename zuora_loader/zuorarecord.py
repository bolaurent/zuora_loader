from dateutil.parser import parse
import pdb

from .accounttemplate import MANGLE_EMAIL_ADDRESSES
from .zuoraproductcatalogue import ZuoraProductCatalogue

import logging


logger = logging.getLogger("loader")

ZUORA_CHUNKSIZE = 50

def getProductCatalogue(zuora):
    try:
        productCatalogue = getProductCatalogue.productCatalogue
    except AttributeError:
        productCatalogue = ZuoraProductCatalogue(zuora)
        getProductCatalogue.productCatalogue = productCatalogue

    return productCatalogue

def getPaymentMethods(zuora):
    try:
        paymentMethods = getPaymentMethods.paymentMethods
    except AttributeError:
        paymentMethods = {record['Name']: record for record in
                        zuora.query('select id, name from paymentmethod')['records']}
        getPaymentMethods.paymentMethods = paymentMethods
    return paymentMethods


def getAccountId(zuora, accountNumber):
    try:
        accountIdByAccountNumber = getAccountId.accountIdByAccountNumber
    except AttributeError:
        accountIdByAccountNumber = {}
        for record in zuora.query('select Id, AccountNumber from Account')['records']:
            accountIdByAccountNumber[record['AccountNumber']] = record['Id']
        getAccountId.accountIdByAccountNumber = accountIdByAccountNumber

    return accountIdByAccountNumber[accountNumber]

subscriptionIdBySubscriptionName = None
def getSubscriptionId(subscriptionName):
    global subscriptionIdBySubscriptionName
    if not subscriptionIdBySubscriptionName:
        subscriptionIdBySubscriptionName = {}
        for record in self.zuora.query('select Id, Name from Subscription')['records']:
            subscriptionIdBySubscriptionName[record['Name']] = record['Id']

    return subscriptionIdBySubscriptionName[subscriptionName]

class CreateZObjectFailureException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

def createSubscriptions(zuora, subscriptions):
    chunkSize = ZUORA_CHUNKSIZE
    # chunkSize = 1
    for chunk in [subscriptions[i:i + chunkSize] for i in range(0, len(subscriptions), chunkSize)]:
        subscribeRequests = [subscription.getSubscribeRequest() for subscription in chunk]
        subscribeResults = zuora.subscribe(subscribeRequests)

        for i in range(len(subscribeResults)):
            subscription = chunk[i]
            result = subscribeResults[i]
            if not result['Success']:
                logger.error("Subscription {} failed: {}".format(subscription.row['Name'], result))


def updateZObjects(zuora, zObjects):
    responses = zuora.updateRecords([zObject.getRecord() for zObject in zObjects])
    distributeResponses(zObjects, responses)

def createZObjects(zuora, zObjs):
    records = [zObj.getRecord() for zObj in zObjs]
    responses = zuora.create(records)
    if distributeResponses(zObjs, responses) == False:
        pdb.set_trace()
        raise CreateZObjectFailureException(type(zObjs[0]))

    children = []
    for zObj in zObjs:
        children = children + zObj.getChildren()

    if children:
        createZObjects(zuora, children)

def distributeResponses(zRecords, responses):
    success = True
    for i in range(0, len(zRecords)):
        zRecord = zRecords[i]
        response = responses[i]
        if response.Success == False:
            pdb.set_trace()
            success = False
        else:
            zRecord.setId(response['Id'])
        zRecord.addZuoraResponse(response)

    return success


class ZuoraRecord():
    mapFields = {}
    keyPrefix = ''
    ignoreFields = set()

    def __init__(self, zuora, row, rowNumber):
        self.zuora = zuora
        self.errors = []
        self.record = None
        self.success = None
        self.row = row
        self.rowNumber = rowNumber

    def setSuccess(self, val):
        self.success = val;

    def getSuccess(self):
        return self.success

    def addErrors(self, errors):
        self.errors = self.errors + errors

    def getErrors(self):
        return self.errors

    def setId(self, id):
        if self.record:
            self.record.Id = id

    def getId(self):
        return self.record.Id

    def getRow(self):
        return self.row

    def getRowNumber(self):
        return self.rowNumber

    def activate(self):
        self.record['Status'] = 'Active'

    def prepareFactoryArgs(self):
        kwargs = {}
        for field, item in self.row.items():
            if field not in self.ignoreFields:
                if field in self.mapFields:
                    field = self.mapFields[field]

                if item and item.lower() == 'false':
                    item = False
                elif item and item.lower() == 'true':
                    item = True

                if item and (field.endswith('Date') or field.endswith('Date__QT')):
                    itemAsDate = parse(item)
                    item = itemAsDate

                kwargs[field] = item
        return kwargs

    def logErrors(self):
        for error in self.errors:
            logger.error(';'.join(['row#'+str(self.rowNumber), self.row['Name'], str(error)]))

        for child in self.getChildren():
            child.logErrors()

    def addZuoraResponse(self, response):
        self.setSuccess(response.Success)
        if response.Success:
            self.setId(response.Id)
        else:
            self.addErrors(response.Errors)

    def getRecord(self):
        return self.record


class ZuoraContactRecord(ZuoraRecord):
    factory = None
    mapFields = {
        'StateProvince': 'State'
    }
    keyPrefix = 'Account'
    ignoreFields = set([
        'IsNewContactStart'
        ,'IsBillTo'
        ,'IsSoldTo'
    ])

    def mangle(self, email):
        return email.replace('@', '=') + '@example.com'

    def __init__(self, zuora, row, rowNumber, account, mangle=True):
        super().__init__(zuora, row, rowNumber)
        if not ZuoraContactRecord.factory:
            ZuoraContactRecord.factory = self.zuora.typeFactory('Contact')
        self.account = account
        kwargs = self.prepareFactoryArgs()
        if mangle:
            for f in MANGLE_EMAIL_ADDRESSES:
                if f in kwargs:
                    kwargs[f] = self.mangle(kwargs[f])

        assert self.row['Country']
        if self.row['Country'] in ['US', 'CA']:
            assert self.row['StateProvince'], row
        try:
            self.record = self.factory(**kwargs)
        except TypeError as err:
            print("Type error likely due to out-of-date wsdl")
            print(err)
            exit(1)

    def setId(self, id):
        super().setId(id)
        if self.row['IsBillTo']:
            self.account.setBillToId(id)
        if self.row['IsSoldTo']:
            self.account.setSoldToId(id)

    def getChildren(self):
        return []



class ZuoraAccountRecord(ZuoraRecord):
    factory = None
    mapFields = {
        'SalesRep': 'SalesRepName'
        ,'Number':  'AccountNumber'
        ,'CRMID': 'CrmId'
        ,'InvoiceDeliveryByEmail': 'InvoiceDeliveryPrefsEmail'
    }
    keyPrefix = 'Account'
    ignoreFields = set([
        'ParentID'          # This functionality not implemented in this loader
    ])

    def __init__(self, zuora, row, rowNumber):
        super().__init__(zuora, row, rowNumber)
        if not ZuoraAccountRecord.factory:
            ZuoraAccountRecord.factory = self.zuora.typeFactory('Account')
        self.contacts = []
        kwargs = self.prepareFactoryArgs()
        if 'Legal_Entity__c' not in kwargs or not kwargs['Legal_Entity__c']:
            kwargs['Legal_Entity__c'] = 'CGL'
        kwargs['Status'] = 'Draft'
        kwargs['BillCycleDay'] = 1
        try:
            self.record = self.factory(**kwargs)
        except TypeError as err:
            print("Type error likely due to out-of-date wsdl")
            print(err)
            exit(1)

    def setBillToId(self, id):
        self.record.BillToId = id

    def setSoldToId(self, id):
        self.record.SoldToId = id

    def getContacts(self):
        return self.contacts

    def addContact(self, row, rowNumber):
        self.contacts.append(ZuoraContactRecord(self.zuora, row, rowNumber, self))

    def setId(self, id):
        super().setId(id)
        for contact in self.contacts:
            contact.record.AccountId = id

    def getChildren(self):
        return self.contacts



class ZuoraRatePlanChargeTierRecord(ZuoraRecord):
    factory = None
    mapFields = {}
    ignoreFields = {}

    def __init__(self, zuora, row, rowNumber):
        super().__init__(zuora, row, rowNumber)
        if not ZuoraRatePlanChargeTierRecord.factory:
            ZuoraRatePlanChargeTierRecord.factory = self.zuora.typeFactory('RatePlanChargeTier')
        kwargs = self.prepareFactoryArgs()
        kwargs['Tier'] = '1'
        try:
            self.record = self.factory(**kwargs)
        except TypeError as err:
            print("Type error likely due to out-of-date wsdl")
            print(err)
            exit(1)

    def getChildren(self):
        return []


class ZuoraRatePlanChargeRecord(ZuoraRecord):
    factory = None


    # ns1:RatePlanChargeData(RatePlanCharge: RatePlanCharge, RatePlanChargeTier: RatePlanChargeTier[])
    dataFactory = None

    mapFields = {
        'TriggerCondition': 'TriggerEvent'
    }
    ignoreFields = {
        'Name'
    }

    def __init__(self, zuora, ratePlan, chargeRow, tierRow, rowNumber):
        super().__init__(zuora, chargeRow, rowNumber)
        if not ZuoraRatePlanChargeRecord.factory:
            ZuoraRatePlanChargeRecord.factory = self.zuora.typeFactory('RatePlanCharge')
        if not ZuoraRatePlanChargeRecord.dataFactory:
            ZuoraRatePlanChargeRecord.dataFactory = self.zuora.typeFactory('RatePlanChargeData', ns='ns1')
        self.ratePlanChargeTiers = []
        kwargs = self.prepareFactoryArgs()

        productRatePlanCharge = ratePlan.getChildByName(chargeRow['Name'])
        if productRatePlanCharge is None:
            pdb.set_trace()
        kwargs['ProductRatePlanChargeId'] = productRatePlanCharge.record['Id']
        kwargs['RatePlanId'] = ratePlan.record['Id']
        if 'Department__c' in kwargs:
            del kwargs['Department__c']
        try:
            self.record = self.factory(**kwargs)
        except TypeError as err:
            print("Type error likely due to out-of-date wsdl")
            print(err)
            exit(1)

        if tierRow:
            self.addRatePlanChargeTier(tierRow, rowNumber)

    def addRatePlanChargeTier(self, tierRow, rowNumber):
        self.ratePlanChargeTiers.append(ZuoraRatePlanChargeTierRecord(tierRow, rowNumber))

    def setId(self, id):
        super().setId(id)
        for ratePlanChargeTier in self.ratePlanChargeTiers:
            ratePlanChargeTier.record.RatePlanChargeId = id

    def getChildren(self):
        return self.ratePlanChargeTiers

    def getRatePlanChargeData(self):
        ratePlanChargeTierList = [ratePlanChargeTier.record for ratePlanChargeTier in self.ratePlanChargeTiers]
        return self.dataFactory(RatePlanCharge=self.record, RatePlanChargeTier=ratePlanChargeTierList)


class ZuoraRatePlanRecord(ZuoraRecord):
    factory = None
    dataFactory = None
    mapFields = {
        'ID': 'Id'
    }
    ignoreFields = {
        'ProductName'
        ,'IsNewRatePlanBegin'
        ,'Name'
    }

    def __init__(self, zuora, ratePlanRow, chargeRow, tierRow, rowNumber):
        super().__init__(zuora, ratePlanRow, rowNumber)
        if not ZuoraRatePlanRecord.factory:
            ZuoraRatePlanRecord.factory = self.zuora.typeFactory('RatePlan')
        if not ZuoraRatePlanRecord.dataFactory:
            ZuoraRatePlanRecord.dataFactory = self.zuora.typeFactory('RatePlanData', ns='ns1')
        self.ratePlanCharges = []
        kwargs = self.prepareFactoryArgs()
        productName = ratePlanRow['ProductName']
        product = getProductCatalogue(zuora).productByName[productName.upper()]
        if ratePlanRow['Name'].upper() not in product.getChildren():
            print(rowNumber, ratePlanRow['Name'], productName)
        ratePlan = product.getChildByName(ratePlanRow['Name'].upper())
        if not ratePlan:
            print(ratePlanRow['Name'])
            pdb.set_trace()
        kwargs['ProductRatePlanId'] = ratePlan.record['Id']
        try:
            self.record = self.factory(**kwargs)
        except TypeError as err:
            print("Type error likely due to out-of-date wsdl")
            print(err)
            exit(1)

        self.addRatePlanCharge(ratePlan, chargeRow, tierRow, rowNumber)

    def addRatePlanCharge(self, ratePlan, chargeRow, tierRow, rowNumber):
        ratePlanCharge = ZuoraRatePlanChargeRecord(self.zuora, ratePlan, chargeRow, tierRow, rowNumber)
        self.ratePlanCharges.append(ratePlanCharge)

    def setId(self, id):
        super().setId(id)
        for ratePlanCharge in self.ratePlanCharges:
            ratePlanCharge.record.SubscriptionId = id

    def getChildren(self):
        return self.ratePlanCharges

    def getRatePlanData(self):
        ratePlanChargeData = [ratePlanCharge.getRatePlanChargeData() for ratePlanCharge in self.ratePlanCharges]
        return self.dataFactory(RatePlan=self.record, RatePlanChargeData=ratePlanChargeData)


class ZuoraAmendmentRecord(ZuoraRecord):
    factory = None
    amendRequestFactory = None
    amendOptionsFactory = None

    mapFields = {
        'OrderType': 'Type'
    }
    ignoreFields = {
        'AccountNumber'
        ,'InvoiceOwnerNumber'
        ,'InvoiceOwnerId'
    }

    def __init__(self, zuora, amendmentRow, subscriptionRow, rowNumber):
        super().__init__(zuora, amendmentRow, rowNumber)
        if not ZuoraAmendmentRecord.factory:
            ZuoraAmendmentRecord.factory = self.zuora.typeFactory('Amendment')
        if not ZuoraAmendmentRecord.amendRequestFactory:
            ZuoraAmendmentRecord.amendRequestFactory = self.zuora.typeFactory('AmendRequest', ns='ns1')
        if not ZuoraAmendmentRecord.amendOptionsFactory:
            ZuoraAmendmentRecord.amendOptionsFactory = self.zuora.typeFactory('AmendOptions', ns='ns1')
        self.ratePlan = None
        kwargs = self.prepareFactoryArgs()
        orderType = amendmentRow['OrderType']
        assert orderType == 'NewProduct', "unsupported Amendment OrderType {}".format(orderType)
        kwargs['Type'] = orderType
        subscriptionId = getSubscriptionId(subscriptionRow['Name'])
        kwargs['SubscriptionId'] = subscriptionId
        try:
            self.record = self.factory(**kwargs)
        except TypeError as err:
            print("Type error likely due to out-of-date wsdl")
            print(err)
            exit(1)


    def setRatePlan(self, ratePlanRow, chargeRow, tierRow, rowNumber):
        self.ratePlan = ZuoraRatePlanRecord(ratePlanRow, chargeRow, tierRow, rowNumber)

    # amend(requests: AmendRequest[], _soapheaders={SessionHeader: SessionHeader()}) -> body: {results: AmendResult[]}, header: {}
    # ns1:AmendRequest(Amendments: {fieldsToNull: xsd:string[], Id: ID, AutoRenew: xsd:boolean, Code:
    # xsd:string, ContractEffectiveDate: xsd:date, CreatedById: ID, CreatedDate: xsd:dateTime, CurrentTerm:
    # xsd:long, CurrentTermPeriodType: xsd:string, CustomerAcceptanceDate: xsd:date, Description: xsd:string,
    # DestinationAccountId: ID, DestinationInvoiceOwnerId: ID, EffectiveDate: xsd:date, Name: xsd:string,
    # RatePlanData: RatePlanData, RenewalSetting: xsd:string, RenewalTerm: xsd:long, RenewalTermPeriodType:
    # xsd:string, ServiceActivationDate: xsd:date, SpecificUpdateDate: xsd:date, Status: xsd:string,
    # SubscriptionId: ID, TermStartDate: xsd:date, TermType: xsd:string, Type: xsd:string, UpdatedById: ID,
    # UpdatedDate: xsd:dateTime}[], AmendOptions: AmendOptions, PreviewOptions: PreviewOptions)

    def getAmendRequest(self):
        ratePlanData = self.ratePlan.getRatePlanData()
        self.record['RatePlanData'] = ratePlanData
        amendOptions = self.amendOptionsFactory(GenerateInvoice=False)
        amendmentRequest = self.amendRequestFactory(
                                    Amendments=self.record,
                                    AmendOptions=amendOptions
                                    )
        return amendmentRequest

    def getChildren(self):
        return []

class ZuoraSubscriptionRecord(ZuoraRecord):
    factory = None
    accountFactory = None
    paymentMethodFactory = None
    otherPaymentMethod = None

    # ns1:SubscribeRequest(Account: Account, PaymentMethod: PaymentMethod, BillToContact: Contact, PreviewOptions: PreviewOptions, SoldToContact: Contact, SubscribeOptions: SubscribeOptions, SubscriptionData: SubscriptionData)
    subscribeRequestFactory = None


    # ns1:SubscriptionData(Subscription: Subscription, RatePlanData: RatePlanData[])
    subscriptionDataFactory = None


    # ns1:SubscribeOptions(ElectronicPaymentOptions: ElectronicPaymentOptions, ExternalPaymentOptions: ExternalPaymentOptions, GenerateInvoice: xsd:boolean, ProcessPayments: xsd:boolean, SubscribeInvoiceProcessingOptions: SubscribeInvoiceProcessingOptions)
    subscribeOptionsFactory = None


    mapFields = {
        'CustomerAcceptanceDate': 'ContractAcceptanceDate'
    }
    ignoreFields = {
        'AccountNumber'
        ,'InvoiceOwnerNumber'
        ,'Description__c'
        ,'SaveAsDraft'
    }

    def __init__(self, zuora, subscriptionRow, rowNumber):
        super().__init__(zuora, subscriptionRow, rowNumber)
        if not ZuoraSubscriptionRecord.factory:
            ZuoraSubscriptionRecord.factory = self.zuora.typeFactory('Subscription')
        if not ZuoraSubscriptionRecord.accountFactory:
            ZuoraSubscriptionRecord.accountFactory = self.zuora.typeFactory('Account')
        if not ZuoraSubscriptionRecord.paymentMethodFactory:
            ZuoraSubscriptionRecord.paymentMethodFactory = self.zuora.typeFactory('PaymentMethod')
        if not ZuoraSubscriptionRecord.otherPaymentMethod:
            ZuoraSubscriptionRecord.otherPaymentMethod = getPaymentMethods(self.zuora)['Other']
        if not ZuoraSubscriptionRecord.subscribeRequestFactory:
            ZuoraSubscriptionRecord.subscribeRequestFactory = self.zuora.typeFactory('SubscribeRequest', ns='ns1')
        if not ZuoraSubscriptionRecord.subscriptionDataFactory:
            ZuoraSubscriptionRecord.subscriptionDataFactory = self.zuora.typeFactory('SubscriptionData', ns='ns1')
        if not ZuoraSubscriptionRecord.subscribeOptionsFactory:
            ZuoraSubscriptionRecord.subscribeOptionsFactory = self.zuora.typeFactory('SubscribeOptions', ns='ns1')
        self.ratePlans = []
        kwargs = self.prepareFactoryArgs()
        accountId = getAccountId(zuora, subscriptionRow['AccountNumber'])
        kwargs['AccountId'] = accountId
        kwargs['InvoiceOwnerId'] = accountId
        if subscriptionRow['InvoiceOwnerNumber']:
            kwargs['InvoiceOwnerId'] = getAccountId(zuora, subscriptionRow['InvoiceOwnerNumber'])
        kwargs['Status'] = 'Draft'
        if not kwargs['InitialTermPeriodType']:
            kwargs['InitialTermPeriodType'] = 'Month'
        try:
            self.record = self.factory(**kwargs)
        except TypeError as err:
            print("Type error likely due to out-of-date wsdl")
            print(err)
            exit(1)

    def addRatePlan(self, ratePlanRow, chargeRow, tierRow, rowNumber):
        ratePlan = ZuoraRatePlanRecord(self.zuora, ratePlanRow, chargeRow, tierRow, rowNumber)
        self.ratePlans.append(ratePlan)

    def setId(self, id):
        super().setId(id)
        for rateplan in self.ratePlans:
            rateplan.record.SubscriptionId = id

    def getChildren(self):
        return self.ratePlans

    def activate(self):
        self.record.status = 'Active'

    def getSubscribeRequest(self):
        account = self.accountFactory(Id=self.record['AccountId'])

        ratePlanDataList = [ratePlan.getRatePlanData() for ratePlan in self.ratePlans]
        subscriptionData = self.subscriptionDataFactory(Subscription=self.record, RatePlanData=ratePlanDataList)
        subscribeOptions = self.subscribeOptionsFactory(ProcessPayments=False, GenerateInvoice=False)
        subscribeRequest = self.subscribeRequestFactory(
                                    Account=account,
                                    SubscriptionData=subscriptionData,
                                    SubscribeOptions=subscribeOptions,
                                    PaymentMethod=self.paymentMethodFactory(Id=self.otherPaymentMethod['Id'])
                                    )
        return subscribeRequest


