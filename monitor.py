from ctypes import wintypes
from win32api import GetSystemMetrics, ChangeDisplaySettings
import ctypes
import pywintypes
import win32con
import json
import os

# --- Variables ---
RES_FILE = "resolutions.json"
BASE_RES = [1920, 1080]
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
dc = user32.GetDC(0)


# --- Res Managment ---
def load_resolutions():
    if os.path.exists(RES_FILE):
        with open(RES_FILE, "r") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return [
        [1920, 1080],
        [1680, 1050],
        [1440, 1080],
        [1280, 960]
    ]

def save_resolutions(res_list):
    with open(RES_FILE, "w") as f:
        json.dump(res_list, f, indent=2)

def select_resolution(res_list, current_res):
    print(f"Current resolution: {current_res[0]}x{current_res[1]}")
    print("Choose a resolution:")
    print("0 - Custom (e.g. 1440x1080)")
    for idx, res in enumerate(res_list, 1):
        print(f"{idx} - {res[0]}x{res[1]}")
    choice = input("Enter your choice: ").strip()

    if choice == '0':
        return get_custom_resolution(res_list)
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(res_list):
                return res_list[idx]
            print(f"Invalid choice. Please use 0 for custom or 1-{len(res_list)} for presets.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    exit(1)

def get_custom_resolution(res_list):
    res_input = input("Enter custom resolution (WIDTHxHEIGHT): ").strip().lower()
    try:
        width, height = map(int, res_input.split('x'))
        new_res = [width, height]
        save_custom = input("Save this resolution for future use? (Y/N): ").strip().lower()
        if save_custom == 'y' and new_res not in res_list:
            res_list.append(new_res)
            save_resolutions(res_list)
        return new_res
    except ValueError:
        print("Invalid format. Please use WIDTHxHEIGHT (e.g., 1440x1080)")
        exit(1)

def apply_resolution(new_res):
    print(f'Changing resolution to {new_res[0]}x{new_res[1]}...')
    devmode = pywintypes.DEVMODEType()
    devmode.PelsWidth = new_res[0]
    devmode.PelsHeight = new_res[1]
    devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT
    ChangeDisplaySettings(devmode, 0)


# --- Gamma ---
def set_gamma_ramp(gamma):
    gamma_array = (wintypes.WORD * 256)()
    for i in range(256):
        value = int(((i / 255.0) ** (1.0 / gamma)) * 65535 + 0.5)
        gamma_array[i] = min(max(value, 0), 65535)
    ramp_array = (wintypes.WORD * (256 * 3))(*gamma_array, *gamma_array, *gamma_array)
    gdi32.SetDeviceGammaRamp(dc, ctypes.byref(ramp_array))

def prompt_gamma():
    gamma_choice = input("Change gamma to (0 = 1.5, 1 = default): ").strip()
    if gamma_choice == '0':
        set_gamma_ramp(1.5)
    else:
        try:
            gamma_value = float(gamma_choice)
            set_gamma_ramp(gamma_value)
        except ValueError:
            print("Invalid gamma value. Skipping gamma adjustment.")


# --- Exec ---
resX, resY = GetSystemMetrics(0), GetSystemMetrics(1)
res_list = load_resolutions()
selected_res = select_resolution(res_list, [resX, resY])

if selected_res == [resX, resY]:
    print(f"The selected resolution {selected_res[0]}x{selected_res[1]} is already active. Resetting to {BASE_RES[0]}x{BASE_RES[1]}...")
    selected_res = BASE_RES

apply_resolution(selected_res)
prompt_gamma()
