#!/usr/bin/env bash

# past three months usage costs (including current month)
python3 ~/aws-cost-reminder/eyws.py email-costs --months 3 --profile pozitron --template ~/aws-cost-reminder/email_costs.j2 \
--smtp-host handel.pozitron.com --smtp-port 10025 --smtp-from=aws-cost-reminder@commencis.com \
--emails=can@commencis.com