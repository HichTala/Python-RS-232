import binascii
import sys

import serial
import time


def read(ser):
    out = []
    while ser.inWaiting() > 0:
        out.append(ser.read(1))
    print("Answer:")
    print([binascii.hexlify(b).decode() for b in out])
    return out


def send(ser, cmd):
    send = [0x90, 0x05, 0x00, 0x03, 0x00]
    send[2] += cmd
    cs = 0x00
    for b in send:
        cs += b
    send[4] = cs % 256

    send_bytes = [b.to_bytes(1, 'big') for b in send]
    print("Sent bytes:")
    print([binascii.hexlify(b).decode() for b in send_bytes])
    ser.write(send)
    time.sleep(0.1)
    return read(ser)


def main(portname):
    ser = serial.Serial(
        port=portname,
        baudrate=9600,
        bytesize=serial.SEVENBITS,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE
    )
    currency_dict = {1: 0.5, 2: 1, 3: 2}
    amount = None

    print("Order amount to pay?")

    while ser.isOpen():
        try:
            if amount is None:
                amount = float(input())
                print("Still to be paid:", amount)

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
                    print("-------- Here disable de coin acceptor --------")
                else:
                    print("Still to be paid:", amount)

        except KeyboardInterrupt:
            print('\n\nGoodbye!')
            print('Port {:s} closed'.format(portname))
            break


if __name__ == "__main__":
    main(sys.argv[1])
