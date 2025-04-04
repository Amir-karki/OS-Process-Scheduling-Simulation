import pandas as pd
import numpy as np

class PerformanceMetrics:
    """
    Utility class for calculating and comparing scheduling algorithm performance metrics.
    """
    
    @staticmethod
    def calculate_metrics(completed_processes, total_time, scheduler_name):
        """
        Calculate performance metrics for a set of completed processes.
        
        Args:
            completed_processes (list): List of completed Process objects
            total_time (int): Total simulation time
            scheduler_name (str): Name of the scheduler
            
        Returns:
            dict: Dictionary containing the calculated metrics
        """
        if not completed_processes:
            return {
                'scheduler': scheduler_name,
                'avg_waiting_time': 0,
                'avg_turnaround_time': 0,
                'avg_response_time': 0,
                'throughput': 0,
                'cpu_utilization': 0
            }
        
        # Calculate metrics
        waiting_times = [p.get_waiting_time() for p in completed_processes]
        turnaround_times = [p.get_turnaround_time() for p in completed_processes]
        response_times = [p.get_response_time() for p in completed_processes]
        
        # Calculate idle time based on execution history
        execution_times = sum(end - start for p in completed_processes for start, end in p.execution_history)
        idle_time = total_time - execution_times
        
        # Calculate metrics
        avg_waiting_time = sum(waiting_times) / len(completed_processes)
        avg_turnaround_time = sum(turnaround_times) / len(completed_processes)
        avg_response_time = sum(response_times) / len(completed_processes)
        throughput = len(completed_processes) / total_time
        cpu_utilization = (execution_times / total_time) * 100 if total_time > 0 else 0
        
        return {
            'scheduler': scheduler_name,
            'avg_waiting_time': avg_waiting_time,
            'avg_turnaround_time': avg_turnaround_time,
            'avg_response_time': avg_response_time,
            'throughput': throughput,
            'cpu_utilization': cpu_utilization
        }
    
    @staticmethod
    def compare_schedulers(metrics_list):
        """
        Compare performance metrics across different schedulers.
        
        Args:
            metrics_list (list): List of metric dictionaries from different schedulers
            
        Returns:
            pd.DataFrame: DataFrame containing the comparison
        """
        if not metrics_list:
            return pd.DataFrame()
        
        # Create DataFrame from metrics
        df = pd.DataFrame(metrics_list)
        
        # Set scheduler as index for easier comparison
        df = df.set_index('scheduler')
        
        # Return the sorted DataFrame
        return df.sort_values('avg_waiting_time')
    
    @staticmethod
    def process_details_table(completed_processes):
        """
        Create a detailed table of process performance metrics.
        
        Args:
            completed_processes (list): List of completed Process objects
            
        Returns:
            pd.DataFrame: DataFrame containing process details
        """
        if not completed_processes:
            return pd.DataFrame()
        
        # Create data for each process
        data = []
        for p in completed_processes:
            data.append({
                'PID': p.pid,
                'Name': p.name,
                'Arrival Time': p.arrival_time,
                'Burst Time': p.burst_time,
                'Priority': p.priority,
                'Start Time': p.start_time,
                'Finish Time': p.finish_time,
                'Waiting Time': p.waiting_time,
                'Turnaround Time': p.get_turnaround_time(),
                'Response Time': p.response_time
            })
        
        # Create and return DataFrame
        return pd.DataFrame(data)