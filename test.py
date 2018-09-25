import operate
import time
import os
import traceback


def getdevice():
    lines = os.popen('adb devices').readlines()
    if len(lines) > 1:
        return lines[1].split('\t')[0]
    else:
        return ''


if __name__ == '__main__':
    devices = getdevice()
    if devices != '':
        o = operate.Operate(devices)
        # o.complete()
        while True:
            o.open_game()
            try:
                o.rank()
            except Exception as e:
                traceback.print_exc()
                time.sleep(50)
