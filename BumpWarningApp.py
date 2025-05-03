# Imports
#-------------------------------------------------------------------------------
import math
import TestFirebase as TF
import serial               #import serial pacakge
from time import sleep
import sys                  #import system package
import RPi.GPIO as GPIO
import time
import TestWarning as TW
import threading

# Initialization
#-----------------------------------------------------------------------------
gpgga_info = "$GPGGA,"
ser = serial.Serial ("/dev/ttyAMA0")              #Open port with baud rate
GPGGA_buffer = 0
NMEA_buff = 0
lat_in_degrees = 0
long_in_degrees = 0
currentLocation={'0':0.0,'1':0.0}
counter=0 
BumpCounter=1
BumpData={"PuplicId":1,"Location":"24324.2343,23432.397","Status":False}


# Set the GPIO mode
GPIO.setmode(GPIO.BCM)

#set warning to false
GPIO.setwarnings(False)
	
# Set the GPIO pin as output
GPIO.setup(13, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#Apply PWM to the led and buzzer
led=GPIO.PWM(12,2)
buzzer=GPIO.PWM(13,2)




# Functions Implemetation
#--------------------------------------------------------

def GPS_Info():
    global NMEA_buff
    global lat_in_degrees
    global long_in_degrees
    nmea_time = []
    nmea_latitude = []
    nmea_longitude = []
    nmea_time = NMEA_buff[0]                    #extract time from GPGGA string
    nmea_latitude = NMEA_buff[1]                #extract latitude from GPGGA string
    nmea_longitude = NMEA_buff[3]               #extract longitude from GPGGA string
    TF.updateData("181020","Location",nmea_latitude + "," + nmea_longitude)
    lat = float(nmea_latitude)                  #convert string into float for calculation
    longi = float(nmea_longitude)               #convertr string into float for calculation
    location={'0':lat,'1':longi}
    
    print("NMEA Time: ", nmea_time,'\n')
    print ("NMEA Latitude:", nmea_latitude,"NMEA Longitude:", nmea_longitude,'\n')
    return location
    
#convert raw NMEA string into degree decimal format   
def convert_to_degrees(raw_value):
    decimal_value = raw_value/100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value))/0.6
    position = degrees + mm_mmmm
    position = "%.4f" %(position)
    return position

def calculateDistance(lat1,lon1,lat2,lon2):
    dx = (lon2 - lon1)#*math.cos(lat1)
    dy = lat2 - lat1
    distance = math.sqrt(dx * dx + dy * dy)
    return distance
    
def ExtINT_Callback(channel):
    global BumpCounter
    global currentLocation
    global BumpData
    print(TF.bumpFlag)
    BumpData["PuplicId"] = BumpCounter
    BumpData["Location"] = str(currentLocation['0']) + "+" + str(currentLocation['1'])
    BumpData["Status"] = True
    TF.addBump(BumpData)
    bumpTimer=threading.Timer(3,TF.bumpRelease,[BumpCounter])
    bumpTimer.start()
    TF.bumpFlag=1
    BumpCounter=BumpCounter+1
    
GPIO.add_event_detect(23, GPIO.FALLING, callback=ExtINT_Callback, bouncetime=200)

# wait for GPS to work
time.sleep(6)

while True:
	received_data = (str)(ser.readline())                   #read NMEA string received
	GPGGA_data_available = received_data.find(gpgga_info)   #check for NMEA GPGGA string                 
	if (GPGGA_data_available>0):
		GPGGA_buffer = received_data.split("$GPGGA,",1)[1]  #store data coming after "$GPGGA," string 
		NMEA_buff = (GPGGA_buffer.split(','))               #store comma separated data in buffer
		currentLocation=GPS_Info()
		if counter == 0:
			firstLocation = currentLocation
			# Strart the timer
			start_time = time.perf_counter()
		elif counter == 5:
			fifthLocation = currentLocation
			# Get the timer value
			end_time = time.perf_counter()
			# Calculate the time difference in huors 
			time_difference = (end_time - start_time) /60*60
			# Calculate the distance
			distance = calculateDistance(firstLocation['0'],firstLocation['1'],fifthLocation['0'],fifthLocation['1']) 
			print(distance)
			# Calculate the speed
			speed = distance/time_difference
			TF.updateData("181020","Speed",str(speed))
			counter =-1
			
		else:
			pass
		
		if  ((TF.readStatus(BumpCounter) == True)and(TF.bumpFlag!=1)):
		    TW.SetWarning(3,led,buzzer)
		counter=counter+1
            
