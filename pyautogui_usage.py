import pyautogui as gui
import time
import os



# firefox location: (34, 68)
# littlefield bookmark: (298, 134)
# Data button: (197, 642)

def main():
   print('Let\'s do this!')
   gui.moveTo(34, 68)
   gui.click(34, 68)
   time.sleep(30)
   gui.click(298, 134)
   time.sleep(30)
   gui.click(187, 642)
   time.sleep(15)
   gui.hotkey('alt', 'f4')

