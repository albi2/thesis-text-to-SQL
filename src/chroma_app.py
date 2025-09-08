import modal

# Separate app just for Chroma
app = modal.App("chroma-server")

# Create a persistent volume for Chroma data
chroma_volume = modal.Volume.from_name("data", create_if_missing=True)

# Lightweight image just for Chroma
chroma_image = modal.Image.debian_slim(python_version="3.12").pip_install([
    "chromadb==1.0.16",
    "requests"
])

@app.function(
    image=chroma_image,
    cpu=2,
    memory=4096,
    volumes={"/root/data": chroma_volume},
    keep_warm=1,   # Keep container alive
    timeout=0      # Run indefinitely
)
@modal.web_server(port=8080)
def chroma_server():
    """Dedicated Chroma server"""
    import subprocess
    import os
    
    # Ensure the Chroma DB is stored in the volume
    os.makedirs("/root/data/chroma", exist_ok=True)
    
    print("Starting dedicated Chroma server...")
    
    # Start Chroma server
    subprocess.run([
        "chroma", "run", 
        "--host", "0.0.0.0",
        "--path", "/root/data/chroma",
        "--port", "8080"
    ], check=True)


# if __name__ == "__main__":
#     # Deploy just the Chroma app
#     with app.run():
#         print("Chroma server is running...")
#         print(f"Access at: {chroma_server.web_url}")
#         # Keep running
#         import time
#         while True:
#             time.sleep(60)