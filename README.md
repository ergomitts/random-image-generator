# Random Image Generator

## Usage
This app is used to combine a user selected image and a randomly generated background. The app uses a prompt provided by the user to select a random background from Google's Custom Search API search results. 

## Setup
### Requirements/Installations
* Language-specific ZeroMQ package
* Google API Key
* [Python Google API Documentation](https://pypi.org/project/Google-Images-Search/)
### Command to Install Depedencies
```python3
pip install google-api-python-client
pip install zmq
```
### Instructions
1. Complete the setup first. The app utilizes Google's Custom Search API and won't function properly without it.
2. Make sure to run server.py before main.py.
3. Run server.py and main.py on separate instances.


## Microservices
* [Image Fetching MS](https://github.com/ergomitts/image-fetching-microservice/)
    - Developed by Dan Quan and Nora Jacobi
* [Image Editing MS](https://github.com/ergomitts/image-editing-microservice/)
    - Developed by Dan Quan
* [Image Saving MS](https://github.com/ergomitts/image-saving-microservice/)
    - Developed by Dan Quan
* [File Reading MS](https://github.com/BeckWJohnson/cs361-file-reading/)
    - Developed by Beck Johnson