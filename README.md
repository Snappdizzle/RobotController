# RobotController
Uses robot proxy app to control Dash with keyboard and mouse.

## Installation/Setup:
1. Install Python
1. Install Pygame
1. Check out the repository `git clone git@github.com:Snappdizzle/RobotController.git`

## Running the Program:
1. Type ```./main.py``` in terminal
1. Program will ```scan for robots...```
1. Type in the robot's name you wish to connect to
1. Program finds and connects to said robot
1. Opens Robot Control window
1. Use keyboard and mouse controls shown below to control robot.

## Controls:
- Use ```WASD``` controls to move Dash. You may also press multiple keys at once to combine movements. Use ```w``` or ```s```  with ```a``` or ```d``` to increase the angle that you are turning. (Easier to use than TANK CONTROLS):
  - w = Move forward
  - a = Turn left
  - s = Move Backwards
  - d = Turn right
  
- Use ```UOJL ('Tank')``` controls to move Dash. You may also press multiple keys at once to combine movements. Use ```U & O``` at the same time to move forward. Use ```J & L``` to move backward. (Harder to use than WASD CONTROLS):
  - u = Turn forwards clockwise in place
  - o = Turn forwards counter-clockwise in place
  - j = Turn backwards counter-clockwise in place
  - l = Turn backwards clockwise in place
  
- Use ``` f, c, and esc``` for other commands:
  - f = Go to fullscreen
  - c = Center robot's head and mouse cursor
  - esc = Exit program
  - Space = Change _right_ear_color_, _left_ear_color_, & _chest_color_ to RED 
  
- Use mouse to control head movements Moving mouse turns robot's head in that direction. ```Only works if cursor is on RobotControl Window ```
  - Left Mouse Click = Turn off _eye_light_
