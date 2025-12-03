import zmq
import json
import io
import os
from PIL import Image

PORT = 1739

image_path = None

def load_image(path):
    global image_path 
    if not os.path.exists(path):
        return {"status": "error", "message": "Image path does not exist"}
    image_path = path
    return {"status": "success", "message": "Image loaded successfully"}

def save_image(img):
    global image_path
    img = img.copy() 
    img.save(image_path) 
    return True

def resize_image(width, height):
    global image_path 
    if image_path is None:
        return {"status": "error", "message": "No image loaded"}
    img = Image.open(image_path)
    new_img = img.resize((width, height))
    save_image(new_img)
    return {"status": "success", "message": "Image resized successfully"}

def apply_monochrome():
    global image_path 
    if image_path is None:
        return {"status": "error", "message": "No image loaded"}
    img = Image.open(image_path)
    new_img = img.convert("L")
    save_image(new_img)
    return {"status": "success", "message": "Image filtered successfully"}

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{PORT}")
    print("Image Editing Microservice ready.")

    while True:
        message = socket.recv_json()
        print(f"Received message: {message}")
        command = message.get("command")
        response = {"status": "error", "message": "unknown command"}

        if command == "load":
            response = load_image(message["path"])
        elif command == "resize":
            response = resize_image(int(message["width"]), int(message["height"]))
        elif command == "monochrome":
            response = apply_monochrome()

        socket.send_json(response)
        print()


if __name__ == "__main__":
    main()