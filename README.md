zuora_loader
======

A python tool for loading accounts, contacts, subscriptions, and amendments into a Zuora instance, 
using the same format at the Zuora Connect tool.

Note that this code is extremely rough, and I won't be maintaining it. 

I wrote it to migrate a complex set of data from Salesforce to Zuora. If I were starting
from scratch now, I would use the Zuora REST API (it wasn't complete when I started this project).


Requirements
------------

Python 3
[zeep](https://github.com/mvantellingen/python-zeep)

Install
-------

```
pip install git+git://github.com/bolaurent/zuora_loader.git
```

Usage
-----

Execute the load as follows:

```
zuora_loader-runner.py  --sandbox zuora_loader/sample_data/account.csv account
zuora_loader-runner.py  --sandbox zuora_loader/sample_data/subscription.csv subscription
```


Credentials are stored in one of the following files in your home directory:

```
~/.zuora-sandbox-config.json
~/.zuora-production-config.json
```

The format of the credentials file is like this:

```
    {
      "user":     "me@mycompany.com",
      "password": "ksjfklsjklsdl",
      "wsdl":     "/Users/bo/.zuora-production/zuora.a.84.0.wsdl",
      "//endpoint": "https://apisandbox.zuora.com/apps/services/a/78.0",
      "verboseLog": false
    }
```




About
-----

