from machine import Pin, Timer,I2C
from mfrc522 import MFRC522
from time import sleep, ticks_ms, ticks_diff
from tastatura import Tastatura, TastController
from pico_i2c_lcd import I2cLcd

# Konstante za potrebe displeja
I2C_ADDR     = 63
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

# Inicijalizacija dva RFID citaca
reader1 = MFRC522(spi_id=0,sck=2,miso=4,mosi=3,cs=1,rst=5) 			# Recepcija - konfiguracija sobe
reader2 = MFRC522(spi_id=1,sck=10,miso=12,mosi=11,cs=9,rst=13)		# Pri ulasku u sobu

soba = 0						# Uneseni broj sobe
tastatura = TastController()
debounce = ticks_ms()
       
button = Pin(0, Pin.IN)			# Pritiskom na button se zapocinje unos na tastaturi

# LED koje signaliziraju ispravnost ocitane kartice pri ulasku u sobu
red = Pin(7, Pin.OUT)
green = Pin(6, Pin.OUT)
red.value(0)
green.value(0)

# Inicijalizacija displeja
i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

# Mapa u kojoj su pohranjeni parovi soba i odgovarajucih kartica
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

# Funkcija koja se poziva pritiskom na button, cime se zapocinje unos broja sobe
def unosSobe():
    global soba, sobaUnesena, debounce, tastatura

    if ticks_diff(ticks_ms(), debounce) < 300: 			# Debouncing
        return
    else:
        debounce = ticks_ms()

    soba = tastatura.getUnos()

while True:
    red(0)
    green(0)
    
    # Pritisnut taster - konfiguracija sobe
    if button.value():
        unosSobe() 
        lcd.clear()
        if soba == -1:							# Ukoliko je iz funkcije za ocitanje unosa vraceno -1, unos nije validan
            lcd.putstr("Pogresan unos!")
            sleep(2)
            lcd.clear()
            lcd.putstr("Kliknite taster\ni unesite opet")
        else:									# Validan unos, zapocinje se konfiguracija sobe
            lcd.putstr("Unijeli ste: \n" + soba)  
            sleep(2)
            lcd.clear()
            lcd.putstr("Prislonite\nkarticu: \n") 
            reader1.init()
            stat1 = False

            sleep(2)
            lcd.clear()
            (stat1, tag_type1) = reader1.request(reader1.REQIDL)		# Ocitava se da li je prislonjena kartica na RFID citac 
            
            if stat1 == reader1.OK:
                (stat, uid) = reader1.SelectTagSN()						# Ocitava se ID prislonjene kartice
                if stat == reader1.OK:
                    card = int.from_bytes(bytes(uid),"little",False) 
                    karticeISobe[int(soba)] = card						# Unesenoj sobi se dodjeljuje ID prislonjene kartice
                    
                    lcd.putstr("Povezano!")
                    sleep(1)
                    lcd.clear()
                    lcd.putstr("Uklonite\nkarticu!")
                    sleep(1)
                    lcd.clear()
    
    # Nije pritisnut taster - ispituje se da li se pokusava pristupiti sobi
    else:
        reader2.init()
        (stat2, tag_type2) = reader2.request(reader2.REQIDL)			# Ocitava se da li je prislonjena kartica na RFID citac 
   
        if stat2 == reader2.OK:
            (stat, uid) = reader2.SelectTagSN()							# Ocitava se ID prislonjene kartice
            if stat == reader2.OK:
                card = int.from_bytes(bytes(uid),"little",False)

                if karticeISobe[1000] == card:							# Ako je prislonjena kartica odgovarajuca, pali se zelena LED
                    red.value(0)
                    green.value(1)
                    sleep(2)
                    green.value(0)
                else:													# Prislonjena kartica nije odgovarajuca, pali se crvena LED
                    red.value(1)
                    green.value(0)
                    sleep(2)
                    red.value(0)
    sleep(0.1)
