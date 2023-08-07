# © 2023 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at
# http: // aws.amazon.com/agreement or other written agreement between Customer and either
# Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import boto3
from datetime import datetime
from dateutil import parser, tz

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


def lambda_handler(event: dict, context):
    request_status = event["status"]
    requester_email = event["email"]
    approvers = event.get("approvers", "")
    account = "{0} ({})".format(event["accountName"], event["accountId"])
    role = event["role"]
    # TODO: Make duration more readable
    duration = event["duration"]
    justification = event.get("justification", "No justification provided")
    ticket = event.get("ticketNo", "No ticket provided")
    # TODO: Get the login url from somewhere
    login_url = "http://aws.team"

    match request_status:
        case "pending":
            # Notify approvers pending request
            pass
        case "expired":
            # Notify requester request expired
            pass
        case "rejected":
            # Notify requester request rejected
            pass
        case "cancelled":
            # Notify approvers request cancelled
            pass
        case "scheduled":
            # Notify requester access scheduled
            pass
        case "in progress":
            # Notify requester access granted
            pass
        case "error":
            # Notify approvers and requester error
            pass
        case "ended" | "revoked":
            # Notify requester ended
            pass
        case _:
            print(f"Request status unexpected: {request_status}")

    # TODO: loop through people as applicable

    # Get Slack user ids for each person, by their email address
    try:
        requester = slack_client.users_lookupByEmail(email=requester_email)
        requester_slack_id = requester["user"]["id"]
        approver_timezone = timezone = tz.gettz(name=["user"]["tz"])
    except SlackApiError as error:
        print("Error getting Slack user info for {0}: {1}".format(requester_email, error))
        return
    
    # Build formatted date, localized to approver's timezone
    request_start_time = event["startTime"]
    parsed_date = parser.parse(request_start_time)
    localized_date = parsed_date.astimezone(approver_timezone)
    formatted_date = localized_date.strftime('%B %d, %Y at %I:%M %p %Z')

    # Build message using Slack blocks
    message_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "AWS Access Request from {0} is *{1}*".format(requester_email, request_status),
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
            channel=requester_slack_id,
            blocks=message_blocks,
            text="AWS Access Request Notification",
        )
    except SlackApiError as error:
        print(
            "Error posting chat message to channel/user id {0}: {1}".format(
                requester_slack_id, error
            )
        )

