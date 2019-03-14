#!/usr/bin/python
# -*- coding: utf-8 -*-

import pexpect
import time
from datetime import datetime

uuid_pre = "F000"
uuid_pos = "-0451-4000-B000-000000000000"
#format: handle = [data, config]
temp_uuid = ["AA01", "AA02"]
move_uuid = ["AA81", "AA82"]
humd_uuid = ["AA21", "AA22"]
baro_uuid = ["AA41", "AA42"]
opti_uuid = ["AA71", "AA72"]
leds_uuid = ["AA65", "AA66"]

sensor_mac = "B0:B4:48:C0:CA:03"
prompt = "\[CON\]\[" + sensor_mac + "\]\[LE\]>"

stealth_mode = False
active_sensors = [temp_uuid, move_uuid, humd_uuid, baro_uuid, opti_uuid]
sensor_uuid_to_cvh = {}

def log(data):
	f = open("log.txt", "a")
	f.write(data + "\n")
	print data
	f.close()

def turn_sensor_on(cnfg, hnd):
	child.sendline("char-write-cmd " + sensor_uuid_to_cvh[uuid_pre + cnfg + uuid_pos] + " " + hnd)
	child.expect(prompt)

def turn_sensor_off(cnfg, hnd):
	child.sendline("char-write-cmd " + sensor_uuid_to_cvh[uuid_pre + cnfg + uuid_pos] + " " + hnd)
	child.expect(prompt)

def read_sensor_data(data):
	child.sendline("char-read-hnd " + sensor_uuid_to_cvh[uuid_pre + data + uuid_pos])
	child.expect(prompt)
	child.before
	child.expect(prompt)
	data = child.before
	return data.strip().split(": ")[1]

def print_temp_data(value):
	SCALE_LSB = 0.03125

	value = value.split(" ")
	obj_temp = "0x" + value[1] + value[0]
	amb_temp = "0x" + value[3] + value[2]

	obj_temp_cel = (float)(int(obj_temp, 16) >> 2) * SCALE_LSB
	amb_temp_cel = (float)(int(amb_temp, 16) >> 2) * SCALE_LSB
	obj_temp_fah = obj_temp_cel * (9.0/5.0) + 32.0
	amb_temp_fah = amb_temp_cel * (9.0/5.0) + 32.0
	
	log("IR TEMPERATURE")
	log("\tOBJECT\t\t: " + str(obj_temp_cel) + "°C" + " | " + str(obj_temp_fah) + "°F")
	log("\tAMBIENT\t\t: " + str(amb_temp_cel) + "°C" + " | " + str(amb_temp_fah) + "°F")

def print_move_data(value):
	value = value.split(" ")
	gyro_x = "0x" + value[1] + value[0]
	gyro_y = "0x" + value[3] + value[2]
	gyro_z = "0x" + value[5] + value[4]
	acc_x = "0x" + value[7] + value[6]
	acc_y = "0x" + value[9] + value[8]
	acc_z = "0x" + value[11] + value[10]
	mag_x = "0x" + value[13] + value[12]
	mag_y = "0x" + value[15] + value[14]
	mag_z = "0x" + value[17] + value[16]

	gyro_x_dps = (((float)(int(gyro_x, 16))) * 1.0) / (65536.0 / 500.0)
	gyro_y_dps = (((float)(int(gyro_y, 16))) * 1.0) / (65536.0 / 500.0)
	gyro_z_dps = (((float)(int(gyro_z, 16))) * 1.0) / (65536.0 / 500.0)

	acc_range = 16.0 # turning on handle to 0xffff sets to 16

	acc_x_mps = (((float)(int(acc_x, 16))) * 1.0) / (32768.0 / acc_range)
	acc_y_mps = (((float)(int(acc_y, 16))) * 1.0) / (32768.0 / acc_range)
	acc_z_mps = (((float)(int(acc_z, 16))) * 1.0) / (32768.0 / acc_range)

	mag_x_ut = ((float)(int(mag_x, 16))) * 1.0
	mag_y_ut = ((float)(int(mag_y, 16))) * 1.0
	mag_z_ut = ((float)(int(mag_z, 16))) * 1.0

	log("MOVEMENT")
	log("\tGYROSCOPE\t: " + "X: " + str(gyro_x_dps) + "°/s" + " | " + "Y: " + str(gyro_y_dps) + "°/s" + " | " + "Z: " + str(gyro_z_dps) + "°/s")
	log("\tACCELEROMETER\t: " + "X: " + str(acc_x_mps) + "m/s" + " | " + "Y: " + str(acc_y_mps) + "m/s" + " | " + "Z: " + str(acc_z_mps) + "m/s")
	log("\tMAGNETOMETER\t: " + "X: " + str(mag_x_ut) + "µT" + " | " + "Y: " + str(mag_y_ut) + "µT" + " | " + "Z: " + str(mag_z_ut) + "µT")

def print_humd_data(value):
	value = value.split(" ")
	temp = "0x" + value[1] + value[0]
	humd = "0x" + value[3] + value[2]

	temp_cel = ((float)(int(temp, 16))) / 65536.0 * 165.0 - 40.0
	temp_fah = temp_cel * (9.0/5.0) + 32.0

	humd_rel = (float)(int(humd, 16) & ~0x0003) / 65536.0 * 100.0

	log("HUMIDITY")
	log("\tTEMPERATURE\t: " + str(temp_cel) + "°C" + " | " + str(temp_fah) + "°F")
	log("\tHUMDITY\t\t: " + str(humd_rel) + "%")

def print_baro_data(value):
	value = value.split(" ")
	temp = "0x" + value[2] + value[1] + value[0]
	baro = "0x" + value[5] + value[4] + value[3]

	temp_cel = ((float)(int(temp, 16))) / 100.0
	temp_fah = temp_cel * (9.0/5.0) + 32.0

	baro_hpa = ((float)(int(baro, 16))) / 100.0
	baro_kpa = baro_hpa / 10.0

	log("BAROMETER")
	log("\tTEMPERATURE\t: " + str(temp_cel) + "°C" + " | " + str(temp_fah) + "°F")
	log("\tPRESSURE\t: " + str(baro_kpa) + "kPa" + " | " + str(baro_hpa) + "hPa")

def print_opti_data(value):
	value = value.split(" ")
	opti = "0x" + value[1] + value[0]

	m = int(opti, 16) & 0x0FFF
	e = (int(opti, 16) & 0xF000) >> 12

	if (e == 0):
		e = 1
	else:
		e = 2 << (e - 1)
 
	opti_lux = m * (0.01 * e)
	
	log("OPTICAL")
	log("\tLIGHT INTENSITY\t: " + str(opti_lux) + "lux")

def turn_sensors_on():
	for sensor in active_sensors:
		if sensor[1] == move_uuid[1]:
			turn_sensor_on(sensor[1], "ffff")
		else:
			turn_sensor_on(sensor[1], "01")

def turn_sensors_off():
	for sensor in active_sensors:
		if sensor[1] == move_uuid[1]:
			turn_sensor_off(sensor[1], "0000")
		else:
			turn_sensor_off(sensor[1], "00")

def init_led():
	if not stealth_mode:
		turn_sensor_on(leds_uuid[1], "01")

def set_led(hnd):
	if not stealth_mode:
		turn_sensor_on(leds_uuid[0], hnd)

child = pexpect.spawn("gatttool -I")
child.sendline("connect " + sensor_mac)
child.expect(prompt)
child.sendline("characteristics")
child.expect(prompt)
child.before
child.expect(prompt)
characteristics = child.before
handles = characteristics.split("\r\n")

for i in handles:
	if len(i) >= 11:
		handle = i.replace(":", ",").split(", ")
		char_value_handle_value_index = handle.index("char value handle") + 1
		uuid_value_index = handle.index("uuid") + 1
		
		if handle[uuid_value_index] not in sensor_uuid_to_cvh:
			sensor_uuid_to_cvh[handle[uuid_value_index].upper()] = handle[char_value_handle_value_index].upper()

init_led()

while (True):
	set_led("03")

	turn_sensors_on()

	set_led("01")

	time.sleep(10)
	log("===")
	log(str(datetime.now()))
	
	set_led("02")

	for sensor in active_sensors:
		if sensor[0] == temp_uuid[0]:
			print_temp_data(read_sensor_data(sensor[0]))
		if sensor[0] == move_uuid[0]:
			print_move_data(read_sensor_data(sensor[0]))
		if sensor[0] == humd_uuid[0]:
			print_humd_data(read_sensor_data(sensor[0]))
		if sensor[0] == baro_uuid[0]:
			print_baro_data(read_sensor_data(sensor[0]))
		if sensor[0] == opti_uuid[0]:
			print_opti_data(read_sensor_data(sensor[0]))

	set_led("03")

	turn_sensors_off()
	log("===")

	set_led("00")

	time.sleep(590)