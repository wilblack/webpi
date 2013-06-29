import os
import glob
import time
import urllib2
from datetime import datetime as dt

 
os.system("modprobe w1-gpio")
os.system("modprobe w1-therm")

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
DT = 60*5 # reporting period in seconds


def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    API_URL = "http://192.168.1.140:8888/api"
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        now = dt.now()
        now  = now.strftime("%H-%M-%S")
        
        # Send over temp_c 
        _url = "%s?id=degc&value=%s&timestamp=%s" %(API_URL, temp_c, now)	
        print _url
        req = urllib2.Request(_url)      
        try:
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, error:
            print "HTTP Error"

        # Send over temp_f 
        _url = "%s?id=degf&value=%s&timestamp=%s" %(API_URL, temp_f, now)	
        print _url
        req = urllib2.Request(_url)      
        try:
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, error:
            print "HTTP Error"
        
        # Send to thingspeak.com
        _url = "http://api.thingspeak.com/update?key=HJIOA6601OOPCQX6&field1=%s&field2=%s&field3=%s" %(temp_c, temp_f, now)
        print _url
        req = urllib2.Request(_url)      
        try:
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, error:
            print "HTTP Error"

        return temp_c, temp_f


while True:
    print(read_temp())
    time.sleep(DT)
