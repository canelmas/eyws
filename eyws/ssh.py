import pipes
import subprocess
import time
from sys import stderr


def ssh(host, opts, command):
    tries = 0
    while True:
        try:
            return subprocess.check_call(ssh_command(opts) + ['-t', '-t', '%s@%s' % (opts.user, host), stringify_command(command)])
        except subprocess.CalledProcessError as e:
            if tries > 5:
                if e.returncode == 255:
                    raise Exception(
                        "Failed to SSH to remote host {0}.\n" +
                        "Please check that you have provided the correct --identity and " +
                        "--key-pair parameters and try again.".format(host))
                else:
                    raise e
            print("Error executing remote command, retrying after 15 seconds: {0}".format(e),
                  file=stderr)
            time.sleep(15)


def ssh_command(opts):
    return ['ssh'] + ssh_args(opts)


def ssh_args(opts):
    parts = ['-o', 'StrictHostKeyChecking=no']
    parts += ['-o', 'UserKnownHostsFile=/dev/null']
    if opts.identity is not None:
        parts += ['-i', opts.identity]
    return parts


def stringify_command(parts):
    if isinstance(parts, str):
        return parts
    else:
        return ' '.join(map(pipes.quote, parts))
