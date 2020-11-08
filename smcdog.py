# TODO: increase fan speed when temperature goes up to the critical level
# TODO: decrease fan speed when temperature goes down to the normal level
#   NOTE: command to get CPU temperature:
#   smc -k TC0D -r | sed 's/.*bytes \(.*\))/\1/' |sed 's/\([0-9a-fA-F]*\)/0x\1/g' | perl -ne 'chomp; ($low,$high) = split(/ /); print (((hex($low)*256)+hex($high))/4/64); print "\n";'


import re
import json
import os
import subprocess
from typing import Tuple
from datetime import datetime
from collections import namedtuple


SMC_PATH = '/Applications/smcFanControl.app/Contents/Resources/smc'
LOG_FILE = 'logfile.log'


def to_log(message):
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), LOG_FILE)
    print(logpath)
    with open(logpath, 'a') as f:
        f.write(f"{date}: {message}\n")


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
    return "%X" % (target_speed * 4)


def change_speed(target_speed: int) -> Tuple[str, str]:
    speed = hex_speed(target_speed)
    return exec_cmd(SMC_PATH, params=['-k', 'F0Mx', '-w', speed])


def get_current_speed() -> int:
    out, err = exec_cmd(SMC_PATH, params=['-k', 'F0Mx', '-r'])
    return parse_speed(out)


def parse_speed(smc_output: str) -> int:
    """parse utility output to get fan speed value"""
    speed = extract_byte_value(smc_output) / 4
    return int(speed)


def parse_temperature(smc_output: str) -> float:
    """parse utility output to get cpu temp value"""
    temp = extract_byte_value(smc_output) / 256
    return float(temp)


def extract_byte_value(data: str) -> int:
    bytes_reg = '.*bytes (.*)\)'
    low, high = re.search(bytes_reg, data).group(1).split()
    return ((int(low, 16) * 256) + int(high, 16))


def manage_speed() -> int:
    target_speed = config().speed
    if target_speed != get_current_speed():
        to_log('Change to: %s' % target_speed)
        change_speed(target_speed)

    return get_current_speed()


if __name__ == '__main__':
    print(manage_speed())
