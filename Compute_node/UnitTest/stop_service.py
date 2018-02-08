import subprocess
import time

check_status_cmd = "systemctl -r --type service --all | grep 'qemu-kvm'"
stop_service_cmd = "systemctl stop qemu-kvm"


def main():
    count = 100
    while count > 0:
        if checkStatus(check_status_cmd):
            stopService(stop_service_cmd)
            print count
            count -= 1
        time.sleep(0.5)


def checkStatus(cmd):
    response = subprocess.check_output(cmd, shell=True)
    if "dead" in response:
        return False
    else:
        return True


def stopService(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)


if __name__ == '__main__':
    main()
