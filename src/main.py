from executor.running_manager import RunningManager

def main():
    """
    Initializes the RunningManager and starts the evaluation process.
    """
    dataset_path = "../dataset/dev/bird_subset.json"
    manager = RunningManager(dataset_path)
    manager.load_tasks()
    manager.run_evaluation()

if __name__ == "__main__":
    main()
