import re
import zmq

context = zmq.Context()
PORT = 5557                     
SEPARATOR = b'\x21'             


PATTERN = re.compile(r"^[\w\-()\[\]\.\ ]*[\w\-()\[\]]$")


def validate_filename(name, pattern, socket):
    if not pattern.match(name):
        socket.send(b"ERROR: Invalid filename")
        return False
    return True


def read_file(path):
    try:
        with open(path, "r") as f:
            data = f.read()
        return True, data.encode()
    except Exception as e:
        return False, f"ERROR: {e}".encode()


def process_operation(operation, filename):
    if operation != "get":
        return False, b"ERROR: Unsupported operation"
    return read_file(filename)


def main():
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{PORT}")
    print(f"Get-file microservice running on port {PORT}")

    while True:
        buffer = socket.recv()

        # Expected message format:  get!filename
        parts = buffer.decode().split("!")

        if len(parts) != 2:
            socket.send(b"ERROR: Bad request format")
            continue

        operation, filename = parts
        print(f"Operation: {operation}")
        print(f"Filename: {filename}")

        # Validate
        if not validate_filename(filename, PATTERN, socket):
            continue

        ok, response = process_operation(operation, filename)

        socket.send(response)
        print()


if __name__ == "__main__":
    main()
