import subprocess
import time
import os

SERVICES = [
    ("microservices/image-edit.py", "Image Editor"),
    ("microservices/image-fetching.py", "Image Fetcher"),
    ("microservices/image-saving.py", "Image Saving"),
    ("microservices/file-reader.py", "File Reader"),
]

processes = []

def main():
    print("Starting all microservices...\n")

    for script, name in SERVICES:
        if not os.path.exists(script):
            print(f"[ERROR] Could not find {script}")
            continue
        
        print(f"Starting {name} ({script})...")
        p = subprocess.Popen(["python", script])
        processes.append(p)
        time.sleep(0.5)

    print("Press CTRL+C to kill all services.")

    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("\nShutting down")
        for p in processes:
            p.terminate()

if __name__ == "__main__":
    main()