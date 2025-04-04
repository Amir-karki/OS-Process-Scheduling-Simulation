from models.scheduler import Scheduler

class PriorityScheduler(Scheduler):
    """
    Priority scheduling algorithm.
    
    Processes are executed in order of their priority.
    Non-preemptive algorithm.
    """
    
    def __init__(self, preemptive=False):
        """
        Initialize a Priority scheduler.
        
        Args:
            preemptive (bool): Whether to use preemptive scheduling
        """
        super().__init__("Priority" + (" (Preemptive)" if preemptive else ""))
        self.preemptive = preemptive
    
    def get_next_process(self, ready_processes):
        """
        Select the process with the highest priority.
        
        Args:
            ready_processes (list): List of processes that are ready to execute
            
        Returns:
            Process: The process with the highest priority
        """
        # If the current process is still running and we're non-preemptive, continue with it
        if not self.preemptive and self.current_process in ready_processes and not self.current_process.is_terminated():
            return self.current_process
        
        # Otherwise, select the process with the highest priority
        # Note: Higher priority value means higher priority
        return max(ready_processes, key=lambda p: (p.priority, -p.arrival_time, p.pid))