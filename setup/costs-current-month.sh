#!/usr/bin/env bash

# current usage costs (current month or the past month if below is called on the first day of the month)
python3 ~/aws-cost-reminder/eyws.py email-costs --profile pozitron --template ~/aws-cost-reminder/email_costs.j2 \
--smtp-host handel.pozitron.com --smtp-port 10025 --smtp-from=aws-cost-reminder@commencis.com \
--emails=can@commencis.com