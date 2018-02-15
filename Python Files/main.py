from machine import Pin, I2C
import network
import json
import time
import machine
from umqtt.simple import MQTTClient

# setup sensor and ESP8266 and the needed variables
i2cport = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
i2cport.writeto(0x1E, bytearray([0x02, 0x00]))  # set the register in the continous measurement mode
ledgreen1 = Pin(13, Pin.OUT)                    # right led/mum led
ledred = Pin(14, Pin.OUT)                       # middle led/dad led
ledgreen2 = Pin(12, Pin.OUT)                    # left led/kid led

threshold = 0   # detect a change only if the value of the change is bigger than the average fluctation (=threshold)
sensitivity = 5	# how much bigger is set by sensitivity
mumhome = False
dadhome = False
kidhome = False
mum_dict = {}
dad_dict = {}
kid_dict = {}
nokeys_dict = {}

def datapull():
    # datapull updates the data_dictionary with the last readings from the x,z,y axes registers and returns it
    xMSB = i2cport.readfrom_mem(0x1E, 0x03, 1)
    xLSB = i2cport.readfrom_mem(0x1E, 0x04, 1)
    zMSB = i2cport.readfrom_mem(0x1E, 0x05, 1)
    zLSB = i2cport.readfrom_mem(0x1E, 0x06, 1)
    yMSB = i2cport.readfrom_mem(0x1E, 0x07, 1)
    yLSB = i2cport.readfrom_mem(0x1E, 0x08, 1)

    data_dictionary = {}
    data_dictionary["x"] = data_formatting(xMSB, xLSB)
    data_dictionary["y"] = data_formatting(yMSB, yLSB)
    data_dictionary["z"] = data_formatting(zMSB, zLSB)
    return data_dictionary

def data_formatting (aMSB, aLSB):
    # the function converts the raw data from twos complement and avoid the divide by zero error
    # the returned value will have units in Gauss
    a_raw = aMSB + aLSB
    a = int.from_bytes(a_raw, 'big')
    if a > 0x7fff:
        a = a - 0x10000
    if a == 0:
        a = a + 0.0001
    return a

def threshold_calc():
    # this function calcluates the average fluctuation over 10 readings and sets it as a threshold to detect change
    global threshold
    data_dictionary = {}
    data_dictionary_old = {}
    i = 10
    j = i
    data_dictionary_old = datapull()
    time.sleep(0.2)

    # computes the percentage difference between successive readings for all axes to calculate average fluctuations
    while (i > 0):
        data_dictionary = datapull()
        tot_change = tot_percent_change (data_dictionary_old, data_dictionary)
        if (threshold == 0):
            threshold = tot_change                                      # set threshold = tot_change for first run only
        threshold = ((((threshold)*(j-i+1)) + tot_change)/(1+(j-i+1)))  # computes the cumulative average
        i = i-1
        time.sleep(0.2)
        data_dictionary_old = data_dictionary                           # updates the values

def calibration():
    # this function takes the reading from they keys in some position and records the values for later detection
    # the lights in the corresponding positions turn on letting the user know which position is being calibrated
    # the user needs to hang the key in the corresponding position for it to record value
    # waiting_time sets how long should it wait (for user to hang the keys) before recording value (to avoid unstable magnetic field)
    global mum_dict
    global dad_dict
    global kid_dict
    global nokeys_dict
    waiting_time = 7

    print("calibration initiated, please wait")
    time.sleep(2)
    nokeys_dict = data_averaging()
    print("calibrate mum's keys")
    ledgreen1.on()
    time.sleep(7)
    mum_dict = data_averaging()
    ledgreen1.off()
    print("calibrate dad's keys")
    ledred.on()
    time.sleep(7)
    dad_dict = data_averaging()
    ledred.off()
    print("calibrate kid's keys")
    ledgreen2.on()
    time.sleep(7)
    kid_dict = data_averaging()
    ledgreen2.off()

    print("calibration has ended")
    led_blink() # the led wil blink to let user know that it has finished calibrating
    time.sleep(3)

def led_blink():
    ledgreen1.on()
    ledgreen2.on()
    ledred.on()
    time.sleep(0.3)
    ledgreen1.off()
    ledgreen2.off()
    ledred.off()

def data_averaging():
    #this function returns an average for each axis after 10 readings
    data_dictionary = {}
    averaged_data_dictionary = {}
    i = 10
    j = i

    while (i > 0):
        time.sleep(0.2)
        data_dictionary = datapull()
        #set the average readings to current reading only if we are at the first run of the loop, then calculates the cumulative average
        if (i == j):
            averaged_data_dictionary = data_dictionary
        else:
            averaged_data_dictionary["x"] = (((j-i)*averaged_data_dictionary["x"])+(data_dictionary["x"]))/(j-i+1)
            averaged_data_dictionary["y"] = (((j-i)*averaged_data_dictionary["y"])+(data_dictionary["y"]))/(j-i+1)
            averaged_data_dictionary["z"] = (((j-i)*averaged_data_dictionary["z"])+(data_dictionary["z"]))/(j-i+1)
        i = i - 1
    return averaged_data_dictionary

def tot_percent_change (v1, vref):
    # returns the percentage change in each axis between v1 and vref
    x_change = abs((v1["x"]-vref["x"])/v1["x"])
    y_change = abs((v1["y"]-vref["y"])/v1["y"])
    z_change = abs((v1["z"]-vref["z"])/v1["z"])
    return (x_change + y_change + z_change)

def networkconnect():
    # connects to the EEERover
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if=network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect('EEERover', 'exhibition')

def brokerconnect(Json):
    # formats the message and publish it to the MQTT broker
    m_id=machine.unique_id()
    client = MQTTClient(m_id, '192.168.0.10')
    client.connect()
    client.publish('esys/stripes', bytes(Json, 'utf-8'))
    client.disconnect()


data_diction = {}
data_diction_old = {}
networkconnect()
calibration()
threshold_calc()
led_blink() # let the user know that the device is in action
data_diction_old = datapull()

# the code is done such that it registers three states using the calibration function
# after which, if it detects a change, it compares the new measured value with the reference values
# finally, it adjust the who is home variables by checking which of the reference values is most similar to current values
# this means that when putting keys for detection, it needs to in the same position as done during calibration to produce the same magnetic field values

while True:
    data_diction = datapull()
    tot_change = tot_percent_change (data_diction_old, data_diction)
    # detects if any changes have occured and computes who it is
    if (tot_change > (threshold*sensitivity)):
        # computes the difference from the calibrated reference values and current values
        print ("change has been detected")
        mum_tot_change = tot_percent_change (data_diction, mum_dict)
        dad_tot_change = tot_percent_change (data_diction, dad_dict)
        kid_tot_change = tot_percent_change (data_diction, kid_dict)
        nokeys_tot_change = tot_percent_change (data_diction, nokeys_dict)
        # set the state to whichever state with the least error
        if (mum_tot_change == min(mum_tot_change, dad_tot_change, kid_tot_change, nokeys_tot_change)):
            mumhome = True
            dadhome = False
            kidhome = False
        elif (dad_tot_change == min(mum_tot_change, dad_tot_change, kid_tot_change, nokeys_tot_change)):
            mumhome = False
            dadhome = True
            kidhome = False
        elif (kid_tot_change == min(mum_tot_change, dad_tot_change, kid_tot_change, nokeys_tot_change)):
	    kidhome = True
            mumhome = False
            dadhome = False
        else:
            mumhome = False
            dadhome = False
            kidhome = False
    data_diction_old = data_diction
    led_blink() #signals when the computation has ended

    #sets up the led display and the json message to be sent
    jsonDictMsg = {}
    if (kidhome):
        jsonDictMsg["kid"] = "home"
        ledgreen2.on()
    else:
        jsonDictMsg["kid"] = "away"
        ledgreen2.off()
    if (dadhome):
        jsonDictMsg["dad"] = "home"
        ledred.on()
    else:
        jsonDictMsg["dad"] = "away"
        ledred.off()
    if (mumhome):
        jsonDictMsg["mum"] = "home"
        ledgreen1.on()
    else:
        jsonDictMsg["mum"] = "away"
        ledgreen1.off()

    jsonData = {"data":[{'person':key,"where":value} for key,value in jsonDictMsg.items()]}
    jsonDump = json.dumps(jsonData)
    print(jsonDump)
    brokerconnect(jsonDump)
    time.sleep(7)
