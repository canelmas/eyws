#!/usr/bin/env bash

scp eyws.py requirements.txt templates/email_costs.j2 \
setup/setup-weekly-usage-costs.sh setup/send-aws-usage-costs-weekly.sh \
setup/send-aws-usage-costs-every-3day.sh \
terryadmin@terry.vm.pozitron.com:~/aws-cost-reminder/