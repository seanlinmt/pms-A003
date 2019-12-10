#!/usr/bin/env python2

import serial
import time
import sys
import json
import datetime as dt
import binascii
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
import argparse

xs = []
y1s = []
y2s = []
y3s = []


class pmsA003():
    def __init__(self, dev):
        self.id = 0
        self.d = {}
        self.line_labels = ["PM1.0", "PM2.5", "PM10"]
        self.serial = serial.Serial(dev, baudrate=9600, timeout=3)

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.fig.suptitle('PMSA003 Air Quality')

        self.ani = animation.FuncAnimation(
                            self.fig, 
                            self.animate, 
                            fargs=(xs,y1s,y2s,y3s,), 
                            interval=3000)
        plt.show()

    def __exit__(self, exc_type, exc_value, traceback):
        self.serial.close()


    def setIdel(self):
        idelcmd = b'\x42\x4d\xe4\x00\x00\x01\x73'
        ary = bytearray(idelcmd)
        self.serial.write(ary)

    def setNormal(self):
        normalcmd = b'\x42\x4d\xe4\x00\x01\x01\x74'
        ary = bytearray(normalcmd)
        self.serial.write(ary)

    def vertify_data(self):
        if not self.data:
            return False
        return True

    def read_data(self):
        while True:
            b = self.serial.read(1)
            if b == b'\x42':
                data = self.serial.read(31)
                if data[0] == b'\x4d':
                    self.data = bytearray(b'\x42' + data)
                    if self.vertify_data():
                        return self._PMdata()

    def _PMdata(self):
        self.id += 1
        self.d['time'] = dt.datetime.now()
        self.d['apm25'] = self.data[6] * 256 + self.data[7]
        self.d['apm10'] = self.data[4] * 256 + self.data[5]
        self.d['apm100'] = self.data[8] * 256 + self.data[9]
        return self.d

    def animate(self, i, xs, y1s, y2s, y3s):
        self.read_data()
        print(self.d)
        xs.append(i)
        y1s.append(self.d['apm10'])
        y2s.append(self.d['apm25'])
        y3s.append(self.d['apm100'])

        # Limit x and y lists to 20 items
        xs = xs[-1000:]
        y1s = y1s[-1000:]
        y2s = y2s[-1000:]
        y3s = y3s[-1000:]

        # Draw x and y lists
        self.ax.clear()
        l1 = self.ax.plot(xs, y1s, 'r', label='PM10')[0]
        l2 = self.ax.plot(xs, y2s, 'g', label='PM25')[0]
        l3 = self.ax.plot(xs, y3s, 'b', label='PM100')[0]

        self.ax.legend([l1, l2, l3],
               labels= self.line_labels,
               loc='lower left') 


def main():
    # create parser
    parser = argparse.ArgumentParser(description="serial port")
    # add expected arguments
    parser.add_argument('--port', dest='port', required=False, default="/dev/cu.SLAB_USBtoUART")

    # parse args
    args = parser.parse_args()

    con = pmsA003(args.port)
    

if __name__ == '__main__':
    main()

