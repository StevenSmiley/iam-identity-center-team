# Copyright 2023 Amazon Web Services, Inc
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env bash
set -xe

. "./parameters.sh"

export AWS_PROFILE=$TEAM_ACCOUNT_PROFILE

git remote remove origin
git remote add origin codecommit::$REGION://team-idc-app
git remote add team https://github.com/aws-samples/iam-identity-center-team.git
git pull team main

if [[ ! -z "$TAGS" ]];
then
  aws cloudformation deploy --region $REGION --template-file template.yml \
  --stack-name TEAM-IDC-APP \
  --parameter-overrides \
    Login=$IDC_LOGIN_URL \
    teamAdminGroup="$TEAM_ADMIN_GROUP" \
    teamAuditGroup="$TEAM_AUDITOR_GROUP" \
    tags="$TAGS" \
  --tags $TAGS \
  --no-fail-on-empty-changeset --capabilities CAPABILITY_NAMED_IAM
else
  aws cloudformation deploy --region $REGION --template-file template.yml \
  --stack-name TEAM-IDC-APP \
  --parameter-overrides \
    Login=$IDC_LOGIN_URL \
    teamAdminGroup="$TEAM_ADMIN_GROUP" \
    teamAuditGroup="$TEAM_AUDITOR_GROUP" \
    tags="$TAGS" \
  --no-fail-on-empty-changeset --capabilities CAPABILITY_NAMED_IAM
fi

git push origin main
git remote remove team