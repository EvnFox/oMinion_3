from zipfile import ZipFile
import os
import time

def get_all_files(directory):

    paths = []

    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root,filename)
            paths.append(filepath)

    return paths

def clear_log():
    with open('/var/www/html/livefeed.txt','w') as output:
        output.write('')


data_dir = "/home/pi/Desktop/minion_data/"
pics_dir = "/home/pi/Desktop/minion_pics/"
conf = "/home/pi/Desktop/Minion_config.ini"

endmessage = "Files Compressed!"

data_paths = get_all_files(data_dir)
pics_paths = get_all_files(pics_dir)

paths = data_paths + pics_paths

paths.append(conf)

clear_log()

with ZipFile('MinionXXX.zip','w') as zip:
    for file in paths:
        filename = file.replace('/home/pi/Desktop','')
        zip.write(file,filename)
        with open('/var/www/html/livefeed.txt','a+') as output:
            output.write(file)
            output.write('<br><br>')

with open('/var/www/html/livefeed.txt','w') as output:
    output.write(endmessage)
    output.write("<br><br>")

time.sleep(10)

clear_log()
