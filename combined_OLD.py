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

#Heroku adress'
host = 'gardenspace.herokuapp.com'
port = 80
light_device = 'gardenspace003'
moisture_device = 'gardenspace002'
moisture_device2 = 'gardenspace004'
temp_device = 'gardenspace001'

#Set up GardenSpaceClient
gsc_temp = GardenSpaceClient(host, port, temp_device)
gsc_temp.register_device()
gsc_moist = GardenSpaceClient(host, port, moisture_device)
gsc_moist.register_device()
gsc_moist2 = GardenSpaceClient(host, port, moisture_device2)
gsc_moist.register_device()
gsc_light = GardenSpaceClient(host, port, light_device)
gsc_light.register_device()



sleep_time = 60 # in seconds, how often it checks the sensors

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
            gsc_moist.send_data('moisture', moisture1)
            if moisture1 < 650 and not sent_email:




                server.sendmail("gardenspacebot@gmail.com", user_email, "\n Your GardenSpace needs water!")
                sent_email = True

            #Moisture sensor2
            moisture2 = grovepi.analogRead(moisture_sensor2)
            time.sleep(.5)
            gsc_moist2.send_data('moisture2', moisture2)
            if moisture2 < 650 and not sent_email:
                server.sendmail("gardenspacebot@gmail.com", user_email, "\n Your GardenSpace needs water!")
                sent_email = True

            #Temperature / humidity
            time.sleep(.5)
            [ temp,hum ] = dht(dht_sensor_port,dht_sensor_type)
            print "temp =", temp, "C\thumidity =", hum,"%"
            t = str(temp)
	    h = str(hum)
	    gsc_temp.send_data('temperature', t)
	    gsc_temp.send_data('humidity', h)

            #Light sensor
            light_value = grovepi.analogRead(light_sensor)
            resistance = (float)(1023 - light_value) * 10 / light_value
            if resistance > threshold:
                    grovepi.digitalWrite(led,1)
            else:
                    grovepi.digitalWrite(led,0)
            print ("light_value =", light_value, " resistance =", resistance)
            time.sleep(.5)
            gsc_light.send_data('light', light_value)
            if light_value < 0 and not sent_email:
                server.sendmail("gardenspacebot@gmail.com", user_email, "\n Your GardenSpace needs light!")
                sent_email = True


            #Wait sleep_time seconds until checking sensors again
            time.sleep(sleep_time)
	except (IOError, TypeError) as e:
            print "Error"
