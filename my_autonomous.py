import pygame
import math
import random
import matplotlib.pyplot as plt
import numpy as np

# Initialize Pygame
pygame.init()

# Window setup
WIDTH, HEIGHT = 1000, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicle Maze Navigation")

# Font setup for display text
font = pygame.font.Font(None, 36)

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
TRACE_COLOR = (0, 255, 0)  # Green trace

# User Inputs
try:
    max_speed = float(input("Enter Robot Max Speed (default 5): ") or 5)
    turn_rate = float(input("Enter Turning Rate in degrees/unit time (default 2): ") or 2)
    sensor_range = float(input("Enter Sensor Range (default 150): ") or 150)
    sensitivity = float(input("Enter Sensitivity Factor (0.2-1.0, default 0.6): ") or 0.6)
except ValueError:
    print("Invalid input! Using default values.")
    max_speed = 5
    turn_rate = 2
    sensor_range = 150
    sensitivity = 0.6

# Robot setup
robot_x, robot_y = 100, 100  # Start position
robot_size = 40
heading_angle = 270  # Facing upwards
speed = 0  # Initial speed
acceleration = 0.2  # Acceleration rate
deceleration = 0.1  # Deceleration rate

# Sensor setup
left_sensor_angle = 45  # Degrees offset from heading
right_sensor_angle = -45  # Degrees offset from heading
left_sensor_reading = 0
right_sensor_reading = 0

# Maze walls - defined as line segments (x1, y1, x2, y2)
walls = []

# Function to add a wall segment
def add_wall(x1, y1, x2, y2):
    walls.append((x1, y1, x2, y2))

# Create outer boundary
add_wall(50, 50, 950, 50)    # Top wall
add_wall(50, 50, 50, 950)    # Left wall
add_wall(50, 950, 950, 950)  # Bottom wall
add_wall(950, 50, 950, 950)  # Right wall

# Add internal walls to create a maze
# Horizontal walls
add_wall(400, 200, 800, 200)
add_wall(200, 800, 600, 800)
add_wall(200, 400, 600, 400)
add_wall(400, 600, 800, 600)
# add_wall(350, 800, 950, 800)

# Vertical walls
add_wall(200, 50, 200, 800)
add_wall(800, 200, 800, 950)
# add_wall(500, 350, 500, 800)
# add_wall(650, 50, 650, 650)
# add_wall(800, 200, 800, 800)

# Start and finish positions
start_x, start_y = 100, 100
finish_x, finish_y = 900, 900

# Store trace positions
trace_points = []

# Performance metrics
collision_count = 0
start_time = pygame.time.get_ticks()
elapsed_time = 0
completed = False

# Helper functions for collision detection and sensor readings
def point_to_line_distance(x, y, x1, y1, x2, y2):
    # Calculate distance from point (x,y) to line segment (x1,y1)-(x2,y2)
    A = x - x1
    B = y - y1
    C = x2 - x1
    D = y2 - y1

    dot = A * C + B * D
    len_sq = C * C + D * D
    
    if len_sq == 0:  # Line segment is just a point
        return math.sqrt(A * A + B * B)
    
    # Calculate projection parameter
    param = dot / len_sq
    
    if param < 0:
        xx = x1
        yy = y1
    elif param > 1:
        xx = x2
        yy = y2
    else:
        xx = x1 + param * C
        yy = y1 + param * D
    
    return math.sqrt((x - xx) ** 2 + (y - yy) ** 2)

def line_intersection(x1, y1, x2, y2, x3, y3, x4, y4):
    # Calculate intersection of two line segments
    den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
    
    if den == 0:
        return None  # Lines are parallel
    
    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den
    ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den
    
    if 0 <= ua <= 1 and 0 <= ub <= 1:
        x = x1 + ua * (x2 - x1)
        y = y1 + ua * (y2 - y1)
        return (x, y)
    
    return None

def check_collision():
    # Check collision with any wall
    robot_radius = robot_size / 2
    for x1, y1, x2, y2 in walls:
        distance = point_to_line_distance(robot_x, robot_y, x1, y1, x2, y2)
        if distance < robot_radius:
            return True
    return False

def get_sensor_readings():
    global left_sensor_reading, right_sensor_reading
    
    # Calculate sensor positions and directions
    left_sensor_angle_rad = math.radians(heading_angle + left_sensor_angle)
    right_sensor_angle_rad = math.radians(heading_angle + right_sensor_angle)
    
    left_sensor_x = robot_x + math.cos(left_sensor_angle_rad) * (robot_size/2)
    left_sensor_y = robot_y - math.sin(left_sensor_angle_rad) * (robot_size/2)
    
    right_sensor_x = robot_x + math.cos(right_sensor_angle_rad) * (robot_size/2)
    right_sensor_y = robot_y - math.sin(right_sensor_angle_rad) * (robot_size/2)
    
    # Reset readings
    left_sensor_reading = 0
    right_sensor_reading = 0
    
    # Calculate sensor ray endpoints
    left_ray_end_x = left_sensor_x + math.cos(left_sensor_angle_rad) * sensor_range
    left_ray_end_y = left_sensor_y - math.sin(left_sensor_angle_rad) * sensor_range
    
    right_ray_end_x = right_sensor_x + math.cos(right_sensor_angle_rad) * sensor_range
    right_ray_end_y = right_sensor_y - math.sin(right_sensor_angle_rad) * sensor_range
    
    # Check for ray intersection with walls
    left_min_distance = sensor_range
    right_min_distance = sensor_range
    
    for wall_x1, wall_y1, wall_x2, wall_y2 in walls:
        # Check left sensor
        left_intersection = line_intersection(
            left_sensor_x, left_sensor_y, left_ray_end_x, left_ray_end_y,
            wall_x1, wall_y1, wall_x2, wall_y2
        )
        
        if left_intersection:
            ix, iy = left_intersection
            distance = math.sqrt((left_sensor_x - ix)**2 + (left_sensor_y - iy)**2)
            if distance < left_min_distance:
                left_min_distance = distance
        
        # Check right sensor
        right_intersection = line_intersection(
            right_sensor_x, right_sensor_y, right_ray_end_x, right_ray_end_y,
            wall_x1, wall_y1, wall_x2, wall_y2
        )
        
        if right_intersection:
            ix, iy = right_intersection
            distance = math.sqrt((right_sensor_x - ix)**2 + (right_sensor_y - iy)**2)
            if distance < right_min_distance:
                right_min_distance = distance
    
    # Convert distances to readings (closer = higher reading)
    if left_min_distance < sensor_range:
        left_sensor_reading = max(0, 1 - (left_min_distance / sensor_range))
    
    if right_min_distance < sensor_range:
        right_sensor_reading = max(0, 1 - (right_min_distance / sensor_range))
    
    # Apply sensitivity factor
    left_sensor_reading *= sensitivity
    right_sensor_reading *= sensitivity
    
    return left_sensor_reading, right_sensor_reading

def check_finish():
    # Check if robot has reached the finish
    distance_to_finish = math.sqrt((robot_x - finish_x)**2 + (robot_y - finish_y)**2)
    if distance_to_finish < 30:  # Finish radius
        return True
    return False

# Main loop
running = True
auto_mode = True
mode_text = "Mode: Auto"

# For sensitivity analysis
sensitivity_values = [0.2, 0.4, 0.6, 0.8, 1.0]
results = []
current_sensitivity_index = 0
current_trial = 0
max_trials = len(sensitivity_values)
timeout = 90000  # 90 seconds timeout per trial

def run_sensitivity_analysis():
    global robot_x, robot_y, heading_angle, speed, trace_points, collision_count, start_time, elapsed_time, completed, sensitivity
    
    sensitivity_values = [0.2, 0.4, 0.6, 0.8, 1.0]
    results = []
    
    for sens in sensitivity_values:
        print(f"\nRunning trial with sensitivity = {sens}")
        sensitivity = sens
        
        # Reset robot
        robot_x, robot_y = start_x, start_y
        heading_angle = 270
        speed = 0
        trace_points = []
        collision_count = 0
        start_time = pygame.time.get_ticks()
        elapsed_time = 0
        completed = False
        
        # Run simulation in auto mode
        auto_mode = True
        trial_running = True
        timeout = 90000  # 90 seconds timeout
        
        while trial_running and pygame.time.get_ticks() - start_time < timeout:
            # Process events to keep window responsive
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            
            # Get sensor readings
            left_reading, right_reading = get_sensor_readings()
            
            # Braitenberg vehicle behavior
            turn_amount = (right_reading - left_reading) * turn_rate
            heading_angle += turn_amount
            
            obstacle_factor = max(left_reading, right_reading)
            target_speed = max_speed * (1 - obstacle_factor * 0.8)
            
            if speed < target_speed:
                speed = min(target_speed, speed + acceleration)
            elif speed > target_speed:
                speed = max(target_speed, speed - deceleration)
            
            # Move robot
            old_x, old_y = robot_x, robot_y
            robot_x += speed * math.cos(math.radians(heading_angle))
            robot_y -= speed * math.sin(math.radians(heading_angle))
            
            # Check for collision
            if check_collision():
                robot_x, robot_y = old_x, old_y
                heading_angle += random.uniform(-45, 45)
                speed = -speed * 0.5
                collision_count += 1
            
            # Check if finished
            if check_finish():
                elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
                trial_running = False
                completed = True
                print(f"Completed with sensitivity {sens}: Time = {elapsed_time:.2f}s, Collisions = {collision_count}")
            
            # Update display for visualization
            screen.fill(WHITE)
            
            # Draw trace
            for point in trace_points:
                pygame.draw.circle(screen, TRACE_COLOR, point, 2)
            
            # Draw maze walls
            for x1, y1, x2, y2 in walls:
                pygame.draw.line(screen, BLACK, (x1, y1), (x2, y2), 3)
            
            # Draw start and finish
            pygame.draw.circle(screen, GREEN, (start_x, start_y), 20, 2)
            pygame.draw.circle(screen, RED, (finish_x, finish_y), 20, 2)
            
            # Draw robot
            robot = pygame.Surface((robot_size, robot_size), pygame.SRCALPHA)
            pygame.draw.polygon(robot, RED, [(robot_size // 2, 0), (0, robot_size), (robot_size, robot_size)])
            rotated_robot = pygame.transform.rotate(robot, heading_angle - 90)
            rect = rotated_robot.get_rect(center=(robot_x, robot_y))
            screen.blit(rotated_robot, rect.topleft)
            
            # Draw sensor rays
            left_sensor_angle_rad = math.radians(heading_angle + left_sensor_angle)
            right_sensor_angle_rad = math.radians(heading_angle + right_sensor_angle)
            
            left_sensor_x = robot_x + math.cos(left_sensor_angle_rad) * (robot_size/2)
            left_sensor_y = robot_y - math.sin(left_sensor_angle_rad) * (robot_size/2)
            
            right_sensor_x = robot_x + math.cos(right_sensor_angle_rad) * (robot_size/2)
            right_sensor_y = robot_y - math.sin(right_sensor_angle_rad) * (robot_size/2)
            
            left_ray_end_x = left_sensor_x + math.cos(left_sensor_angle_rad) * sensor_range
            left_ray_end_y = left_sensor_y - math.sin(left_sensor_angle_rad) * sensor_range
            
            right_ray_end_x = right_sensor_x + math.cos(right_sensor_angle_rad) * sensor_range
            right_ray_end_y = right_sensor_y - math.sin(right_sensor_angle_rad) * sensor_range
            
            left_color = (int(255 * left_reading), 0, 0)
            right_color = (int(255 * right_reading), 0, 0)
            
            pygame.draw.line(screen, left_color, (left_sensor_x, left_sensor_y), (left_ray_end_x, left_ray_end_y), 2)
            pygame.draw.line(screen, right_color, (right_sensor_x, right_sensor_y), (right_ray_end_x, right_ray_end_y), 2)
            
            # Display information
            current_time = (pygame.time.get_ticks() - start_time) / 1000
            info_text = [
                f"Mode: Auto (Analysis)",
                f"Sensitivity: {sensitivity:.2f}",
                f"Speed: {speed:.2f}",
                f"Time: {current_time:.2f}s",
                f"Collisions: {collision_count}"
            ]
            
            for i, text in enumerate(info_text):
                text_surface = font.render(text, True, BLACK)
                screen.blit(text_surface, (10, 10 + i * 30))
            
            pygame.display.update()
            
            # Store trace
            trace_points.append((int(robot_x), int(robot_y)))
            
            # Check for timeout
            if pygame.time.get_ticks() - start_time > timeout:
                elapsed_time = timeout / 1000
                trial_running = False
                print(f"Trial timed out with sensitivity {sens}")
        
        # Record results
        performance_score = elapsed_time + collision_count * 2  # Penalize collisions more
        results.append((sens, elapsed_time, collision_count, performance_score))
    
    # Find best sensitivity
    best_sensitivity = min(results, key=lambda x: x[3])
    print("\nSensitivity Analysis Results:")
    print("Sensitivity | Time (s) | Collisions | Performance Score")
    print("-" * 50)
    for sens, time, collisions, score in results:
        print(f"{sens:.1f}        | {time:.2f}    | {collisions}         | {score:.2f}")
    print(f"\nBest sensitivity: {best_sensitivity[0]} (Score: {best_sensitivity[3]:.2f})")
    
    # Plot results
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        sens_values = [r[0] for r in results]
        times = [r[1] for r in results]
        collisions = [r[2] for r in results]
        scores = [r[3] for r in results]
        
        plt.figure(figsize=(12, 8))
        
        # Plot completion time
        plt.subplot(3, 1, 1)
        plt.plot(sens_values, times, 'bo-')
        plt.xlabel('Sensitivity')
        plt.ylabel('Completion Time (s)')
        plt.title('Effect of Sensitivity on Completion Time')
        plt.grid(True)
        
        # Plot collision count
        plt.subplot(3, 1, 2)
        plt.plot(sens_values, collisions, 'ro-')
        plt.xlabel('Sensitivity')
        plt.ylabel('Collision Count')
        plt.title('Effect of Sensitivity on Collision Count')
        plt.grid(True)
        
        # Plot performance score
        plt.subplot(3, 1, 3)
        plt.plot(sens_values, scores, 'go-')
        plt.xlabel('Sensitivity')
        plt.ylabel('Performance Score')
        plt.title('Effect of Sensitivity on Overall Performance')
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('sensitivity_analysis.png')
        print("Analysis graphs saved to 'sensitivity_analysis.png'")
        
    except ImportError:
        print("Matplotlib not available. Skipping graph generation.")


while running:
    screen.fill(WHITE)  # Clear screen
    
    # Draw trace
    for point in trace_points:
        pygame.draw.circle(screen, TRACE_COLOR, point, 2)
    
    # Draw maze walls
    for x1, y1, x2, y2 in walls:
        pygame.draw.line(screen, BLACK, (x1, y1), (x2, y2), 3)
    
    # Draw start and finish
    pygame.draw.circle(screen, GREEN, (start_x, start_y), 20, 2)
    pygame.draw.circle(screen, RED, (finish_x, finish_y), 20, 2)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                print("Starting sensitivity analysis...")
                run_sensitivity_analysis()
                print("Analysis complete!")
    
    # Get sensor readings
    left_reading, right_reading = get_sensor_readings()
    
    if auto_mode:
        # Braitenberg vehicle behavior (cross-wired)
        # Right sensor controls left wheel, left sensor controls right wheel
        # This creates obstacle avoidance behavior
        
        # Calculate turn based on sensor difference
        turn_amount = (right_reading - left_reading) * turn_rate
        heading_angle += turn_amount
        
        # Adjust speed based on sensor readings
        # Slow down when obstacles are detected
        obstacle_factor = max(left_reading, right_reading)
        target_speed = max_speed * (1 - obstacle_factor * 0.8)
        
        if speed < target_speed:
            speed = min(target_speed, speed + acceleration)
        elif speed > target_speed:
            speed = max(target_speed, speed - deceleration)
    
    # Convert angle to movement
    old_x, old_y = robot_x, robot_y
    robot_x += speed * math.cos(math.radians(heading_angle))
    robot_y -= speed * math.sin(math.radians(heading_angle))
    
    # Check for collision
    if check_collision():
        # Collision response - back up and turn randomly
        robot_x, robot_y = old_x, old_y
        heading_angle += random.uniform(-45, 45)
        speed = -speed * 0.5  # Reverse at half speed
        collision_count += 1
        print(f"Collision! Count: {collision_count}")
    
    # Check if finished
    if check_finish() and not completed:
        completed = True
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000  # Convert to seconds
        print(f"Maze completed! Time: {elapsed_time:.2f} seconds, Collisions: {collision_count}")
        running = False
    
    # Store trace
    trace_points.append((int(robot_x), int(robot_y)))
    
    # Draw the robot (rotating triangle)
    robot = pygame.Surface((robot_size, robot_size), pygame.SRCALPHA)
    pygame.draw.polygon(robot, RED, [(robot_size // 2, 0), (0, robot_size), (robot_size, robot_size)])
    rotated_robot = pygame.transform.rotate(robot, heading_angle - 90)
    rect = rotated_robot.get_rect(center=(robot_x, robot_y))
    screen.blit(rotated_robot, rect.topleft)
    
    # Draw sensor rays
    left_sensor_angle_rad = math.radians(heading_angle + left_sensor_angle)
    right_sensor_angle_rad = math.radians(heading_angle + right_sensor_angle)
    
    left_sensor_x = robot_x + math.cos(left_sensor_angle_rad) * (robot_size/2)
    left_sensor_y = robot_y - math.sin(left_sensor_angle_rad) * (robot_size/2)
    
    right_sensor_x = robot_x + math.cos(right_sensor_angle_rad) * (robot_size/2)
    right_sensor_y = robot_y - math.sin(right_sensor_angle_rad) * (robot_size/2)
    
    left_ray_end_x = left_sensor_x + math.cos(left_sensor_angle_rad) * sensor_range
    left_ray_end_y = left_sensor_y - math.sin(left_sensor_angle_rad) * sensor_range
    
    right_ray_end_x = right_sensor_x + math.cos(right_sensor_angle_rad) * sensor_range
    right_ray_end_y = right_sensor_y - math.sin(right_sensor_angle_rad) * sensor_range
    
    # Draw sensor rays with color based on reading intensity
    left_color = (int(255 * left_reading), 0, 0)
    right_color = (int(255 * right_reading), 0, 0)
    
    pygame.draw.line(screen, left_color, (left_sensor_x, left_sensor_y), (left_ray_end_x, left_ray_end_y), 2)
    pygame.draw.line(screen, right_color, (right_sensor_x, right_sensor_y), (right_ray_end_x, right_ray_end_y), 2)
    
    # Display information
    if not completed:
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
    
   
    # Add to your info_text list:
    info_text = [
        f"{mode_text}",
        f"Speed: {speed:.2f}",
        f"Sensitivity: {sensitivity:.2f}",
        f"Time: {elapsed_time:.2f}s",
        f"Collisions: {collision_count}",
        "Press A to run sensitivity analysis"
    ]

    
    for i, text in enumerate(info_text):
        text_surface = font.render(text, True, BLACK)
        screen.blit(text_surface, (10, 10 + i * 30))
    
    pygame.display.update()
    
    # Check for timeout
    if auto_mode and elapsed_time > timeout and not completed:
        print(f"Trial timed out after {timeout/1000} seconds")
        completed = True

pygame.quit()
