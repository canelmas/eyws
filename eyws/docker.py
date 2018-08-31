# Copyright 2018 Can Elmas

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from eyws import ssh


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
