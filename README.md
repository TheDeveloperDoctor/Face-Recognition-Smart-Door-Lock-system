# Face-Recognition-Smart-Door-Lock-system

## Overview
This project implements an IoT-based dual authentication smart door lock system that uses **face recognition** and **QR code scanning** for secure access control. The system is powered by a **Raspberry Pi 4** and integrates with a **Flutter** mobile app to allow remote monitoring and control.

## Features
- Dual-factor authentication combining face recognition and QR code scanning.
- Real-time remote access control and lock status monitoring via mobile app.
- Local processing of face recognition using OpenCV on Raspberry Pi 4.
- Secure communication between mobile app and IoT device over Wi-Fi.
- User-friendly Flutter app for managing access permissions and receiving notifications.

## Hardware Components
- Raspberry Pi 4
- Camera Module (compatible with RPi)
- QR Code Scanner (USB or camera-based)
- Electronic Door Lock (e.g., solenoid lock or servo motor)
- Power supply and connecting wires

## Software Components
- Raspberry Pi OS (Linux-based)
- Python 3 with OpenCV for face recognition
- Flutter SDK for mobile app development
- REST API or Firebase for communication (customize based on your implementation)

## Installation & Setup

### Raspberry Pi
1. Install Raspberry Pi OS and enable camera support.
2. Install Python 3 and required libraries:
   ```bash
   sudo apt update
   sudo apt install python3-opencv python3-pip
   pip3 install flask numpy
