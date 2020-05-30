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

def get_indices_list(prefix):
    indices = []
    _list = es.indices.get_alias()
    print(_list)
    for index in _list:
        # Use only indices that match our prefix
        if index.startswith(prefix + '-2'):
            indices.append(str(index))
    return indices

def remove_index(index):
    if not index:
        print "ERROR: Input is empty. Exiting!"
        exit(1)
    output = es.indices.delete(index)
    print "INFO: Index '"+index+"' removed."
    return output

def es_index_cleanup_handler(event, context):
    indices = get_indices_list(event['index_name'])
    indices = sorted(indices)
    print "INFO: Total",len(indices),"indices found."
    print "INFO: From",indices[0],"to",indices[-1]
    # 3 days ago was last_keep_date date by default
    if 'keep_days' in event:
        keep_days = int(event['keep_days'])
    else:
        keep_days = 3
    last_keep_date = datetime.strftime((datetime.now() - timedelta(days=keep_days)).date(), '%Y.%m.%d')
    #last_keep_date = '2020.01.31'
    last_keep_index = event['index_name'] + '-' + last_keep_date
    print('Will be deleted indexies older '+last_keep_date)

    for i in indices:
        if i<(last_keep_index):
            remove_index(i)
            print(i+" deleted")


#if __name__ == "__main__":
#    event = {'index_name': 'dlq', 'keep_days': '21'}
#    es_index_cleanup_handler(event, "")