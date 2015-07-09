#!/usr/bin/env python
import socket
import struct
import json
import sys
from robot import Robot
import random
import time
from robotControl import RobotControl

BUFF_SIZE = 4096
MCAST_GRP = '239.21.21.11'
MCAST_PORT = 2121
_mCastSock = None

def padding(str):
    nl = "\n\n"
    return nl + str + nl

def pp(str):
    print padding(str)

def getMCastSock():
    global _mCastSock
    if _mCastSock == None:
        mcs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        mcs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        mcs.bind((MCAST_GRP, MCAST_PORT))
        mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
        mcs.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        _mCastSock = mcs
    return _mCastSock


def doScan():
    m_sock = getMCastSock()
    robot_ip_tpl = m_sock.recvfrom(BUFF_SIZE)
    robot_json = robot_ip_tpl[0]
    ip_port_tpl = robot_ip_tpl[1]
    robotDataList = json.loads(robot_json)
    ip = ip_port_tpl[0]
    port = ip_port_tpl[1]

    robots = []
    for rd in robotDataList:
        robot = Robot(rd['name'], rd['id'], rd['personalityColor'], rd['firmwareVersion'], rd['state'], rd['type'], ip, port)
        robots.append(robot)

    return robots



def scanUntilFound(robotName):
    print "Scanning for robot named", robotName
    while True:
        for some_robot in doScan():
            if some_robot.name == robotName:
                pp( "!!! Found robot %s::%d at %s:%d" % (robotName, some_robot.robotId, some_robot.ip, some_robot.port))
                return some_robot


def scanAndListRobots(numScans = 5):
    scanCnt = 0
    robots = {}
    while scanCnt < numScans:
        scannedRobots = doScan()
        for r in scannedRobots:
            robots[r.robotId] = r
        time.sleep(2)
        scanCnt += 1
    return robots



print "Scanning for robots..."
apple = scanUntilFound('Drew')      #(raw_input("What is your robot's name? "))
apple.connect()

rbtCtrl = RobotControl(apple)
rbtCtrl.start()

apple.disconnect()


'''
apple.set_left_ear_rgb(1, 0, 0)
apple.set_right_ear_rgb(1, 0, 0)
apple.set_chest_rgb(1, 0, 0)
apple.pan_head(120)
apple.send_cmd_set()
time.sleep(4)
apple.lin_ang_body(50.0, 1.0, 30.0, 12)
time.sleep(3)
apple.send_cmd_set()
apple.disconnect()
'''
