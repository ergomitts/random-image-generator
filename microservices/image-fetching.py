from googleapiclient.discovery import build
import zmq
import json
import requests
import random 
import os

api_key = "AIzaSyCdA_yJKXtW7WNdJnQE9Hxu2rLEbRnkseQ"
cse_id = "114bca9babc1b4338"

PORT = 1738

IMAGE_SIZES = ["XLARGE", "XXLARGE", "HUGE"]

def get_links(input):
    service = build("customsearch", "v1", developerKey=api_key)

    img_size = random.choice(IMAGE_SIZES)

    res = service.cse().list(
        q=input,
        cx=cse_id,
        searchType="image",
        num=5,
        imgSize=img_size,
        imgType="photo"
    ).execute()
    # This returns the raw JSON file
    return [item["link"] for item in res.get("items", [])]

def fetch_random_image(query, save_folder="backgrounds"):
    os.makedirs(save_folder, exist_ok=True)
    
    links = get_links(query)
    if not links:
        return {"status": "error", "message": "No links found"}

    url = random.choice(links)
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        filename = os.path.basename(url.split("?")[0])
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            filename += ".jpg"
        save_path = os.path.join(save_folder, filename)
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return {"status": "success", "message": f"Saved at {save_path}", "save_path" : str(save_path)}
    else:
        return {"status": "error", "message": f"Failed to download image {response.status_code}"}

def main(): 
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{PORT}")
    print("Image Fetching Microservice Ready.")

    while True:
        message = socket.recv_json()
        print(f"Received message: {message}")
        command = message.get("command")
        response = {"status": "error", "message": "unknown command"}

        if command == "get_links":
            response = {"status": "success", "message": "Retrieved links", "links": get_links(message["query"])}
        elif command == "fetch":
            response = fetch_random_image(message["query"], message["save_folder"])
        socket.send_json(response)
        print()

if __name__ == "__main__":
    main()