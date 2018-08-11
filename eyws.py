import os
import sys
from optparse import OptionParser

import boto3

VERSION = "1.0.0"
UBUNTU_AMI = "ami-1e339e71"
DRY_RUN = False
DEFAULT_AMI = UBUNTU_AMI
DEFAULT_NUM_OF_INSTANCES = 1


def aws():
    s3 = boto3.resource("s3")
    for bucket in s3.buckets.all():
        print(bucket.name)


def parse_args():
    parser = OptionParser(usage="eyws-ec2 [options] <action>"
                                + "\n\n<action> can be: create-ec2, stop-ec2, terminate-ec2, list-ec2," +
                                "list-zones, list-regions, list-images",
                          version="%prog {}".format(VERSION))

    parser.add_option("-n", "--number", type="int", default=DEFAULT_NUM_OF_INSTANCES,
                      help="Number of instances to launch (default=1)")

    parser.add_option("-w", "--wait", type="int", default=120,
                      help="Number of seconds to wait for nodes to start (default=120)")

    parser.add_option("-t", "--instance-type", default="m1.large",
                      help="Type of instances to launch (default=m1.large")

    parser.add_option("-r", "--region",
                      help="EC2 region to list and launch instances in")

    parser.add_option("-z", "--zone", default="",
                      help="Availability zone to list and launch instances in")

    parser.add_option("-a", "--ami", default=DEFAULT_AMI,
                      help="AMI ID to use")

    parser.add_option("-d", "--dry-run", default=DRY_RUN,
                      help="Dry run")

    (opts, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        sys.exit(1)

    (action) = args[0]

    return opts, action


def list_instances(ec2, opts):
    for res in ec2.describe_instances()["Reservations"]:
        for instance in res["Instances"]:
            print("imageId = {}\n"
                  "state = {}\n"
                  "state-message = {}\n"
                  "instanceId = {}\n"
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
                  "security-groups = {}\n\n".format(instance["ImageId"],
                                                    instance["State"]["Name"],
                                                    instance["StateTransitionReason"],
                                                    instance["InstanceId"],
                                                    instance["InstanceType"],
                                                    instance["KeyName"],
                                                    instance["Monitoring"]["State"],
                                                    instance["Placement"]["AvailabilityZone"],
                                                    instance["PrivateDnsName"],
                                                    instance["PrivateIpAddress"],
                                                    instance["PublicDnsName"],
                                                    "" if instance["State"]["Name"] == "stopped" else instance[
                                                        "PublicIpAddress"],
                                                    instance["SubnetId"],
                                                    instance["VpcId"],
                                                    instance["Tags"],
                                                    instance["CpuOptions"]["CoreCount"],
                                                    instance["CpuOptions"]["ThreadsPerCore"],
                                                    instance["SecurityGroups"]))


def list_regions(ec2, opts):
    for region in [region['RegionName'] for region in ec2.describe_regions()["Regions"]]:
        print(region)


def list_availability_zones(ec2, opts):
    for zone in [zone["ZoneName"] for zone in ec2.describe_availability_zones()["AvailabilityZones"]]:
        print(zone)


def list_images(ec2, opts):
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

    for image_info in [(image["Name"], image["ImageId"]) for image in
                       ec2.describe_images(Filters=filters)["Images"]]:
        print(image_info)


def parse():
    (opts, action) = parse_args()

    try:

        ec2 = boto3.client("ec2", region_name=opts.region if opts.region else None)

        if action == "create":
            print("'{}' will be supported soon.".format(action))
        elif action == "list-instances":
            list_instances(ec2, opts)
        elif action == "list-regions":
            list_regions(ec2, opts)
        elif action == "list-azones":
            list_availability_zones(ec2, opts)
        elif action == "list-images":
            list_images(ec2, opts)
        else:
            print("'{}' not supported!".format(action))

    except Exception as e:
        print(e)
        sys.exit(1)


def main():
    parse()


if __name__ == "__main__":
    main()
