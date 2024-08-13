import pyautogui
from time import sleep, perf_counter
import os
import json
import random

def main():
    initializePyAutoGUI()
    countdownTimer()
    playActions("macro_1.json")
    print("Done")

def initializePyAutoGUI():
    pyautogui.FAILSAFE = True

def countdownTimer():
    print("Starting", end="", flush=True)
    for i in range(0, 3):
        print(".", end="", flush=True)
        sleep(1)
    print("Go")

def load_all_macros(directory_path):
    macros = {}
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            macro_name = os.path.splitext(filename)[0]
            filepath = os.path.join(directory_path, filename)
            try:
                with open(filepath, 'r') as jsonfile:
                    macros[macro_name] = json.load(jsonfile)
            except json.JSONDecodeError:
                print(f"Error decoding JSON from {filepath}.")
    return macros

def playActions(filename):
    script_dir = os.path.dirname(__file__)
    filepath = os.path.join(script_dir, 'recordings', filename)
    with open(filepath, 'r') as jsonfile:
        data = json.load(jsonfile)
        start_time = perf_counter()
        
        for action in data:
            action_time = start_time + action['time']
            
            # Wait until it's time for the next action
            current_time = perf_counter()
            sleep_time = action_time - current_time
            if sleep_time > 0:
                sleep(sleep_time)
            
            if action['button'] == 'Key.esc':
                break

            action_start_time = perf_counter()

            if action['type'] == 'keyDown':
                key = convertKey(action['button'])
                pyautogui.keyDown(key)
                print("keyDown on {}".format(key))
            elif action['type'] == 'keyUp':
                key = convertKey(action['button'])
                pyautogui.keyUp(key)
                print("keyUp on {}".format(key))
            elif action['type'] == 'click':
                click_start_time = perf_counter()
                pyautogui.click(action['pos'][0], action['pos'][1], duration=0.05)  # Reduced duration
                click_end_time = perf_counter()
                print(f"Click action took {click_end_time - click_start_time:.2f} seconds")
                print("click on {}".format(action['pos']))
            elif action['type'] == 'move':
                moveMouseHumanLike(action['pos'][0], action['pos'][1])

            action_end_time = perf_counter()
            # Track the time taken by each action
            action_duration = action_end_time - action_start_time
            print(f"Action took {action_duration:.2f} seconds")

        total_time = perf_counter() - start_time
        print(f"Playback completed in {total_time:.2f} seconds")

def moveMouseHumanLike(x, y):
    start_x, start_y = pyautogui.position()
    distance = math.hypot(x - start_x, y - start_y)
    steps = max(1, int(distance / 10))
    step_x = (x - start_x) / steps
    step_y = (y - start_y) / steps

    for _ in range(steps):
        start_x += step_x
        start_y += step_y
        pyautogui.moveTo(int(start_x), int(start_y))
        sleep(0.001)  # Slight sleep for smoother movement

def convertKey(button):
    PYNPUT_SPECIAL_CASE_MAP = {
        'alt_l': 'altleft',
        'alt_r': 'altright',
        'alt_gr': 'altright',
        'caps_lock': 'capslock',
        'ctrl_l': 'ctrlleft',
        'ctrl_r': 'ctrlright',
        'page_down': 'pagedown',
        'page_up': 'pageup',
        'shift_l': 'shiftleft',
        'shift_r': 'shiftright',
        'num_lock': 'numlock',
        'print_screen': 'printscreen',
        'scroll_lock': 'scrolllock',
    }

    cleaned_key = button.replace('Key.', '')
    if cleaned_key in PYNPUT_SPECIAL_CASE_MAP:
        return PYNPUT_SPECIAL_CASE_MAP[cleaned_key]
    return cleaned_key

if __name__ == "__main__":
    main()
