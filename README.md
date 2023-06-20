# mysql-custom-metrics
This repository contains python script to get metrics out of mysql queries and to send them to Coralogix

The repository contains 3 files:
main.py - Python file to process the queries and to send metrics to Coralogix
queries.json - json file that contains the queries and the metrics+labels setup

Run the following command to address mysql client pre-requisites:
```
sudo apt-get install mysql-client
sudo apt-get install libmysqlclient-dev
pip install mysqlclient
pip install mysql-connector-python
```

Run the following commands (make sure to fill the api key and endpoint):

```
export CX_ENDPOINT=<custom metrics endpoint>
export CX_TOKEN=<send your data api key>
pip install -r requirements.txt
python main.py
```

Run the following commands to define mysql account(s) and password(s) as defined in the queries.json file:
```
export <mysql account>=<account name>
export <mysql account password>=<account password>
```
For the US cluster the endpoint is: https://ingress.coralogix.us:443 - Visit the [Coralogix Domains](https://coralogix.com/docs/coralogix-domain/) to learn more.

queries.json file contains all the queries requires to generate metrics in an array.
Please see below a generic structure for one query:
```
{
  "queries": [
    {
      "server": "<mysql server>",
      "user": "<mysql account>",
      "password": "<mysql account password>",
      "database": "<mysql database (or can be left empty)",
      "query": "SELECT l1,l2,m1,m2 FROM <table>;",
      "metric_name": "<metric prefix>",
      "metric_fields": [
        {
          "index" : 2,
          "name": "m1"
        },
        {
          "index" : 3,
          "name": "m2"
        }
      ],
       "label_fields": [
         {
           "index": 0,
           "name": "l1"
         },
         {
           "index": 1,
           "name": "l2"
         }

      ]
    }
  ]
}
```