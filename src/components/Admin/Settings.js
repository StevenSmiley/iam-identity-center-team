// © 2023 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
// This AWS Content is provided subject to the terms of the AWS Customer Agreement available at
// http://aws.amazon.com/agreement or other written agreement between Customer and either
// Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.
import React, { useState, useEffect } from "react";
import Box from "@awsui/components-react/box";
import SpaceBetween from "@awsui/components-react/space-between";
import RadioGroup from "@awsui/components-react/radio-group";
import Container from "@awsui/components-react/container";
import Header from "@awsui/components-react/header";
import ColumnLayout from "@awsui/components-react/column-layout";
import Button from "@awsui/components-react/button";
import Link from "@awsui/components-react/link";
import { ContentLayout, Modal, Toggle, Form, FormField, Input, Spinner } from "@awsui/components-react";
import StatusIndicator from "@awsui/components-react/status-indicator";
import { Divider } from "antd";
import "../../index.css";
import { getSetting, createSetting, updateSetting } from "../Shared/RequestService";

function Settings(props) {
  const [duration, setDuration] = useState(null);
  const [durationError, setDurationError] = useState("")
  const [expiry, setExpiry] = useState(null);
  const [expiryError, setExpiryError] = useState("")
  const [comments, setComments] = useState(null);
  const [ticketNo, setTicketNo] = useState(null);
  const [approval, setApproval] = useState(null);
  const [notificationService, setNotificationService] = useState(null);
  const [slackToken, setSlackToken] = useState("");
  const [sourceEmail, setSourceEmail] = useState(null);
  const [sourceEmailError, setSourceEmailError] = useState(null);
  const [visible, setVisible] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [item, setItem] = useState(null);

  const slackAppManifest = {
    display_information: {
      name: 'AWS TEAM Access Requests',
      description: 'AWS Temporary Elevated Access Management',
      background_color: '#252F3E',
    },
    features: {
      bot_user: {
        display_name: 'AWS TEAM',
        always_online: false,
      },
    },
    oauth_config: {
      scopes: {
        bot: [
          'channels:read',
          'chat:write',
          'groups:read',
          'im:write',
          'usergroups:read',
          'users:read',
          'users.profile:read',
          'users:read.email',
        ],
      },
    },
    settings: {
      org_deploy_enabled: false,
      socket_mode_enabled: false,
      token_rotation_enabled: false,
    },
  };
  const encodedSlackAppManifest = encodeURIComponent(JSON.stringify(slackAppManifest))
  const baseSlackAppUrl = 'https://api.slack.com/apps?new_app=1&manifest_json=';
  const slackAppInstallUrl = baseSlackAppUrl + encodedSlackAppManifest;

  useEffect(() => {
    views();
  }, []);

  function views() {
      setVisible(false);
      setSubmitLoading(false);
      getSettings()
    };
  
    async function validate() {
      let error = false;
      const emailRegex = /\S+@\S+\.\S+/;
    
      if (!duration || isNaN(duration) || Number(duration) > 8000 ||  Number(duration) < 1) {
        setDurationError(`Enter valid duration as a number between 1 - 8000`);
        error = true;
      }
      if (!expiry || isNaN(expiry) || Number(expiry) > 8000 || Number(expiry) < 1) {
        setExpiryError(`Enter valid expiry timeout as a number between 1 - 8000`);
        error = true;
      }
      if (notificationService === "SES" && !emailRegex.test(sourceEmail)) {
        setSourceEmailError(`Enter a valid email address`);
        error = true;
      }
      return error;
    }
    

  function handleEdit() {
    setVisible(true);
  }
  function handleDismiss() {
    // Reset item states
    setDuration(item.duration);
    setExpiry(item.expiry);
    setComments(item.comments);
    setTicketNo(item.ticketNo);
    setApproval(item.approval);
    setNotificationService(item.notificationService);
    setSourceEmail(item.sourceEmail);
    setSlackToken(item.slackToken);
    setVisible(false);
  }
  async function handleSubmit() {
    setSubmitLoading(true);
    if (!(await validate())) {
      const data = {
        id: "settings",
        duration,
        expiry,
        comments,
        ticketNo,
        approval,
        notificationService,
        sourceEmail,
        slackToken,
      };
      const action = item === null ? createSetting : updateSetting;
      action(data).then(() => {
        views();
        props.addNotification([
          {
            type: "success",
            content: "TEAM configuration edited successfully",
            dismissible: true,
            onDismiss: () => props.addNotification([]),
          },
        ]);
      });
  }
  else setSubmitLoading(false)
  }

  function getSettings(){
    getSetting("settings").then((data) => {
      if (data !== null) {
        setItem(data);
        setDuration(data.duration);
        setExpiry(data.expiry);
        setComments(data.comments);
        setTicketNo(data.ticketNo);
        setApproval(data.approval);
        setNotificationService(data.notificationService);
        setSourceEmail(data.sourceEmail);
        setSlackToken(data.slackToken);
      } else {
        setDuration("9");
        setExpiry("3");
        setComments(true);
        setTicketNo(true);
        setApproval(true);
        setNotificationService("None");
        setSourceEmail("");
        setSlackToken("");
      }
    });
  }

  return (
    <div className="container">
      <ContentLayout>
        <Container
          header={
            <Header
              variant="h2"
              description="Custom configuration settings for TEAM application"
              actions={
                <Button variant="primary" onClick={handleEdit}>
                  Edit
                </Button>
              }
            >
              Configuration settings
            </Header>
          }
        >
          <ColumnLayout columns={4} variant="text-grid">
            <SpaceBetween size="l">
              <div>
                <Box variant="h3">Timer settings</Box>
                <Box variant="small">Request Form timer settings</Box>
                <Divider style={{ marginBottom: "7px", marginTop: "7px" }} />
              </div>
              <div>
                <Box variant="awsui-key-label">Max request duration</Box>
                <> {duration !== null ?  <div>{duration} hours</div> : <Spinner />  }</>
              </div>
              <div>
                <Box variant="awsui-key-label">Request expiry timeout</Box>
                <> {expiry !== null ? <div>{expiry} hours</div> : <Spinner /> }</>
              </div>
            </SpaceBetween>
            <SpaceBetween size="l">
              <div>
                <Box variant="h3">Mandatory fields</Box>
                <Box variant="small">Request Form mandatory fields</Box>
                <Divider style={{ marginBottom: "7px", marginTop: "7px" }} />
              </div>
              <div>
                <Box variant="awsui-key-label">Comments</Box>
                <> {comments !== null ? <div>{comments === true ? "On" : "Off"}</div> : <Spinner /> }</>
              </div>
              <div>
                <Box variant="awsui-key-label">Ticket number</Box>
                <> {ticketNo !== null ? <div>{ticketNo === true ? "On" : "Off"}</div> : <Spinner /> }</>
              </div>
            </SpaceBetween>
            <SpaceBetween size="l">
              <div>
                <Box variant="h3">Workflow settings</Box>
                <Box variant="small">Request approval workflow settings</Box>
                <Divider style={{ marginBottom: "7px", marginTop: "7px" }} />
              </div>
              <div>
                <Box variant="awsui-key-label">Approval required</Box>
                <> {approval !== null ? 
                <div>
                  <StatusIndicator type={approval === true ? "success" : "error"}>
                    {approval === true ? "Yes" : "No"}
                  </StatusIndicator>
                </div>
                :<Spinner /> 
                }</>
              </div>
            </SpaceBetween>
            <SpaceBetween size="l">
              <div>
                <Box variant="h3">Notification settings</Box>
                <Box variant="small">Notification settings for request and approval events</Box>
                <Divider style={{ marginBottom: "7px", marginTop: "7px" }} />
              </div>
              <div>
                <Box variant="awsui-key-label">Notification service</Box>
                <> {notificationService !== null ?  <div>{notificationService}</div> : <Spinner />  }</>
              </div>
              {notificationService === "SES" && (
              <div>
                <Box variant="awsui-key-label">SES source email</Box>
                <> {sourceEmail !== null ? <div>{sourceEmail}</div> : <Spinner /> }</>
              </div>
              )}
              {notificationService === "Slack" && (
              <div>
                <Box variant="awsui-key-label">Slack OAuth Token</Box>
                <> {slackToken !== null ? <div>{slackToken}</div> : <Spinner /> }</>
              </div>
              )}
            </SpaceBetween>
          </ColumnLayout>
        </Container>
        <Modal
          onDismiss={() => handleDismiss()}
          visible={visible}
          closeAriaLabel="Close modal"
          size="large"
          header="Edit configuration settings"
        >
          <Form
            actions={
              <SpaceBetween direction="horizontal" size="xs">
                <Button
                  variant="link"
                  onClick={handleDismiss}
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  type="submit"
                  onClick={handleSubmit}
                  loading={submitLoading}
                >
                  Submit
                </Button>
              </SpaceBetween>
            }
          >
            <SpaceBetween direction="vertical" size="l">
              <div>
                <Box variant="h3">Timer settings</Box>
                <Box variant="small">Request Form timer settings</Box>
                <Divider style={{ marginBottom: "1px", marginTop: "7px" }} />
              </div>
              <FormField
                label="Max request duration"
                stretch
                description="Default maximum request duration in hours"
                errorText={durationError}
              >
                <Input
                  value={duration}
                  onChange={(event) => {
                    setDurationError();
                    setDuration(event.detail.value);
                  }}
                  type="number"
                />
              </FormField>
              <FormField
                label="Request expiry timeout"
                stretch
                description="Number of time in hours before an unapproved TEAM request expires"
                errorText={expiryError}
              >
                <Input
                  value={expiry}
                  onChange={(event) => {
                    setExpiryError();
                    setExpiry(event.detail.value);
                  }}
                  type="number"
                />
              </FormField>
              <div>
                <Box variant="h3">Mandatory fields</Box>
                <Box variant="small">Request Form mandatory fields</Box>
                <Divider style={{ marginBottom: "1px", marginTop: "7px" }} />
              </div>
              <FormField
                label="Comments"
                stretch
                description="Determines if comment field is mandatory"
              >
                <Toggle
                  onChange={({ detail }) => setComments(detail.checked)}
                  checked={comments}
                >
                  Comments
                </Toggle>
              </FormField>
              <FormField
                label="Ticket number"
                stretch
                description="Determines if ticket number field is mandatory"
              >
                <Toggle
                  onChange={({ detail }) => setTicketNo(detail.checked)}
                  checked={ticketNo}
                >
                  Ticket number
                </Toggle>
              </FormField>
              <div>
                <Box variant="h3">Workflow settings</Box>
                <Box variant="small">Request approval workflow settings</Box>
                <Divider style={{ marginBottom: "1px", marginTop: "7px" }} />
              </div>
              <FormField
                label="Approval required"
                stretch
                description="Turn on/off approval workflow for all elevated access request"
              >
                <Toggle
                  onChange={({ detail }) => setApproval(detail.checked)}
                  checked={approval}
                >
                  Approval required
                </Toggle>
              </FormField>
              <div>
                <Box variant="h3">Notification settings</Box>
                <Box variant="small">Notification settings for request and approval events</Box>
                <Divider style={{ marginBottom: "1px", marginTop: "7px" }} />
              </div>
              <FormField
                label="Notification service"
                stretch
                description="The AWS service to use to send notifications about request and approval events"
              >
                <RadioGroup
                  onChange={({ detail }) => {
                    setNotificationService(detail.value)
                    if (notificationService === "SES") { setSlackToken("") }
                    if (notificationService === "Slack") { setSourceEmail("") }
                    if (notificationService === "SNS" | notificationService === "None") {
                      setSlackToken("")
                      setSourceEmail("")
                    }
                  }}
                  value={notificationService}
                  items={[
                    { label: "Amazon SES", value: "SES" },
                    { label: "Amazon SNS", value: "SNS" },
                    { label: "Slack", value: "Slack" },
                    { label: "None", value: "None" },
                  ]}
                >
                  Notification service
                </RadioGroup>
              </FormField>
              {notificationService === "SES" && (
                <FormField
                  label="Source email"
                  stretch
                  description="Email address to send notifications from, when using SES as the notification service. Must be verified in SES."
                  errorText={sourceEmailError}
                >
                  <Input
                    value={sourceEmail}
                    onChange={(event) => {
                      setSourceEmailError()
                      setSourceEmail(event.detail.value)
                    }}
                  >
                    Source email
                  </Input>
                </FormField>
              )}
              {notificationService === "Slack" && (
                <div>
                  <Link external href={slackAppInstallUrl} rel="noopener noreferrer">
                    Install Slack App
                  </Link>
                  <br />
                  <FormField
                    label="Slack OAuth Token"
                    stretch
                    description="Slack OAuth token with permission to the Slack workspace."
                  >
                    <Input
                      value={slackToken}
                      onChange={(event) => {
                        setSlackToken(event.detail.value)
                      }}
                    >
                      Slack token
                    </Input>
                  </FormField>
                </div>
              )}
            </SpaceBetween>
          </Form>
        </Modal>
      </ContentLayout>
    </div>
  );
}

export default Settings;
