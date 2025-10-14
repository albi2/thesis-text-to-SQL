import os
base_cache = "/var/tmp/ge62nok"

os.environ["HF_HOME"] = base_cache
os.environ["HF_HUB_CACHE"] = os.path.join(base_cache, "hub")
os.environ["TRANSFORMERS_CACHE"] = os.path.join(base_cache, "transformers")
os.environ["HF_DATASETS_CACHE"] = os.path.join(base_cache, "datasets")
os.environ["HF_MODULES_CACHE"] = os.path.join(base_cache, "modules")


from executor.running_manager import RunningManager
from infrastructure.vector_db.load_comment_collection import load_comments
import pysqlite3
import sys
sys.modules["sqlite3"] = pysqlite3

def main():
    """
    Initializes the RunningManager and starts the evaluation process.
    """
    # load_comments()

    dataset_path = "/var/tmp/ge62nok/thesis/dataset/dev/dev.json"
    manager = RunningManager(dataset_path)
    manager.load_tasks()
    manager.run_evaluation()

if __name__ == "__main__":
    main()