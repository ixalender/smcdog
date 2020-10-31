# TODO: smc -k TC0D -r - from hex to decimal / 256
# TODO: increase fan speed when temperature goes up to critical level
#   NOTE: command to get CPU temperature:
#   smc -k TC0D -r | sed 's/.*bytes \(.*\))/\1/' |sed 's/\([0-9a-fA-F]*\)/0x\1/g' | perl -ne 'chomp; ($low,$high) = split(/ /); print (((hex($low)*256)+hex($high))/4/64); print "\n";'


import re
import json
import os
import subprocess
from typing import Tuple
from datetime import datetime
from collections import namedtuple

FAN_SPEEDS = {
    6200: '60e0',
    5600: '5780',
    5000: '4e20',
    4800: '4b00',
    4000: '3e80',
    3600: '3840',
    3000: '2ee0',
    2500: '2710',
}


SMC_PATH = '/Applications/smcFanControl.app/Contents/Resources/smc'


def to_log(message):
    with open(os.path.dirname(os.path.realpath(__file__)) + '/logfile.log', 'a') as f:
        f.write("%s: %s\n" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message))


def config(filepath=None):
    def decoder(obj_dict: dict) -> namedtuple:
        return namedtuple('X', obj_dict.keys())(*obj_dict.values())

    with open(filepath or os.path.dirname(os.path.realpath(__file__)) + '/smcdog.conf', 'r') as f:
        return json.loads(f.read(), object_hook=decoder)


def exec_cmd(cmd_path, params=None) -> Tuple[str, str]:
    p = subprocess.Popen([cmd_path] + (params or []), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (output, error) = p.communicate()

    return str(output), error


def hex_speed(target_speed: int) -> str:
    speed = FAN_SPEEDS.get(target_speed)
    if speed is None:
        speed = "%X" % (target_speed * 4)
    return speed


def change_speed(target_speed: int) -> Tuple[str, str]:
    speed = hex_speed(target_speed)
    return exec_cmd(SMC_PATH, params=['-k', 'F0Mx', '-w', speed])


def get_current_speed() -> int:
    out, err = exec_cmd(SMC_PATH, params=['-k', 'F0Mx', '-r'])
    return int(parse_speed(out))


def parse_speed(smc_output: str) -> str:
    """parsing: F0Mx  [fpe2]  4000 (bytes 3e 80)"""

    bytes_reg = '.*bytes (.*)\)'

    low, high = re.search(bytes_reg, smc_output).group(1).split()
    speed = ((int(low, 16) * 256) + int(high, 16)) / 4

    return str(int(speed))


def check_speed():
    target_speed = config().speed

    if target_speed != get_current_speed():
        to_log('Change to: %s' % target_speed)
        change_speed(target_speed)

    return get_current_speed()


if __name__ == '__main__':
    print(check_speed())
