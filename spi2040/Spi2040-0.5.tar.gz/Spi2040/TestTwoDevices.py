if __name__ == "__main__":
    from Spi2040 import BasysV1

    SCK = 22
    COPI = 23
    CIPO = 20

    Dev1 = BasysV1.SpiDevice(SCK, COPI, CIPO, 21, 11)
    Dev2 = BasysV1.SpiDevice(SCK, COPI, CIPO, 28, 11)

    msg1 = bytearray()
    msg2 = bytearray()
    for i in range(256):
        msg1.append(i)
        msg2.append(255-i)

    Dev1.Send(msg1)
    Dev2.Send(msg2)

    out1 = Dev1.Receive()
    out2 = Dev2.Receive()

    if out1 == msg1:
        print("Success")
    else:
        print("Failure")
        #