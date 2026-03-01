# AirDraw Pastel Edition

A computer vision project by **Navyatha G** using **Python, OpenCV, MediaPipe, and NumPy**.

## Overview

**AirDraw Pastel Edition** is a hand gesture–based virtual drawing application that lets the user draw in the air using a webcam. The system tracks hand landmarks in real time, identifies simple gestures, and allows the user to draw, erase, change colors, adjust brush size, undo, save, and clear the canvas.

The project begins with a short intro screen displaying:

**Computer Vision Project by Navyatha G**

After that, the app launches into the main drawing interface.

## Features

- Real-time **hand tracking** using MediaPipe
- **Air drawing** using the index finger
- Soft **pastel color palette**
- **Brush size selection**: Small, Medium, Large
- **Eraser mode**
- **Undo**, **Save**, and **Clear** actions
- **Hold gestures** for save and clear to reduce accidental triggers
- Smooth stroke drawing
- White drawing canvas with softened webcam background
- Animated intro splash screen
- On-screen toolbar and action buttons

## Technologies Used

- **Python**
- **OpenCV**
- **MediaPipe**
- **NumPy**

## How It Works

The webcam captures live video input, and MediaPipe detects hand landmarks from each frame. Based on the relative positions of the fingers, the application determines whether the user is drawing, selecting tools, saving, or clearing the screen.

The drawing is done on a white canvas layer, which is displayed on top of a softened webcam feed to create a cleaner visual appearance.

## Controls

### Hand Gestures

- **Index finger only** → Draw
- **Index + middle finger** → Select colors, brush size, or action buttons
- **Hold all 5 fingers up** → Clear canvas
- **Hold thumb + index up** → Save drawing

### Keyboard Shortcuts

- **u** → Undo
- **c** → Clear canvas
- **s** → Save drawing
- **q** / **Enter** / **Esc** → Quit application

## Toolbar Options

### Colors
- Pink
- Mint
- Blue
- Lavender
- Peach

### Tools
- Eraser

### Brush Sizes
- Small
- Medium
- Large

### Actions
- Undo
- Save
- Clear

## Project Structure

```text
Computer-Vision-proj1/
│── main.py
│── README.md
│── .gitignore
│── saved_drawings/


