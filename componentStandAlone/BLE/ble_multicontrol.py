import sys
import ble_discover
#from componentClasses.powerstation import BluettiAC180 as AC180
import asyncio
import json
import signal
import logging

from typing import Any, Dict, Optional, Tuple, List
from shelly import ShellyDevice

# ============================
# Shelly Configuration Constants
# ============================
SHELLY_GATT_SERVICE_UUID = "5f6d4f53-5f52-5043-5f53-56435f49445f"
RPC_CHAR_DATA_UUID = "5f6d4f53-5f52-5043-5f64-6174615f5f5f"
RPC_CHAR_TX_CTL_UUID = "5f6d4f53-5f52-5043-5f74-785f63746c5f"
RPC_CHAR_RX_CTL_UUID = "5f6d4f53-5f52-5043-5f72-785f63746c5f"
ALLTERCO_MFID = 0x0BA9  # Manufacturer ID for Shelly devices

BLUETTI_GATT_SERVICE_UUID = "0000ff00-0000-1000-8000-00805f9b34fb"

printInfo = True
printDebug = True
printError = True
#logging.basicConfig(level=logging.DEBUG)

fileName = 'devices.json'

# ============================
# Logging Helper
# ============================
def log_info(message: str) -> None:
    """Logs an info message."""
    logging.info(message)
    log_print(message, printInfo)

def log_error(message: str) -> None:
    """Logs an error message."""
    logging.error(message)
    log_print(message, printError)

def log_debug(message: str) -> None:
    """Logs a debug message."""
    logging.debug(message)
    log_print(message, printDebug)

def log_print(message:str, b:bool):
    if b:
        print(message)

# ============================
# Utilities
# ============================
def handle_signal(signal_num: int, frame: Any) -> None:
    """Handles termination signals for graceful shutdown."""
    log_info(f"Received signal {signal_num}, shutting down gracefully...")
    sys.exit(0)

async def main() -> None:
    # Read data from a JSON file
    try:
        with open(fileName, "r") as json_file:
            devices = json.load(json_file)
    except Exception as e:
        log_error(f"Error during reading devices.json file: {e}")
        savedDevices = []

    if not devices:
        log_error("No devices found. Exiting")
        sys.exit(0)

    for entry in devices:
        if entry['manufacturer'] == 'shelly':
            selected_device_info = entry

    device = ShellyDevice(selected_device_info["address"])

    result = await execute_toggle(device)

    if result:
        print(f"RPC Method '{rpc_method}' executed successfully. Result:")
        print_with_jq(result.get("result", {}))
    else:
        print(f"RPC Method executed successfully. No data returned.")

    result = await getStatus(device)

    if result:
        print(f"RPC Method  executed successfully. Result:")
        print_with_jq(json.dumps(result.get("result", {})))
    else:
        print(f"RPC Method executed successfully. No data returned.")

# built-in Shelly commands
shellyCommands = [
    "Shelly.ListMethods",
    "Shelly.GetDeviceInfo",
    "Shelly.GetStatus",
    "Shelly.GetConfig",
    "WiFi.SetConfig",
    "WiFi.GetStatus",
    "Eth.GetConfig",
    "Eth.SetConfig",
    "Eth.GetStatus",         # Added Eth.GetStatus
    "Shelly.Reboot",        # Added Shelly.Reboot
    "Switch.Toggle",
    "Custom Command",
]

# toggle relay
async def execute_toggle(device: ShellyDevice) -> Optional[str]:

    id_input = 0
    params = {"id": 0}
    rpc_method='Switch.Toggle'
    
    try:
        result = await device.call_rpc(rpc_method, params=params)
        if result:
            print(f"RPC Method '{rpc_method}' executed successfully. Result:")
        else:
            print(f"RPC Method '{rpc_method}' executed successfully. No data returned.")

    except Exception as e:
        print(f"Unexpected error during command execution: {e}")

    return None  # Continue normally

# toggle relay
async def getStatus(device: ShellyDevice) -> Optional[str]:

    #id_input = 0
    params = None
    rpc_method='Shelly.GetStatus'
    
    try:
        result = await device.call_rpc(rpc_method, params=params)
        if result:
            print(f"RPC Method '{rpc_method}' executed successfully. Result:")
        else:
            print(f"RPC Method '{rpc_method}' executed successfully. No data returned.")

    except Exception as e:
        print(f"Unexpected error during command execution: {e}")

    return None  # Continue normally
# # function to get info from shelly
# def shellyGetInfo():
#     {
#         "id": 123456789,
#         "src": "user_1",
#         "method": "Shelly.GetDeviceInfo",
#         "params": {}
#     }

# #function to change relay status
# def shellyChangeStatus():
#     {
#         "id": 0, # 0 is the default ID with 1 relay
#         "src": "user_1",
#         "method": "Shelly.GetDeviceInfo",
#         "params": {}
#     }

# # function to get info from Bluetti
# def bluettiGetInfo():
#     pass

# # function to change port status of Bluetti
# def bluettiGetInfo():
#     pass

        

if __name__ == "__main__":
    # Suppress FutureWarnings
    import warnings

    warnings.simplefilter("ignore", FutureWarning)

    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log_info("Script interrupted by user via KeyboardInterrupt.")
    except Exception as e:
        log_error(f"Unexpected error in main: {e}")