# Weather Probe

Configure a TI CC2650 SensorTag to broadcast indefinitely and retrieve sensor readings from the BLE stack using GATT.

## Prerequisites

- [Texas Instruments SimpleLink Bluetooth low energy/Multi-standard SensorTag (CC2650STK)](http://www.ti.com/tool/CC2650STK)
- [Texas Instruments SimpleLink SensorTag Debugger DevPack](http://www.ti.com/tool/CC-DEVPACK-DEBUG)
- [Code Composer Studio 8.3.0.00009](http://processors.wiki.ti.com/index.php/Download_CCS)
- [BLE-STACK v2.2.2 supports Bluetooth 4.2 for CC2640/CC2650](http://www.ti.com/tool/BLE-Stack)
- [SmartRF Flash Programmer v2](http://www.ti.com/tool/FLASH-PROGRAMMER)
- Windows 10
- Ubuntu 16.04

---

## Configuring SensorTag

With the default firmware, the CC2650 SensorTag will broadcast for about half a minute, then go into idle/sleep mode when no connection is established. This increases battery life but the button must be pressed to wake the probe again. If the probe is installed in an inaccessible location, it would be inconvenient to reach for the button. In this case, it would be best to prevent the probe from going into sleep when its disconnected, at the cost of battery life.

*The instructions for this section is specific to Windows 10.*

### Preparing

1. Download and install Code Composer Studio, BLE Stack for CC2650, and Flash Programmer 2.
2. Attach the Debugger onto the SensorTag and connect the computer to the Debugger over USB cable.

### Erasing the SensorTag

1. Launch Flash Programmer 2.
2. Select CC2650 from the list of connected devices.
3. Under *Actions*, check *Erase*. Uncheck *Program* and *Verify*.
4. Under Erase, Select *All unprotected pages*.
5. Click *Play* to erase.

### Importing Projects

1. Launch Code Composer Studio.
2. Import 3 Projects:
```
examples\util\bim_extflash\cc2640\ccs
examples\cc2650stk\sensortag\ccs\stack
examples\cc2650stk\sensortag\ccs\app
```
If you did not change the default installation path when installing BLE Stack, it should be installed into: `C:\ti\simplelink\ble_sdk_*`.

### Keeping SensorTag Alive

1. Open `sensortag.c` in the *Application* folder of *sensortag_cc2650stk_app* project.
2. Modify:
```
#define DEFAULT_DISCOVERABLE_MODE             GAP_ADTYPE_FLAGS_LIMITED
```
to
```
#define DEFAULT_DISCOVERABLE_MODE             GAP_ADTYPE_FLAGS_GENERAL
```
and
```
uint16_t advertOffTime = 0;
```
to
```
uint16_t advertOffTime = 1;
```
*Courtesy of [Frederic Klein](https://stackoverflow.com/questions/38042880/sensortag-2-cc2650-advertising-indefinately-firmware)*.

3. Save changes.

### Flashing into SensorTag

1. Flash *bim_extflash*.
2. Flash *sensortag_cc2650stk_stack*.
3. Flash *sensortag_cc2650stk_app*.

### Debugging

SensorTag should now be flashing green indefinitely. If it is solid red, Erase and Flash again. Erasing can be done with Flash Programmer 2, or holding down both left and right buttons for 6s.

---

## Retrieving Sensor Readings

Sensor setting and data can be controlled by and retrieved from the GATT table. The sensor needs to be turned on first. Allow a few seconds between turning on sensors and getting sensor data from handle address, otherwise readings will be zeros. 

CC2650 IR Temperature sensor handle address does not follow most guides you find [online](https://developer.ibm.com/recipes/tutorials/ti-sensor-tag-and-raspberry-pi/). This is because newer versions of CC2650 no longer use the TMP007 sensor, but you can find the handle address from the sensor UUID address which looks something like this: `F000____-0451-4000-B000-000000000000` where ____ is specific to the sensor. Check the user guide for more.

*The instructions for this section is specific to Ubuntu 16.04.*

### Preparing

Install `hcitool` and `gatttool`.

### Finding SensorTag Hardware Address

1. Scan for nearby Bluetooth interfaces:
```
sudo hcitool lescan
```
2. Note down the hardware address returned for *CC2650 SensorTag*.

### Connecting to SensorTag using GATTtool

1. Run GATTtool in interactive mode:
```
gatttool -I
```
2. Connect to the SensorTag using its hardware address:
```
connect <HW_ADDR>
```

### Viewing the GATT table

The GATT table lists the handle and UUID addresses of the relevant sensor components. You will need the configuration and data handle address to turn on/off the sensor and read data respectively.
```
characteristics
```
Refer to the user guide for the complete list of sensor UUID addresses.

### Controlling Sensors and Retrieving Sensor Data

- To turn on or off sensors:
```
char-write-cmd <HANDLE> <VALUE>
```
- To read sensor data:
```
char-read-hnd <HANDLE>
```
See code for specifics.

### Automating Data Collection

To automate sensor data collection on your machine or SBC, use the programming language you prefer to interact with `gatttool` or other GATT API. Remember to allow sometime between turning on sensors and reading sensor data for sensor to create readings, and turn off sensors after reading sensor data to conserve energy.

An example written in Python 2 with `pexpect` is provided.

---

### References
- [CC2650 SensorTag User's Guide](http://processors.wiki.ti.com/index.php/CC2650_SensorTag_User%27s_Guide)
- [Controlling the Texas Instruments SensorTag (CC2650) from anywhere in the world](https://github.com/uffebjorklund/TI-CC2650)
- [Forked: Controlling the Texas Instruments SensorTag (CC2650) from anywhere in the world](https://github.com/codeplanner/TI-CC2650-1)
- [Using Python to Store Data from many BLE Devices](https://mcuoneclipse.com/2017/06/04/using-python-to-store-data-from-many-ble-devices/)
- [TI Sensor Tag and Raspberry Pi](https://developer.ibm.com/recipes/tutorials/ti-sensor-tag-and-raspberry-pi/)
- [Bluetooth LE in Python using pexpect and gatttool](http://flowcloud.github.io/ci20-bluetooth-LE/2015/09/10/bluetooth-control-in-python/)
- [Pexpect API Overview](https://pexpect.readthedocs.io/en/stable/overview.html)
- [SensorTag 2 CC2650 advertising indefinately firmware](https://stackoverflow.com/questions/38042880/sensortag-2-cc2650-advertising-indefinately-firmware)
- [CCS/TIDC-CC2650STK-SENSORTAG: Loading hex files gives red light](https://e2e.ti.com/support/wireless-connectivity/bluetooth/f/538/t/599529)
- [Download CCS](http://processors.wiki.ti.com/index.php/Download_CCS)
- [Bluetooth low energy software stack](http://www.ti.com/tool/BLE-Stack)
- [SmartRF Flash Programmer v2](http://www.ti.com/tool/download/FLASH-PROGRAMMER-2)

v1.0
March 14, 2019