import subprocess
import time
import sys
from threading import Thread
from fastapi import FastAPI
import uvicorn
from pyngrok import ngrok

# --------------------------
# Your FastAPI app
# --------------------------
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from local server!"}

# --------------------------
# Function to start ngrok
# --------------------------
def start_ngrok(port: int):
    url = ngrok.connect(port)
    print(f"Public URL (share this with teammates): {url}")
    return url

# --------------------------
# Run server and ngrok
# --------------------------
if __name__ == "__main__":
    PORT = 8000

    # Start ngrok in a separate thread
    Thread(target=start_ngrok, args=(PORT,), daemon=True).start()

    # Run FastAPI app
    uvicorn.run(app, host="127.0.0.1", port=PORT, loop="asyncio")
