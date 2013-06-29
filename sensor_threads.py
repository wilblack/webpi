import os
import threading
import glob
import time
import urllib2
from datetime import datetime as dt

class TaskThread(threading.Thread):
    """Thread that executes a task every N seconds"""
    
    def __init__(self, interval):
        self._interval = interval
        threading.Thread.__init__(self)       
        self._finished = threading.Event()
        
    def setInterval(self, interval):
        """Set the number of seconds we sleep between executing our task"""
        self._interval = interval
    
    def shutdown(self):
        """Stop this thread"""
        self._finished.set()
    
    def run(self):
        while 1:
            if self._finished.isSet(): return
            self.task()
            
            # sleep for interval or until shutdown
            self._finished.wait(self._interval)
    
    def task(self):
        """
        The task done by this thread - override in your own subclass.

        """
        raise Exception("Implement this method in your sublcass.")

        
class DS18B20Thread(TaskThread):
    
    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'

    API_URL = "http://localhost:8888/api"
    THINGSPEAK_URL = "http://api.thingspeak.com/update"
    THINGSPEAK_KEY = "HJIOA6601OOPCQX6"

    def __init__(self, interval):
        os.system("modprobe w1-gpio")
        os.system("modprobe w1-therm")
        super(DS18B20Thread, self).__init__(interval)

    def task(self):
        print(self.read_temp())


    def read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self):
        lines = self.read_temp_raw()
        
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            now = dt.now()
            now  = now.strftime("%H-%M-%S")
            
            # Send over temp_c 
            _url = "%s?id=degc&value=%s&timestamp=%s" %(self.API_URL, temp_c, now)   
            res = self.send(_url)

            # Send over temp_f 
            _url = "%s?id=degf&value=%s&timestamp=%s" %(self.API_URL, temp_f, now)   
            res = self.send(_url)
            
            # Send to thingspeak.com
            _url = "%s?key=%s&field1=%s&field2=%s&field3=%s" %(self.THINGSPEAK_URL, self.THINGSPEAK_KEY, temp_c, temp_f, now)
            res = self.send(_url)

            return temp_c, temp_f

    def send(self, url):  
        print url
        req = urllib2.Request(url)      
        res = None
        try:
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, error:
            print "HTTP Error"
        except urllib2.URLError, error:
            print "URL Error"

        return res