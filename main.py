# This Python script integrates metrics generated from mySQL SQL and send them to Coralogix via OTEL

# the script requires a file in a json format as described in queries.json

from os import environ

import json
import mysql.connector

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

with open('queries.json') as file:
    config_data = json.load(file)

resource = Resource(attributes={
    SERVICE_NAME: "mysql-metrics"
})

# define the OTEL metrics exporter. Need to define the CX_ENDPOINT and CX_TOKEN environment variables
reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(
        endpoint=environ.get('CX_ENDPOINT'),
        headers=[('authorization', "Bearer " + environ.get("CX_TOKEN"))])
)


provider = MeterProvider(resource=resource, metric_readers=[reader])

metrics.set_meter_provider(provider)

meter = metrics.get_meter(__name__)


# reading the queries
for query in config_data['queries']:
    # MySQL connection parameters
    mysql_host = query['server']
    mysql_user = environ.get(query['user'])
    mysql_password = environ.get(query['password'])
    mysql_database = query['database']

    metric_name = query['metric_name']
    # Query statement
    query_statement = query['query']

    # Establish a connection to the MySQL server
    connection = mysql.connector.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database,
        auth_plugin='mysql_native_password'
    )

    # Create a cursor object to execute queries
    cursor = connection.cursor()

    # Execute the query
    cursor.execute(query_statement)

    # Fetch all the rows returned by the query
    result = cursor.fetchall()

    # defining the metrics work counter based on metric fields define
    metric_work_counter = []
    for metric_field in query['metric_fields']:
        work_counter_metric_name = "{}_{}".format(metric_name, metric_field['name'])
        metric_work_counter.append( meter.create_counter(
            work_counter_metric_name, unit="", description=''
        ))

    # running on results
    for row in result:
        # defining the labels
        label_data = ''
        comma = ''
        for label_field in query['label_fields']:
            label_data = '{}{}"{}":"{}"'.format(label_data,comma,label_field['name'], row[label_field['index']])
            comma = ','
        label_data = '{'+label_data + '}'
        json_label_data = json.loads(label_data)
        index = 0
        # sending metrics
        for metric_field in query['metric_fields']:
            metric_work_counter[index].add(row[metric_field['index']], json_label_data)
            index += 1
        print(row)

    # Close the cursor and connection
    cursor.close()
    connection.close()
