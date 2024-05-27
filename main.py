from machine import Pin, I2C
from mfrc522 import MFRC522
from tastatura import Tastatura, TastController
from time import sleep
import utime
from pico_i2c_lcd import I2cLcd
       
# MOSI na SPI TX (spi0 -> 3,7,19; spi1 -> 11,15)
# SCK na SPI SCK (spi0 -> 2,6,18; spi1 -> 10,14)
# MISO na SPI RX (spi0 -> 0,4,16; spi1 -> 8,12)
# CS/SDA na bilo koji (GP1 SDA on most RFID-RC522 boards)
# RST na bilo koji
reader1 = MFRC522(spi_id=0,sck=2,miso=4,mosi=3,cs=1,rst=5) # cs = sda
reader2 = MFRC522(spi_id=1,sck=10,miso=12,mosi=11,cs=9,rst=13)

button = Pin(0, Pin.IN)
 
red = Pin(7, Pin.OUT)
green = Pin(6, Pin.OUT)

tastatura = TastController()

karticeISobe = {
  "1000": 0,
  "1001": 0,
  "1002": 0,
  "2000": 0,
  "2001": 0,
  "2002": 0,
  "3000": 0,
  "3001": 0,
  "3002": 0
}
 
while True:
    if button.value() == 1: # konfiguracija na recepciji
        soba = tastatura.getUnos()
        
        reader1.init()
        (stat1, tag_type1) = reader1.request(reader.REQIDL)
    
        if stat1 == reader.OK: 
            (stat, uid) = reader.SelectTagSN()
            if stat == reader.OK:
                card = int.from_bytes(bytes(uid),"little",False)
                
                karticeISobe[soba] = card

    else: # ulazak u sobu
        reader2.init()
        (stat2, tag_type2) = reader2.request(reader.REQIDL)
    
        if stat2 == reader.OK: 
            (stat, uid) = reader.SelectTagSN()
        if stat == reader.OK:
            card = int.from_bytes(bytes(uid),"little",False)
            if karticeISobe["1000"] == card:
                red.value(0)
                green.value(1)
            else:
                red.value(1)
                green.value(0)
    sleep(0.1)