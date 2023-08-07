# © 2023 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at
# http: // aws.amazon.com/agreement or other written agreement between Customer and either
# Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import boto3
from datetime import datetime
from dateutil import tz

def get_settings():
    response = settings_table.get_item(
        Key={
            'id': 'settings'
        }
    )
    return response

settings_table_name = os.getenv("SETTINGS_TABLE_NAME")
dynamodb = boto3.resource('dynamodb')
settings_table = dynamodb.Table(settings_table_name)
settings = get_settings()
item_settings = settings.get("Item", {})
try:
    slack_token = item_settings.get("slackToken")
    slack_client = WebClient(token=slack_token)
except Exception as error:
    print("Error retrieving Slack OAuth token, cannot continue: ".format(error))
    exit


def lambda_handler(event, context):
    # TODO: loop through people as applicable

    # Get Slack user ids for each person, by their email address
    user_email = event["email"]
    
    try:
        user = slack_client.users_lookupByEmail(email=user_email)
        user_id = user["user"]["id"]
        approver_timezone = timezone = tz.gettz(name=["user"]["tz"])
    except SlackApiError as error:
        print("Error getting Slack user info for {0}: {1}".format(user_email, error))
        return
    
    # Build formatted date, localized to approver's timezone
    utc_zone=tz.tzutc()
    # TODO: populate this from the request data
    request_start_time = "2023-04-21T12:43:39.879Z"
    parsed_date = datetime.strptime(request_start_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    parsed_date = parsed_date.replace(tzinfo=utc_zone)
    localized_date = parsed_date.astimezone(approver_timezone)
    formatted_date = localized_date.strftime('%B %d, %Y at %I:%M %p %Z')

    # Build message using Slack blocks
    # TODO: populate these from the request data
    status = "pending"
    requester = "requester@domain.com"
    account = "Testing (123456789012)"
    role = "CICDAdministrator"
    duration = "1 hours"
    justification = "Need access to fix the CICD pipeline"
    ticket = "JIRA111"
    login_url = "http://aws.team"
    message_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "AWS Access Request from {0} is *{1}*".format(requester, status),
            },
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*Account:*\n{}".format(account)},
                {"type": "mrkdwn", "text": "*Start time:*\n{}".format(formatted_date)},
                {"type": "mrkdwn", "text": "*Role:*\n{}".format(role)},
                {"type": "mrkdwn", "text": "*Duration:*\n{}".format(duration)},
                {
                    "type": "mrkdwn",
                    "text": "*Justification:*\n{}".format(justification),
                },
                {"type": "mrkdwn", "text": "*Ticket Number:*\n{}".format(ticket)},
            ],
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Log into TEAM to approve or deny this request.",
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Open TEAM",
                },
                "url": login_url,
                "action_id": "button-action",
            },
        },
    ]

    # Send message to user
    try:
        post_message_response = slack_client.chat_postMessage(
            channel=user_id,
            blocks=message_blocks,
            text="AWS Access Request Notification",
        )
    except SlackApiError as error:
        print(
            "Error posting chat message to channel/user id {0}: {1}".format(
                user_id, error
            )
        )

