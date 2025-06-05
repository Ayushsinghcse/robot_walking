# Autonomous Wall-Finishing Robot Control System

This project provides a backend system for an autonomous wall-finishing robot, including path planning, data storage, and visualization.

## Features

- Coverage path planning for rectangular walls with obstacles
- REST API for trajectory management
- SQLite database storage
- Web-based visualization of paths
- Path playback functionality

## Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On Unix/macOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

## Running the Application

Start the FastAPI server:
```bash
uvicorn application.main:app --reload