import pickle
import sys
import os

pickle_file_name = "/home/pi/Documents/Minion_scripts/final_samp_status.pkl"

msg1 = "Final Sample Status Flag Reset Utility  "
msg2 = "  - False : Final Samples Not Performed"
msg3 = "  - True  : Final Samples Were Performed"

print("-"*len(msg1))
print(msg1)
print(msg2)
print(msg3)
print("-"*len(msg1))

try:
    #Read out the current value
    with open(pickle_file_name,"rb") as pickle_file_fid:
        final_sample_status_flag = pickle.load(pickle_file_fid)
    print("final_sample_status_flag current value: " + str(final_sample_status_flag))

except:
    sys.exit(os.path.basename(__file__) + ": sampcount.pk1 file not found or open failed")


#Reset the value to False
with open(pickle_file_name,"wb") as pickle_file_fid:
    print("Resetting Final Sampling Status Flag to False...")
    final_sample_status_flag = False
    pickle.dump(final_sample_status_flag, pickle_file_fid)

#Verify
with open(pickle_file_name,"rb") as pickle_file_fid:
    final_sample_status_flag_verify = pickle.load(pickle_file_fid)
    
print("Verify final_sample_status_flag: " + str(final_sample_status_flag))

if final_sample_status_flag == False:
    print("Verify OK")
else:
    print("Error: final_sample_status_flag is not False!")
