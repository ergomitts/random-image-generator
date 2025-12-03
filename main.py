from PIL import Image
import random
import os
import zmq

FILE_READ_PORT = 5557
IMAGE_FETCH_PORT = 1738
IMAGE_EDIT_PORT = 1739
IMAGE_SAVE_PORT = 1740

PROJECT_DIR = str(os.getcwd())

context = zmq.Context()

class Client:
    def __init__(self, host="localhost", port=1738):
        self.socket = context.socket(zmq.REQ)
        self.socket.connect(f"tcp://{host}:{port}")

    def send(self, data):
        self.socket.send(data)
        return self.socket.recv()
    
    def send_json(self, data):
        self.socket.send_json(data)
        return self.socket.recv_json()
    
file_read_ms = Client(port=FILE_READ_PORT)
image_fetch_ms = Client(port=IMAGE_FETCH_PORT)
image_edit_ms = Client(port=IMAGE_EDIT_PORT)
image_save_ms = Client(port=IMAGE_SAVE_PORT)

def save_image(input_path, output_path, output_name, quality="low"):
    if os.path.exists(output_path):
        print("Replacing...")

    response = image_save_ms.send_json({
        "command": "convert",
        "quality": quality,
        "input": input_path,
        "directory": output_path,
        "name": output_name
    })

    if response and response["status"] == "success":
        if os.path.exists("temp.jpg"):
            try:
                os.remove("temp.jpg")
            except OSError as e:
                print(f"Error deleting temp file': {e}")
    else:
        raise ValueError(f"Error converting image!: {response}")
    return os.path.join(output_path, output_name)

def insert_into_random_background(small_path, bg_query):
    small_img = Image.open(small_path)

    # Convert to RGBA (keeps transparency if PNG)
    if small_img.mode != "RGBA":
        small_img = small_img.convert("RGBA")

    response = download_random_background(bg_query)
    if not response or response["status"] != "success":
        raise ValueError("No background images found!")

    bg_path = response["save_path"]

    bg_img = Image.open(bg_path)

    max_x = bg_img.width - small_img.width
    max_y = bg_img.height - small_img.height

    if max_x < 0 or max_y < 0:
        raise ValueError("Small image is larger than background")

    pos_x = random.randint(0, max_x)
    pos_y = random.randint(0, max_y)

    bg_img.paste(small_img, (pos_x, pos_y), small_img)

    if bg_img.mode == "RGBA":
        bg_img = bg_img.convert("RGB")
    bg_img.save("temp.jpg")

    return {
        "status": "success",
        "background_path": bg_path,
        "position": (pos_x, pos_y),
        "output": "temp.jpg"
    }

def download_random_background(query):
    response = image_fetch_ms.send_json({
        "command": "fetch",
        "save_folder": "backgrounds",
        "query": query
    })
    return response

def read_file(filename):
    message = f"get!{filename}"
    response = file_read_ms.send(message.encode('utf-8'))
    return response.decode('utf-8')

def resize_image(output_path="temp.jpg", width=512, height=512):
    response = image_edit_ms.send_json({
        "command": "load",
        "path": output_path
    })
    if response["status"] == "success":
        image_edit_ms.send_json({
            "command": "resize",
            "width": width,
            "height": height
        })
    return response

def mono_image(output_path="temp.jpg"):
    response = image_edit_ms.send_json({
        "command": "load",
        "path": output_path
    })
    if response["status"] == "success":
        image_edit_ms.send_json({
            "command": "monochrome"
        })
    return response

def main():
    # Low Quality Test
    result = insert_into_random_background("small.png", "green hills background")
    resize_image(result["output"], 500, 500)
    mono_image(result["output"])
    my_path = save_image(result["output"], PROJECT_DIR, "my_image.jpg", "low")
    img = Image.open(my_path)
    img.show()

    # High Quality Test
    result = insert_into_random_background("small.png", "beach background")
    resize_image(result["output"], 1280, 720)
    my_path = save_image(result["output"], PROJECT_DIR, "my_image_second.jpg", "high")
    img = Image.open(my_path)
    img.show()
    read_file("test.txt")

if __name__ == "__main__":
    main()