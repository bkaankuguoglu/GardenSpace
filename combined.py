from garden_space_client import GardenSpaceClient
import random
from time import sleep
from grovepi import *
import requests
import time
import datetime
import grovepi
import smtplib

#Sensor ports
led = 4
threshold = 10
light_sensor = 2
moisture_sensor = 0
moisture_sensor2 = 1
dht_sensor_port = 7
dht_sensor_type = 0
grovepi.pinMode(light_sensor,"INPUT")
grovepi.pinMode(led,"OUTPUT")

aws_host = "http://52.65.30.143:9000/senddata"
aws_host_getdata = "http://52.65.30.143:9000/getdata"

sleep_time = 600 # in seconds, how often it checks the sensors

#Email Sync
server = smtplib.SMTP('smtp.gmail.com', 587)
server.ehlo()
server.starttls()

config = open("/home/pi/Desktop/GS/config.cfg", "r+")
user_email = config.readline()
user_email = "".join(user_email.split())
if not user_email:
    user_email =  raw_input("Enter your email: ") # input() for python 3
    config.write(user_email)
config.close()

#Next, log in to the server
server.login("gardenspacebot", "G4rdenspace")

# boolean to check whether an email has been sent in the past 24 Hours
sent_email = False
start_day = datetime.date
current_day = start_day
while True:
        try:       
            current_day = datetime.date
            if sent_email and current_day > start_day:
                sent_email = False
            #Moisture sensor
            moisture1 = grovepi.analogRead(moisture_sensor)
            print (moisture1)
            time.sleep(.5)
            if moisture1 < 650 and not sent_email:
                server.sendmail("gardenspacebot@gmail.com", user_email, "\n Your GardenSpace needs water, please give your pants a light spray.")
                sent_email = True

            #Moisture sensor2
            moisture2 = grovepi.analogRead(moisture_sensor2)
            print (moisture2)
            time.sleep(.5)
            if moisture2 < 620 and not sent_email:
                server.sendmail("gardenspacebot@gmail.com", user_email, "\n Your GardenSpace needs a water, please give your pants a water at the roots.")
                sent_email = True

            #Temperature / humidity
            time.sleep(.5)
            [ temp,hum ] = dht(dht_sensor_port,dht_sensor_type)
            print "temp =", temp, "C\thumidity =", hum,"%"
            temperature = str(temp)
    	    humidity = str(hum)
            # T > 35
            if temp > 35 and not sent_email:
                server.sendmail("gardenspacebot@gmail.com", user_email, "\n The outside temperature is so high that it may harm your plant.")
                sent_email = True
            # T < 0
            if temp < 0 and not sent_email:
                server.sendmail("gardenspacebot@gmail.com", user_email, "\n The outside temperature is so low that it may harm your plant.")
                sent_email = True

            #Light sensor
            light_value = grovepi.analogRead(light_sensor)
            resistance = (float)(1023 - light_value) * 10 / light_value
            if resistance > threshold:
                    grovepi.digitalWrite(led,1)
            else:
                    grovepi.digitalWrite(led,0)
            print ("light_value =", light_value, " resistance =", resistance)
            time.sleep(.5)
            if light_value < 0 and not sent_email:
                server.sendmail("gardenspacebot@gmail.com", user_email, "\n Your GardenSpace needs light!")
                sent_email = True

            requests.post(aws_host, data ={'gardenspace_id' : 1,
                                           'temp' : temperature,
                                           'hum' : humidity,
                                           'moist1' : moisture1,
                                           'moist2' : moisture2,
                                           'light' : light_value,
                                           'plant_category_id' : 1,
                                           'user_user_id' : 1,
                                           'user_location_location_id' : 2600
                                           })

            #Wait sleep_time seconds until checking sensors again

            r = requests.post(aws_host_getdata, data ={'gardenspace_id' : 1,
                                           'temp' : temperature,
                                           'hum' : humidity,
                                           'moist1' : moisture1,
                                           'moist2' : moisture2,
                                           'light' : light_value,
                                           'plant_category_id' : 1,
                                           'user_user_id' : 1,
                                           'user_location_location_id' : 2600
                                           });
            print(r.json());
            time.sleep(sleep_time)
	except (IOError, TypeError) as e:
            print "Error"
