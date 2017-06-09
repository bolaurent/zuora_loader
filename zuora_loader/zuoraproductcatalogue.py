#!/usr/local/bin/python3

import pdb
import logging



 # ns0:Product(fieldsToNull: xsd:string[], Id: xsd:ID, Canonical_Duration_Days__c: xsd:string, Canonical_Family_Product__c: xsd:string, Category: xsd:string, CreatedById: xsd:ID, CreatedDate: xsd:dateTime, Department__c: xsd:string, Description: xsd:string, Discount_Schedule_Name__c: xsd:string, EffectiveEndDate: xsd:date, EffectiveStartDate: xsd:date, Name: xsd:string, SKU: xsd:string, Sub_Family__c: xsd:string, UpdatedById: xsd:ID, UpdatedDate: xsd:dateTime)
productFields = [
    'Id'
    ,'Category'
    ,'CreatedById'
    ,'CreatedDate'
    ,'Department__c'
    ,'Description'
    ,'Discount_Schedule_Name__c'
    ,'EffectiveEndDate'
    ,'EffectiveStartDate'
    ,'Name'
    ,'SKU'
    ,'Sub_Family__c'
    ,'UpdatedById'
    ,'UpdatedDate'
    ,'Zuora_Duration_Days__c'
    ,'Zuora_Product_Family__c'
]
    
#ns0:ProductRatePlan(fieldsToNull: xsd:string[], Id: xsd:ID, ActiveCurrencies: xsd:string, CreatedById: xsd:ID, CreatedDate: xsd:dateTime, Description: xsd:string, EffectiveEndDate: xsd:date, EffectiveStartDate: xsd:date, Name: xsd:string, ProductId: xsd:ID, SFProductCode__c: xsd:string, UpdatedById: xsd:ID, UpdatedDate: xsd:dateTime)

productRatePlanFields = [
    'Id'
    
    # zeep.exceptions.Fault: When querying for active currencies, you cannot query for other fields at the same time.
    # ,'ActiveCurrencies'
    
    ,'CreatedById'
    ,'CreatedDate'
    ,'Description'
    ,'EffectiveEndDate'
    ,'EffectiveStartDate'
    ,'Name'
    ,'ProductId'
    # ,'SFProductCode__c'
    ,'UpdatedById'
    ,'UpdatedDate'
]
    
# ns0:ProductRatePlanCharge(fieldsToNull: xsd:string[], Id: xsd:ID, AccountingCode: xsd:string, ApplyDiscountTo: xsd:string, BillCycleDay: xsd:int, BillCycleType: xsd:string, BillingPeriod: xsd:string, BillingPeriodAlignment: xsd:string, BillingTiming: xsd:string, ChargeModel: xsd:string, ChargeType: xsd:string, CreatedById: xsd:ID, CreatedDate: xsd:dateTime, DefaultQuantity: xsd:decimal, DeferredRevenueAccount: xsd:string, Description: xsd:string, DiscountLevel: xsd:string, EndDateCondition: xsd:string, IncludedUnits: xsd:decimal, LegacyRevenueReporting: xsd:boolean, ListPriceBase: xsd:string, MaxQuantity: xsd:decimal, MinQuantity: xsd:decimal, Name: xsd:string, NumberOfPeriod: xsd:long, OverageCalculationOption: xsd:string, OverageUnusedUnitsCreditOption: xsd:string, PriceChangeOption: xsd:string, PriceIncreasePercentage: xsd:decimal, ProductRatePlanChargeTierData: ProductRatePlanChargeTierData, ProductRatePlanId: xsd:ID, RecognizedRevenueAccount: xsd:string, RevenueRecognitionRuleName: xsd:string, RevRecCode: xsd:string, RevRecTriggerCondition: xsd:string, SmoothingModel: xsd:string, SpecificBillingPeriod: xsd:long, Taxable: xsd:boolean, TaxCode: xsd:string, TaxMode: xsd:string, TriggerEvent: xsd:string, UOM: xsd:string, UpdatedById: xsd:ID, UpdatedDate: xsd:dateTime, UpToPeriods: xsd:long, UpToPeriodsType: xsd:string, UsageRecordRatingOption: xsd:string, UseDiscountSpecificAccountingCode: xsd:boolean, UseTenantDefaultForPriceChange: xsd:boolean, WeeklyBillCycleDay: xsd:string)
productRatePlanChargeFields = [
    'Id'
    ,'AccountingCode'
    ,'ApplyDiscountTo'
    ,'BillCycleDay'
    ,'BillCycleType'
    ,'BillingPeriod'
    ,'BillingPeriodAlignment'
    ,'BillingTiming'
    ,'ChargeModel'
    ,'ChargeType'
    ,'CreatedById'
    ,'CreatedDate'
    ,'DefaultQuantity'
    ,'DeferredRevenueAccount'
    ,'Description'
    ,'DiscountLevel'
    ,'EndDateCondition'
    ,'IncludedUnits'
    ,'LegacyRevenueReporting'
    ,'ListPriceBase'
    ,'MaxQuantity'
    ,'MinQuantity'
    ,'Name'
    ,'NumberOfPeriod'
    ,'OverageCalculationOption'
    ,'OverageUnusedUnitsCreditOption'
    ,'PriceChangeOption'
    ,'PriceIncreasePercentage'
    
    # zeep.exceptions.Fault: invalid field for query: ProductRatePlanCharge.productrateplanchargetierdata
    # ,'ProductRatePlanChargeTierData'
    ,'ProductRatePlanId'
    ,'RecognizedRevenueAccount'
    ,'RevenueRecognitionRuleName'
    ,'RevRecCode'
    ,'RevRecTriggerCondition'
    ,'SmoothingModel'
    ,'SpecificBillingPeriod'
    ,'Taxable'
    ,'TaxCode'
    ,'TaxMode'
    ,'TriggerEvent'
    ,'UOM'
    ,'UpdatedById'
    ,'UpdatedDate'
    ,'UpToPeriods'
    ,'UpToPeriodsType'
    ,'UsageRecordRatingOption'
    ,'UseDiscountSpecificAccountingCode'
    ,'UseTenantDefaultForPriceChange'
    ,'WeeklyBillCycleDay'
        ]  
            
#      ns0:ProductRatePlanChargeTier(fieldsToNull: xsd:string[], Id: xsd:ID, CreatedById: xsd:ID, CreatedDate: xsd:dateTime, Currency: xsd:string, DiscountAmount: xsd:decimal, DiscountPercentage: xsd:decimal, EndingUnit: xsd:decimal, IsOveragePrice: xsd:boolean, Price: xsd:decimal, PriceFormat: xsd:string, ProductRatePlanChargeId: xsd:ID, StartingUnit: xsd:decimal, Tier: xsd:int, UpdatedById: xsd:ID, UpdatedDate: xsd:dateTime)

productRatePlanChargeTierFields = [
    'Id'
    ,'CreatedById'
    ,'CreatedDate'
    ,'Currency'
    
    # zeep.exceptions.Fault: You can only use Price or DiscountAmount or DiscountPercentage in one ProductRatePlanChargeTier query.
    # ,'DiscountAmount'
    # ,'DiscountPercentage'
    
    ,'EndingUnit'
    ,'IsOveragePrice'
    ,'Price'
    ,'PriceFormat'
    ,'ProductRatePlanChargeId'
    ,'StartingUnit'
    ,'Tier'
    ,'UpdatedById'
    ,'UpdatedDate'
]


class ProductBase():
    def __init__(self, record, parent):
        self.record = record
        self.parent = parent
    
    def getChildren(self):
        return []
        
    def getChildByName(self, name):
        children = self.getChildren()
        if name.upper() in children:
            return children[name.upper()]

        return None
        
class Product(ProductBase):
    def __init__(self, record):
        super().__init__(record, None)
        self.ratePlans = {}
        
    def addRatePlan(self, ratePlan):
        self.ratePlans[ratePlan.record['Name'].upper()] = ratePlan

    def getChildren(self):
        return self.ratePlans
        
class ProductRatePlan(ProductBase):
    def __init__(self, record, parent):
        super().__init__(record, parent)
        self.ratePlanCharges = {}
        
    def addRatePlanCharge(self, productRatePlan):
        self.ratePlanCharges[productRatePlan.record['Name'].upper()] = productRatePlan

    def getChildren(self):
        return self.ratePlanCharges

class ProductRatePlanCharge(ProductBase):
    def __init(self, record, parent):
        super().__init__(record, parent)
        
        

class ZuoraProductCatalogue():
    def __init__(self, zuora):
        self.zuora = zuora
        self.productByName = {}
        self.productById = {}
        self.productRatePlanById = {}
        self.productRatePlanChargeById = {}

        # Get Products
        for record in self.zquery('Product', productFields):
            product = Product(record)
            productId = record['Id']
            self.productByName[record['Name'].upper()] = product
            self.productById[record['Id']] = product

        # Get ProductRatePlans
        for record in self.zquery('ProductRatePlan', productRatePlanFields):
            product = self.productById[record['ProductId']]
            productRatePlan = ProductRatePlan(record, product)
            productId = record['ProductId']
            self.productById[productId].addRatePlan(productRatePlan)
            self.productRatePlanById[record['Id']] = productRatePlan        

        # Get ProductRatePlanCharges
        for record in self.zquery('ProductRatePlanCharge', productRatePlanChargeFields):
            productRatePlan = self.productRatePlanById[record['ProductRatePlanId']]
            productRatePlanCharge = ProductRatePlanCharge(record, productRatePlan)
            self.productRatePlanChargeById[record['Id']] = productRatePlanCharge
            productRatePlanId = record['ProductRatePlanId']
            self.productRatePlanById[productRatePlanId].addRatePlanCharge(productRatePlanCharge)
                
    def zquery(self, object, fields, where=''):
        response = self.zuora.query('select ' + ','.join(fields) + ' from ' + object + ' ' + where)
        assert response['done']
        return response.records
    

    
   
