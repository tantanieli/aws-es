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

ROLLOVER = "7d"

def create_index(index_name, mapping_file = "mapping.json"):
    index_exists = es.indices.exists(index=index_name)
    print("Index exists - {}".format(index_exists))
    if not index_exists:
        print("Creating index - {} using file - {}").format(index_name,mapping_file)
        mapping = json.loads(open(mapping_file, "r").read())
        mapping.pop('index_patterns', None)
        create_response = es.indices.create(index=index_name, body=json.dumps(mapping))
        print(create_response)


def es_index_cleanup_handler(event, context):
    if 'create_index' in event and event['create_index']:
        if 'mapping_file' in event:
            create_index(event['index_name'], event['mapping_file'])
        else:
            create_index(event['index_name'])
        return
    # rolling index and insert template if not exists
    elif 'index_name' in event:
        i_template = "{}_template".format(event['index_name'])
        template_exists = es.indices.exists_template(name=i_template)
        print("Template exists - {}".format(template_exists))
        if not template_exists:
            mapping_file = open("mapping-{}.json".format(event['index_name']), "r")
            es.indices.put_template(name=i_template, body=mapping_file.read())

        index_list = es.cat.indices(index="<{}-2*>".format(event['index_name']), h="index", s="creation.date:desc")
        #index_list = sorted(index_list)
        print("Index list - {}".format(index_list))
        # add new index if needed(update index list by today date)
        today = datetime.strftime((datetime.now()).date(), '%Y.%m.%d')
        #today = "2020.02.20"
        if today in index_list:
            print("For today index has been already created")
        else:
            print("creating new index")
            # is empty or index data < current data
            index_name = event['index_name'] + '-' + today
            #index_name = "new-2020.02.20"
            if 'alias' not in event:
                index_alias = event['index_name']
            else:
                index_alias = event['alias']
            print("Index alias {}".format(index_alias))
            if not index_list:
                es.indices.create(index=index_name, body=json.dumps(
                    {
                        "aliases": {
                            "{}".format(index_alias): {
                                "is_write_index": True
                            }
                        }
                    }
                ))
            else:
                rollover_response = es.indices.rollover(alias=index_alias, body=json.dumps(
                    {
                        "conditions": {
                            "max_age": "23h"
                        }
                    }
                ), new_index=index_name)


#if __name__ == "__main__":
#    event = {'index_name': 'app', 'alias': 'app_time_window'}
#    es_index_cleanup_handler(event, "")