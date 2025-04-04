import json
import csv
import os
import pandas as pd
from datetime import datetime

class FileHandler:
    """
    Utility class for handling file operations related to process scheduling.
    """
    
    @staticmethod
    def save_processes_to_json(processes, filename):
        """
        Save a list of processes to a JSON file.
        
        Args:
            processes (list): List of Process objects
            filename (str): The filename to save to
            
        Returns:
            str: The path to the saved file
        """
        # Create data for each process
        data = []
        for p in processes:
            process_data = {
                'pid': p.pid,
                'name': p.name,
                'arrival_time': p.arrival_time,
                'burst_time': p.burst_time,
                'priority': p.priority
            }
            data.append(process_data)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Write to file
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        
        return filename
    
    @staticmethod
    def load_processes_from_json(filename):
        """
        Load processes from a JSON file.
        
        Args:
            filename (str): The filename to load from
            
        Returns:
            list: List of process data dictionaries
        """
        if not os.path.exists(filename):
            return []
        
        with open(filename, 'r') as f:
            try:
                data = json.load(f)
                return data
            except json.JSONDecodeError:
                return []
    
    @staticmethod
    def save_results_to_csv(metrics_df, filename):
        """
        Save performance metrics to a CSV file.
        
        Args:
            metrics_df (pd.DataFrame): DataFrame containing performance metrics
            filename (str): The filename to save to
            
        Returns:
            str: The path to the saved file
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Save to CSV
        metrics_df.to_csv(filename)
        return filename
    
    @staticmethod
    def save_simulation_results(metrics, process_details, execution_logs, base_path="data/results"):
        """
        Save all simulation results to files.
        
        Args:
            metrics (pd.DataFrame): DataFrame containing scheduler metrics
            process_details (dict): Dictionary mapping scheduler names to process details DataFrames
            execution_logs (dict): Dictionary mapping scheduler names to execution logs
            base_path (str): Base path for saving files
            
        Returns:
            dict: Dictionary containing paths to saved files
        """
        # Create timestamp for unique folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_path = os.path.join(base_path, f"simulation_{timestamp}")
        os.makedirs(result_path, exist_ok=True)
        
        # Save metrics
        metrics_path = os.path.join(result_path, "metrics.csv")
        FileHandler.save_results_to_csv(metrics, metrics_path)
        
        # Save process details for each scheduler
        details_path = {}
        for scheduler, details in process_details.items():
            filename = os.path.join(result_path, f"{scheduler.replace(' ', '_')}_process_details.csv")
            details.to_csv(filename)
            details_path[scheduler] = filename
        
        # Save execution logs for each scheduler
        logs_path = {}
        for scheduler, log in execution_logs.items():
            filename = os.path.join(result_path, f"{scheduler.replace(' ', '_')}_execution_log.json")
            with open(filename, 'w') as f:
                json.dump(log, f, indent=4)
            logs_path[scheduler] = filename
        
        return {
            "metrics": metrics_path,
            "process_details": details_path,
            "execution_logs": logs_path,
            "base_path": result_path
        }