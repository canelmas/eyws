#!/usr/bin/env bash

# sent every 3 day, includes current month usage
python3 ~/aws-cost-reminder/eyws.py email-costs --months 1 --profile pozitron --template ~/aws-cost-reminder/email_costs.j2 \
--smtp-host handel.pozitron.com --smtp-port 10025 --smtp-from=aws-cost-reminder@commencis.com \
--emails=can@commencis.com