#!/usr/bin/env bash

scp eyws.py requirements.txt templates/email_costs.j2 \
setup/costs-current-month.sh setup/costs-3months.sh \
terryadmin@terry.vm.pozitron.com:~/aws-cost-reminder/