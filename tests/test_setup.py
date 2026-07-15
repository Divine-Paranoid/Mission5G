import sys
import cv2
import requests
import yaml

def verify_environment():
    print("=" * 50)
    print("DTU Private 5G Innovation Lab - Environment Verification")
    print("=" * 50)
    print(f"Python Version: {sys.version}")
    print(f"OpenCV Version: {cv2.__version__}")
    print(f"Requests Version: {requests.__version__}")
    print(f"PyYAML Version: {yaml.__version__}")
    print("-" * 50)
    print("Result: Environment setup is fully SUCCESSFUL and verified!")
    print("=" * 50)

if __name__ == "__main__":
    verify_environment()