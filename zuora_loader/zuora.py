#!/usr/local/bin/python3

import pdb
import json
import datetime
import sys
import zeep
import copy


from lxml import etree 
from zeep import Plugin

ZUORA_CHUNKSIZE = 50



class MyLoggingPlugin(Plugin):
    def ingress(self, envelope, http_headers, operation):
        print(etree.tostring(envelope, pretty_print=True)) 
        return envelope, http_headers
        
    def egress(self, envelope, http_headers, operation, binding_options):
        print(etree.tostring(envelope, pretty_print=True))
        return envelope, http_headers

zeepPlugins =[
    # MyLoggingPlugin()
]

class Zuora():
    def __init__(self, config):
        if isinstance(config, dict):
            self.config = config
        else:
            configfile = open(config)
            self.config = json.load(configfile)

        self.client = zeep.Client(wsdl=self.config['wsdl'])
        # self.client = zeep.Client(wsdl=self.config['wsdl'], plugins=zeepPlugins)
        
        response = self.client.service.login(self.config['user'], self.config['password'])
        sessionid = response.Session

        sessionheader_cls = self.client.get_element('ns1:SessionHeader')
        self.sessionheader = sessionheader_cls(session=sessionid)
        
        self.batchSize = 2000
        self.caseSensitive = False
        
    def query(self, query):
        queryoptions_cls = self.elementFactory('QueryOptions')
        queryoptions = queryoptions_cls(batchSize=self.batchSize, caseSensitive=self.caseSensitive)
        
        query_response = self.client.service.query(
                        queryString=query, 
                        _soapheaders={'QueryOptions': queryoptions, 'SessionHeader': self.sessionheader})
        return query_response
        
    def typeFactory(self, type, ns='ns0'):
        return self.client.get_type(ns + ':' + type)
        
    def elementFactory(self, element, ns='ns1'):
        return self.client.get_element(ns + ':' + element)
        
    # wsdl:
    # create(zObjects: zObject[], _soapheaders={CallOptions: CallOptions(), SessionHeader: SessionHeader()})
    # -> Errors: Error[], Id: xsd:ID, Success: xsd:boolean
    
    def create(self, records):
        saveResults = []

        calloptions_cls = self.elementFactory('CallOptions')
        calloptions = calloptions_cls(useSingleTransaction=False)

        chunks = [records[i:i + ZUORA_CHUNKSIZE] for i in range(0, len(records), ZUORA_CHUNKSIZE)]
        
        # For some reason, the create service mangles the records passed into it
        # We work around that by using deepcopy
        for chunk in chunks:
            saveResults += self.client.service.create(
                                zObjects=copy.deepcopy(chunk),
                                    _soapheaders={'CallOptions': calloptions, 'SessionHeader': self.sessionheader})
        return saveResults


    # wsdl:
    # subscribe(subscribes: SubscribeRequest[], _soapheaders={SessionHeader: SessionHeader()}) -> AccountId: xsd:ID,
    # AccountNumber: xsd:string, ChargeMetricsData: ChargeMetricsData, Errors: Error[], GatewayResponse: xsd:string,
    # GatewayResponseCode: xsd:string, InvoiceData: InvoiceData[], InvoiceId: xsd:ID, InvoiceNumber: xsd:string, 
    # InvoiceResult: InvoiceResult, PaymentId: xsd:ID, PaymentTransactionNumber: xsd:string, SubscriptionId: xsd:ID, 
    # SubscriptionNumber: xsd:string, Success: xsd:boolean, TotalMrr: xsd:decimal, TotalTcv: xsd:decimal
    
    def subscribe(self, subscribeRequests):
        subscribeResults = []

        for chunk in [subscribeRequests[i:i + ZUORA_CHUNKSIZE] for i in range(0, len(subscribeRequests), ZUORA_CHUNKSIZE)]:
            results = self.client.service.subscribe(
                                subscribes=chunk,
                                _soapheaders={'SessionHeader': self.sessionheader})
            subscribeResults += results
        return subscribeResults   
        

    def amend(self, amendRequest):
        return self.client.service.amend(
                                requests=amendRequest,
                                _soapheaders={'SessionHeader': self.sessionheader})


    # wsdl:
    # delete(type: xsd:string, ids: xsd:ID[], _soapheaders={SessionHeader: SessionHeader()}) 
    # -> errors: Error[], id: xsd:ID, success: xsd:boolean
    #
    # 50 objects are supported in a single call.
    # 1,000 calls are supported per 10-minute time window per tenant

    def delete(self, type, ids):
        assert len(ids) <= 50
        response = self.client.service.delete(
                type=type,
                ids=ids,
                _soapheaders={'SessionHeader': self.sessionheader})
        return response


    def updateRecords(self, records):
        saveResults = []
        for chunk in [records[i:i + ZUORA_CHUNKSIZE] for i in range(0, len(records), ZUORA_CHUNKSIZE)]:
            saveResults += self.client.service.update(
                        zObjects=chunk,
                        _soapheaders={'SessionHeader': self.sessionheader})
        return saveResults        
        
    # generate(zObjects: zObject[], _soapheaders={SessionHeader: SessionHeader()}) -> Errors: Error[], Id: xsd:ID, Success: xsd:boolean
    # https://knowledgecenter.zuora.com/DC_Developers/SOAP_API/E_SOAP_API_Calls/generate_call
    def generate(self, invoices): 
        results = []
        chunks = [invoices[i:i + ZUORA_CHUNKSIZE] for i in range(0, len(invoices), ZUORA_CHUNKSIZE)]
        for chunk in chunks:
            results += self.client.service.generate(
                    zObjects=chunk,
                    _soapheaders={'SessionHeader': self.sessionheader})

        return results




