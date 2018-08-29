from eyws.ssh import ssh


def install_docker(opts, instances):
    for res in instances:
        for instance in res["Instances"]:
            instance_id = instance["InstanceId"]
            public_dns = instance["PublicDnsName"]
            print("installing docker on {id} ({pdns})...".format(id=instance_id, pdns=public_dns))
            execute(instance, opts, "sudo apt-get update")
            execute(instance, opts, "sudo apt-get install apt-transport-https ca-certificates curl "
                                    "software-properties-common")
            execute(instance, opts, "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -")
            execute(instance, opts, "sudo apt-key fingerprint 0EBFCD88")
            execute(instance, opts, "sudo add-apt-repository \"deb [arch=amd64] "
                                    "https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\"")
            execute(instance, opts, "sudo apt-get update")
            execute(instance, opts, "apt-cache policy docker-ce")
            execute(instance, opts, "sudo apt-get install docker-ce")
            execute(instance, opts, "sudo usermod -aG docker $USER")
            execute(instance, opts, "sudo systemctl enable docker")
            print("docker installed on {id} ({pdns})".format(id=instance_id, pdns=public_dns))


def execute(instance, opts, cmnd):
    ssh(host=instance["PublicDnsName"],
        opts=opts,
        command=cmnd)
