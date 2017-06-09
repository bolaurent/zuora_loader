zuora_loader
======

A python tool for loading accounts, contacts, subscriptions, and amendments into a Zuora instance, 
using the same format at the Zuora Connect tool.

Note that this code is extremely rough, and I won't be maintaining it. 

I wrote it to migrate a complex set of data from Salesforce to Zuora. If I were starting
from scratch now, I would use the Zuora REST API (it wasn't complete when I started this project).


Requirements
------------

Python 3.

Install
-------

Install latest version: **pip install --process-dependency-links shop_provision**.

Usage
-----

```
zuora_loader-runner.py  --sandbox zuora_loader/sample_data/account.csv account
zuora_loader-runner.py  --sandbox zuora_loader/sample_data/subscription.csv subscription
```


About
-----

