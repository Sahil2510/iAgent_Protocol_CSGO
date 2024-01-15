import cv2
import pygetwindow as gw
import pyautogui
import numpy as np
import time

# Assuming you have a config file (config.py) with IS_CONTRAST and csgo_img_dimension defined
from config import *

def grab_window(window_title='Counter-Strike 2', game_resolution=(1024, 768), SHOW_IMAGE=False):
    try:
        cs_window = gw.getWindowsWithTitle(window_title)[0]

        # Check if the window is minimized
        if not cs_window.isMinimized:
            cs_window.activate()

            left, top, width, height = cs_window.left, cs_window.top, cs_window.width, cs_window.height

            # Adjust these offsets based on your needs
            offset_height_top = 135
            offset_height_bottom = 135
            offset_sides = 100

            left += offset_sides
            top += offset_height_top
            width -= 2 * offset_sides
            height -= offset_height_top + offset_height_bottom

            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

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

    except IndexError:
        pass  # Ignore window not found error
    except gw.PyGetWindowException as e:
        pass  # Ignore PyGetWindowException

    return None

def fps_capture_test():
    time_start = time.time()
    n_grabs = 20000
    window_title = 'Counter-Strike 2'

    try:
        for i in range(n_grabs):
            img_small = grab_window(window_title, game_resolution=(1024, 768), SHOW_IMAGE=False)

            if img_small is not None:
                target_width = 800
                scale = target_width / img_small.shape[1]
                dim = (target_width, int(img_small.shape[0] * scale))
                resized = cv2.resize(img_small, dim, interpolation=cv2.INTER_AREA)
                cv2.imshow('resized', resized)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

    except KeyboardInterrupt:
        pass  # Handle KeyboardInterrupt to gracefully exit the loop

    cv2.destroyAllWindows()
    time_end = time.time()
    avg_time = (time_end - time_start) / n_grabs
    fps = 1 / avg_time
    print('avg_time', np.round(avg_time, 5))
    print('fps', np.round(fps, 2))
    return

if _name_ == "_main_":
    fps_capture_test()
