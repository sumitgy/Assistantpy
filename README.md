# Jarvis browser assistant

A small Hindi-friendly Jarvis web app. It uses only Python's built-in server modules, so there is no Flask or other Python package to install. It runs on a phone or computer browser and is configured for Render.

## Run on your computer

1. Install Python 3.10 or newer.
2. In this folder, run `py -m venv .venv`.
3. Activate it with `.venv\Scripts\Activate.ps1` (PowerShell).
4. Run `python main.py`, then open http://127.0.0.1:5000.

## Put it on GitHub and Render

1. Create a new GitHub repository and upload the contents of this folder. Do not upload `.venv`.
2. In Render, choose **New + → Blueprint** and select that repository. Render reads `render.yaml` to build and start the web service.
3. Open the deployed `https://…onrender.com` address in Chrome on your phone. Allow microphone access when prompted. If voice recognition is unavailable, type in the command box.

Render also supports creating a Web Service manually: set the root directory to this project folder if needed, build command to `pip install -r requirements.txt`, and start command to `python main.py`.

## Current commands

- Open Google, YouTube, Facebook, Instagram, LinkedIn, WhatsApp, Gmail, GitHub, or Maps.
- Tell the current server time or date.
- Search Google or find music on YouTube.

Voice capture and speech are handled by the browser. Commands are processed by this app; it does not currently connect to an AI service or control other apps on your phone.
