import time
import serial

reply = ''

i = 1


ser= serial.Serial(
	port='/dev/serial0', #serial port the object should read
	baudrate= 19200,      #rate at which information is transfered over comm channel
	parity=serial.PARITY_NONE, #no parity checking
	stopbits=serial.STOPBITS_ONE, #pattern of bits to expect which indicates the end of a character
	bytesize=serial.EIGHTBITS, #number of data bits
	timeout=1
)

time.sleep(1)

while(1):

	comm = 1

	print('Welcome to the OXYBASE tester v0.2 \n')

	print('1. Print status report')
	print('2. Set data request mode')
	print('3. Set temperature compensation with interne NTC 22k sensor active.')
	print('4. Stores currently measured values (phase and temperature) as low pO 2 calibration')
	print('5. Stores currently measured values (phase and temperature) as high pO 2 calibration')
	print('6. Returns self-test message\n\n')
	print('9. Returns N data samples and saves to local direcotry')
	print('0. Type your own command')

	func = raw_input('-')
	
	ser.flushInput()
	ser.flushOutput()

# Print status report

	if func == '1':

		ser.write(b'repo\r')

		reply = ser.read_until('\r\r')

		print(reply)

# Set data request mode

	elif func == '2':

		print('Which data request mode?')

		modeNum = raw_input('-')

		if modeNum == 0 or 1 or 2 or 3:

			ser.write(b'data000%s\r' % modeNum)

			reply = ser.read_until('\r\r')

			print(reply)

		else:
			
			print("Please select modes 0 - 3")


# Set temperature compensation with interne NTC 22k sensor active

	elif func == '3':

		ser.write(b'tmpa\r')

		reply = ser.read_until('\r\r')

		print(reply)

# Stores currently measured values (phase and temperature) as low pO 2 calibration

	elif func == '4':

		ser.write(b'calz\r')

		reply = ser.read_until('\r\r')

		print(reply)

# Stores currently measured values (phase and temperature) as high pO 2 calibration

	elif func == '5':

		ser.write(b'calh\r')

		reply = ser.read_until('\r\r')

		print(reply)

# Returns self-test message

	elif func == '6':

		ser.write(b'post\r')

		reply = ser.read_until('\r\r')

		print(reply)

# Returns N data samples and saves to local direcotry

	elif func == '9':

		cmd = int(raw_input('Please input number of samples:'))

		ser.write(b'mode0001\r')

		timestr = str(time.strftime("%Y%m-%d_%H-%M-%S"))

		file_name = "./OXYBASE" + timestr

		file = open(file_name,"a+")

		file.write(file_name + "\r\n")

		while(i <= cmd):

			ser.write(b'data\r')

			reply = ser.read_until('\r')

			reply = '\n' + reply

			file.write(reply)

			print(reply)

			i = i + 1

			time.sleep(1)

		ser.write(b'mode0000\r')

		i = 0

# Type your own command

	elif func == '0':

		print('Please type your commands below or q to exit:')

		while(comm == 1):

			cmd = raw_input('-> ')

			if cmd == 'q':
				comm = 0

			else:

				cmd = cmd + '\r'

				ser.write(cmd)

				reply = ser.read_until('\r\r')

				reply = '\n' + reply

				print(reply)

	else:
		print('You broke it..')
