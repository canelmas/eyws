#!/usr/bin/env bash

cmd_3_months_usage=~/aws-cost-reminder/costs-3months.sh
cmd_1_month_usage=~/aws-cost-reminder/costs-current-month.sh

# every first day of every month at 06:00 AM
job_monthly="0 6 1 * * $cmd_1_month_usage"

# every 3 days at 06:00
job_every_3_day="0 6 */3 * * $cmd_3_months_usage"

( crontab -l | grep -v -F "$cmd_1_month_usage" ; echo "$job_every_3_day" ) | crontab -
( crontab -l | grep -v -F "$cmd_1_month_usage" ; echo "$job_monthly" ) | crontab -