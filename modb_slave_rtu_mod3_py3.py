#!/usr/bin/env python3

"""
Pymodbus Asynchronous Server Example with Changing Values
--------------------------------------------------------------------------

This script runs a Modbus server that continuously updates the values of
Modbus registers (0-3000) at regular intervals.
"""

from pymodbus import __version__ as version
from pymodbus.server.async_io import StartSerialServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer
import logging
import time
from threading import Thread

# Configure logging
FORMAT = ('%(asctime)-15s %(threadName)-15s %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.INFO)

# Initialize the Modbus context
change_var = 120
store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [17] * 100),
    co=ModbusSequentialDataBlock(0, [17] * 100),
    hr=ModbusSequentialDataBlock(0x00, [change_var] * 3001),  # Extend to 3000
    ir=ModbusSequentialDataBlock(0, [17] * 100)
)
context = ModbusServerContext(slaves=store, single=True)

def run_modbus_server():
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
    identity.ProductName = 'Pymodbus Server'
    identity.ModelName = 'Pymodbus Server'
    identity.MajorMinorRevision = version  # Directly assign the version string

    # Start the RTU server with keyword arguments
    StartSerialServer(
        context=context,
        identity=identity,
        port='/dev/ttyUSB0',
        framer=ModbusRtuFramer,
        baudrate=9600,
        parity='E',
        bytesize=8,
        stopbits=1,
        ignore_missing_slaves=True
    )

def update_modbus_registers():
    global change_var
    while True:
        change_var += 10
        # Update registers 0-3000 with the new value
        context[0].setValues(3, 0, [change_var] * 3001)
        print(f"Updated registers 0-3000 with value: {change_var}")
        if change_var > 1000:
            change_var = 0
        time.sleep(10)

if __name__ == "__main__":
    # Start the Modbus server in a separate thread
    server_thread = Thread(target=run_modbus_server)
    server_thread.daemon = True
    server_thread.start()

    # Continuously update the Modbus registers
    update_modbus_registers()
