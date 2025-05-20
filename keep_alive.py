from flask import Flask
from threading import Thread
import atexit

app = Flask(__name__)
server = None

@app.route('/')
def index():
    return "I'm Alive Because Of RefOo"

def run():
    app.run(host='0.0.0.0', port=8000)

def keep_alive():
    global server
    server = Thread(target=run)
    server.daemon = True  # Set as daemon thread
    server.start()

def cleanup():
    global server
    if server and server.is_alive():
        # Cleanup code here if needed
        print("Shutting down server...")

# Register cleanup function
atexit.register(cleanup)