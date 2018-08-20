#!/usr/bin/env bash

# 2 months usage
cmd_weekly=~/aws-cost-reminder/send-aws-usage-costs-weekly.sh
cmd_every_3_day=~/aws-cost-reminder/send-aws-usage-costs-every-3day.sh

# every monday at 06:00
job_weekly="0 6 * * MON $cmd_weekly"

# every 3 days at 06:00
job_every_3_day="0 6 */3 * * $cmd_every_3_day"

( crontab -l | grep -v -F "$cmd_weekly" ; echo "$job_weekly" ) | crontab -
( crontab -l | grep -v -F "$cmd_every_3_day" ; echo "$job_every_3_day" ) | crontab -