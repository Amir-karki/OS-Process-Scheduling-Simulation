from models.scheduler import Scheduler

class SJFScheduler(Scheduler):
    """
    Shortest Job First (SJF) scheduling algorithm.
    
    Processes are executed in order of their remaining burst time.
    Non-preemptive algorithm.
    """
    
    def __init__(self):
        """Initialize a SJF scheduler."""
        super().__init__("Shortest Job First")
    
    def get_next_process(self, ready_processes):
        """
        Select the process with the shortest burst time.
        
        Args:
            ready_processes (list): List of processes that are ready to execute
            
        Returns:
            Process: The process with the shortest burst time
        """
        # If the current process is still running, continue with it (non-preemptive)
        if self.current_process in ready_processes and not self.current_process.is_terminated():
            return self.current_process
        
        # Otherwise, select the process with the shortest burst time
        return min(ready_processes, key=lambda p: (p.remaining_time, p.arrival_time, p.pid))


class SRTFScheduler(Scheduler):
    """
    Shortest Remaining Time First (SRTF) scheduling algorithm.
    
    Processes are executed in order of their remaining burst time.
    Preemptive version of SJF.
    """
    
    def __init__(self):
        """Initialize a SRTF scheduler."""
        super().__init__("Shortest Remaining Time First")
    
    def get_next_process(self, ready_processes):
        """
        Select the process with the shortest remaining time.
        
        Args:
            ready_processes (list): List of processes that are ready to execute
            
        Returns:
            Process: The process with the shortest remaining time
        """
        # Always select the process with the shortest remaining time (preemptive)
        return min(ready_processes, key=lambda p: (p.remaining_time, p.arrival_time, p.pid))