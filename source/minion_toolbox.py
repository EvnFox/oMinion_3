#!/usr/bin/env python3

import configparser
import os
import RPi.GPIO as GPIO
import time

#Pin Definitions
light = 12


data_config_file = '/home/pi/Documents/Minion_scripts/Data_config.ini'
#data_config_file = 'Data_config.ini'
data_xmt_status_pickle_file = '/home/pi/Documents/Minion_scripts/data_xmt_status.pickle'

class MinionToolbox():
    
    def str2bool(self,v):
        """Convert a string to a boolean"""
        return v.lower() in ("Y", "y", "yes", "true", "t", "1")   

    def read_data_config(self):
        """Read the Minion Data Configuration Directory File"""

        keys = ['Data_Dir']

        data_config = dict.fromkeys(keys)
        
        config = configparser.ConfigParser()
        config.read(data_config_file)

        data_config['Data_Dir'] = config['Data_Dir']['Directory']  

        print('Data Config: ' + data_config['Data_Dir'])
        return data_config
        pass

    def read_mission_config(self):
        """Read the Minion Mission Configuration File

        Parameters
        ----------
        none

        Returns:
        --------
        dict mission_config : Minion Mission Configuration Dictionary
            keys:
                str Minion_ID : Minion Serial Number
                bool Abort : Enable / Disable Mission Abort Feature
                float MAX_Depth : Maximum Depth Limit in meters
                float IG_WIFI_D : Ignore WIFI Days
                float IG_WIFI_H : Ingnore WIFI Hours
                float INIsamp_hours : Number Sampling Hours (Initial Mode)
                float INIsamp_camera_rate : Camera Sample Rate (Initial Mode)
                float INIsamp_tempPres_rate : Temperature/Pressure Sample Rate (Initial Mode)
                float INIsamp_oxygen_rate : Oxygen Sample Rate (Initial Mode)
                float FINsamp_hours : Number Sampling Hours (Final Mode)
                float FINsamp_camera_rate : Camera Sample Rate (Finall Mode)
                float FINsamp_tempPres_rate : Temperature/Pressure Sample Rate (Final Mode)
                float FINsamp_oxygen_rate : Oxygen Sample Rate (Final Mode)
                int Ddays : Number of Deployment Days
                int Dhours : Number of Deployment Hours
                float Srate : Sleep Cycle
                float Stime : Sample Time
                float TLPsamp_minion_rate : Minion Sample Rate (Time-Lapse Mode)
                float TLPsamp_oxygen_rate : Oxygen Sample Rate (Time-Lapse Mode)
                bool iniImg : Enable / Disable Image Capture
                bool iniP30 : Enable / Disable 30 Bar Pressure Sensor
                bool iniP100 : Enable / Disable 100 Bar Pressure Sensor
                bool iniTmp : Enable/Disable Temperature Sensor
                bool iniO2 : Enable/Disable Oxygen Sensor
                bool iniAcc : Enable/Disable Accelerometer


        """

        #list of keys
        keys = ['Minion_ID','Abort','MAX_Depth','IG_WIFI_D','IG_WIFI_H',\
                'INIsamp_hours','INIsamp_camera_rate','INIsamp_tempPres_rate',\
                'INIsamp_oxygen_rate','FINsamp_hours','FINsamp_camera_rate',\
                'FINsamp_tempPres_rate','FINsamp_oxygen_rate','TLPsamp_minion_rate',\
                'TLPsamp_oxygen_rate','Ddays','Dhours','Stime','Srate','iniImg',\
                'iniP30','iniP100','iniTmp','iniO2','iniAcc'\
                ]

        mission_config = dict.fromkeys(keys)

        data_config = self.read_data_config()
        config_file = '{}/Minion_config.ini'.format(data_config['Data_Dir'])
        print('Mission Config: ' + config_file)

        config = configparser.ConfigParser()
        config.read(config_file)

        mission_config['Minion_ID'] = str(config['MINION']['Number'])

        mission_config['Abort'] = self.str2bool(config['Mission']['Abort'])
        mission_config['MAX_Depth'] = float(config['Mission']['Max_Depth'])       
        mission_config['IG_WIFI_D'] = float(config['Mission']['Ignore_WIFI-days'])
        mission_config['IG_WIFI_H'] = float(config['Mission']['Ignore_WIFI-hours'])

        mission_config['INIsamp_hours'] = float(config['Initial_Samples']['hours'])
        mission_config['INIsamp_camera_rate'] = float(config['Initial_Samples']['Camera_sample_rate'])
        mission_config['INIsamp_tempPres_rate'] = float(config['Initial_Samples']['TempPres_sample_rate'])
        mission_config['INIsamp_oxygen_rate'] = float(config['Initial_Samples']['Oxygen_sample_rate'])

        mission_config['FINsamp_hours'] = float(config['Final_Samples']['hours'])
        mission_config['FINsamp_camera_rate'] = float(config['Final_Samples']['Camera_sample_rate'])
        mission_config['FINsamp_tempPres_rate'] = float(config['Final_Samples']['TempPres_sample_rate'])
        mission_config['FINsamp_oxygen_rate'] = float(config['Final_Samples']['Oxygen_sample_rate'])
        
        mission_config['Ddays'] = int(config['Deployment_Time']['days'])
        mission_config['Dhours'] = int(config['Deployment_Time']['hours'])
 
        mission_config['Srate'] = float(config['Sleep_cycle']['Minion_sleep_cycle'])
        
        Stime = config['Data_Sample']['Minion_sample_time']
        #Determine if the value entered into 'Minion_sample_time' is
        #    'Camera' or an actual number.
        #Note: Any text will work, not just 'Camera'
        try:
            mission_config['Stime'] = float(Stime)
        except:
            #Since Stime cannot be cast as a float, there must be some text
            #in the field such as 'Camera'
            mission_config['Stime'] = float(.2)
        mission_config['TLPsamp_minion_rate'] = float(config['Data_Sample']['Minion_sample_rate'])
        mission_config['TLPsamp_oxygen_rate'] = float(config['Data_Sample']['Oxygen_sample_rate'])
        
        mission_config['iniImg'] = self.str2bool(config['Sampling_scripts']['Image'])
        mission_config['iniP30'] = self.str2bool(config['Sampling_scripts']['30Ba-Pres'])
        mission_config['iniP100'] = self.str2bool(config['Sampling_scripts']['100Ba-Pres'])
        mission_config['iniTmp'] = self.str2bool(config['Sampling_scripts']['Temperature'])
        mission_config['iniO2']  = self.str2bool(config['Sampling_scripts']['Oxybase'])
        mission_config['iniAcc'] = self.str2bool(config['Sampling_scripts']['ACC_100Hz'])

        return mission_config


    def delete_data_xmt_status_pickle(self):
        """Delete the Data Transmit Status Pickle File"""
        if os.path.exists(data_xmt_status_pickle_file):
            os.remove(data_xmt_status_pickle_file)
            print('[OK] Data Transmit Status Pickle File Removed.')
        else:
            print("[OK] Data Transmit Status Pickle File Already Removed or Does Not Exist.")


    def flash(self,num_flashes, ton, toff):
        """Flash the sampling LED Ring

        Parameters
        ----------
        num_flashes : number of flashes
        ton : Flash on time in milliseconds
        toff : Flash off time milliseconds

        Returns:
        --------
        none

        Example: Generate 2 flashes, 250ms on time, 250ms off time
        
            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            minion_tools.strobe(2,250,250)

        Example: Simply illuminates the LED Ring for 2 seconds

            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            minion_tools.strobe(1,2000,0)

        Example: Dimmable Setting

            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            minion_tools.strobe(100,5,5)#Dim by 50%
        
        """
        #Setup the pin - eventually move this to its own method
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(light, GPIO.OUT)
        
        for val in range(num_flashes):
            GPIO.output(light, 1)
            time.sleep(ton/1000)
            #If we have done the requisite number of flashes,
            #no need for the final off time.
            if val == num_flashes - 1:
                break
            GPIO.output(light, 0)
            time.sleep(toff/1000)
            
        #Finally, turn off the LED Ring    
        GPIO.output(light, 0)

    def write_data_file_header(self,data_type,file_path_name,file_name,samp_rate,iniP30,iniP100,iniTmp):
        """Write Header Record to Pressure & Temperature Data File

        Parameters
        ----------
        data_type : Data Type - INI:$02, TML:$03, FIN:$04
        file_path_name : Full path and name of the data file
        file_name : Name of data file
        samp_rate : Sample Rate
        iniP30 : Sensor Enabled - 30Bar Pressure Sensor
        iniP100 : Sensor Enabled - 100Bar Pressure Sensor
        iniTmp : Sensor Enabled - Temperature Sensor

        Returns:
        --------
        none
        """

        with open(file_path_name,"a+") as file:

            file.write(data_type) #Write Data Type Identifier
            file.write("," + file_name)  #Write the file name
            file.write("," + str(samp_rate))  #Write the sample rate

            if iniP30 == True:
                #file.write("Pressure(dbar),Temp(C)")
                file.write(",Pressure(dbar*1000),Temp(C*100)")  #Meta-Record for fixed field Press and Temp

            if iniP100 == True:
                #file.write("Pressure(dbar),Temp(C)")
                file.write(",Pressure(dbar*1000),Temp(C*100)")  #Meta-Record for fixed field Press and Temp

            if iniTmp == True:
                #file.write(", TempTSYS01(C)")
                file.write(",TempTSYS01(C*100)")
        
        
        
