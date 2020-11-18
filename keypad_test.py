import time
import RPi.GPIO as GPIO
from keypad import keypad
 
GPIO.setwarnings(False)
 
if __name__ == '__main__':
    # Initialize the keypad
    kp = keypad(columnCount = 3)
 
    ###### Wait for user to input digit code ######
    sequence = []
    for i in range(4):
        digit = None
        while digit == None:
            digit = kp.getKey()
        sequence.append(digit)
        print(digit)
        time.sleep(0.4)
 
    # Check digit code
    print(sequence)
    if sequence == [1, 2, 3, '#']:
        print ("code accepted")
    else:
        print("code invalid")