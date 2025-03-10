# Use Python 3.10.12 as base image
FROM python:3.10.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for pygame
RUN apt-get update && apt-get install -y \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    pygame \
    matplotlib \
    numpy

# Copy your Python scripts
COPY my_teleoperation.py /app/
COPY my_autonomous.py /app/

# Set display environment variable for pygame
ENV SDL_VIDEODRIVER=x11

# Command to" run when container starts
ENTRYPOINT ["python"]

# Default script to run (can be overridden)
# If you want to enter the container and run commands manually 
# then comment the Entrypoint and uncomment the CMD
# CMD ["bash"]
