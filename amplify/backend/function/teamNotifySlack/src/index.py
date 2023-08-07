# © 2023 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at
# http: // aws.amazon.com/agreement or other written agreement between Customer and either
# Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from datetime import datetime
from dateutil import tz

slack_token = os.environ["SLACK_BOT_TOKEN"]
slack_client = WebClient(token=slack_token)


def lambda_handler(event, context):
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
    request_start_time = "2023-04-21T12:43:39.879Z"
    parsed_date = datetime.strptime(request_start_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    parsed_date = parsed_date.replace(tzinfo=utc_zone)
    localized_date = parsed_date.astimezone(approver_timezone)
    formatted_date = localized_date.strftime('%B %d, %Y at %I:%M %p %Z')

    # Build message using Slack blocks
    message_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "AWS Access Request from requester@domain.com is *pending*",
            },
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*Account:*\nTesting (123456789012)"},
                {"type": "mrkdwn", "text": "*Start time:*\n2023-04-21T12:43:39.879Z"},
                {"type": "mrkdwn", "text": "*Role:*\nCICDAdministrator"},
                {"type": "mrkdwn", "text": "*Duration:*\n1 hours"},
                {
                    "type": "mrkdwn",
                    "text": "*Justification:*\nNeed access to fix the CICD pipeline",
                },
                {"type": "mrkdwn", "text": "*Ticket Number:*\nJIRA111"},
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
                "url": "https://aws.team",
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
