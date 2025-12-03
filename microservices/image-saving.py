import zmq
import os 
import json
from PIL import Image

PORT = 1740
PROJECT_DIR = str(os.getcwd())

def convert_quality(input_path="", quality="", output_dir="", output_name=""):
    if not os.path.isdir(output_dir):
        if PROJECT_DIR:
            output_dir = PROJECT_DIR
        else:
            return {"status": "error", "message": "unknown directory"}
    
    try:
        with Image.open(input_path) as original_img:
            original_dpi = original_img.info.get("dpi", (72, 72))
            img = original_img.copy()  

        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")

        output_path = os.path.join(output_dir, output_name)
        if not output_path.lower().endswith(".jpg"):
            output_path += ".jpg"

        if quality == "low":
            img = img.resize(
                (max(1, img.width // 2), max(1, img.height // 2)),
                resample=Image.LANCZOS
            )
            img.save(
                output_path, 
                format="JPEG",
                quality=25, 
                optimize=True, 
                subsampling=1, 
                dpi=original_dpi,
                jfif_unit=1,
                jfif_density=(original_dpi[0], original_dpi[1])
            )
        elif quality == "high":
             img.save(
                output_path, 
                format="JPEG",
                quality=95, 
                optimize=True, 
                subsampling=0, 
                dpi=original_dpi,
                jfif_unit=1,
                jfif_density=(original_dpi[0], original_dpi[1])
            )
        else:
            img.save(output_path)
        return {"status": "success", "message": f"Image saved at {output_path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{PORT}")
    print("Image Saving Microservice ready.")

    while True:
        message = socket.recv_json()
        print(f"Received message: {message}")
        command = message.get("command")
        response = {"status": "error", "message": "unknown command"}

        if command == "save":
            response = convert_quality(message["input"], "", message["directory"], message["name"])
        elif command == "convert":
            response = convert_quality(message["input"], message["quality"], message["directory"], message["name"])
        socket.send_json(response)
        print()

if __name__ == "__main__":
    main()