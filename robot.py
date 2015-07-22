import json
import socket
import time
import logging
from threading import Timer, RLock
#Imports all important files and systems

#---------------------------------#
#-make methods that hold commands-#
#---------------------------------#
message = "You are connected at:"

BUFF_SIZE = 4096
FORMAT = '[%(levelname)5s] %(asctime)-15s %(filename)s:%(lineno)d %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('robot')
logger.setLevel(logging.DEBUG)

class Robot(object):
    """created a class that holds robots information"""

    def __init__(self, name, robotId, personalityColor, firmwareVersion, state, rType, ip, port):
        """Init Function that sets all of the important variables"""
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
        self.seeRobot = False
        self.isButton1Pressed = False
        self.isButton2Pressed = False
        self.isButton3Pressed = False
        self.isButtonMainPressed = False

    def isConnected(self):
        """Function that tells robot it is connected"""
        return self.socket != None

    def notConnected(self):
        """Function that tells the robot thaat it isnt connected"""
        return not self.isConnected()

    def waitForConnectMsg(self):
        """Function that tells the robot to wait for the connection message to print"""
        cnctMsgFound = False
        while not cnctMsgFound:
            nextMsg = self.popMessage()
            if nextMsg != None:
                logger.info("Connected to robot: %s" % self.name)
                cnctMsgFound = True
            time.sleep(1)


    def connect(self):
        """Function that tells the robot to connect to a unicast socket with the robot and send information. Also sends a connect messagge to the proxy app."""
        logger.debug("Opening socket to robot: (%d) %s @ %s:%d" % (self.robotId, self.name, self.ip, self.port))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))
        conn_msg = {"robotId": self.robotId,
                    "userAgentName":"LongCat",
                    "userAgentVersion":"1.1.1.1"
                    }
        conn_json = json.dumps(conn_msg) + '\n'
        logger.debug('connection data sent')
        self.socket.sendall(conn_json)
        self.schedMsgReader()
        self.waitForConnectMsg()


    def disconnect(self):
        """Function that disconnects your robot"""
        self.socket.close()
        self.socket = None

    def send_cmd_set(self):
        """Function that sends a set of commands to your robot, which then will act them out."""
        if self.notConnected():
            print "!!! Robot cannot send command because it isn't connected."
            return

        if len(self.cmd_dict) > 0:
            cmd_set = {"typ":"RobotCommandSet","data":self.cmd_dict}
            json_cmd = json.dumps(cmd_set) + '\n'
            logger.debug ("sending command set: %s",  json_cmd)
            self.socket.sendall(json_cmd)
            self.cmd_dict = {}
#---------------------------------------------------------------------------------------------------------------------------------------------#
#-All of the following commands are built in to the robot. Have there own unique IDs, and send themselves to a command set when you call them-#
#---------------------------------------------------------------------------------------------------------------------------------------------#

    def set_left_ear_rgb(self, r, g, b):
        """Left ear color function: takes 0-1 values for r:red, g:green, & b:blue in that order. 102 is the robot has built in commandID's which is what the 102 is for, so the robot knows 102 = set left ear color. Sends command to command set."""
        self.cmd_dict[102] = {"r":r, "g":g, "b":b}

    def set_right_ear_rgb(self, r, g, b):
        """Right ear color function takes same values as left ear color. ID: 103"""
        self.cmd_dict[103] = {"r":r, "g":g, "b":b}

    def set_chest_rgb(self, r, g, b):
        """Chest color function takes same values as left and right ear color. ID:104"""
        self.cmd_dict[104] = {"r":r, "g":g, "b":b}

    def pan_head(self, degree):
        """Function that turns head left to right. takes a degrees parameter. range from (-120(leftmost) to 120(rightmost)) ID: 203"""
        self.cmd_dict[203] = {"degree":degree}

    def tilt_head(self, degree):
        """Function that tilts heaad up and down. takes a degrees parameter. range from (-20(Downmost) to 7.5(upmost)) ID: 202"""
        self.cmd_dict[202] = {"degree":degree}

    def set_wheels(self, left_whl_velo, right_whl_velo):
        """Function that sets wheel speed. Takes a right and left wheel velocity parameter. Infinite range negative and positive, negative = backwards, positive = forwards. You can set each wheel at different velocities if you like. ID:211"""
        self.cmd_dict[211] = {"right_cm_s": right_whl_velo, "left_cm_s": left_whl_velo}

    def lin_ang_body(self, speed_linear, speed_angular_rad, acc_linear, acc_angular):
        """function that sets speed, intensity of turn, acceleration rate of speed and turn speed. speed (infinite neg. and pos.), turn (-12(left tight turn) to 12(right tight turn)), acceleration of speed and turn speed (1-1000). ID:204"""
        self.cmd_dict[204] = {"linear_cm_s":speed_linear, "angular_cm_s":speed_angular_rad, "linear_acc_cm_s_s":acc_linear, "angular_acc_deg_s_s":acc_angular}

    def set_eye(self, eye_on):
        """Function that sets eye lights on or off.   ID:100"""
        self.cmd_dict[100] = {"index": [eye_on for x in range(0, 12)]}

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Robot(id: %d, name: %s, personalityColor: %s, isConnected: %s)" % (self.robotId, self.name, self.personalityColor, self.isConnected())

    def readAndSched(self):
        """Function  that reads messages recieved from robot, Keeps reading data constantly keeping you up to date with robot."""
        try:
            logger.debug("socket.recv(%d)" % BUFF_SIZE)
            self.msgBuffer += self.socket.recv(BUFF_SIZE)
            logger.debug(self.msgBuffer)
            index = self.msgBuffer.find('\n')
            logger.debug("index: %d, msgBuffer length: %d", index, len(self.msgBuffer))
            while index > 0:
                msgStr = self.msgBuffer[0:index]
                self.msgBuffer = self.msgBuffer[index + 1:]
                self.msgCnt += 1
                msg = json.loads(msgStr)
                self.addMessage(msg)
                index = self.msgBuffer.find('\n')
        except err:
            logger.error('Error reading from socket: %s', err.message)

        self.schedMsgReader()

    def handleSensorSet(self, sensorSet):
        if msg['sensorId'] == '1001':
            self.isButtonMainPressed = msg['pressed']
        if msg['sensorId'] == '1002':
            self.isbutton1Pressed = msg['Pressed']
        if msg['sensorId'] == '1003':
            self.isButton2Pressed = msg['Pressed']
        if msg['sensorId'] == '1004':
            self.isButton3Pressed = msg['Pressed']
        

    def addMessage(self, msg):
        """Function that only reads last 10 messages, taking one off the end and adding one to the beginning"""
        with self.msgLock:
            self.msgs.insert(0,msg)
            self.msgs = self.msgs[0:10]
            if msg['event'] == 'RobotSensortSetUpdated':
                handleSensorSet(msg['data']['sensorSet'])
            return len(self.msgs)

    def popMessage(self):
        """Function that pops a message off the list after it is read."""
        with self.msgLock:
            try:
                return self.msgs.pop()
            except IndexError:
                return None

    def schedMsgReader(self):
        """Function that starts reading messages and waits a certain amount of time then reads another."""
        if self.msgReader != None:
            self.msgReader.cancel()
        self.msgReader = Timer(.03, self.readAndSched)
        self.msgReader.setName("%s-msg-reader" % self.name)
        self.msgReader.setDaemon(True)
        self.msgReader.start()
