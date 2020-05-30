from requests_aws4auth import AWS4Auth
from warrant import Cognito
import boto3
import requests
import argparse
import traceback
import json

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--domain", help="AWS ElasticSearch domain")
parser.add_argument("-r", "--region", default="us-east-1", help="Region to use")
parser.add_argument("-p", "--profile", default="devqa", help="Profile to use")
parser.add_argument("-up", "--user_pool", help="Cognito User Pool ID")
parser.add_argument("-ci", "--client_id", help="Cognito User Pool Client ID")
parser.add_argument("-cs", "--client_secret", help="Cognito User Pool Client Secret")
parser.add_argument("-cu", "--client_username", help="Cognito username")
parser.add_argument("-cp", "--client_password", help="Cognito password")
args = parser.parse_args()

host = "https://{}/".format(args.domain)
credentials = boto3.Session(profile_name=args.profile).get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, args.region, "es", session_token=credentials.token)

u = Cognito(args.user_pool, args.client_id, client_secret=args.client_secret, username=args.client_username)
u.authenticate(password=args.client_password)
cookies = {'ACCESS-TOKEN': u.access_token, 'ID-TOKEN': u.id_token, 'REFRESH-TOKEN': u.refresh_token}


def prepare_import_data(exported_data):
    exportedObjects = json.loads(exported_data)
    objectsToImport = []
    i = 0
    while i < len(exportedObjects):
        current = exportedObjects[i]
        objectsToImport.append({
            'type': current['_type'],
            'id': current['_id'],
            'attributes': current['_source']
        })
        i += 1
    return json.dumps(objectsToImport)


def create_dashboards():

    kibana_objects_file = open("kibana/kibana_data.json", "r")

    response = requests.post(
        host + "_plugin/kibana/api/saved_objects/_bulk_create?overwrite=true",
        cookies=cookies, json=prepare_import_data(kibana_objects_file.read()), headers={"kbn-xsrf": "reporting"})
    print(response.text)


try:
    response = requests.get(
        host + "_plugin/kibana/api/saved_objects/_find?type=dashboard&per_page=1000&page=1&search_fields=title%5E3&search_fields=description",
        cookies=cookies)

    print response.text
    responseDict = json.loads(response.text)
    print (responseDict)
    if responseDict['total'] == 0:
        create_dashboards()
    else:
        print("There are already {} dashboards".format(responseDict['total']))
except Exception:
    print(traceback.format_exc())
    raise Exception
