# © 2023 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at
# http: // aws.amazon.com/agreement or other written agreement between Customer and either
# Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import boto3
from dateutil import parser, tz


def get_settings():
    response = settings_table.get_item(Key={"id": "settings"})
    return response


settings_table_name = os.getenv("SETTINGS_TABLE_NAME")
dynamodb = boto3.resource("dynamodb")
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
    requester = event["email"]
    approvers = event.get("approvers", "")
    account = "{0} ({})".format(event["accountName"], event["accountId"])
    role = event["role"]
    duration_hours = event["duration"]
    justification = event.get("justification", "No justification provided")
    ticket = event.get("ticketNo", "No ticket provided")
    # TODO: Get the login url from somewhere
    login_url = "http://aws.team"

    match request_status:
        case "pending":
            # Notify approvers pending request
            send_slack_notifications(
                recipients=approvers,
                include_request_details=True,
                message=f"{requester} requests access to AWS, please approve or reject this request in TEAM.",
            )
        case "expired":
            # Notify requester request expired
            send_slack_notifications(
                recipients=[requester],
                include_request_details=True,
                message="Your AWS access request has expired.",
            )
        case "rejected":
            # Notify requester request rejected
            send_slack_notifications(
                recipients=[requester],
                include_request_details=True,
                message="Your AWS access request was rejected.",
            )
        case "cancelled":
            # Notify approvers request cancelled
            send_slack_notifications(
                recipients=[approvers],
                include_request_details=True,
                message=f"{requester} cancelled this AWS access request.",
            )
        case "scheduled":
            # Notify requester access scheduled
            send_slack_notifications(
                recipients=[requester],
                include_request_details=True,
                message="AWS access is scheduled.",
            )
        case "in progress":
            # Notify requester access granted
            send_slack_notifications(
                recipients=[requester],
                include_request_details=True,
                message="Your AWS access session has started",
            )
        case "error":
            # Notify approvers and requester error
            send_slack_notifications(
                recipients=approvers + [requester],
                include_request_details=True,
                message="Error with AWS access request.",
            )
        case "ended" | "revoked":
            # Notify requester ended
            send_slack_notifications(
                recipients=[requester],
                include_request_details=True,
                message="Your AWS access session has ended.",
            )
        case _:
            print(f"Request status unexpected: {request_status}")

    def send_slack_notifications(
        recipients: list, include_request_details: bool, message
    ):
        request_start_time = event["startTime"]
        parsed_date = parser.parse(request_start_time)

        for recipient in recipients:
            try:
                recipient_slack_user = slack_client.users_lookupByEmail(email=recipient)
                recipient_slack_id = recipient_slack_user["user"]["id"]
                recipient_timezone = tz.gettz(name=["user"]["tz"])
            except SlackApiError as error:
                print(
                    "Error getting Slack user info for {0}: {1}".format(
                        recipient, error
                    )
                )
                continue

            # Format date, localized to recipient's timezone
            localized_date = parsed_date.astimezone(recipient_timezone)
            formatted_date = localized_date.strftime("%B %d, %Y at %I:%M %p %Z")

            # Build message using Slack blocks
            message_blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{message}*",
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
                }
            ]

            if include_request_details:
                message_blocks.append(
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": "*Account:*\n{}".format(account),
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*Start time:*\n{}".format(formatted_date),
                            },
                            {"type": "mrkdwn", "text": "*Role:*\n{}".format(role)},
                            {
                                "type": "mrkdwn",
                                "text": "*Duration:*\n{} hours".format(duration_hours),
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*Justification:*\n{}".format(justification),
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*Ticket Number:*\n{}".format(ticket),
                            },
                        ],
                    }
                )

            # Send message to user
            try:
                post_message_response = slack_client.chat_postMessage(
                    channel=recipient_slack_id,
                    blocks=message_blocks,
                    text="AWS Access Request Notification",
                )
            except SlackApiError as error:
                print(
                    "Error posting chat message to channel/user id {0}: {1}".format(
                        recipient_slack_id, error
                    )
                )
