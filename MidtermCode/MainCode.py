import RPi.GPIO as GPIO
import time
from datetime import datetime
import Adafruit_ADS1x15
import lcddriver


from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.virtual import viewport, sevensegment

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

LEDpin = 7
GPIO.setup(LEDpin,GPIO.OUT)
p = GPIO.PWM(LEDpin,1000)
p.start(0)


adc = Adafruit_ADS1x15.ADS1115()
cd = lcddriver.lcd()

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=1)
seg = sevensegment(device)

#clean the past output
f = open('/home/egco/Desktop/raw.txt','w')
f.close()

GAIN = 1
status = ""

while True:
    #Read value from FSR sensor
    value = adc.read_adc(0,gain=GAIN)
    print(value)
    
    #Display value in 7-segment
    seg.text = str(value)
    
    #Display value at line 1 in LCD
    cd.lcd_display_string("value: "+str(value),1)
    
    #Condition for LED and LCD display text (My customized CONDITION)
    """
    LOW : less than 10000
    MEDIUM : 10000-20000
    HIGH: more than 20000
    """
    if(value < 10000):
        status = "Low"
        if(value < 2000):
            p.ChangeDutyCycle(0)
        else:
            p.ChangeDutyCycle(25)
        
    elif(value >= 10000 and value <= 20000):
        status = "Medium"
        p.ChangeDutyCycle(50)
    elif(value > 20000):
        status = "High"
        if(value > 25000):
            p.ChangeDutyCycle(100)
        else:
            p.ChangeDutyCycle(75)
            
    #Display into the line 2 of LCD
    cd.lcd_display_string("status: "+status,2)
    
    #Create File at the Desktop
    f = open('/home/egco/Desktop/raw.txt','a')
    
    output = "value: " + str(value) + " status: " + status + "\n"
    print(output)
    f.write(output)
    f.close()
    
    time.sleep(0.2)
    cd.lcd_clear()
