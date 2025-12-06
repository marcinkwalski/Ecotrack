import shutil
import time
import os

DB_PATH = "ecotrack.db"

def backup_loop():
    while True:
        timestamp = time.strftime("%Y-%m-%d_%H-%M")
        backup_name = f"backup_{timestamp}.db"
        shutil.copy(DB_PATH, backup_name)
        print(f"[BACKUP] Utworzono kopię {backup_name}")
        time.sleep(48 * 3600)  # 48 godzin

if __name__ == "__main__":
    backup_loop()
