from machine import Pin, Timer, I2C
from time import sleep, ticks_ms, ticks_diff
from pico_i2c_lcd import I2cLcd

# Konstante za potrebe displeja
I2C_ADDR     = 63
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

# Tasteri 'A', 'B', 'D' i '*' nisu dozvoljeni, 'C' brise posljednji uneseni karakter, '#' potvrdjuje cetverocifreni unos
class Tastatura:
    def __init__(self):
        self.matrica = [['1', '2', '3', 'A'],
                        ['4', '5', '6', 'B'],
                        ['7', '8', '9', 'C'],
                        ['*', '0', '#', 'D']]

        self.rows = [Pin(i, Pin.OUT) for i in [16, 17, 18, 19]]
        self.cols = [Pin(i, Pin.IN, Pin.PULL_DOWN) for i in [20, 21, 22, 26]]
       
        self.string = ""		# Varijabla u koju se pohranjuje unos 
        self.currentRow = 0		# Varijabla za trenutno aktivni red
        self.currentCol= 0		# Varijabla za trenutno pritisnutu kolonu
        self.debounce = ticks_ms()
        self.potvrdjeno = False
        self.pogresanUnos = False
        self.timer = None

        for row in self.rows:	# Ugaseni svi redovi na pocetku
            row.value(0)
           
        for i in range(4):		# Hardverski interrupti koji se aktiviraju pritiskom na taster u odredjenoj koloni
            self.cols[i].irq(handler = self.colPress, trigger = Pin.IRQ_RISING)

        # Postavke displeja
        self.i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
        self.lcd = I2cLcd(self.i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
        self.lcd.hal_backlight_on()
           
    # Callback funkcija za pritisak na taster, vezana za interrupte na kolonama
    def colPress(self, Pin):
        if ticks_diff(ticks_ms(), self.debounce) < 350: # Debouncing
            return
        else:
            self.debounce = ticks_ms()

        for i in range(4):
            if self.cols[i].value() == 1: # U atribut currentCol se pohranjuje broj pritisnute kolone
                self.currentCol = i
                break
           
        # Unos vise od 4 cifre uzastopno, koji se ne prihvata
        if len(self.string) == 4 and self.matrica[self.currentRow][self.currentCol] != 'C' and self.matrica[self.currentRow][self.currentCol] != '#':
            self.timer.deinit()		# Deinicijalizacija timer-a, s ciljem obustave pokusaja unosa
            self.pogresanUnos = True
            return
           
        # Slucaj ako je pritisnut taster iz 4. kolone
        elif self.currentCol == 3: 
            if self.currentRow == 2: # pritisnuto 'C' - brise se posljednji uneseni karakter i ispisuje unos na displeju
                self.string = self.string[:-1]         
                self.lcd.clear()
                self.lcd.putstr(self.string)
                return
               
            # Prekida se unos ukoliko je pritisnut neki od tastera 'A', 'B' ili 'D'
            else: 
                self.timer.deinit()
                self.pogresanUnos = True
                return
           
        # Slucaj kada je pritisnut taster '*' ili '#'
        elif self.currentRow == 3:
            if self.currentCol == 0 or (self.currentCol == 2 and len(self.string) != 4): 		# Pritisnuta '*' ili '#' prije nego sto su unesene 4 cifre,
                                                                                                # unos nije validan
                self.timer.deinit()
                self.pogresanUnos = True
                return
            elif self.currentCol == 2 and len(self.string) == 4: # Pritisnut '#' - ispravan unos 4 cifre, koji se potvrdjuje
                self.timer.deinit()
                self.potvrdjeno = True
                return
         
        # Ukoliko je unos ispravan, cifra se dodaje na string, koji se ispisuje na displej
        if not self.pogresanUnos:
            self.string += self.matrica[self.currentRow][self.currentCol]
            self.lcd.clear()
            self.lcd.putstr(self.string)
   
    # Callback funkcija za timer, svakih 50ms se pali jedan od cetiri reda s ciljem ocitanja pritiska tastera
    def rowFun(self, Pin):
        self.rows[self.currentRow].value(0)
        self.currentRow = (self.currentRow + 1) % 4
        self.rows[self.currentRow].value(1)

    # Zapocinje novi unos na tastaturi
    def ocitaj(self):
        if self.timer == None:
            self.timer = Timer(period = 50, mode = Timer.PERIODIC, callback = self.rowFun)		# Kreiranje timer-a za redove pri prvom pritisku na button
        else:
            self.timer.init(period = 50, mode = Timer.PERIODIC, callback = self.rowFun)			# Reinicijalizacija u slucaju naknadnih unosa

# Koristi se iz glavnog programa za upravljanje tastaturom i ocitanje unosa, sadrzi instancu klase Tastatura
class TastController:
    def __init__(self):
        self.tastatura = Tastatura()

    def getUnos(self):				# Poziva se iz glavnog programa, nakon pritiska na button
        self.tastatura.lcd.clear()
        self.tastatura.lcd.putstr("Unesite broj \n sobe:")
        
        self.tastatura.ocitaj()		# Poziva se funkcija ocitaj() i inicijalizira timer za paljenje redova, kako bi se pritisnuti tasteri mogli registrovati
        self.string = ""
        self.tastatura.pogresanUnos = False
        self.tastatura.potvrdjeno = False
        while True:
            # Unos se ne prihvaca, a u glavni program se vraca -1 kao znak greske
            if self.tastatura.pogresanUnos:
                self.tastatura.string = ""
                return -1
               
            # Unos se prihvaca i u glavni program se vraca uneseni broj sobe   
            if self.tastatura.potvrdjeno:
                result = self.tastatura.string
                self.tastatura.string = ""
                return result 
