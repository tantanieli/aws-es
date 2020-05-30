#!/usr/bin/python

from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import json
from datetime import datetime, timedelta
import os
import json

host = os.getenv("ES_HOST")
credentials = boto3.Session().get_credentials()
es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=AWS4Auth(credentials.access_key, credentials.secret_key, 'us-east-1', 'es', session_token=credentials.token),
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)


def update_template(index_name):

    i_template = "{}_template".format(index_name)
    # your *.json must called like mapping-{}.json
    # for example: mapping-appname.json
    mapping_file = open("mapping-{}.json".format(index_name), "r")
    es.indices.put_template(name=i_template, body=mapping_file.read())


#if __name__ == "__main__":
#    index_name = "app"
#    update_template(index_name)