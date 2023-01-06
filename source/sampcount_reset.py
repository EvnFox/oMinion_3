import pickle
import sys
import os

pickle_file_name = "/home/pi/Documents/Minion_scripts/sampcount.pkl"

msg1 = "Sample Counter Reset Utility  "

print("-"*len(msg1))
print(msg1)
print("-"*len(msg1))


try:
    #Read out the current value
    with open(pickle_file_name,"rb") as sampcount:
        sampcount = pickle.load(countp)
    print("sampcount current value: " + str(sampcount))

except:
    sys.exit(os.path.basename(__file__) + ": sampcount.pk1 file not found or open failed")


#Reset the value to zero
with open(pickle_file_name,"wb") as countp:
    print("Resetting the Sample Counter to 0...")
    sampcount = 0
    pickle.dump(sampcount, countp)


#Verify
with open(pickle_file_name,"rb") as countp:
    sampcount_verify = pickle.load(countp)
print("Verify sampcount: " + str(sampcount_verify))
if sampcount_verify == 0:
    print("Verify OK")
else:
    print("sampcount is not zero!")
