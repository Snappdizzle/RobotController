#!/usr/bin/env python
import socket
import struct
import json
import sys
from robot import Robot
import random
import time
from robotControl import RobotControl
"""Import all important files and systems"""

BUFF_SIZE = 4096
MCAST_GRP = '239.21.21.11'
MCAST_PORT = 2121
_mCastSock = None

def padding(str):
    """Function that creates new lines between print statements"""
    nl = "\n\n"
    return nl + str + nl

def pp(str):
    print padding(str)

def getMCastSock():
    """Function that creates and opens a Multicast socket letting you find robots to connect to"""
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
    """Function that scans for robots and lists them"""
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
    """Function that scans for robots unitl it finds a robot with a matching name yoou entered"""
    print "Scanning for robot named", robotName
    while True:
        for some_robot in doScan():
            if some_robot.name == robotName:
                pp( "!!! Found robot %s::%d at %s:%d" % (robotName, some_robot.robotId, some_robot.ip, some_robot.port))
                return some_robot


def scanAndListRobots(numScans = 5):
    """function that scans for robots a given amount of times, and lists all robots found within that nuber of scans (If you want more scans change 'numScans' to a different value)"""
    scanCnt = 0
    robots = {}
    while scanCnt < numScans:
        scannedRobots = doScan()
        for r in scannedRobots:
            robots[r.robotId] = r
        time.sleep(2)
        scanCnt += 1
    return robots.values()


print "Scanning for available robots ..."
fndRbts = scanAndListRobots(3)

print "--------------------------------"
print "Found robots: "
print "--------------------------------"
for idx, r in enumerate(fndRbts, start=1):
    print idx, "-----> ", r.name

print ""
tgtRobotName = raw_input("Please enter your robot's name: ")
print "Scanning for robots..."
yourRobot = scanUntilFound(tgtRobotName)
yourRobot.connect()

rbtCtrl = RobotControl(yourRobot)
rbtCtrl.start()

yourRobot.disconnect()
