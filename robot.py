import json
import socket
import time
import logging
from threading import Timer, RLock
#---------------------------------#
#-make methods that hold commands-#
#---------------------------------#
message = "You are connected at:"

BUFF_SIZE = 4096
FORMAT = '[%(levelname)5s] %(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('robot')
logger.setLevel(logging.DEBUG)

class Robot(object):
    """ A class for robots"""

    def __init__(self, name, robotId, personalityColor, firmwareVersion, state, rType, ip, port):
        self.name = name
        self.robotId = robotId
        self.firmwareVersion = firmwareVersion
        self.personalityColor = personalityColor
        self.state = state
        self.robotType = rType
        self.ip = ip
        self.port = port
        self.cmd_dict = {}
        self.sensors = {}
        self.socket = None
        self.sensorTimer = None
        self.msgCnt = 0
        self.msgBuffer = ""
        self.msgs = []
        self.msgReader = None
        self.msgLock = RLock()
        self.MIN_HEAD_PAN = -120
        self.MAX_HEAD_PAN = 120
        self.MAX_HEAD_TILT = 30
        self.MIN_HEAD_TILT = -17

    def isConnected(self):
        return self.socket != None

    def notConnected(self):
        return not self.isConnected()

    def waitForConnectMsg(self):
        cnctMsgFound = False
        while not cnctMsgFound:
            nextMsg = self.popMessage()
            if nextMsg != None:
                logger.info("Connected to robot: %s" % self.name)
                cnctMsgFound = True
            time.sleep(1)


    def connect(self):
        logger.debug("Opening socket to robot: (%d) %s @ %s:%d" % (self.robotId, self.name, self.ip, self.port))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))
        conn_msg = {"robotId": self.robotId,
                    "userAgentName":"LongCat",
                    "userAgentVersion":"1.1.1.1"
                    }
        conn_json = json.dumps(conn_msg) + '\n'
        logger.debug('sending connection data: %s' % conn_json)
        self.socket.sendall(conn_json)
        logger.debug('connection data sent')
        self.startMsgReader()
        self.waitForConnectMsg()


    def disconnect(self):
        self.socket.close()
        self.socket = None

    def send_cmd_set(self):
        if self.notConnected():
            print "!!! Robot cannot send command because it isn't connected."
            return

        if len(self.cmd_dict) > 0:
            cmd_set = {"typ":"RobotCommandSet","data":self.cmd_dict}
            json_cmd = json.dumps(cmd_set) + '\n'
            logger.debug ("sending command set: %s",  json_cmd)
            self.socket.sendall(json_cmd)
            self.cmd_dict = {}

    def set_left_ear_rgb(self, r, g, b):
        self.cmd_dict[102] = {"r":r, "g":g, "b":b}

    def set_right_ear_rgb(self, r, g, b):
        self.cmd_dict[103] = {"r":r, "g":g, "b":b}

    def set_chest_rgb(self, w, d, x):
        self.cmd_dict[104] = {"r":w, "g":d, "b":x}

    def pan_head(self, degree):
        self.cmd_dict[203] = {"degree":degree}

    def tilt_head(self, degree):
        self.cmd_dict[202] = {"degree":degree}

    def lin_ang_body(self, speed_linear, speed_angular_rad, acc_linear, acc_angular):
        self.cmd_dict[204] = {"linear_cm_s":speed_linear, "angular_cm_s":speed_angular_rad, "linear_acc_cm_s_s":acc_linear, "angular_acc_deg_s_s":acc_angular}

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Robot(id: %d, name: %s, personalityColor: %s, isConnected: %s)" % (self.robotId, self.name, self.personalityColor, self.isConnected())

    def readNextMsg(self):
        logger.debug("socket.recv(%d)" % BUFF_SIZE)
        self.msgBuffer += self.socket.recv(BUFF_SIZE)
        index = self.msgBuffer.find('\n')
        logger.debug("index: %d, msgBuffer length: %d", index, len(self.msgBuffer))
        while index > 0:
            msgStr = self.msgBuffer[0:index]
            self.msgBuffer = self.msgBuffer[index + 1:]
            self.msgCnt += 1
            msg = json.loads(msgStr)
            logger.debug("eventType: %s", msg['event'])
            self.addMessage(msg)
            index = self.msgBuffer.find('\n')

    def addMessage(self, msg):
        with self.msgLock:
            self.msgs.insert(0,msg)
            self.msgs = self.msgs[0:10]
            return len(self.msgs)

    def popMessage(self):
        with self.msgLock:
            try:
                return self.msgs.pop()
            except IndexError:
                return None

    def startMsgReader(self):
        if self.msgReader != None:
            self.msgReader.cancel()
        self.msgReader = Timer(.03, self.readNextMsg)
        self.msgReader.setName("%s-msg-reader" % self.name)
        self.msgReader.setDaemon(True)
        self.msgReader.start()
