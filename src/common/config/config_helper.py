import yaml
import os

class ConfigurationHelper:
    def __init__(self, config_dir="/root/thesis/config"):
        """
        Initializes the ConfigurationHelper.

        Args:
            config_dir (str): The directory where configuration files are located.
        """
        self.config_dir = config_dir
        self._configs = {} # Cache for loaded configurations

    def _load_yaml_file(self, filename):
        """Loads a YAML file from the configuration directory."""
        file_path = os.path.join(self.config_dir, filename)
        if file_path in self._configs:
            return self._configs[file_path]

        try:
            with open(file_path, 'r') as f:
                config = yaml.safe_load(f)
                self._configs[file_path] = config # Cache the loaded config
                return config
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {file_path}")
            return None
        except yaml.YAMLError as e:
            print(f"Error parsing YAML configuration file '{filename}': {e}")
            return None

    def get_config(self, filename, config_path=None):
        """
        Loads configuration from a YAML file and extracts a specific section.

        Args:
            filename (str): The name of the YAML configuration file.
            config_path (str, optional): A dot-separated path to the desired configuration section
                                         (e.g., 'database.connection_string'). If None, returns
                                         the entire configuration.

        Returns:
            dict or any: The extracted configuration section, or None if file/path not found.
        """
        config = self._load_yaml_file(filename)
        if config is None:
            return None

        if config_path is None:
            return config

        # Navigate through the config using the dot-separated path
        current_config = config
        path_elements = config_path.split('.')
        try:
            for element in path_elements:
                current_config = current_config[element]
            return current_config
        except (KeyError, TypeError):
            print(f"Error: Configuration path '{config_path}' not found in '{filename}'.")
            return None

# Example Usage (optional, for testing)
# if __name__ == "__main__":
#     # Assuming a config/database.yaml exists
#     # database:
#     #   connection_string: "..."
#     #   pool_size: 10
#
#     config_manager = ConfigurationHelper()
#
#     # Get the entire database config
#     db_config = config_manager.get_config("database.yaml", "database")
#     if db_config:
#         print("Database Config:", db_config)
#         print("Connection String:", db_config.get("connection_string"))
#
#     # Get a specific value
#     conn_string = config_manager.get_config("database.yaml", "database.connection_string")
#     if conn_string:
#         print("Connection String (direct):", conn_string)
#
#     # Test non-existent path
#     non_existent = config_manager.get_config("database.yaml", "database.username")
#     if non_existent is None:
#         print("Non-existent path correctly returned None.")