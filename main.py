import binascii
import sys

import serial
import time


def read(ser):
    out = []
    while ser.inWaiting() > 0:
        out.append(ser.read(1))
    # print("Answer:")
    # print([binascii.hexlify(b).decode() for b in out])
    return out


def send(ser, cmd):
    send = [0x90, 0x05, 0x00, 0x03, 0x00]
    send[2] += cmd
    cs = 0x00
    for b in send:
        cs += b
    send[4] = cs % 256

    send_bytes = [b.to_bytes(1, 'big') for b in send]
    # print("Sent bytes:")
    # print([binascii.hexlify(b).decode() for b in send_bytes])

    ser.write(send)
    time.sleep(0.1)
    return read(ser)


def main(portname_coin, portname_bill):
    ser_coin = serial.Serial(
        port=portname_coin,
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE
    )

    ser_bill = serial.Serial(
        port=portname_bill,
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE
    )

    currency_dict_coin = {1: 0.5, 2: 1, 3: 2}
    currency_dict_bill = {254: 2000, 255: 1000}
    amount = None

    print("Order amount to pay?")
    out = []
    while not out:
        ser_bill.write([0x5e])
        while ser_bill.inWaiting() > 0:
            out.append(ser_bill.read(1))

    send(ser_coin, 0x02)

    while ser_coin.isOpen() and ser_bill.isOpen():
        try:
            if amount is None:
                amount = float(input())
                print("Still to be paid:", amount)
                ser_bill.write([0x3e])
                send(ser_coin, 0x01)

            ser_bill.write([0x02])

            out = []
            while ser_bill.inWaiting() > 0:
                out.append(ser_bill.read(1))

            if out:
                if len(out) > 1 and (ord(out[1]) in [0xfe, 0xff]):
                    print(out)
                    status = currency_dict_bill[ord(out[1])]

                    if amount is not None:
                        amount -= status
                        print("Amount collected", status)
                        if amount <= 0:
                            out = []
                            while not out:
                                ser_bill.write([0x5e])
                                while ser_bill.inWaiting() > 0:
                                    out.append(ser_bill.read(1))
                            send(ser_coin, 0x02)
                            print("Currency to be returned", -amount)
                            break
                        else:
                            print("Still to be paid:", amount)
            else:
                while ser_coin.inWaiting() > 0:
                    out.append(ser_coin.read(1))

                if not out:
                    continue

                status = currency_dict_coin[ord(out[3])]

                if amount is not None:
                    amount -= status
                    print("Amount collected", status)
                    if amount <= 0:
                        out = []
                        while not out:
                            ser_bill.write([0x5e])
                            while ser_bill.inWaiting() > 0:
                                out.append(ser_bill.read(1))
                        send(ser_coin, 0x02)
                        print("Currency to be returned", -amount)
                        break
                    else:
                        print("Still to be paid:", amount)

        except KeyboardInterrupt:
            print('\n\nGoodbye!')
            # print('Port {:s} closed'.format(portname))
            break


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
