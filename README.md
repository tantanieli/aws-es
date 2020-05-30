# Index management. Kibana. ES

-------------------------------------------------------------------------------------------------

This project can help you a little to unterstand, what is index management, how you can implement it in EFK using python, and also how to restore your dashboards from json with python.

Also there is an example CloudFormation template for AWS Lambda functions and s3 bucket.

-------------------------------------------------------------------------------------------------
UPDATE CURRENT TEMPLATE MANUALLY (current data structure)


- change "index_name" to *component_name* and check ES host in index_management/update_mapping.py
  
- add your changes to your component's template index_management/mapping-*component_name*.json

- run index_management/update_mapping.py

- don't forget to push your index_management/mapping-*component_name*.json changes 

-------------------------------------------------------------------------------------------------

For deletion

example(lambda input): {'index_name': 'app', 'keep_days': '14'} 

For rolling

example(lambda input):{'index_name': 'app', 'alias': 'app_time_window'}

By default keep_days=3, alias=index_name

You may to write logs to es by alias.

index_name is necessarily field

How to set name your mapping .json file: mapping-*component*.json. 

For example: mapping-app.json
