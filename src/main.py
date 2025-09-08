from executor.running_manager import RunningManager

<<<<<<< Updated upstream
def main():
=======
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
            remote_path="/root/data/thesis",
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
>>>>>>> Stashed changes
    """
    Initializes the RunningManager and starts the evaluation process.
    """
    dataset_path = "./dataset/dev/bird_subset.json"
    manager = RunningManager(dataset_path)
    manager.load_tasks()
    manager.run_evaluation()

if __name__ == "__main__":
    main()
