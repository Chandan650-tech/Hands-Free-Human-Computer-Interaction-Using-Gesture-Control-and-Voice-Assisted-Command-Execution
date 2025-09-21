from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading
import cv2
import pyautogui
import numpy as np
import math
import screen_brightness_control as sbc
from cvzone.HandTrackingModule import HandDetector

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gesture_logs = []
tracking_thread = None
running = False
prev_action = ""
prev_x, prev_y = 0, 0
brightness_level = 50  # initial brightness

def detect_gestures():
    global running, gesture_logs, prev_action, prev_x, prev_y, brightness_level

    cap = cv2.VideoCapture(0)
    detector = HandDetector(detectionCon=0.8, maxHands=1)
    screen_w, screen_h = pyautogui.size()
    cam_w, cam_h = 640, 480
    cap.set(3, cam_w)
    cap.set(4, cam_h)

    while running:
        success, img = cap.read()
        if not success:
            break

        hands, img = detector.findHands(img, flipType=False)
        if hands:
            hand = hands[0]
            lm_list = hand['lmList']
            fingers = detector.fingersUp(hand)

            index_finger = lm_list[8]
            thumb = lm_list[4]
            pinky = lm_list[20]

            # Faster cursor movement
            x = np.interp(index_finger[0], (0, cam_w), (0, screen_w))
            y = np.interp(index_finger[1], (0, cam_h), (0, screen_h))
            smooth_x = int(prev_x + (x - prev_x) * 0.8)
            smooth_y = int(prev_y + (y - prev_y) * 0.8)
            prev_x, prev_y = smooth_x, smooth_y

            # 1. Move Cursor
            if fingers == [0, 1, 0, 0, 0]:
                pyautogui.moveTo(smooth_x, smooth_y)
                gesture_logs.append("Move Cursor")

            # 2. Left Click
            elif fingers == [0, 1, 1, 0, 0] and prev_action != "left_click":
                pyautogui.click()
                prev_action = "left_click"
                gesture_logs.append("Left Click")

            # 3. Right Click
            elif fingers == [0, 0, 0, 0, 1] and prev_action != "right_click":
                pyautogui.click(button='right')
                prev_action = "right_click"
                gesture_logs.append("Right Click")

            # 4. Double Click
            elif fingers == [0, 1, 1, 1, 0] and prev_action != "double_click":
                pyautogui.doubleClick()
                prev_action = "double_click"
                gesture_logs.append("Double Click")

            # 5. Scroll Up
            elif fingers == [0, 1, 1, 1, 1]:
                pyautogui.scroll(40)
                gesture_logs.append("Scroll Up")

            # 6. Scroll Down
            elif fingers == [1, 1, 1, 1, 0]:
                pyautogui.scroll(-40)
                gesture_logs.append("Scroll Down")

            # 7. Drag and Drop
            elif fingers == [1, 0, 0, 0, 1]:
                pyautogui.mouseDown()
                pyautogui.moveTo(smooth_x, smooth_y)
                pyautogui.mouseUp()
                gesture_logs.append("Drag and Drop")

            # 8. Multiple Selection
            elif fingers == [0, 1, 0, 0, 1] and prev_action != "select_multi":
                pyautogui.keyDown('shift')
                pyautogui.click()
                pyautogui.keyUp('shift')
                prev_action = "select_multi"
                gesture_logs.append("Multiple Selection")

            # 9. Volume Control
            elif fingers == [1, 0, 0, 0, 0]:
                dist = math.dist(index_finger, thumb)
                if dist > 80:
                    pyautogui.press("volumeup")
                    gesture_logs.append("Volume Up")
                elif dist < 50:
                    pyautogui.press("volumedown")
                    gesture_logs.append("Volume Down")

            # 10. Brightness Control
            elif fingers == [0, 0, 0, 0, 1]:
                dist = math.dist(pinky, thumb)
                try:
                    if dist > 80 and brightness_level < 100:
                        brightness_level += 10
                        try:
                            sbc.set_brightness(brightness_level)
                        except:
                            pyautogui.hotkey("fn", "f3")
                        gesture_logs.append("Brightness Up")
                    elif dist < 50 and brightness_level > 0:
                        brightness_level -= 10
                        try:
                            sbc.set_brightness(brightness_level)
                        except:
                            pyautogui.hotkey("fn", "f2")
                        gesture_logs.append("Brightness Down")
                except Exception as e:
                    gesture_logs.append(f"Brightness Error: {e}")

            # 11. Switch Tab
            elif fingers == [1, 1, 0, 0, 1] and prev_action != "alt_tab":
                pyautogui.hotkey("alt", "tab")
                prev_action = "alt_tab"
                gesture_logs.append("Switch Tab")

            # 12. Reset Previous Action
            elif fingers == [1, 1, 1, 1, 1]:
                prev_action = ""

        # Optional preview
        # cv2.imshow("Cam", img)
        # if cv2.waitKey(1) & 0xFF == 27:
        #     break

    cap.release()
    cv2.destroyAllWindows()

@app.get("/start")
def start_tracking():
    global running, tracking_thread
    if not running:
        running = True
        tracking_thread = threading.Thread(target=detect_gestures)
        tracking_thread.start()
        return {"message": "Gesture tracking started"}
    else:
        return {"message": "Gesture tracking already running"}

@app.get("/stop")
def stop_tracking():
    global running
    if running:
        running = False
        return {"message": "Gesture tracking stopped"}
    else:
        return {"message": "Tracking not running"}

@app.get("/logs")
def get_logs():
    return {"logs": gesture_logs[-50:]}

@app.get("/refresh")
def refresh_logs():
    global gesture_logs
    gesture_logs = []
    return {"message": "Logs refreshed"}
