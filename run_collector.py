import subprocess
import sys
import time

INTERVAL_SECONDS = 60

print("Collector started. Press Ctrl+C to stop.")

try:
    while True:
        try:
            subprocess.run([sys.executable, "collect.py"], check=True)
        except Exception as e:
            print("Collection failed, will try again:", e)
        time.sleep(INTERVAL_SECONDS)
except KeyboardInterrupt:
    print("Collector stopped.")