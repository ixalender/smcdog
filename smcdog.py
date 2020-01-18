import os
import subprocess
import json
from datetime import datetime

# TODO: smc -k TC0D -r - from hex to decimal / 256
# TODO: increase fan speed when temperature goes up to critical level

# NOTE: command to get CPU temperature
# smc -k TC0D -r | sed 's/.*bytes \(.*\))/\1/' |sed 's/\([0-9a-fA-F]*\)/0x\1/g' | perl -ne 'chomp; ($low,$high) = split(/ /); print (((hex($low)*256)+hex($high))/4/64); print "\n";'


FAN_SPEEDS = {
    '6200': '60e0',
    '5600': '5780',
    '5000': '4e20',
    '4800': '4b00',
    '4000': '3e80',
    '3600': '3840',
    '3000': '2ee0',
    '2500': '2710',
}

SMC_PATH = '/Applications/smcFanControl.app/Contents/Resources/smc'


def to_log(message):
    with open(os.path.dirname(os.path.realpath(__file__)) + '/logfile.log', 'a') as f:
        f.write("%s: %s\n" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message))


def settings():
    with open(os.path.dirname(os.path.realpath(__file__)) + '/smcdog.conf', 'r') as f:
        return json.loads(f.read())


def exec_cmd(cmd_path, params=None):
    p = subprocess.Popen([cmd_path] + (params or []), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (output, error) = p.communicate()

    return str(output), error


def calc_speed(target_speed) -> str:
    speed = FAN_SPEEDS.get(target_speed)
    if not speed:
        speed = "%X" % (int(target_speed) * 4)
    return speed


def change_speed(target_speed):
    speed: str = calc_speed(target_speed)
    exec_cmd(SMC_PATH, params=['-k', 'F0Mx', '-w', speed])


def get_speed() -> str:
    out, err = exec_cmd(SMC_PATH, params=['-k', 'F0Mx', '-r'])
    return parse_speed(str(out))


def parse_speed(smc_output: str) -> str:
    """parsing: F0Mx  [fpe2]  4000 (bytes 3e 80)"""
    FLAG = '[fpe2]'
    pos = smc_output.find(FLAG) + len(FLAG)
    return smc_output[pos:pos + 6].strip()


def check_speed():
    speed = get_speed()
    cfg_speed = settings()['speed']

    if speed != cfg_speed:
        to_log('Change to: %s' % cfg_speed)
        change_speed(cfg_speed)

    return get_speed()


if __name__ == '__main__':
    print(check_speed())
