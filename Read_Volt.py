import spidev
import time

delay = 0.5
ldr_channel = 0  #Using channel 0 of the chip

#Create SPI
spi = spidev.SpiDev()

#Opening SPI_PORT 0,and SPI_DEVICE 0
spi.open(0,0)

def readadc(num):
    if adcnum > 7 or adcnum < 0:
        return -1
    r = spi.xfer([1, 8+adcnum << 4, 0])
    data = ((r[1]&3)<<8 + r[2])
    return data

while True:
    for i in range(8):
        Sum=0
        Sum2=0
        ldr_value=readadc(i)
        if ldr_value != 0:
            result = ldr_value/1024;
            Sum=Sum+10
            while result != (ldr_value%1023):
                result = result/1024
                Sum = Sum + 10
                if Sum > 1024:
                    break
                
            result = ldr_value%1023
            while result != 1:
                result = result/2
                Sum2 = Sum2 + 1
                if Sum2 > 1024:
                    break

        vout = ((Sum + Sum2) * 5.0)/1024
        vin = vout / 0.2 #(75/300 + 75)
        print ("_______________________")
        print ("LDR Value:" + str(vin) + " " + str(i))
        time.sleep(delay)
