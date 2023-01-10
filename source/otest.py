import serial 

ser= serial.Serial(
                    port='/dev/serial0', #serial port the object should read
                    baudrate= 19200,      #rate at which information is transfered over comm channel
                    parity=serial.PARITY_NONE, #no parity checking
                    stopbits=serial.STOPBITS_ONE, #pattern of bits to expect which indicates the end of a character
                    bytesize=serial.EIGHTBITS, #number of data bits
                    timeout=1
                )
ser.flushInput()
ser.flushOutput()
ser.write(b'mode0001\r')
ser.write(b'data\r')
reply = ser.read_until('\r')
print("OXYBase: {}".format(reply))
