import pygame
import math

# Initialize Pygame
pygame.init()

# Window setup
WIDTH, HEIGHT = 1000, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Robot Teleoperation")
# Font setup for indisplay text
font = pygame.font.Font(None, 36)
text = font.render("Key: ", True, (0, 0, 0))


# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
TRACE_COLOR = (0, 255, 0)  # Green trace

# User Inputs
try:
    max_speed = float(input("Enter Robot Max Speed (default 1): ") or 1)  # Default = 1
    turn_speed = float(input("Enter Turning Speed (default 1): ") or 1)  # Default = 1
except ValueError:
    print("Invalid input! Using default values.")
    max_speed = 1
    turn_speed = 1

# Robot setup
robot_x, robot_y = WIDTH // 2, HEIGHT // 2  # Start in the middle
robot_size = 40
heading_angle = 90  # Facing upwards
speed = 0  # Initial speed
acceleration = 0.2  # Acceleration rate
deceleration = 0.1  # Deceleration rate

# Store trace positions
trace_points = []

# Main loop
running = True
while running:
    screen.fill(WHITE)  # Clear screen

    # Draw trace
    for point in trace_points:
        pygame.draw.circle(screen, TRACE_COLOR, point, 2)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get key presses
    keys = pygame.key.get_pressed()

    # Rotation
    if keys[pygame.K_LEFT]:  
        heading_angle += turn_speed  # Turn left (counterclockwise)
        print("LEFT arrow pressed")
        text = font.render("Key: LEFT", True, (0, 0, 0))
        print(f"Turning LEFT (Angle: {heading_angle%360} degrees)")

    if keys[pygame.K_RIGHT]:  
        heading_angle -= turn_speed  # Turn right (clockwise)
        print("RIGHT arrow pressed")
        text = font.render("Key: RIGHT", True, (0, 0, 0))
        print(f"Turning RIGHT (Angle: {heading_angle%360} degrees)")

    # Acceleration & Deceleration
    if keys[pygame.K_UP]:  
        speed = min(max_speed, speed + acceleration)  # Accelerate forward
        print("UP arrow pressed")
        text = font.render("Key: UP", True, (0, 0, 0))
        print(f"Accelerating FORWARD X:{robot_x}, Y:{robot_y}")

    elif keys[pygame.K_DOWN]:  
        speed = max(-max_speed, speed - acceleration)  # Accelerate backward
        print("DOWN arrow pressed")
        text = font.render("Key: DOWN", True, (0, 0, 0))
        print(f"Accelerating BACKWARD X:{robot_x}, Y:{robot_y}")

    else:  
        if speed > 0:
            speed = max(0, speed - deceleration)  # Gradually slow down
        elif speed < 0:
            speed = min(0, speed + deceleration)  # Gradually slow down

    # Convert angle to movement
    robot_x += speed * math.cos(math.radians(heading_angle))
    robot_y -= speed * math.sin(math.radians(heading_angle))

    # Boundary conditions (keep robot inside window)
    robot_x = max(robot_size // 2, min(WIDTH - robot_size // 2, robot_x))
    robot_y = max(robot_size // 2, min(HEIGHT - robot_size // 2, robot_y))

    # Store trace
    trace_points.append((int(robot_x), int(robot_y)))

    # Draw the robot (rotating triangle)
    robot = pygame.Surface((robot_size, robot_size), pygame.SRCALPHA)
    pygame.draw.polygon(robot, RED, [(robot_size // 2, 0), (0, robot_size), (robot_size, robot_size)])
    rotated_robot = pygame.transform.rotate(robot, heading_angle - 90)  # Rotate for correct orientation

    # Get new rectangle position
    rect = rotated_robot.get_rect(center=(robot_x, robot_y))
    screen.blit(rotated_robot, rect.topleft)  # Draw robot
    screen.blit(text, (10, 10))  # Display key press

    pygame.display.update()  # Update display

pygame.quit()
