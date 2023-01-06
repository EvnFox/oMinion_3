import os
import pickle
import sys #for sys.path
sys.path.insert(0,'/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox

#print("\n\rClearing the Sample Counter...")
with open("/home/pi/Documents/Minion_scripts/sampcount.pkl","wb") as countp:
    sampcount = 0
    pickle.dump(sampcount, countp)

#Sets the Final Sample Status Flag to False
#    False : Final Samples Not Performed
#    True  : Final Samples Were Performed
try:
    print("\n\rSetting Final Sample Status Flag to False...")
    with open("/home/pi/Documents/Minion_scripts/final_samp_status.pkl","wb") as final_samp_status_fid:
        final_sample_status_flag = False
        pickle.dump(final_sample_status_flag, final_samp_status_fid)
    print("Done")
except:
    print("Could Not Set the Final Sample Status Flag to False")

#Load the Minion Configuration
minion_tools = MinionToolbox() #create an instance of MinionToolbox() called minion_tools
#Delete the Data Transmit Status Pickle prior to mission start
minion_tools.delete_data_xmt_status_pickle()

time = os.popen('ls /home/pi/Desktop/minion_data/INI/1-*.txt').read()

time = time.strip('/home/pi/Desktop/minion_data/INI/1-')

time = time.strip('_TEMPPRES-INI.txt\n')

num_mem = int(len(os.listdir("/home/pi/Desktop/minion_memory/"))) + 1

save_dir = '/home/pi/Desktop/minion_memory/{}-{}'.format(num_mem, time)

os.system('sudo mkdir {}'.format(save_dir))

os.system('sudo mv /home/pi/Desktop/minion_data/ /home/pi/Desktop/minion_pics/ {}'.format(save_dir))

os.system('sudo cp /home/pi/Desktop/Minion_config.ini {}'.format(save_dir))

os.system('sudo mkdir /home/pi/Desktop/minion_data/ /home/pi/Desktop/minion_pics/')

os.system('sudo mkdir /home/pi/Desktop/minion_data/INI/ /home/pi/Desktop/minion_data/FIN/')

dir_name = save_dir.strip('/home/pi/Desktop/minion_memory/')

print('Files are saved to {}'.format(dir_name))
