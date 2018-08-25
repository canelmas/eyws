import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from optparse import OptionParser

import boto3
from botocore.exceptions import ClientError
from collections import defaultdict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP
from jinja2 import Environment, FileSystemLoader

VERSION = "1.0.0"
UBUNTU_AMI = "ami-de8fb135"  # Ubuntu Server 16.04 LTS SSD
DEFAULT_AMI = UBUNTU_AMI
DEFAULT_NUM_OF_INSTANCES = 1
DEFAULT_INSTANCE_TYPE = "t2.micro"
DEFAULT_IOPS = 100
DEFAULT_EBS_VOLUME_SIZE = 8
DEFAULT_EBS_VOLUME_TYPE = "gp2"
DEFAULT_EBS_DELETE_ON_TERMINATION = True
DEFAULT_EBS_VOLUME_NAME = "/dev/sda1"
DEFAULT_NUM_OF_MONTHS_TO_CHECK_COST = 1  # current month
DEFAULT_COST_METRICS_TYPE = "BlendedCost"
DEFAULT_COST_EMAIL_SUBJECT = "AWS Usage Costs"

EBS_VOLUME_TYPES = [("standard", "Magnetic"),
                    ("io1", "Provisioned IOPS SSD"),
                    ("gp2", "General Purpose SSD"),
                    ("sc1", "Cold HDD"),
                    ("st1", "Throughput Optimized HDD")]


def parse_args():
    parser = OptionParser(usage="eyws <action> [options]\n\n<action> can be:\n\t\t"
                                "create-instances\n\t\t"
                                "stop-instances\n\t\t"
                                "terminate-instances\n\t\t"
                                "list-instances\n\t\t"
                                "list-zones\n\t\t"
                                "list-regions\n\t\t"
                                "list-images\n\t\t"
                                "list-sec-groups\n\t\t"
                                "list-costs\n\t\t"
                                "list-key-pairs\n\t\t"
                                "list-costs\n\t\t"
                                "email-costs",
                          version="%prog {}".format(VERSION),
                          add_help_option=False)

    parser.add_option("-h", "--help", action="help",
                      help="Show this help message and exit")

    parser.add_option("-p", "--profile", help="aws profile to use (~/.aws/config) (default=default profile)")

    parser.add_option("-c", "--count", metavar="Instance Count", type="int", default=DEFAULT_NUM_OF_INSTANCES,
                      help="Number of instances to launch (default={})".format(DEFAULT_NUM_OF_INSTANCES))

    parser.add_option("-n", "--name", metavar="Name Tag", dest="name_tag", default="",
                      help="Append a name tag to instances")

    parser.add_option("-w", "--wait", type="int", default=120,
                      help="Number of seconds to wait for nodes to start (default=120)")

    parser.add_option("-t", "--instance-type", metavar="Instance Type", default=DEFAULT_INSTANCE_TYPE,
                      help="Type of instances to launch (default={})".format(DEFAULT_INSTANCE_TYPE))

    parser.add_option("-r", "--region", metavar="Region",
                      help="EC2 region to list and launch instances in (default=.aws/config)")

    parser.add_option("-z", "--zone", metavar="Zone", default="",
                      help="Availability zone to list and launch instances in (default=random when launching instances)")

    parser.add_option("-a", "--ami", metavar="Ami", default=DEFAULT_AMI,
                      help="AMI ID to use (default={})".format(DEFAULT_AMI))

    parser.add_option("-k", "--key-pair", metavar="Key Pair",
                      help="Key pair to use on instances")

    parser.add_option("-e", "--ebs-vol-size", dest="ebs_vol_size", metavar="Size", type="int",
                      default=DEFAULT_EBS_VOLUME_SIZE,
                      help="EBS volume size in GB to attach each instance (default={})".format(DEFAULT_EBS_VOLUME_SIZE))

    parser.add_option("--ebs-vol-type", dest="ebs_vol_type", metavar="Volume Type", default=DEFAULT_EBS_VOLUME_TYPE,
                      help="Volume type to attach (default={})\ntypes={}".format(DEFAULT_EBS_VOLUME_TYPE,
                                                                                 EBS_VOLUME_TYPES))

    parser.add_option("--ebs-delete", dest="ebs_delete_on_term", metavar="Delete On Termination",
                      default=DEFAULT_EBS_DELETE_ON_TERMINATION,
                      help="Delete volume on termination (default={})".format(DEFAULT_EBS_DELETE_ON_TERMINATION))

    parser.add_option("--ebs-vol-name", dest="ebs_vol_name", default=DEFAULT_EBS_VOLUME_NAME,
                      help="Volume name (default={})".format(DEFAULT_EBS_VOLUME_NAME))

    parser.add_option("--iops", type="int", default=DEFAULT_IOPS,
                      help="IOPS. Not supported for volume type gp2 (default={})".format(DEFAULT_IOPS))

    parser.add_option("-s", "--sec-group", metavar="Security Group Name",
                      help="Security Group name to use for launching instances")

    parser.add_option("--instance-id", metavar="instance Id", action="append", dest="instance_ids",
                      help="instance ids to start/stop/destroy")

    parser.add_option("--days", type="int", help="Usage cost charged since <days> days")

    parser.add_option("--months", help="Months to check costs for. 1 means current month. (default=1)",
                      type="int", default=DEFAULT_NUM_OF_MONTHS_TO_CHECK_COST)

    parser.add_option("--ignore-service-usage", action="store_true",
                      help="Do not display costs for each service type")

    parser.add_option("--emails", action="append", dest="emails",
                      help="Comma separated email addresses to send cost information")

    parser.add_option("--template", help="Jinja template file")

    parser.add_option("--smtp-host", help="SMTP host")

    parser.add_option("--smtp-port", type="int", default=0, help="SMTP port")

    parser.add_option("--smtp-from", help="Sender email address")

    parser.add_option("--dry-run", action="store_true", help="Dry run operations")

    (opts, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        sys.exit(1)

    (action) = args[0]

    return opts, action


def list_instances(ec2):
    for res in ec2.describe_instances()["Reservations"]:
        for instance in res["Instances"]:
            print("instanceId = {}\n"
                  "imageId = {}\n"
                  "state = {}\n"
                  "state-message = {}\n"
                  "type = {}\n"
                  "keyname = {}\n"
                  "monitoring = {}\n"
                  "azone = {}\n"
                  "private-dns = {}\n"
                  "private-ip = {}\n"
                  "public-dns = {}\n"
                  "public-ip = {}\n"
                  "subnet-id = {}\n"
                  "vpc-id = {}\n"
                  "tags = {}\n"
                  "core-count = {}\n"
                  "thread-per-core = {}\n"
                  "security-groups = {}\n\n".format(instance["InstanceId"],
                                                    instance["ImageId"],
                                                    instance["State"]["Name"],
                                                    instance["StateTransitionReason"],
                                                    instance["InstanceType"],
                                                    instance["KeyName"],
                                                    instance["Monitoring"]["State"],
                                                    instance["Placement"]["AvailabilityZone"],
                                                    instance["PrivateDnsName"],
                                                    instance[
                                                        "PrivateIpAddress"] if "PrivateIpAddress" in instance else "",
                                                    instance["PublicDnsName"],
                                                    instance[
                                                        "PublicIpAddress"] if "PublicIpAddress" in instance else "",
                                                    instance["SubnetId"] if "SubnetId" in instance else "",
                                                    instance["VpcId"] if "VpcId" in instance else "",
                                                    instance["Tags"] if "Tags" in instance else "",
                                                    instance["CpuOptions"]["CoreCount"],
                                                    instance["CpuOptions"]["ThreadsPerCore"],
                                                    instance["SecurityGroups"]))


def list_regions(ec2, opts):
    for region in [region['RegionName'] for region in ec2.describe_regions()["Regions"]]:
        print(region)


def list_availability_zones(ec2, opts):
    for zone in [zone["ZoneName"] for zone in ec2.describe_availability_zones()["AvailabilityZones"]]:
        print(zone)


def list_images(ec2):
    # for now listS only ubuntu images
    filters = [
        {
            'Name': 'name',
            'Values': ['ubuntu*']
        }, {
            'Name': 'state',
            'Values': ['available']
        }, {
            'Name': 'architecture',
            'Values': ['x86_64']
        }, {
            'Name': 'root-device-type',
            'Values': ['ebs']
        }, {
            'Name': 'virtualization-type',
            'Values': ['hvm']
        }, {
            'Name': 'hypervisor',
            'Values': ['xen']
        }, {
            'Name': 'image-type',
            'Values': ['machine']
        }, {
            'Name': 'is-public',
            'Values': ['true']
        }]

    for image_info in [(image["Name"], image["ImageId"]) for image in ec2.describe_images(Filters=filters)["Images"]]:
        print(image_info)


def create_instances(ec2, opts):
    # todo : key pair must be set

    # use existing keypair or create new one
    key = get_or_create_key_pair(ec2, opts)

    # use existing security group or create new one
    sec_group = get_or_create_security_group(ec2, opts)

    ec2.run_instances(
        ImageId=opts.ami,
        KeyName=key,
        InstanceType=opts.instance_type,
        MinCount=opts.count,
        MaxCount=opts.count,
        SecurityGroups=[sec_group],
        Placement={
            "AvailabilityZone": opts.zone
        },
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": opts.name_tag}
                ]
            }
        ],
        BlockDeviceMappings=create_new_block_device_mapping(opts),
        DryRun=bool(opts.dry_run)
    )


def create_new_block_device_mapping(opts):
    block_device_mappings = [
        {
            "DeviceName": opts.ebs_vol_name,
            "Ebs": {
                "VolumeSize": opts.ebs_vol_size,
                "VolumeType": opts.ebs_vol_type,
                "DeleteOnTermination": bool(opts.ebs_delete_on_term)
            }
        }
    ]

    if opts.ebs_vol_type != "gp2":
        block_device_mappings[0]["Ebs"]["Iops"] = opts.iops

    return block_device_mappings


def list_security_groups(ec2):
    for sec_group in ec2.describe_security_groups()["SecurityGroups"]:
        print("name={}\ngroupId={}\ndescription={}\nIpPermissions={}\n"
              .format(sec_group["GroupName"],
                      sec_group["GroupId"],
                      sec_group["Description"],
                      [("port={}".format(ip_permission["FromPort"]),
                        "cidr={}".format(ip_permission["IpRanges"][0]["CidrIp"])) for ip_permission in
                       sec_group["IpPermissions"]]))


def list_key_pairs(ec2):
    for key_pair in [key_pair["KeyName"] for key_pair in ec2.describe_key_pairs()["KeyPairs"]]:
        print(key_pair)


def get_or_create_key_pair(ec2, opts):
    try:
        return ec2.describe_key_pairs(KeyNames=[opts.key_pair])["KeyPairs"][0]["KeyName"]
    except ClientError as e:
        if e.response["Error"]['Code'] == "InvalidKeyPair.NotFound":

            print("Keypair {} doesn't exist, will create a new keypair...".format(opts.key_pair))
            key = ec2.create_key_pair(KeyName=opts.key_pair, DryRun=bool(opts.dry_run))
            print("Go save the content below\n\n{}\n\n".format(key["KeyMaterial"]))
            return key["KeyName"]
        else:
            raise


def get_or_create_security_group(ec2, opts):
    try:
        return ec2.describe_security_groups(GroupNames=[opts.sec_group])["SecurityGroups"][0]["GroupName"]
    except ClientError as e:
        if e.response["Error"]["Code"] == "InvalidGroup.NotFound":

            print("Security Group '{}' doesn't exist, will create a new security group...".format(opts.sec_group))
            ec2.create_security_group(GroupName=opts.sec_group,
                                      Description="Security Group for SSH access only",
                                      DryRun=bool(opts.dry_run))

            print("Authorizing SSH access to security group '{}'...".format(opts.sec_group))
            ec2.authorize_security_group_ingress(GroupName=opts.sec_group,
                                                 IpPermissions=[
                                                     {"IpProtocol": "tcp",
                                                      "FromPort": 22,
                                                      "ToPort": 22,
                                                      "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
                                                      }],
                                                 DryRun=bool(opts.dry_run))
            return opts.sec_group
        else:
            raise


def list_opts(opts):
    print("ami={}".format(opts.ami))
    print("type={}".format(opts.instance_type))
    print("keypair={}".format(opts.key_pair))
    print("dryrun={}".format(opts.dry_run))
    print("zone={}".format(opts.zone))
    print("region={}".format(opts.region))
    print("count={}".format(opts.count))
    print("sec_group={}".format(opts.sec_group))
    print("nametag={}".format(opts.name_tag))
    print("iops={}".format(opts.iops))
    print("vol={}".format(opts.ebs_vol_size))
    print("volumeType={}".format(opts.ebs_vol_type))
    print("deleteTerm={}".format(opts.ebs_delete_on_term))
    print("volName={}".format(opts.ebs_vol_name))
    print("instanceids={}".format(opts.instance_ids))
    print("days={}".format(opts.days))
    print("months={}".format(opts.months))
    print("profile={}".format(opts.profile))
    print("ignore-service-usage={}".format(opts.ignore_service_usage))
    print("emails={}".format(opts.emails))
    print("template={}".format(opts.template))


def stop_instances(ec2, opts):
    resp = input("Following instances will be stopped {}\n\nAre you sure you want to stop instances? (y/N):".
                 format(opts.instance_ids))

    if resp == 'y':
        print("Stopping following instances {}...".format(opts.instance_ids))
        resp = ec2.stop_instances(InstanceIds=opts.instance_ids, DryRun=bool(opts.dry_run))

        for instance_info in [(state["InstanceId"], state["PreviousState"]["Name"], state["CurrentState"]["Name"])
                              for state in resp["StoppingInstances"]]:
            print("\ninstanceId={}\npreviousState={}\ncurrentState={}\n".format(instance_info[0],
                                                                                instance_info[1],
                                                                                instance_info[2]))


def terminate_instances(ec2, opts):
    resp = input("Following instances will be terminated {}\n\nAre you sure you want to terminate instances? (y/N):".
                 format(opts.instance_ids))

    if resp == 'y':
        print("Terminating following instances {}...".format(opts.instance_ids))
        resp = ec2.terminate_instances(InstanceIds=opts.instance_ids, DryRun=bool(opts.dry_run))

        for instance_info in [(state["InstanceId"], state["PreviousState"]["Name"], state["CurrentState"]["Name"])
                              for state in resp["TerminatingInstances"]]:
            print("\ninstanceId={}\npreviousState={}\ncurrentState={}\n".format(instance_info[0],
                                                                                instance_info[1],
                                                                                instance_info[2]))


def start_instances(ec2, opts):
    print("Starting following instances {}...".format(opts.instance_ids))
    resp = ec2.start_instances(InstanceIds=opts.instance_ids, DryRun=bool(opts.dry_run))

    for instance_info in [(instance["InstanceId"], instance["PreviousState"]["Name"], instance["CurrentState"]["Name"])
                          for instance in resp["StartingInstances"]]:
        print("\ninstanceId={}\npreviousState={}\ncurrentState={}\n".format(instance_info[0],
                                                                            instance_info[1],
                                                                            instance_info[2]))


def list_costs(ce, opts):
    for periodic_cost in get_costs(ce, opts):
        periodic_cost.prettify()


def send_email(host, port, sender, to, data):
    msg = MIMEMultipart('alternative')

    msg['Subject'] = DEFAULT_COST_EMAIL_SUBJECT
    msg['To'] = ', '.join(to)
    msg['From'] = sender

    msg.attach(MIMEText(data, 'html'))

    s = smtplib.SMTP(host=host, port=port)
    s.sendmail(sender, to, msg.as_string())
    s.quit()


def email_costs(ce, opts):
    if not opts.template or not os.path.isfile(opts.template):
        raise ValueError("--template value is required. Make sure to pass a valid existing file.")

    if not opts.emails or not opts.smtp_host or not opts.smtp_from:
        raise ValueError("--emails, --smtp-host and --smtp-from are required for sending email")

    # get costs
    costs = get_costs(ce, opts)

    # render template
    template_dir = os.path.abspath(os.path.join(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), opts.template), ".."))

    j2_env = Environment(loader=FileSystemLoader(template_dir))

    template = j2_env.get_template(os.path.basename(opts.template))

    rendered_text = template.render(costs=costs)

    # send email
    send_email(opts.smtp_host, opts.smtp_port, opts.smtp_from, opts.emails, rendered_text)


def get_costs(ce, opts):
    if opts.days:
        start = datetime.now() - relativedelta(days=opts.days)  # show usage costs starting from X days ago
    else:
        start = datetime.today().replace(day=1)  # first day of the current month for starting date
        if opts.months > 1:  # set starting date to X months back
            start = start - relativedelta(months=opts.months - 1)
        elif datetime.now().date() == start.date():
            # --months is set to 1 and it's the first day of the month, show past month's usage costs
            start = start - relativedelta(months=1)
            pass

    start = start.strftime("%Y-%m-%d")
    end = datetime.now().strftime("%Y-%m-%d")  # end time is always now i.e. date range selection not supported

    account_map = get_account_names(ce, start, end)

    # ignore service details if --ignore-service-usage is set
    group_by = [{"Type": "DIMENSION", "Key": "LINKED_ACCOUNT"}]

    if not opts.ignore_service_usage:
        group_by.append(
            {
                "Type": "DIMENSION",
                "Key": "SERVICE"
            })

    periods = []
    token = None
    while True:
        if token:
            kwargs = {'NextPageToken': token}
        else:
            kwargs = {}

        resp = ce.get_cost_and_usage(
            TimePeriod={
                "Start": start,
                "End": end
            },
            Granularity="MONTHLY",
            Metrics=[DEFAULT_COST_METRICS_TYPE],
            GroupBy=group_by,
            **kwargs)

        periods += resp['ResultsByTime']
        token = resp.get('NextPageToken')
        if not token:
            break

    # desc sort by start time
    try:
        periods.sort(key=lambda json: json["TimePeriod"]["Start"], reverse=True)
    except KeyError as e:
        # do not sort then
        pass

    # prepare cost data
    costs_by_periods = []  # type: List[PeriodicCosts]

    for period in periods:

        month = datetime.strptime(period["TimePeriod"]["Start"], "%Y-%m-%d").strftime("%B %Y") \
            if not opts.days else period["TimePeriod"]["Start"]

        periodic_cost_info = PeriodicCosts(month)

        for service_usage in period["Groups"]:

            value = Decimal(service_usage["Metrics"]["BlendedCost"]["Amount"])

            if value != 0:
                account = account_map[service_usage["Keys"][0]]
                service = service_usage["Keys"][1] if not opts.ignore_service_usage else None
                unit = service_usage["Metrics"]["BlendedCost"]["Unit"]

                periodic_cost_info.add_cost(ServiceUsageCost(account,
                                                             service,
                                                             value.quantize(Decimal(".01"), rounding=ROUND_HALF_UP),
                                                             unit))
        # sort usage costs by account
        periodic_cost_info.account_service_usage = sorted(periodic_cost_info.account_service_usage.items())
        costs_by_periods.append(periodic_cost_info)

    # print(start)
    # print(end)
    return costs_by_periods


def get_account_names(ce, start, end):
    resp = ce.get_dimension_values(
        TimePeriod={
            "Start": start,
            "End": end
        },
        Dimension="LINKED_ACCOUNT"
    )

    account_map = {}
    for account_info in resp["DimensionValues"]:
        account_map[account_info["Value"]] = account_info["Attributes"]["description"]

    return account_map


def execute():
    (opts, action) = parse_args()

    # list_opts(opts)

    try:

        session = boto3.Session(profile_name=opts.profile if opts.profile else None,
                                region_name=opts.region if opts.region else None)

        ec2 = session.client("ec2")

        if action == "create-instances":
            create_instances(ec2, opts)
        elif action == "list-sec-groups":
            list_security_groups(ec2)
        elif action == "list-instances":
            list_instances(ec2)
        elif action == "list-regions":
            list_regions(ec2, opts)
        elif action == "list-zones":
            list_availability_zones(ec2, opts)
        elif action == "list-images":
            list_images(ec2)
        elif action == "list-key-pairs":
            list_key_pairs(ec2)
        elif action == "stop-instances":
            stop_instances(ec2, opts)
        elif action == "start-instances":
            start_instances(ec2, opts)
        elif action == "terminate-instances":
            terminate_instances(ec2, opts)
        elif action == "list-costs":
            list_costs(session.client("ce"), opts)
        elif action == "email-costs":
            email_costs(session.client("ce"), opts)
        else:
            print("'{}' not supported!".format(action))

    except Exception as e:
        print(e)
        sys.exit(1)


class ServiceUsageCost:

    def __init__(self, account, service_name, cost: Decimal, unit) -> None:
        self.account = account
        self.service_name = service_name
        self.cost = cost
        self.unit = unit

    def as_tuple(self):
        return self.service_name, self.cost, self.unit


class PeriodicCosts:

    def __init__(self, period) -> None:
        self.period = period
        self.account_service_usage = defaultdict(list)  # after sorting => [ ("account XYZ", [(), (), ()]), (...) ]
        self.total = 0
        self.account_total = {}

    def add_cost(self, service_usage_cost: ServiceUsageCost):
        self.account_service_usage[service_usage_cost.account].append(service_usage_cost.as_tuple())
        self.total += service_usage_cost.cost

        self.account_total[service_usage_cost.account] = service_usage_cost.cost \
            if service_usage_cost.account not in self.account_total else \
            self.account_total[service_usage_cost.account] + service_usage_cost.cost

    def prettify(self):
        print("\n{} - {} USD".format(self.period, self.total))

        for account, costs in self.account_service_usage:
            print("\n\t{}\n".format(account))
            for service_cost in costs:
                if service_cost[0]:
                    print("\t\t{} {}\t{}".format(service_cost[1], service_cost[2], service_cost[0]))
            print("\t\t------------")
            print("\t\t{} USD".format(self.account_total[account]))


if __name__ == "__main__":
    execute()
