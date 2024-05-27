from machine import Pin, Timer, I2C
from time import sleep, ticks_ms, ticks_diff
from pico_i2c_lcd import I2cLcd

I2C_ADDR     = 63
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

class Tastatura:
    def __init__(self):
        self.matrica = [['1', '2', '3', 'A'],
                        ['4', '5', '6', 'B'],
                        ['7', '8', '9', 'C'],
                        ['*', '0', '#', 'D']]

        self.rows = [Pin(i, Pin.OUT) for i in [26, 22, 21, 20]]
        self.cols = [Pin(i, Pin.IN, Pin.PULL_DOWN) for i in [19, 18, 17, 16]]
        
        self.string = ""
        self.cntr = 0
        self.currentRow = 0
        self.debounce = ticks_ms()
        self.potvrdjeno = False

        for row in self.rows:
            row.value(0)
            
        for i in range(4):
            self.cols[i].irq(handler = self.colPress, trigger = Pin.IRQ_RISING)

        self.i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
        self.lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
            
    def colPress(self):
        currentCol = 0
        for i in range(4):
            if self.cols[i].value() == 1: # cita broj pritisnute kolone
                currentCol = i
                break
        if ticks_diff(ticks_ms(), self.debounce) < 200: # debouncing
            return
        else:
            self.debounce = ticks_ms()
            
        if currentCol == 3: # provjerava 4. kolonu, tj. ako je uneseno A, B, C ili D
            if self.currentRow == 2: # pritisnuto C
                self.cntr -= 1
                self.string = self.string[:-1]
                self.lcd.clear()
                self.lcd.putstr(self.string)
            else: # pritisnuto A, B ili D
                return
        if self.currentRow == 3: 
            if currentCol == 0: # pritisnuta *
                return
            elif currentCol == 2 and len(self.string) == 4: # pritisnut #
                self.potvrdjeno = True
                return
                
        self.string += self.matrica[self.currentRow][currentCol]
        
        self.lcd.clear()
        self.lcd.putstr(self.string)
        
        self.cntr = (self.cntr + 1) % 4
        if self.cntr == 0:
            self.string = ""
    
    def rowFun(t):
        self.rows[self.currentRow].value(0)
        self.currentRow = (self.currentRow + 1) % 4
        self.rows[self.currentRow].value(1)

    def ocitaj(self):
        tim = Timer(period = 50, mode = Timer.PERIODIC, callback = rowFun)
        
        
class TastController:
    def __init__(self):
        self.tastatura = Tastatura()
        self.tastatura.ocitaj()

    def getUnos(self):
        self.lcd.clear()
        self.lcd.putstr("Unesite broj \n sobe:")
        while True:
            if self.potvrdjeno == True:
                self.potvrdjeno = False
                self.cntr = 0
                
                self.lcd.clear()
                self.lcd.putstr("Unijeli ste: \n"+ self.string)
                
                result = self.tastatura.string
                self.tastatura.string = ""
                sleep(2)
                self.lcd.clear()
                self.lcd.putstr("Prisloniti\n karticu...")
                return result  