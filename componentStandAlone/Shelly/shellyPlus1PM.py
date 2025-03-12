# based on https://github.com/ALLTERCO/Utilities/blob/master/shelly-ble-rpc/shelly-ble-rpc.py

# finds all Shelly devices and retrieves status info

import asyncio
import json
import struct
import random
import logging
import sys
import signal
import os
import subprocess
import argparse
from typing import Any, Dict, Optional, Tuple, List
from dataclasses import dataclass

from bleak import BleakClient, BleakError, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from colorama import Fore, Style, init as colorama_init
from logging.handlers import RotatingFileHandler
from prettytable import PrettyTable, TableStyle
from yaspin import yaspin  # Import yaspin for spinner

# ============================
# Configuration Constants
# ============================

SHELLY_GATT_SERVICE_UUID = "5f6d4f53-5f52-5043-5f53-56435f49445f"
RPC_CHAR_DATA_UUID = "5f6d4f53-5f52-5043-5f64-6174615f5f5f"
RPC_CHAR_TX_CTL_UUID = "5f6d4f53-5f52-5043-5f74-785f63746c5f"
RPC_CHAR_RX_CTL_UUID = "5f6d4f53-5f52-5043-5f72-785f63746c5f"
ALLTERCO_MFID = 0x0BA9  # Manufacturer ID for Shelly devices


# ============================
# Shelly Device Class
# ============================

class ShellyDevice:
    """Represents a Shelly BLE device and handles RPC communication."""

    def __init__(self, address: str):
        self.address = address
        self.shelly_service = None
        self.data_char = None
        self.tx_ctl_char = None
        self.rx_ctl_char = None

    async def call_rpc(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 5.0,
        retries: int = 1,
    ) -> Dict[str, Any]:
        """Performs an RPC call to the Shelly device over BLE with retries and timeout."""
        attempt = 0
        while attempt < retries:
            try:
                async with BleakClient(self.address) as client:
                    if client.is_connected:
                        log_info(f"Connected to {self.address}.")
                        print_success(f"Successfully connected to {self.address}.")
                    else:
                        raise DeviceConnectionError(f"Failed to connect to {self.address}.")

                    # Proceed with RPC operations
                    await asyncio.wait_for(self.retrieve_shelly_service(client), timeout=timeout)
                    await asyncio.wait_for(self.fetch_characteristics(client), timeout=timeout)

                    length_bytes, request_id, rpc_request_bytes = self.prepare_rpc_request(
                        method, params
                    )

                    await asyncio.wait_for(
                        self.send_rpc_request(client, length_bytes, rpc_request_bytes),
                        timeout=timeout,
                    )

                    frame_len = await asyncio.wait_for(
                        self.read_expected_response_length(client), timeout=timeout
                    )

                    response = await asyncio.wait_for(
                        self.read_rpc_response(client, frame_len), timeout=timeout,
                    )

                    validated_response = self.validate_rpc_response(response, request_id)

                    return validated_response

            except asyncio.TimeoutError:
                attempt += 1
                error_msg = f"Timeout occurred during RPC call '{method}'."
                print_error(error_msg)
                log_error(error_msg)
                if attempt < retries:
                    backoff_time = 2 ** attempt
                    print_attempt(f"Retrying in {backoff_time} seconds...")
                    await asyncio.sleep(backoff_time)
                else:
                    raise RPCExecutionError(error_msg)
            except (BleakError, Exception) as e:
                error_message = str(e)
                log_error(f"RPC call attempt {attempt + 1} failed: {error_message}")

                # Check if the error indicates an unavailable RPC method
                if "No handler for" in error_message or "'code': 404" in error_message:
                    print_error(f"The RPC method '{method}' is not available on this device.")
                    raise RPCExecutionError(error_message)

                # Check if the error indicates invalid arguments
                if "'code': -103" in error_message or "Invalid argument" in error_message:
                    print_error("Invalid arguments provided for the RPC method.")
                    raise RPCExecutionError(error_message)

                attempt += 1
                if attempt < retries:
                    backoff_time = 2 ** attempt
                    print_attempt(f"Retrying in {backoff_time} seconds...")
                    await asyncio.sleep(backoff_time)
                else:
                    print_error("All RPC call attempts failed.")
                    log_error("All RPC call attempts failed.")
                    raise RPCExecutionError(error_message)

    async def retrieve_shelly_service(self, client: BleakClient) -> None:
        """Retrieves the Shelly GATT service from the BLE client."""
        try:
            await client.get_services()
            services = client.services
            self.shelly_service = services.get_service(SHELLY_GATT_SERVICE_UUID)
            if self.shelly_service is None:
                raise BleakError("Shelly GATT Service not found.")
            log_debug(f"Shelly GATT Service found with UUID: {SHELLY_GATT_SERVICE_UUID}")
        except BleakError as e:
            log_error(f"Error retrieving Shelly GATT Service: {e}")
            raise

    async def fetch_characteristics(self, client: BleakClient) -> None:
        """Fetches the required BLE characteristics from the Shelly service."""
        try:
            self.data_char = self.shelly_service.get_characteristic(RPC_CHAR_DATA_UUID)
            self.tx_ctl_char = self.shelly_service.get_characteristic(RPC_CHAR_TX_CTL_UUID)
            self.rx_ctl_char = self.shelly_service.get_characteristic(RPC_CHAR_RX_CTL_UUID)
            if not all([self.data_char, self.tx_ctl_char, self.rx_ctl_char]):
                raise BleakError("One or more required characteristics not found.")
            log_debug("All required characteristics fetched successfully.")
        except BleakError as e:
            log_error(f"Error fetching characteristics: {e}")
            raise

    def prepare_rpc_request(
        self, method: str, params: Optional[Dict[str, Any]]
    ) -> Tuple[bytes, int, bytes]:
        """Prepares the RPC request."""
        log_debug("Preparing RPC Request...")
        request_id = random.randint(1, 1_000_000_000)
        rpc_request = {"id": request_id, "src": "user_1", "method": method}
        if params:
            rpc_request["params"] = params
        rpc_request_json = json.dumps(rpc_request)
        rpc_request_bytes = rpc_request_json.encode("utf-8")
        rpc_length = len(rpc_request_bytes)
        log_debug(f"RPC Request prepared with ID: {request_id} and length: {rpc_length} bytes.")

        length_bytes = struct.pack(">I", rpc_length)
        log_debug(f"Packed length bytes: {length_bytes.hex()}")

        return length_bytes, request_id, rpc_request_bytes

    async def send_rpc_request(
        self, client: BleakClient, length_bytes: bytes, rpc_request_bytes: bytes
    ) -> None:
        """Sends the RPC request over BLE."""
        log_debug("Writing length to TX Control Characteristic...")
        try:
            await client.write_gatt_char(self.tx_ctl_char, length_bytes, response=True)
            log_debug("Length written to TX Control Characteristic.")
        except BleakError as e:
            log_error(f"Failed to write length to TX Control Characteristic: {e}")
            raise

        log_debug("Writing RPC Request to Data Characteristic...")
        try:
            await client.write_gatt_char(self.data_char, rpc_request_bytes, response=True)
            log_debug("RPC request written to Data Characteristic.")
        except BleakError as e:
            log_error(f"Failed to write RPC request to Data Characteristic: {e}")
            raise

    async def read_expected_response_length(self, client: BleakClient) -> int:
        """Reads the expected response length from RX Control characteristic."""
        log_debug("Reading expected response length from RX Control Characteristic...")
        try:
            raw_rx_frame = await client.read_gatt_char(self.rx_ctl_char)
            frame_len = struct.unpack(">I", raw_rx_frame)[0]
            log_debug(f"Expected response length: {frame_len} bytes.")
            return frame_len
        except BleakError as e:
            log_error(f"Failed to read RX Control Characteristic: {e}")
            raise
        except struct.error as e:
            log_error(f"Failed to unpack RX Control data: {e}")
            raise

    async def read_rpc_response(self, client: BleakClient, frame_len: int) -> Dict[str, Any]:
        """Reads the RPC response data in chunks."""
        log_debug("Reading RPC Response Data in Chunks...")
        response_data = bytearray()
        bytes_remaining = frame_len
        try:
            while bytes_remaining > 0:
                chunk = await client.read_gatt_char(self.data_char)
                response_data.extend(chunk)
                bytes_remaining -= len(chunk)
                log_debug(
                    f"Received chunk of {len(chunk)} bytes, {bytes_remaining} bytes remaining."
                )
            if not response_data:
                log_debug("Received empty response data from the device.")
                return {}  # Return empty dict instead of raising error
            response_json = response_data.decode("utf-8")
            log_debug(f"Raw response data: {response_json}")
            response = json.loads(response_json)
            log_debug("RPC Response received and decoded successfully.")
            return response
        except BleakError as e:
            log_error(f"Failed to read RPC response data: {e}")
            raise
        except UnicodeDecodeError as e:
            log_error(f"Failed to decode RPC response: {e}")
            raise
        except json.JSONDecodeError as e:
            log_error(f"Failed to parse RPC response JSON: {e}")
            log_debug(f"Raw response data for debugging: {response_json}")
            raise

    def validate_rpc_response(
        self, response: Dict[str, Any], request_id: int
    ) -> Dict[str, Any]:
        """Validates the RPC response."""
        log_debug("Validating RPC Response...")
        if response.get("id") != request_id:
            error_msg = "Response ID does not match request ID."
            log_error(error_msg)
            raise Exception(error_msg)
        if "result" in response:
            log_debug("RPC response contains 'result' field.")
            return response
        elif "error" in response:
            error_detail = response["error"]
            error_msg = f"RPC Error: {error_detail}"
            log_error(error_msg)
            raise Exception(error_msg)
        else:
            log_debug("RPC response does not contain 'result' or 'error'. Returning empty result.")
            return response  # Return the response as is, even if it's empty



# ============================
# Scanning Functions
# ============================


async def scan_and_list_devices(
    scan_duration: int,
    filter_name: Optional[str] = None,
    filter_address: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Scans for Shelly devices over BLE with a spinner and optional filters."""
    discovered_devices: List[Dict[str, Any]] = []
    discovered_addresses = set()

    filter_name_lower = filter_name.lower() if filter_name else None
    filter_address_lower = filter_address.lower() if filter_address else None

    def discovery_handler(device: BLEDevice, advertisement_data: AdvertisementData):
        if device.name is None:
            return

        if ALLTERCO_MFID not in advertisement_data.manufacturer_data:
            return

        if "Shelly" not in device.name:
            return

        if device.address in discovered_addresses:
            return

        # Apply name and address filters (case-insensitive)
        if filter_name_lower and filter_name_lower not in device.name.lower():
            return
        if filter_address_lower and filter_address_lower not in device.address.lower():
            return

        # Exclude devices with weak signal
        if advertisement_data.rssi < -80:
            return

        discovered_addresses.add(device.address)
        discovered_devices.append(
            {
                "address": device.address,
                "name": device.name,
                "rssi": advertisement_data.rssi,
            }
        )

    print_header(f"Scanning for BLE devices for {scan_duration} seconds...")

    with yaspin(text="Scanning...", color="cyan") as spinner:
        async with BleakScanner(detection_callback=discovery_handler):
            await asyncio.sleep(scan_duration)
        spinner.ok("✅")  # Replace spinner with a check mark upon completion

    discovered_devices.sort(key=lambda d: d["rssi"], reverse=True)
    return discovered_devices


def print_devices_table(devices: List[Dict[str, str]]):
    """Prints the list of devices in a formatted table."""
    if not devices:
        print_error("No devices found.")
        return

    # Create PrettyTable
    table = PrettyTable(["No", "Name", "Address", "RSSI"])
    table.set_style(TableStyle.SINGLE_BORDER)
    table.align = "l"

    for index, device in enumerate(devices, start=1):
        table.add_row(
            [
                index,
                f"{Fore.GREEN}{device['name']}{Style.RESET_ALL}",
                f"{Fore.MAGENTA}{device['address']}{Style.RESET_ALL}",
                colorize_rssi(device["rssi"]),
            ]
        )
    print(table)


# ============================
# Main Function
# ============================


async def main() -> None:
    """The main function orchestrating the RPC call process."""
    args = parse_arguments()
    config = load_config(args)

    log_info("Script started.")

    # Initialize filters
    current_filter_name = config.filter_name  # Filter by device name
    current_filter_address = config.filter_address  # Filter by device address

    while True:
        try:
            devices = await scan_and_list_devices(
                config.scan_duration, current_filter_name, current_filter_address
            )
        except Exception as e:
            log_error(f"Error during scanning: {e}")
            print_error(f"Error during scanning: {e}")
            return

        if not devices:
            print_error("No devices found.")
            # Offer options to rescan with current filter, remove filter, apply new filter, or quit
            if current_filter_name or current_filter_address:
                action = input(
                    f"{Fore.YELLOW}Options:\n"
                    f"  'r' - Rescan with current filter\n"
                    f"  'n' - Rescan with no filter\n"
                    f"  'f' - Rescan with different filter\n"
                    f"  'q' - Quit\n"
                    f"Choose an option: {Style.RESET_ALL}"
                ).strip().lower()
                if action == 'q':
                    print_success("Exiting...")
                    log_info("Script completed.")
                    sys.exit(0)
                elif action == 'r':
                    continue  # Rescan with current filter
                elif action == 'n':
                    current_filter_name = None
                    current_filter_address = None
                    continue  # Rescan with no filter
                elif action == 'f':
                    new_filter_name = input(f"{Fore.YELLOW}Enter new name filter (or leave empty for no filter): {Style.RESET_ALL}").strip()
                    new_filter_address = input(f"{Fore.YELLOW}Enter new address filter (or leave empty for no filter): {Style.RESET_ALL}").strip()
                    current_filter_name = new_filter_name if new_filter_name else None
                    current_filter_address = new_filter_address if new_filter_address else None
                    continue  # Rescan with new filter
                else:
                    print_error("Invalid input.")
                    continue
            else:
                action = input(
                    f"{Fore.YELLOW}Options:\n"
                    f"  'r' - Rescan\n"
                    f"  'f' - Rescan with different filter\n"
                    f"  'q' - Quit\n"
                    f"Choose an option: {Style.RESET_ALL}"
                ).strip().lower()
                if action == 'q':
                    print_success("Exiting...")
                    log_info("Script completed.")
                    sys.exit(0)
                elif action == 'r':
                    continue  # Rescan with no filter
                elif action == 'f':
                    new_filter_name = input(f"{Fore.YELLOW}Enter new name filter (or leave empty for no filter): {Style.RESET_ALL}").strip()
                    new_filter_address = input(f"{Fore.YELLOW}Enter new address filter (or leave empty for no filter): {Style.RESET_ALL}").strip()
                    current_filter_name = new_filter_name if new_filter_name else None
                    current_filter_address = new_filter_address if new_filter_address else None
                    continue  # Rescan with new filter
                else:
                    print_error("Invalid input.")
                    continue

        # Display devices
        print_header("Discovered devices:")
        print_devices_table(devices)

        # Select a device
        try:
            selected_device_info = await select_device(devices, current_filter_name, current_filter_address)
        except RescanWithNewFiltersException:
            # Prompt for new filters
            new_filter_name = input(
                f"{Fore.YELLOW}Enter new name filter (or leave empty for no filter): {Style.RESET_ALL}"
            ).strip()
            new_filter_address = input(
                f"{Fore.YELLOW}Enter new address filter (or leave empty for no filter): {Style.RESET_ALL}"
            ).strip()
            current_filter_name = new_filter_name if new_filter_name else None
            current_filter_address = new_filter_address if new_filter_address else None
            continue

        if selected_device_info == 'remove_filter':
            # Remove current filters
            current_filter_name = None
            current_filter_address = None
            continue

        if not selected_device_info:
            # User chose to rescan or remove filters
            continue

        # Command selection loop
        try:
            result = await command_selection_loop(selected_device_info, config, current_filter_name, current_filter_address)
            if result == 'rescan':
                continue  # Indicate that we need to rescan
        except RescanWithNewFiltersException:
            # Prompt for new filters
            new_filter_name = input(
                f"{Fore.YELLOW}Enter new name filter (or leave empty for no filter): {Style.RESET_ALL}"
            ).strip()
            new_filter_address = input(
                f"{Fore.YELLOW}Enter new address filter (or leave empty for no filter): {Style.RESET_ALL}"
            ).strip()
            current_filter_name = new_filter_name if new_filter_name else None
            current_filter_address = new_filter_address if new_filter_address else None
            continue


# ============================
# Device Selection Function
# ============================


async def select_device(devices: List[Dict[str, Any]], name_filter: Optional[str], address_filter: Optional[str]) -> Optional[Dict[str, Any]]:
    """Allows the user to select a device from the list."""
    selected_device = None
    while not selected_device:
        prompt_options = (
            f"Select a device by number, 'r' to rescan, 'f' to apply new filters, "
            f"{'n to remove filters, ' if name_filter or address_filter else ''}'q' to quit: "
        )
        selection = input(
            f"{Fore.YELLOW}{prompt_options}{Style.RESET_ALL}"
        ).strip().lower()
        if selection == "q":
            print_success("Exiting...")
            log_info("Script completed.")
            sys.exit(0)
        elif selection == "r":
            return None  # Rescan with current filters
        elif selection == "f":
            # Indicate to apply new filters
            raise RescanWithNewFiltersException()
        elif selection == "n" and (name_filter or address_filter):
            return 'remove_filter'  # Signal to remove filters
        try:
            selection_num = int(selection)
            if 1 <= selection_num <= len(devices):
                selected_device = devices[selection_num - 1]
            else:
                print_error("Invalid selection. Please select a valid device number.")
        except ValueError:
            print_error("Invalid input. Please enter a number, 'r', 'f', 'n', or 'q'.")
    return selected_device


# ============================
# Utility Exception Classes
# ============================

class RescanWithNewFiltersException(Exception):
    """Custom exception to handle rescan with new filters."""
    pass


# ============================
# Entry Point
# ============================

if __name__ == "__main__":
    # Suppress FutureWarnings
    import warnings

    warnings.simplefilter("ignore", FutureWarning)

    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        asyncio.run(main())
    except RescanWithNewFiltersException:
        # Handle rescan with new filters
        # Restart the main function with new filters
        asyncio.run(main())
    except KeyboardInterrupt:
        log_info("Script interrupted by user via KeyboardInterrupt.")
        print_error("\nScript interrupted by user.")
    except Exception as e:
        log_error(f"Unexpected error in main: {e}")
        print_error(f"Unexpected error: {e}")