# Braitenberg_vehicle_behavior
 This project implements a Braitenberg vehicle simulation with both teleoperation and autonomous navigation capabilities. The robot uses sensors to detect obstacles in a maze environment and implements cross-wired Braitenberg behavior for obstacle avoidance. The simulation allows for parameter tuning to analyze the impact of sensitivity on navigation performance.
## Features
- Manual teleoperation using arrow keys
- Autonomous navigation with Braitenberg vehicle behavior
- Sensitivity analysis with performance metrics
- Visualization of sensor readings and robot path
- Containerized application using Docker

## Autonomous Behavior
The robot implements a cross-wired Braitenberg vehicle behavior where:
- Two sensors positioned at 45° angles detect obstacles
- Sensor readings influence turning behavior (right sensor affects left wheel, left sensor affects right wheel)
- The robot slows down when approaching obstacles
- The sensitivity parameter controls how strongly the robot responds to sensor readings

### Sensitivity Parameter
The sensitivity parameter (0.2-1.0) determines how strongly the robot reacts to detected obstacles:
- Higher sensitivity: More aggressive turning and earlier response to obstacles
- Lower sensitivity: More gradual turning and later response to obstacles

The analysis feature tests different sensitivity values to find the optimal setting that minimizes both completion time and collision count.
## Performance Metrics
The sensitivity analysis evaluates robot performance using:
- Completion time: How long it takes to navigate from start to finish
- Collision count: Number of times the robot collides with maze walls
- Performance score: A weighted combination (time + collisions*2) where lower is better

The analysis generates graphs showing how these metrics vary with different sensitivity values.

## Troubleshooting
- If you encounter display issues, ensure X11 forwarding is properly configured
- If the container exits immediately, check that pygame is properly installed
- For performance issues, try adjusting the robot speed and sensor range parameters

# How to run this repository
### Install docker
```bash
sudo apt update
sudo apt install docker.io
sudo usermod -aG docker $USER   # Add yourself to the docker group
newgrp docker  # Apply group change (or logout & re-login)
```
### Clone this repository
```bash
git clone git@github.com:keyurborad5/Braitenberg_vehicle_behavior.git
```
### Build the docker Image
```bash
cd ~/Braitenberg_vehicle_behavior/
#Look for atleast these three files in the folder
#my_teleoperation.py, my_autonomous.py and Dockerfile
ls 
docker build -t simulation_image:latest .
# Check for the built image named: simulation_image:latest
docker images
#now you allow docker to connect with your X server
xhost +local:docker
```

### Run the container with the application
```bash
# First we will run Teleoperation in our container
docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix --name teleop_container simulation_image:latest my_teleoperation.py
# Set the robot speed or just press Enter for DEFAULT speed
# Set the Robot angular speed or just Press Enter for DEFAULT speed
# Use Arrow keys to Teleoperate the robot and you can see the logs publishing on the terminal as well

# Once done exploring the Teleoperation just CLOSE the GUI
# Now, We will run Autonomous behaviour in our contrainer
docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix --name autonomous_container simulation_image:latest my_autonomous.py
# Now terminal will ask some user input values. 
# Enter it of your choice or press ENTER for DEFAULT values selection
# Enter Robot Max Speed (default 5): 5
# Enter Turning Rate in degrees/unit time (default 2): 1
# Enter Sensor Range (default 150): 200
# Enter Sensitivity Factor (0.2-1.0, default 0.6): 0.8
```
Once Start the ROBOT will start to move autonomously based on the above set parameter.
#### EXIT
Container will be closed once the robot reaches the goal location or you can close it by closing the GUI application

### Starting Analysis
Here I have tried to automate the analysis of the robot in a given maze to reach at the goal location in given predefined time that is 90 sec. Parameter I am varying for this analysis is sensitivity, which is being varied from 0.2 to 1.
```bash
# Start the Autonomous behavious once again
docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix --name autonomous_container simulation_image:latest my_autonomous.py

# Now press A from your keyboard
```
It will start the analysis and iterate it for 5 different sensitivity values with given set speed and angular speed.
#### EXIT
Once all the 5 iterations are complete a report will be printed on the terminal as well as a .png file will also be generated inside the container showing the graphical interpretation 

#### NOTE : DONOT CLOSE THE GUI BEFORE COPYING THE GRAPH IMAGE
```bash
# To downlaod this analysis graph image to your local system open another terminal and go to your desired folder
docker cp autonomous_container:/app/sensitivity_analysis.png ./sensitivity_analysis.png

# you will get this output depending on your folder location.
Successfully copied 84kB to /home/ubuntu/sensitivity_analysis.png
```
Now you can access this image from your local system.
Now exit by closing the GUI.


