from models.scheduler import Scheduler

class FCFSScheduler(Scheduler):
    """
    First-Come, First-Served (FCFS) scheduling algorithm.
    
    Processes are executed in the order they arrive.
    Non-preemptive algorithm.
    """
    
    def __init__(self):
        """Initialize a FCFS scheduler."""
        super().__init__("First-Come, First-Served")
    
    def get_next_process(self, ready_processes):
        """
        Select the process that arrived first.
        
        Args:
            ready_processes (list): List of processes that are ready to execute
            
        Returns:
            Process: The process with the earliest arrival time
        """
        # Sort by arrival time and return the first one
        return min(ready_processes, key=lambda p: (p.arrival_time, p.pid))