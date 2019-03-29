#!/bin/bash
while true; do
	ps --no-headers -C python || sudo /usr/bin/python /home/pi/anrg-sensortag-weather-probe/sensor.py &
	sleep 10m
done