
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

    dataset_path = "/var/tmp/ge62nok/thesis/dataset/dev/bird_subset.json"
    manager = RunningManager(dataset_path)
    manager.load_tasks()
    manager.run_evaluation()

if __name__ == "__main__":
    main()