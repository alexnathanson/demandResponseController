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


############### POSITIONS ######################
# Numbers indicate position of relay and sensor in system
#
#     +--2--[BAT]--4--+
# ----|               [TRANSFER SWITCH]--3-->
#     +-------1-------+
#
################################################

class ShellyDevice:
    """Represents a Shelly BLE device and handles RPC communication."""

    def __init__(self, address: str, channel: int, position: int):
        self.address = address
        self.shelly_service = None
        self.data_char = None
        self.tx_ctl_char = None
        self.rx_ctl_char = None
        self.SHELLY_GATT_SERVICE_UUID = "5f6d4f53-5f52-5043-5f53-56435f49445f"
        self.RPC_CHAR_DATA_UUID = "5f6d4f53-5f52-5043-5f64-6174615f5f5f"
        self.RPC_CHAR_TX_CTL_UUID = "5f6d4f53-5f52-5043-5f74-785f63746c5f"
        self.RPC_CHAR_RX_CTL_UUID = "5f6d4f53-5f52-5043-5f72-785f63746c5f"
        self.ALLTERCO_MFID = 0x0BA9  # Manufacturer ID for Shelly devices
        self.relayChannel = channel
        self.positions = ['grid', 'load']
        self.position = 

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
                log_error(error_msg)
                if attempt < retries:
                    backoff_time = 2 ** attempt
                    log_debug(f"Retrying in {backoff_time} seconds...")
                    await asyncio.sleep(backoff_time)
                else:
                    raise Exception(error_msg)
            except (BleakError, Exception) as e:
                error_message = str(e)
                log_error(f"RPC call attempt {attempt + 1} failed: {error_message}")

                # Check if the error indicates an unavailable RPC method
                if "No handler for" in error_message or "'code': 404" in error_message:
                    log_error(f"The RPC method '{method}' is not available on this device.")
                    raise Exception(error_message)

                # Check if the error indicates invalid arguments
                if "'code': -103" in error_message or "Invalid argument" in error_message:
                    log_error("Invalid arguments provided for the RPC method.")
                    raise Exception(error_message)

                attempt += 1
                if attempt < retries:
                    backoff_time = 2 ** attempt
                    log_debug(f"Retrying in {backoff_time} seconds...")
                    await asyncio.sleep(backoff_time)
                else:
                    log_error("All RPC call attempts failed.")
                    raise Exception(error_message)

    async def retrieve_shelly_service(self, client: BleakClient) -> None:
        """Retrieves the Shelly GATT service from the BLE client."""
        try:
            await client.get_services()
            services = client.services
            self.shelly_service = services.get_service(self.SHELLY_GATT_SERVICE_UUID)
            if self.shelly_service is None:
                raise BleakError("Shelly GATT Service not found.")
            log_debug(f"Shelly GATT Service found with UUID: {self.SHELLY_GATT_SERVICE_UUID}")
        except BleakError as e:
            log_error(f"Error retrieving Shelly GATT Service: {e}")
            raise

    async def fetch_characteristics(self, client: BleakClient) -> None:
        """Fetches the required BLE characteristics from the Shelly service."""
        try:
            self.data_char = self.shelly_service.get_characteristic(self.RPC_CHAR_DATA_UUID)
            self.tx_ctl_char = self.shelly_service.get_characteristic(self.RPC_CHAR_TX_CTL_UUID)
            self.rx_ctl_char = self.shelly_service.get_characteristic(self.RPC_CHAR_RX_CTL_UUID)
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
# Logging Helper
# ============================
printError = True
printInfo = True
printDebug = True

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