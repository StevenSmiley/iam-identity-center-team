# © 2023 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at
# http: // aws.amazon.com/agreement or other written agreement between Customer and either
# Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.
import urllib3
import json
http = urllib3.PoolManager()
def lambda_handler(event, context):
    url = event['webhook_url']
    # TODO: parse event and transform before posting?
    print(event)
    encoded_body = json.dumps(event).encode('utf-8')
    resp = http.request('POST', url, body=encoded_body)
    print({
        "body": event, 
        "status_code": resp.status, 
        "response": resp.data
    })
