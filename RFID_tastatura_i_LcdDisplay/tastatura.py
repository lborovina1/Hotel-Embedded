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

        self.rows = [Pin(i, Pin.OUT) for i in [16, 17, 18, 19]]
        self.cols = [Pin(i, Pin.IN, Pin.PULL_DOWN) for i in [20, 21, 22, 26]]
       
        self.string = ""
        self.currentRow = 0
        self.currentCol= 0
        self.debounce = ticks_ms()
        self.potvrdjeno = False
        self.pogresanUnos = False
        self.timer = None

        for row in self.rows:
            row.value(0)
           
        for i in range(4):
            self.cols[i].irq(handler = self.colPress, trigger = Pin.IRQ_RISING)

        self.i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
        self.lcd = I2cLcd(self.i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
        self.lcd.hal_backlight_on()
           
    def colPress(self, Pin):
        if ticks_diff(ticks_ms(), self.debounce) < 350: # debouncing
            return
        else:
            self.debounce = ticks_ms()

        for i in range(4):
            if self.cols[i].value() == 1: # cita broj pritisnute kolone
                self.currentCol = i
                break
           
        if len(self.string) == 4 and self.matrica[self.currentRow][self.currentCol] != 'C' and self.matrica[self.currentRow][self.currentCol] != '#':
            self.timer.deinit()
            self.pogresanUnos = True
            return
           
        elif self.currentCol == 3: # provjerava 4. kolonu, tj. ako je uneseno A, B, C ili D
            if self.currentRow == 2: # pritisnuto C
                self.string = self.string[:-1]
                print(self.string)
                self.lcd.clear()
                self.lcd.putstr(self.string)
                return
               
            else: # pritisnuto A, B ili D
                self.timer.deinit()
                self.pogresanUnos = True
                return
           
        elif self.currentRow == 3:
            if self.currentCol == 0 or (self.currentCol == 2 and len(self.string) != 4): # pritisnuta * ili # kad ne treba
                self.timer.deinit()
                self.pogresanUnos = True
                return
            elif self.currentCol == 2 and len(self.string) == 4: # pritisnut #
                self.timer.deinit()
                self.potvrdjeno = True
                return
         
        if not self.pogresanUnos:
            self.string += self.matrica[self.currentRow][self.currentCol]
            print(self.string)
            self.lcd.clear()
            self.lcd.putstr(self.string)
   
    def rowFun(self, Pin):
        self.rows[self.currentRow].value(0)
        self.currentRow = (self.currentRow + 1) % 4
        self.rows[self.currentRow].value(1)

    def ocitaj(self):
        if self.timer == None:
            self.timer = Timer(period = 50, mode = Timer.PERIODIC, callback = self.rowFun)
        else:
            self.timer.init(period = 50, mode = Timer.PERIODIC, callback = self.rowFun)
       
class TastController:
    def __init__(self):
        self.tastatura = Tastatura()

    def getUnos(self):

        self.tastatura.lcd.clear()
        self.tastatura.lcd.putstr("Unesite broj \n sobe:")
        
        self.tastatura.ocitaj()
        self.string = ""
        self.tastatura.pogresanUnos = False
        self.tastatura.potvrdjeno = False
        while True:
            if self.tastatura.pogresanUnos:
                self.tastatura.string = ""
                return -1
               
            if self.tastatura.potvrdjeno:
                result = self.tastatura.string
                self.tastatura.string = ""
                return result 
