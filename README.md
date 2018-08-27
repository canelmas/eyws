## What?

An alternate easy to use AWS cli, for some specific jobs.

It basically provides functions that I need frequently.

## Install
```bash
pip install eyws
```

## Permissions Required

**list-costs** and **email-costs** require you to enable Cost Explorer first on the console and give following permissions: 

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ce:GetReservationUtilization",
                "ce:GetDimensionValues",
                "ce:GetCostAndUsage",
                "ce:GetTags"
            ],
            "Resource": "*"
        }
    ]
}
``` 
AWSConfigRoleForOrganizations is optional for appending organization information to usage costs.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "organizations:DescribeOrganization",
            "Resource": "*"
        }
    ]
}
```

Keep in mind that each paginated Cost Explorer API request will cost you $0.01 ([Learn more](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-explorer-what-is.html)).

**list-instances**, **list-zones**, **list-regions**, **list-images**, **list-key-pairs**, **list-sec-groups** require:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeAvailabilityZones",
                "ec2:DescribeRegions",
                "ec2:DescribeImages",                                                
                "ec2:DescribeKeyPairs",
                "ec2:DescribeSecurityGroups"
            ],
            "Resource": "*"
        }
    ]
}
```

## Usage
```bash
Usage: eyws <action> [options]

<action> can be:
		create-instances
		stop-instances
		terminate-instances
		list-instances
		list-zones
		list-regions
		list-images
		list-sec-groups
		list-costs
		list-key-pairs
		list-costs
		email-costs

Options:
  --version             show program's version number and exit
  -h, --help            Show this help message and exit
  -p PROFILE, --profile=PROFILE
                        aws profile to use (~/.aws/config) (default=default
                        profile)
  -c Instance Count, --count=Instance Count
                        Number of instances to launch (default=1)
  -n Name Tag, --name=Name Tag
                        Append a name tag to instances
  -w WAIT, --wait=WAIT  Number of seconds to wait for nodes to start
                        (default=120)
  -t Instance Type, --instance-type=Instance Type
                        Type of instances to launch (default=t2.micro)
  -r Region, --region=Region
                        EC2 region to list and launch instances in
                        (default=.aws/config)
  -z Zone, --zone=Zone  Availability zone to list and launch instances in
                        (default=random when launching instances)
  -a Ami, --ami=Ami     AMI ID to use (default=ami-de8fb135)
  -k Key Pair, --key-pair=Key Pair
                        Key pair to use on instances
  -e Size, --ebs-vol-size=Size
                        EBS volume size in GB to attach each instance
                        (default=8)
  --ebs-vol-type=Volume Type
                        Volume type to attach (default=gp2)
                        types=[('standard', 'Magnetic'), ('io1', 'Provisioned
                        IOPS SSD'), ('gp2', 'General Purpose SSD'), ('sc1',
                        'Cold HDD'), ('st1', 'Throughput Optimized HDD')]
  --ebs-delete=Delete On Termination
                        Delete volume on termination (default=True)
  --ebs-vol-name=EBS_VOL_NAME
                        Volume name (default=/dev/sda1)
  --iops=IOPS           IOPS. Not supported for volume type gp2 (default=100)
  -s Security Group Name, --sec-group=Security Group Name
                        Security Group name to use for launching instances
  --instance-id=instance Id
                        instance ids to start/stop/destroy
  --days=DAYS           Usage cost charged since <days> days
  --months=MONTHS       Months to check costs for. 1 means current month.
                        (default=1)
  --ignore-service-usage
                        Do not display costs for each service type
  --emails=EMAILS       Comma separated email addresses to send cost
                        information
  --template=TEMPLATE   Jinja template file
  --smtp-host=SMTP_HOST
                        SMTP host to use for sending emails
  --smtp-port=SMTP_PORT
                        SMTP port to use for sending emails
  --smtp-from=SMTP_FROM
                        Sender email address
  --dry-run             Dry run operations
```

## Todo

* Provision Docker
* Provision and manage a Spark cluster
* --format