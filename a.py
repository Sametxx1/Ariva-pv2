import subprocess
import os
import sys
import time

# Flask uygulamasını başlatma fonksiyonu
def start_app():
    flask_process = subprocess.Popen([sys.executable, "ip.py"])
    try:
        flask_process.wait()
    except KeyboardInterrupt:
        flask_process.terminate()

if __name__ == "__main__":
    start_app()
