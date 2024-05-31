from machine import Pin, Timer,I2C
from mfrc522 import MFRC522
from time import sleep, ticks_ms, ticks_diff
from tastatura import Tastatura, TastController
from pico_i2c_lcd import I2cLcd

I2C_ADDR     = 63
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

reader1 = MFRC522(spi_id=0,sck=2,miso=4,mosi=3,cs=1,rst=5) # cs = sda
reader2 = MFRC522(spi_id=1,sck=10,miso=12,mosi=11,cs=9,rst=13)

soba = 0
tastatura = TastController()
debounce = ticks_ms()
       
button = Pin(0, Pin.IN)

red = Pin(7, Pin.OUT)
green = Pin(6, Pin.OUT)
red.value(0)
green.value(0)

i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

karticeISobe = {
  1000: 0,
  1001: 0,
  1002: 0,
  2000: 0,
  2001: 0,
  2002: 0,
  3000: 0,
  3001: 0,
  3002: 0
}

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
            sleep(2)
            lcd.clear()
            lcd.putstr("Prislonite\nkarticu: \n") 
            reader1.init()
            stat1 = False

            sleep(2)
            lcd.clear()
            (stat1, tag_type1) = reader1.request(reader1.REQIDL)
            
            if stat1 == reader1.OK:
                (stat, uid) = reader1.SelectTagSN()
                if stat == reader1.OK:
                    card = int.from_bytes(bytes(uid),"little",False) # type: ignore
                    karticeISobe[int(soba)] = card 
                    print(karticeISobe[int(soba)])
                    lcd.putstr("Povezano!")
                    sleep(1)
                    lcd.clear()
                    lcd.putstr("Uklonite\nkarticu!")

    else:
        reader2.init()
        (stat2, tag_type2) = reader2.request(reader2.REQIDL)
   
        if stat2 == reader2.OK:
            (stat, uid) = reader2.SelectTagSN()
            if stat == reader2.OK:
                card = int.from_bytes(bytes(uid),"little",False)
                print(card)
                print(karticeISobe[1000])
                if karticeISobe[1000] == card:
                    red.value(0)
                    green.value(1)
                else:
                    red.value(1)
                    green.value(0)
    sleep(0.1)
