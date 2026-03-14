import requests
import json
import sys

def download_model():
    print("Starting download of llama3.2...")
    url = "http://localhost:11434/api/pull"
    data = {"name": "llama3.2", "stream": True}
    
    try:
        with requests.post(url, json=data, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    response = json.loads(line)
                    status = response.get("status", "")
                    
                    if "downloading" in status:
                        completed = response.get("completed", 0)
                        total = response.get("total", 0)
                        if total > 0:
                            percent = (completed / total) * 100
                            sys.stdout.write(f"\rDownload: {status} - {percent:.1f}%")
                            sys.stdout.flush()
                    elif status == "success":
                        print("\nDownload complete!")
                        return
                    else:
                        sys.stdout.write(f"\rStatus: {status}")
                        sys.stdout.flush()
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    download_model()
