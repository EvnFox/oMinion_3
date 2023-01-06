#!/usr/bin/env python3

import glob
import pickle
import sys
import os
import time
import random
import minsat
from minsat import MinSat
sys.path.insert(0,'/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox

#Number of times to try sending the data before sleeping
MAX_TRIES = 5

#Enable/Disable sending data from operating modes
XMT_INI = True
XMT_TLP = True
XMT_FIN = True

#Transmit Data Status Pickle File Name
data_xmt_status_pickle_name = '/home/pi/Documents/Minion_scripts/data_xmt_status.pickle'

#Minsat Board Settings
gps_port = "/dev/ttySC0"
gps_baud = 9600
modem_port = "/dev/ttySC1"
modem_baud = 19200

#Initializations
detect_data_files_flag = False   #Flag indicating if valid data files were found


#Displays the returned struct from sbd_send_file
def display_sbd_resp_struct(resp_struct):
    print("=" * 50)
    print("File Name: " + str(resp_struct.file_name))
    print("File Open Success: " + str(resp_struct.file_open_success))
    print("File Size: " + str(resp_struct.file_size))
    print("File Position Starting Point: " + str(resp_struct.start_file_loc))
    print("Number of SBD Sessions Required: " +str(resp_struct.xmt_num_sbd_req))
    print("Number of SBD Sessions Successfully Transmitted: " + str(resp_struct.xmt_num_sbd_success))
    print("Completed Sending File: " + str(resp_struct.xmt_file_complete))
    print("Number of Bytes Transmitted: " + str(resp_struct.xmt_num_bytes)) #Note that the transmitted number of bytes can be larger than the file size if num_hearder_lines > 0
    print("Current File Location: " + str(resp_struct.curr_file_loc))

#Displays the returned struct from sbd_send_position
def display_gps_resp_struct(ret_info):
    print("="*50)
    print("Valid Position: " + str(ret_info.valid_position))
    print(
        "Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}".format(
            ret_info.tm_mon,  # Grab parts of the time from the
            ret_info.tm_mday,  # struct_time object that holds
            ret_info.tm_year,  # the fix time.  Note you might
            ret_info.tm_hour,  # not get all data like year, day,
            ret_info.tm_min,  # month!
            ret_info.tm_sec,
        )
    )
    print("Latitude,Longitude: {:.6f},{:06f}".format(ret_info.latitude,ret_info.longitude))
    print("="*50)

#Displays the Key-Value pairs contained in the Data Transmit Status Dictionary
def disp_data_xmt_status_dict(data_xmt_status_dict):
    print("Data Transmit Status:")
    for key in data_xmt_status_dict:
        print("    " + str(key) + ": " + str(data_xmt_status_dict[key]))

#clears all values for all keys in dictionary except for curr_file_name
def clear_data_xmt_status_dict(data_xmt_status_dict,keys):
    data_xmt_status_dict['file_open_success'] = False
    data_xmt_status_dict['file_size'] = 0
    data_xmt_status_dict['xmt_file_complete'] = False
    data_xmt_status_dict['xmt_num_bytes'] = 0
    data_xmt_status_dict['xmt_num_sbd_success'] = 0
    data_xmt_status_dict['xmt_num_sbd_required'] = 0
    data_xmt_status_dict['curr_file_location'] = 0
    data_xmt_status_dict['start_file_location'] = 0
    #Do not need to return anything since the dictionary is accessed from here

#Default values for selected keys in dictionary. Except for curr_file_name & all_files_transmitted
def default_data_xmt_status_dict(data_xmt_status_dict):
    data_xmt_status_dict['num_gps_sent'] = 0
    data_xmt_status_dict['all_files_transmitted'] = False
    data_xmt_status_dict['curr_file_name'] = ''
    data_xmt_status_dict['file_open_success'] = False
    data_xmt_status_dict['file_size'] = 0
    data_xmt_status_dict['xmt_file_complete'] = False
    data_xmt_status_dict['xmt_num_bytes'] = 0
    data_xmt_status_dict['xmt_num_sbd_success'] = 0
    data_xmt_status_dict['xmt_num_sbd_required'] = 0
    data_xmt_status_dict['curr_file_location'] = 0
    data_xmt_status_dict['start_file_location'] = 0
    #Do not need to return anything since the dictionary is accessed from here
    
#Writes the Data Transmit Status Dictionary to the pickle file
def write_pickle_file(fname_pickle,dict_to_write):
    #print("File Name: " + fname_pickle)
    #disp_data_xmt_status_dict(dict_to_write)
    with open(fname_pickle,'wb') as pickle_file_fid:
        #pickle_file_fid = open(fname_pickle,'wb')
        pickle.dump(dict_to_write,pickle_file_fid)
        #pickle_file_fid.close()

#create an empty dictionary with empty values
keys = ['num_gps_sent','all_files_transmitted','curr_file_name', 'file_open_success',\
        'file_size','xmt_file_complete', 'xmt_num_bytes','xmt_num_sbd_success',\
        'xmt_num_sbd_required', 'curr_file_location', 'start_file_location']
data_xmt_status_dict = dict.fromkeys(keys)

#try to open the Data Transmit Status pickle file
try:
    #Try to open the pickle file.  If it exists, read the data out.
    #data_xmt_status_pickle_file = open(data_xmt_status_pickle_name,'rb')
    with open(data_xmt_status_pickle_name,'rb') as data_xmt_status_pickle_file:
        print("\n\rFound pickle file: " + data_xmt_status_pickle_name)
        print("Loading " + data_xmt_status_pickle_name)
        data_xmt_status_dict = pickle.load(data_xmt_status_pickle_file)
        disp_data_xmt_status_dict(data_xmt_status_dict)
except:
    #Could not open the pickle file so it must be the first time through
    print("\n\rCould not find the pickle file.  Creating " + data_xmt_status_pickle_name)
    #Write Default Values for all fields
    data_xmt_status_dict['all_files_transmitted'] = False
    data_xmt_status_dict['curr_file_name'] = ''
    default_data_xmt_status_dict(data_xmt_status_dict) #default states for all other members
    write_pickle_file(data_xmt_status_pickle_name,data_xmt_status_dict)
finally:
    #Now, close the pickle file.
    try:
        data_xmt_status_pickle_file.close()
        print("File Closed: " + data_xmt_status_pickle_name)
    except:
        pass

#disp_data_xmt_status_dict(data_xmt_status_dict) #display for testing

#Load the Minion Configuration
minion_tools = MinionToolbox() #create an instance of MinionToolbox() called minion_tools
minion_mission_config = minion_tools.read_mission_config()
for key in minion_mission_config:
        print("    " + str(key) + ": " + str(minion_mission_config[key]))
#Load the Data Configuration
minion_data_config_dict = minion_tools.read_data_config()

#****** Locate Data Files ******
#Get the file names (with paths).
fnames_with_paths = [] #create an empty list
if XMT_INI == True:  #If configured to transmit the Initial Mode Data File
    fnames_with_paths = fnames_with_paths + glob.glob(minion_data_config_dict['Data_Dir']  + '/minion_data/INI/*_TEMPPRES-INI.txt')
if XMT_TLP == True:  #If configured to transmit the Time-Lapse Mode Data Files
    fnames_with_paths = fnames_with_paths + glob.glob(minion_data_config_dict['Data_Dir']  + '/minion_data/*_TEMPPRES.txt')
if XMT_FIN == True:  #If configured to transmit the Final Mode Data File
    fnames_with_paths = fnames_with_paths + glob.glob(minion_data_config_dict['Data_Dir']  + '/minion_data/FIN/*_TEMPPRES-FIN.txt')

if fnames_with_paths:
    print("Found valid file names that match the search critera.")
    detect_data_files_flag = True
else:
    print("Could not find and valid file names that match the search critera.")
    detect_data_files_flag = False


#Choose if to send a GPS Position or move onto transmitting data
if (data_xmt_status_dict['num_gps_sent'] < 2) or \
   (data_xmt_status_dict['num_gps_sent'] >= 2 and data_xmt_status_dict['all_files_transmitted'] == True) or \
   (detect_data_files_flag == False):
    
    print('Acquire and Transmit a GPS Position')

    #Create an instance of the Minsat class (sets up the Minsat hardware and software)
    m1 = MinSat(gps_port,gps_baud,modem_port,modem_baud)
    
    #Attempt to acquire and transmit a GPS Position
    (success,ret_data) = m1.sbd_send_position(verbose=False,maintain_gps_pwr=True,gps_timeout=120)
    
    if success and ret_data.valid_position:
        print('[OK] GPS Position Acquired and Transmitted to Iridium Successfully.')
        m1.gps_pwr(m1.dev_off)
    elif not success and not ret_data.valid_position:
        print('[FAILURE] Could not acquire a GPS Position. ')
        print('Trying Again...')
        (success,ret_data) = m1.sbd_send_position(verbose=False,maintain_gps_pwr=False,gps_timeout=120)
    elif not success and ret_data.valid_position:
        print('[FAILURE] Could not transmit the acquired position to Iridium')
        print('Trying Again...')
        (success,ret_data) = m1.sbd_send_position(verbose=False,maintain_gps_pwr=False,gps_timeout=120)
        
    if success == True:
        data_xmt_status_dict['num_gps_sent'] += 1
        write_pickle_file(data_xmt_status_pickle_name,data_xmt_status_dict)
    if success == False:
        print('[FAILURE] No Position Available or Could not Transmit to Iridium')

    #Cleanup instance of MinSat
    m1.gps_pwr(m1.dev_off)
    m1.modem_pwr(m1.dev_off)
    del m1

#Transmit Data via the Iridium Constellation  
else:
    print('Data Transmission to Iridium Constellation')

    #print(fnames_with_paths)

    #We need to split up the row elements of the list (fnames_with_paths) based on the backslash
    fnames_with_paths_split = [i.split("/") for i in fnames_with_paths]
    #fnames_with_paths_split = [i.split("\\") for i in fnames_with_paths] #FOR WINDOWS OS!!!

    #Now, just grab the last column which is the actual file name without a path
        #Note: the -1 addresses the last column
    fnames = [row[-1] for row in fnames_with_paths_split]
    print("\n\rList of raw file names without paths:")
    for f in fnames:
        print(f)

    #print('\n\rfnames object type: ' + str(type(fnames))) #just a test line!

    #At this point, we have the file names (fnames) without the path.
    #Let's trust that the list is sorted (for now)

    print("")
    print("Sorting the list of file names based on sample number...")
    #Sort the list based on the sample number.
    #The sample number is the first three digits before the first '-'
    #Therefore, we want to key on element 0 when the name is split.
    sorted_list = fnames
    sorted_list.sort(key = lambda x: x.split('-')[0])

    #A very brute force way of getting the full paths back as part of the sorted file names
    #There must be a better way!!!
    for idx,value in enumerate(sorted_list):
        if value.find('INI') > -1:
            #print('Found Initial Type File.')
            sorted_list[idx] = minion_data_config_dict['Data_Dir']  + '/minion_data/INI/' + sorted_list[idx]
        elif value.find('FIN') > -1:
            #print('Found Final Type File.')
            sorted_list[idx] = minion_data_config_dict['Data_Dir']  + '/minion_data/FIN/' + sorted_list[idx]
        else:
            #print('Found Time-Lapse Type File.')
            sorted_list[idx] = minion_data_config_dict['Data_Dir']  + '/minion_data/' + sorted_list[idx]

    #Print out the sorted list with file names
    for f in sorted_list:
        print(f)

    #sys.exit(os.path.basename(__file__) + ": Stop Here for Testing Only!!!")

    #If all files have been transmitted, no need to go on. Exit the script
    if data_xmt_status_dict['all_files_transmitted'] == True:
        sys.exit(os.path.basename(__file__) + ": All Files Transmitted. Nothing to do.")

    #Assign the first file name and save to the pickle file if this is the first time through
    if not data_xmt_status_dict['curr_file_name']:
        print("Assigning the first file name")
        data_xmt_status_dict['curr_file_name'] = fnames[0]
        write_pickle_file(data_xmt_status_pickle_name,data_xmt_status_dict)

    #disp_data_xmt_status_dict(data_xmt_status_dict) #display for testing

    #Create an instance of the Minsat class (sets up the Minsat hardware and software)
    m1 = MinSat(gps_port,gps_baud,modem_port,modem_baud)

    #Main Transmission Loop
    for idx,val in enumerate(fnames):
        num_tries = 0
        #skip over the file names until we get to the current file name
        #this assumes that the fnames list is now sorted properly
        if val  != data_xmt_status_dict['curr_file_name']:
            pass

        #Start sending from the current file name as listed in the dictionary / pickle file
        elif val == data_xmt_status_dict['curr_file_name']:

            while data_xmt_status_dict['xmt_file_complete'] != True and num_tries < MAX_TRIES:
                print("\n\r")
                print(val)
                print("Attempt Number: " + str(num_tries+1))
                disp_data_xmt_status_dict(data_xmt_status_dict) #display for testing

                print("\n\r")
                print("Sending Data to Iridium Constellation...")
                ret_data = m1.sbd_send_file(data_xmt_status_dict['curr_file_name'],\
                                            verbose=False,\
                                            num_header_lines=0,\
                                            start_file_position=data_xmt_status_dict['curr_file_location'])
                
                ### Update the Data Transmit Status dictionary with return values from sbd_send_file
                data_xmt_status_dict['file_size'] = ret_data.file_size
                data_xmt_status_dict['xmt_file_complete'] = ret_data.xmt_file_complete
                data_xmt_status_dict['xmt_num_bytes'] = ret_data.xmt_num_bytes
                data_xmt_status_dict['xmt_num_sbd_success'] = ret_data.xmt_num_sbd_success
                data_xmt_status_dict['xmt_num_sbd_required'] = ret_data.xmt_num_sbd_req
                data_xmt_status_dict['curr_file_location'] = ret_data.curr_file_loc
                data_xmt_status_dict['start_file_location'] = ret_data.start_file_loc
                write_pickle_file(data_xmt_status_pickle_name,data_xmt_status_dict)

                #Adaptive Retry
                # Only needed if the file did not complete sending
                # Also need to update the number of tries in this case
                if data_xmt_status_dict['xmt_file_complete'] == False:
                    time_to_sleep = random.randint(0,30)
                    print("Adaptive Retry Backoff - " + str(time_to_sleep) + " seconds")
                    time.sleep(time_to_sleep)
                    num_tries += 1

            #data_xmt_status_dict['xmt_file_complete'] = True #just for testing

            print("[DEBUG]" + \
                  "  XMT File Complete: " + str(data_xmt_status_dict['xmt_file_complete']) + \
                  "  Number of Files: " + str(len(fnames)) + \
                  "  idx: " + str(idx))

            #----------------------------------------------------------------------------------------#
            #update the dictionay & the pickle file with the next file name to transmit

            #If the file did not finish transmitting, save the current status to the pickle
            if data_xmt_status_dict['xmt_file_complete'] == False:
                write_pickle_file(data_xmt_status_pickle_name,data_xmt_status_dict)

            #If the current file is done but there are still more files, load the next file name in
            # the list.
            elif data_xmt_status_dict['xmt_file_complete'] == True and idx + 1 <= len(fnames) - 1:
                data_xmt_status_dict['curr_file_name'] = fnames[idx+1]
                print("Clearing the data_xmt_status dictionary & pickle")
                clear_data_xmt_status_dict(data_xmt_status_dict,keys)             
                write_pickle_file(data_xmt_status_pickle_name,data_xmt_status_dict)
                
            #If the current file is complete and the next index is beyond the number of files the
            # current file must be the last file.  We're done!
            elif data_xmt_status_dict['xmt_file_complete'] == True and idx + 1 > len(fnames) - 1:
                print("Last File!")
                data_xmt_status_dict['all_files_transmitted'] = True
                #Write the updated status to the pickle
                write_pickle_file(data_xmt_status_pickle_name,data_xmt_status_dict)
                disp_data_xmt_status_dict(data_xmt_status_dict) #display for testing
            else:
                print("Should not end up here!!!")
            #----------------------------------------------------------------------------------------#
        
print("Exiting xmt_minion_data.py...")
time.sleep(5)
sys.exit()



