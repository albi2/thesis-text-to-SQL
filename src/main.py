import modal

app = modal.App("thesis")

# Create a persistent volume for datasets and results
volume = modal.Volume.from_name("data", create_if_missing=True)
# with volume.batch_upload() as batch:
#     batch.put_directory("/Users/I746200/Downloads/dev_20240627/dev_databases", "/dev_databases")

image = (modal.Image
         .debian_slim(python_version="3.12")
        .apt_install("openssh-server")
        .pip_install_from_requirements("requirements.txt")
        .pip_install(["accelerate"])
        .run_commands("mkdir /run/sshd")
        .add_local_file("/Users/I746200/.ssh/modal_rsa.pub", "/root/.ssh/authorized_keys", copy=True)
        .add_local_python_source("init", "util", "prompts", "pipeline", "infrastructure", "executor", "context", "components", "common")
        .add_local_dir(
            local_path=".",
            remote_path="/root/thesis",
            ignore=["venv/*" ])
    )
        
@app.function(
    image=image,
    gpu="l4",  # Each model gets its own A100 
    volumes={"/root/data": volume},
    memory=(100*1024, 150*1024),
    cpu=(2, 16),        # 100GB RAM per model
    timeout=7200,                   # 2 hours
    scaledown_window=600  
)
def run_evaluation():
    """
    Run evaluation with optional dataset path override
    """
    from init import main
    import torch
    import os 

    has_cuda = torch.cuda.is_available()
    print(f"It is {has_cuda} that torch can access CUDA")

    base_path = "/root/data/dev_databases"
    
    for root, dirs, files in os.walk(base_path):
        print("Directory:", root)
        for d in dirs:
            print("  Subdir:", d)
        for f in files:
            print("  File:", f)


    try:
        main()
        return {"status": "success", "message": "Evaluation completed successfully"}
    except Exception as e:
        print(f"ERROR : {str(e)}")
        return {"status": "error", "message": str(e)}


@app.function(
    image=image,
    gpu="l4",  # Each model gets its own A100 
    volumes={"/root/data": volume},
    memory=(100*1024, 150*1024),
    cpu=(8, 16),        # 100GB RAM per model
    timeout=7200,                   # 2 hours
    container_idle_timeout=600  
)
def start_port_forward():
    import subprocess
    import time

    subprocess.Popen(["/usr/sbin/sshd", "-D", "-e"])
    with modal.forward(port=22, unencrypted=True) as tunnel:
        hostname, port = tunnel.tcp_socket
        print(f"HOSTNAME: {hostname} port: {port}")

        while True:
            time.sleep(3600)  # sleep for 1 hour per iteration

@app.local_entrypoint()
def main():
    start_port_forward.remote()
