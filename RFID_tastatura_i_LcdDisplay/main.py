from machine import Pin, Timer,I2C
from mfrc522 import MFRC522
from time import sleep, ticks_ms, ticks_diff
from tastatura import Tastatura, TastController
from pico_i2c_lcd import I2cLcd

I2C_ADDR     = 63
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

soba = 0
tastatura = TastController()
debounce = ticks_ms()
       
button = Pin(0, Pin.IN)

i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

def unosSobe():
    global soba, sobaUnesena, debounce, tastatura

    print("pokrenuto")
    if ticks_diff(ticks_ms(), debounce) < 300: # debouncing
        return
    else:
        debounce = ticks_ms()

    soba = tastatura.getUnos()

while True:
    if button.value():
        unosSobe()
        print(soba) 
        lcd.clear()
        if soba == -1:
            lcd.putstr("Pogresan unos!")
            sleep(2)
            lcd.clear()
            lcd.putstr("Kliknite taster\ni unesite opet")
        else:
            lcd.putstr("Unijeli ste: \n" + soba)  
            #sleep(3) 
    sleep(0.1)
