import binascii
import sys

import serial
import time


def read(ser):
    out = []
    while ser.inWaiting() > 0:
        out.append(ser.read(1))
    return out


def send(ser, cmd):
    ser.write(cmd)
    time.sleep(0.1)
    return read(ser)

def reset(ser):
    ser.write([0x70])
    print(read(ser))
    time.sleep(0.1)
    ser.write([0x73])
    time.sleep(0.1)
    return read(ser)


def main(portname):
    ser = serial.Serial(
        port=portname,
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE
    )
    currency_dict = {1: 0.5, 2: 1, 3: 20, 4: 50, 5: 100, 6: 200}
    amount = None

    while ser.isOpen():
        print("it?")
        iteration = int(input())
        for i in range(iteration):
            print(send(ser, [0x80]))
            print(send(ser, [0x81]))
            print(send(ser, [0x40]))
            send(ser, [0x10])
            time.sleep(0.1)
        breakpoint()


    while ser.isOpen():
        try:
            if amount is None:
                amount = float(input())
                print("Still to be paid:", amount)
                send(ser, 0x01)

            out = []
            while ser.inWaiting() > 0:
                out.append(ser.read(1))

            if not out:
                continue

            status = currency_dict[ord(out[3])]

            if amount is not None:
                amount -= status
                print("Amount collected", status)
                if amount <= 0:
                    print("Currency to be returned", -amount)
                    send(ser, 0x02)
                else:
                    print("Still to be paid:", amount)

        except KeyboardInterrupt:
            print('\n\nGoodbye!')
            print('Port {:s} closed'.format(portname))
            break


if __name__ == "__main__":
    main(sys.argv[1])
