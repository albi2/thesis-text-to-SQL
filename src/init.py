
from executor.running_manager import RunningManager
from infrastructure.vector_db.load_comment_collection import load_comments

def main():
    """
    Initializes the RunningManager and starts the evaluation process.
    """
    load_comments()

    dataset_path = "/root/thesis/dataset/dev/bird_subset.json"
    manager = RunningManager(dataset_path)
    manager.load_tasks()
    manager.run_evaluation()

if __name__ == "__main__":
    main()