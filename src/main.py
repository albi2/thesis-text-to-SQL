import modal
from pathlib import Path

app = modal.App("thesis")

# Create a persistent volume for datasets and results
volume = modal.Volume.from_name("data", create_if_missing=True)

image = modal.Image.debian_slim(python_version="3.12").pip_install_from_requirements("requirements.txt").pip_install(["accelerate"]).add_local_dir(
    ".",
    remote_path="/thesis",
    ignore=["*.venv", "venv", "data"],
)


@app.function(
    image=image,
    gpu="l4",  # Each model gets its own A100 
    volumes={"/root/data": volume},
    memory=(100*1024, 150*1024),        # 100GB RAM per model
    timeout=3600
)
def run_evaluation():
    """
    Run evaluation with optional dataset path override
    """
    import sys
    import os
    from init import main
    import torch

    sys.path.append('/thesis')
        
    has_cuda = torch.cuda.is_available()
    print(f"It is {has_cuda} that torch can access CUDA")

    try:
        main()
        return {"status": "success", "message": "Evaluation completed successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
