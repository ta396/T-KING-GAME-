KidGame (Kivy)
=================

A simple multi-stage, kid-friendly game written in Python using Kivy.

Stages
- Color Match: Tap the color that matches the prompt
- Shape Sort: Drag shapes into the correct boxes
- Count & Collect: Tap apples to collect up to a target number

Quick start (desktop)

Windows (recommended for testing on PC/tablet):
1. Create a virtual environment (optional but recommended):
   python -m venv venv
   venv\Scripts\activate
2. Install Kivy and run:
   pip install --upgrade pip
   pip install kivy
   python main.py

macOS / Linux:
1. Use your normal Python environment and install Kivy:
   pip install kivy
2. Run:
   python main.py

Note: For best touch-testing, run on a touchscreen laptop/tablet or use a mobile device emulator. For real-device testing, see the mobile packaging instructions below.

Assets
- Put optional sound files in the `assets/` folder:
  - ding.wav (success)
  - error.wav (wrong)
  - pick.wav (collect)

Mobile packaging
- Android (common approach): Use Buildozer (requires Linux). On Windows, use WSL (Windows Subsystem for Linux) or a Linux VM, then:
  1) Install buildozer in WSL
  2) create a `buildozer.spec` (run `buildozer init`), edit `requirements = kivy`
  3) run `buildozer -v android debug` to produce an APK
  See: https://buildozer.readthedocs.io/

- Android (alternative): Use service/cloud builders or GitHub Actions to build your APK if you can't run Buildozer locally.

- iOS: Use `kivy-ios` to produce an Xcode project, then build in Xcode on macOS. See: https://kivy.org/doc/stable/guide/packaging-ios.html

Packaging tips
- Keep `requirements` minimal (e.g., `kivy`), include any extra Python packages your game needs.
- Test on desktop first, then on-device. Replace placeholder assets with short, friendly sounds.

Notes
- This is an educational prototype. Replace placeholder sounds/images with friendly child-appropriate assets.
- Use large, colorful assets and short audio cues for best user experience for young children.
