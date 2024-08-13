from pynput import mouse, keyboard
from time import time
import json
import math
import os

# declare listeners globally so they can be stopped
mouse_listener = None
keyboard_listener = None
start_time = None
unreleased_keys = []
input_events = []
is_recording_macro = False  # Flag to indicate macro recording status

class EventType:
    KEYDOWN = 'keyDown'
    KEYUP = 'keyUp'
    CLICK = 'click'
    MOVE = 'move'

# Minimum delay between key events
MIN_KEY_DELAY = 0.05
last_key_event_time = 0

def record():
    global is_recording_macro
    is_recording_macro = True  # Set the flag to indicate recording
    run_listeners()
    print("Recording duration: {} seconds".format(elapsed_time()))
    global input_events

    # Remove ESC key from json file
    filtered_events = [event for event in input_events if event['button'] != "Key.esc"]

    print(json.dumps(filtered_events))

    # determine script directory and ensure recordings directory exists
    script_dir = os.path.dirname(__file__)
    recordings_dir = os.path.join(script_dir, 'recordings')
    if not os.path.exists(recordings_dir):
        os.makedirs(recordings_dir)

    # determine the next available filename
    output_filename = get_next_filename(recordings_dir)

    # write the output to a file
    filepath = os.path.join(recordings_dir, '{}.json'.format(output_filename))
    with open(filepath, 'w') as outfile:
        json.dump(filtered_events, outfile, indent=4)
    print(f"Recording saved to {filepath}")

    is_recording_macro = False  # Clear the flag to indicate recording is complete

def get_next_filename(directory):
    existing_files = os.listdir(directory)
    existing_numbers = [int(f.split('_')[1].split('.')[0]) for f in existing_files if f.startswith('macro_') and f.endswith('.json')]
    if existing_numbers:
        next_number = max(existing_numbers) + 1
    else:
        next_number = 1
    return f"macro_{next_number}"

def elapsed_time():
    global start_time
    return time() - start_time

def record_event(event_type, event_time, button=None, pos=None):
    global input_events, last_key_event_time

    if event_type == EventType.KEYDOWN or event_type == EventType.KEYUP:
        # Ensure the event is at least MIN_KEY_DELAY apart
        if (event_time - last_key_event_time) < MIN_KEY_DELAY:
            event_time = last_key_event_time + MIN_KEY_DELAY

        # Update last_key_event_time to current event time
        last_key_event_time = event_time

    input_events.append({
        'time': event_time,
        'type': event_type,
        'button': str(button),
        'pos': pos
    })

    if event_type == EventType.CLICK or event_type == EventType.MOVE:
        print('{} at pos {} at {}'.format(event_type, pos, event_time))
    else:
        print('{} on {} at {}'.format(event_type, button, event_time))

def on_press(key):
    global unreleased_keys
    if key in unreleased_keys:
        return
    else:
        unreleased_keys.append(key)

    key_char = getattr(key, 'char', str(key))
    record_event(EventType.KEYDOWN, elapsed_time(), key_char)

def on_release(key):
    global unreleased_keys
    try:
        unreleased_keys.remove(key)
    except ValueError:
        print(f'ERROR: {key} not in unreleased_keys')

    key_char = getattr(key, 'char', str(key))
    record_event(EventType.KEYUP, elapsed_time(), key_char)

    # stop listeners with the escape key
    if key == keyboard.Key.esc:
        stop_listeners()

def on_click(x, y, button, pressed):
    if not pressed:
        record_event(EventType.CLICK, elapsed_time(), button, (x, y))

def on_move(x, y):
    record_event(EventType.MOVE, elapsed_time(), pos=(x, y))

def run_listeners():
    global mouse_listener, keyboard_listener
    # Collect mouse input events
    mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move)
    mouse_listener.start()

    # Collect keyboard inputs
    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()
    
    global start_time
    start_time = time()

    try:
        mouse_listener.join()
        keyboard_listener.join()
    except KeyboardInterrupt:
        print("Keyboard Interrupt detected. Stopping...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        stop_listeners()

def stop_listeners():
    global mouse_listener, keyboard_listener
    if mouse_listener is not None:
        mouse_listener.stop()
    if keyboard_listener is not None:
        keyboard_listener.stop()

if __name__ == "__main__":
    record()
