import cv2
import numpy as np
import time
import ctypes
import win32gui
import win32con
import win32api
from PIL import ImageGrab
import threading

# Assuming you have a config file (config.py) with IS_CONTRAST and csgo_img_dimension defined
from config import *

# Global variable to communicate between threads
current_frame = None

def grab_window(window_title='Counter-Strike 2', game_resolution=(1024, 768), SHOW_IMAGE=False):
    try:
        cs_window = win32gui.FindWindow(None, window_title)

        if cs_window != 0:
            win32gui.ShowWindow(cs_window, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(cs_window)

            left, top, right, bottom = win32gui.GetClientRect(cs_window)
            left, top = win32gui.ClientToScreen(cs_window, (left, top))
            right, bottom = win32gui.ClientToScreen(cs_window, (right, bottom))

            # Adjust these offsets based on your needs
            offset_height_top = 135  # Adjust as needed
            offset_height_bottom = 135  # Adjust as needed
            offset_sides = 100  # Adjust as needed

            left += offset_sides
            top += offset_height_top
            right -= offset_sides
            bottom -= offset_height_bottom

            screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
            img = np.array(screenshot)

            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            if IS_CONTRAST:
                contrast = 1.5
                brightness = 1.0
                img = cv2.addWeighted(img, contrast, img, 0, brightness)

            img_small = cv2.resize(img, csgo_img_dimension[::-1])

            if SHOW_IMAGE:
                target_width = 800
                scale = target_width / img_small.shape[1]
                dim = (target_width, int(img_small.shape[0] * scale))
                resized = cv2.resize(img_small, dim, interpolation=cv2.INTER_AREA)
                cv2.imshow('resized', resized)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    raise KeyboardInterrupt  # Raise KeyboardInterrupt to stop the script

            return img_small

    except win32gui.error:
        pass  # Ignore window not found error

    return None

def update_frame(window_title):
    global current_frame
    while True:
        frame = grab_window(window_title)
        if frame is not None:
            current_frame = frame
        time.sleep(0.01)  # Adjust the delay as needed

def show_gui():
    global current_frame
    cv2.namedWindow("CS2_GUI", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("CS2_GUI", 800, 600)
    while True:
        if current_frame is not None:
            cv2.imshow("CS2_GUI", current_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

def main():
    window_title = 'Counter-Strike 2'

    # Start the thread to continuously update the frame
    update_thread = threading.Thread(target=update_frame, args=(window_title,))
    update_thread.daemon = True
    update_thread.start()

    # Show the GUI window
    show_gui()

if __name__ == "__main__":
    main()
