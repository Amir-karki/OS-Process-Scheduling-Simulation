from models.scheduler import Scheduler
from collections import deque
import heapq

class MultilevelQueueScheduler(Scheduler):
        
    def __init__(self, queue_count=3):
        """
        Initialize a Multilevel Queue scheduler.
        
        Args:
            queue_count (int): Number of priority queues
        """
        super().__init__("Multilevel Queue")
        self.queue_count = queue_count
        
        # Create queues with different algorithms
        self.queues = []
        # Highest priority queue - Round Robin with small time quantum
        self.queues.append({"name": "System Processes (High)", "algorithm": "RR", "time_quantum": 2, "queue": deque()})
        
        # Middle priority queue(s)
        for i in range(1, queue_count - 1):
            self.queues.append({"name": f"Interactive Processes (Medium {i})", "algorithm": "RR", "time_quantum": 4, "queue": deque()})
        
        # Lowest priority queue - FCFS
        self.queues.append({"name": "Batch Processes (Low)", "algorithm": "FCFS", "queue": deque()})
    
    def reset(self):
        """Reset the scheduler to its initial state."""
        super().reset()
        # Clear all queues
        for queue in self.queues:
            queue["queue"] = deque()
    
    def get_queue_for_process(self, process):
        """
        Determine which queue a process belongs to based on its priority.
        
        Args:
            process (Process): The process to place in a queue
            
        Returns:
            int: Queue index
        """
        # Simple mapping from process priority to queue
        # Could be made more sophisticated with custom range mappings
        queue_index = min(max(0, self.queue_count - 1 - process.priority), self.queue_count - 1)
        return queue_index
    
    def get_next_process(self, ready_processes):
        """
        Select the next process based on multilevel queue scheduling.
        
        Args:
            ready_processes (list): List of processes that are ready to execute
            
        Returns:
            Process: The next process to execute
        """
        # Update queues with newly arrived processes
        for process in ready_processes:
            # Find if process is already in any queue
            in_queue = False
            for queue in self.queues:
                if process in queue["queue"]:
                    in_queue = True
                    break
            
            # If not in any queue and not the current process, add it to the appropriate queue
            if not in_queue and process != self.current_process:
                queue_index = self.get_queue_for_process(process)
                self.queues[queue_index]["queue"].append(process)
        
        # Handle the current process
        if self.current_process in ready_processes and not self.current_process.is_terminated():
            # Determine if the current process should continue or be moved to the back of its queue
            queue_index = self.get_queue_for_process(self.current_process)
            queue = self.queues[queue_index]
            
            # For Round Robin queues, check if time quantum is exceeded
            if queue["algorithm"] == "RR":
                # Remove from any queue it might be in
                for q in self.queues:
                    try:
                        q["queue"].remove(self.current_process)
                    except (ValueError, AttributeError):
                        pass
                
                # Add back to the end of its queue
                queue["queue"].append(self.current_process)
        
        # Select next process from the highest priority non-empty queue
        for queue in self.queues:
            if queue["queue"]:
                # Get the next process based on the queue's algorithm
                if queue["algorithm"] == "FCFS":
                    # For FCFS, take the first process in the queue (already sorted by arrival time)
                    next_process = queue["queue"].popleft()
                    return next_process
                elif queue["algorithm"] == "RR":
                    # For Round Robin, take the first process and set the time slice
                    next_process = queue["queue"].popleft()
                    self.time_slice = queue["time_quantum"]
                    return next_process
        
        # If no process was selected but we have ready processes, there's an inconsistency
        if ready_processes:
            # Just select the first process based on arrival time
            return min(ready_processes, key=lambda p: (p.arrival_time, p.pid))
        
        return None