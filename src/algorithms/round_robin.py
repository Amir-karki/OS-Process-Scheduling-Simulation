from models.scheduler import Scheduler
from collections import deque

class RoundRobinScheduler(Scheduler):
    """
    Round Robin scheduling algorithm.
    
    Processes are executed in a circular order with a fixed time quantum.
    Preemptive algorithm.
    """
    
    def __init__(self, time_quantum=4):
        """
        Initialize a Round Robin scheduler.
        
        Args:
            time_quantum (int): Time quantum for each process execution
        """
        super().__init__("Round Robin (TQ=" + str(time_quantum) + ")")
        self.time_quantum = time_quantum
        self.time_slice = time_quantum
        self.ready_queue = deque()
    
    def add_process(self, process):
        """Add a process to be scheduled."""
        super().add_process(process)
    
    def reset(self):
        """Reset the scheduler to its initial state."""
        super().reset()
        self.ready_queue = deque()
    
    def get_next_process(self, ready_processes):
        """
        Select the next process based on Round Robin scheduling.
        
        Args:
            ready_processes (list): List of processes that are ready to execute
            
        Returns:
            Process: The next process to execute
        """
        # Update the ready queue with newly arrived processes
        current_pids = {p.pid for p in self.ready_queue}
        for process in ready_processes:
            if process.pid not in current_pids and process not in self.ready_queue:
                self.ready_queue.append(process)
        
        # If the current process has finished its time quantum, move it to the back of the queue
        if self.current_process in ready_processes and not self.current_process.is_terminated():
            # Remove it from wherever it is in the queue
            try:
                self.ready_queue.remove(self.current_process)
            except ValueError:
                pass
            # Add it to the end of the queue
            self.ready_queue.append(self.current_process)
        
        # If the ready queue is empty but we have ready processes, there's an inconsistency
        if not self.ready_queue and ready_processes:
            # Reset the ready queue with all ready processes
            self.ready_queue = deque(sorted(ready_processes, key=lambda p: (p.arrival_time, p.pid)))
        
        # Return the next process from the ready queue
        if self.ready_queue:
            return self.ready_queue.popleft()
        
        # Shouldn't get here if ready_processes is not empty
        return None