#!/usr/bin/env python3
import RPi.GPIO as GPIO
import tsys01
import ms5837
from kellerLD import KellerLD
import pickle
import time
import os
import math
import configparser
import sys

BURN = 33
data_rec = 16

samp_count = 1

NumSamples = 0

BURN_WIRE = False

ps_test = "pgrep -a python"

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(BURN, GPIO.OUT)
GPIO.output(BURN, 1)

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

def abortMission(configLoc):

    abortConfig = configparser.ConfigParser()
    abortConfig.read(configLoc)
    abortConfig.set('Mission','Abort','1')
    with open(config,'wb') as abortFile:
        abortConfig.write(abortFile)

def kill_sampling(scriptNames):

    for script in scriptNames:
        os.system("sudo pkill -9 -f {}".format(script))

def read_sampcount():
    countp = open("/home/pi/Documents/Minion_scripts/sampcount.pkl","rb")
    sampcount = pickle.load(countp)
    countp.close()
    return sampcount

scriptNames = ["TempPres.py", "Minion_image.py","Minion_image_IF.py","OXYBASE_RS232.py","ACC_100Hz.py","Extended_Sampler.py","TempPres_IF.py","OXYBASE_RS232_IF.py","ACC_100Hz_IF.py","Iridium_gps.py","Iridium_data.py"]

if(any(x in os.popen(ps_test).read() for x in scriptNames)) == True:

    kill_sampling(scriptNames)

data_config = configparser.ConfigParser()
data_config.read('/home/pi/Documents/Minion_scripts/Data_config.ini')

configDir = data_config['Data_Dir']['Directory']
configLoc = '{}/Minion_config.ini'.format(configDir)
config = configparser.ConfigParser()
config.read(configLoc)
Abort = str2bool(config['Mission']['Abort'])
iniImg = str2bool(config['Sampling_scripts']['Image'])
iniP30 = str2bool(config['Sampling_scripts']['30Ba-Pres'])
iniP100 = str2bool(config['Sampling_scripts']['100Ba-Pres'])
iniTmp = str2bool(config['Sampling_scripts']['Temperature'])
iniO2  = str2bool(config['Sampling_scripts']['Oxybase'])
iniAcc = str2bool(config['Sampling_scripts']['ACC_100Hz'])

MAX_Depth = int(config['Mission']['MAX_Depth'])

Ddays = int(config['Deployment_Time']['days'])
Dhours = int(config['Deployment_Time']['hours'])

Srate = float(config['Sleep_cycle']['Minion_sleep_cycle'])

TotalCycles = int((((Ddays*24)+Dhours))/Srate)

samp_count = int(read_sampcount())

firstp = open("/home/pi/Documents/Minion_scripts/timesamp.pkl","rb")
samp_time = pickle.load(firstp)

samp_time = "{}-{}".format(samp_count, samp_time)

Stime = float(config['Final_Samples']['hours'])
Srate = float(config['Final_Samples']['TempPres_sample_rate'])

file_name = "{}/minion_data/FIN/{}_TEMPPRES-FIN.txt".format(configDir, samp_time)

Sf = 1/Srate

TotalSamples = Stime*60*60*Srate

######################

time.sleep(1)

file = open(file_name,"a+")

file.write("{}_TEMPPRES.txt".format(samp_time))

if iniP30 == True:

    Psensor = ms5837.MS5837_30BA() # Default I2C bus is 1 (Raspberry Pi 3)

    if not Psensor.init():
        print("Failed to initialize P30 sensor!")
        exit(1)

    depth_factor = .01
    surface_offset = 10

    # We have to read values from sensor to update pressure and temperature
    if Psensor.read():
        Pres_ini = round((Psensor.pressure() * depth_factor) - surface_offset, 3)
    else:
        Pres_ini = "Broken"

    file.write("Pressure(dbar),Temp(C)")

if iniP100 == True:

    Psensor = KellerLD()

    if not Psensor.init():
        print("Failed to initialize P100 sensor!")
        exit(1)

    depth_factor = 10
    surface_offset = 0

    # We have to read values from sensor to update pressure and temperature
    if Psensor.read():
        Pres_ini = round((Psensor.pressure() * depth_factor) - surface_offset, 3)
    else:
        Pres_ini = "Broken"

    file.write("Pressure(dbar),Temp(C)")

if iniTmp == True:

    sensor_temp = tsys01.TSYS01()

    # We must initialize the sensor before reading it
    if not sensor_temp.init():
        print("Error initializing Temperature sensor")
        exit(1)

    file.write(", TempTSYS01(C)")

file.close()

if iniP100 == False and iniP30 == False:
    Pres_ini = 2000

if __name__ == '__main__':

    if Pres_ini == "Broken":
        print("Pressure Sensor Not Working...")
        abortMission(configLoc)
        os.system('sudo python /home/pi/Documents/Minion_scripts/Iridium_gps.py')

#    if Abort == True:
#        GPIO.output(BURN,1)
#        os.system('sudo python /home/pi/Documents/Minion_scripts/Iridium_gps.py')

    if samp_count == TotalCycles + 1:
        GPIO.output(BURN,1)

        if iniImg == True:
            os.system('sudo python3 /home/pi/Documents/Minion_scripts/Minion_image_IF.py &')

        if iniO2 == True:
            os.system('sudo python3 /home/pi/Documents/Minion_scripts/OXYBASE_RS232_IF.py &')

        if iniAcc == True:
            os.system('sudo python3 /home/pi/Documents/Minion_scripts/ACC_100Hz_IF.py &')

        # Spew readings
        while(NumSamples <= TotalSamples):

            tic = time.perf_counter()

            print("Final Sampling Mode")  #Indicate to the user in which mode the Minion is operating

            file = open(file_name,"a")

            sensor_string = ''

            if iniP100 or iniP30 == True:

                if Psensor.read():
                    Ppressure = round((Psensor.pressure() * depth_factor) - surface_offset, 3)
                    Ptemperature = round(Psensor.temperature(),3)
                    Pres_data = "{},{},".format(Ppressure, Ptemperature)
                    print("Pressure sensor data: {}".format(Pres_data))
                    sensor_string = "{}{}".format(sensor_string,Pres_data)

                else:
                    print('Pressure Sensor ded')
                    file.write('Pressure Sensor fail')
                    abortMission(configLoc)

                if Ppressure >= MAX_Depth:
                    file.write("Minion Exceeded Depth Maximum!")
                    abortMission(configLoc)

            if iniTmp == True:

                if not sensor_temp.read():
                    print("Error reading sensor")
                    iniTmp = False

                Temp_acc = round(sensor_temp.temperature(),4)

                print("Temperature_accurate: {} C".format(Temp_acc))

                sensor_string = '{}{}'.format(sensor_string, Temp_acc)


            file.write("{}\n".format(sensor_string))

            NumSamples = NumSamples + 1

            toc = time.perf_counter()

            timeS = toc - tic

            if timeS >= Sf:

                timeS = Sf

            time.sleep(Sf - timeS)


        os.system('sudo python /home/pi/Documents/Minion_scripts/Iridium_gps.py &')
        GPIO.output(data_rec, 0)


    else:
        GPIO.output(BURN,1)
        os.system('sudo python /home/pi/Documents/Minion_scripts/Iridium_gps.py &')

    time.sleep(60)
