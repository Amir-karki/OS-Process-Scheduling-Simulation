class Process:
    """
    Represents a process with attributes required for scheduling simulation.
    """
    
    # Process states
    NEW = 'new'
    READY = 'ready'
    RUNNING = 'running'
    WAITING = 'waiting'
    TERMINATED = 'terminated'
    
    def __init__(self, pid, name, arrival_time, burst_time, priority=0):
        """
        Initialize a process with required attributes.
        
        Args:
            pid (int): Process ID
            name (str): Process name
            arrival_time (int): Time at which process arrives in the ready queue
            burst_time (int): Total CPU time required by the process
            priority (int, optional): Priority of the process (higher value means higher priority)
        """
        self.pid = pid
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        
        # For tracking execution
        self.remaining_time = burst_time
        self.start_time = None  # Time when process first started execution
        self.finish_time = None  # Time when process completed execution
        self.waiting_time = 0  # Total time spent waiting
        self.response_time = None  # Time from arrival to first execution
        self.state = Process.NEW
        
        # For tracking execution history (for Gantt charts)
        self.execution_history = []
    
    def execute(self, current_time, time_quantum=1):
        """
        Execute this process for a given time quantum.
        
        Args:
            current_time (int): Current simulation time
            time_quantum (int): Amount of time to execute for
            
        Returns:
            int: Actual time executed (may be less than time_quantum if process finished)
        """
        if self.state == Process.NEW:
            self.state = Process.READY
            
        if self.state != Process.RUNNING:
            self.state = Process.RUNNING
            
        if self.start_time is None:
            self.start_time = current_time
            self.response_time = current_time - self.arrival_time
        
        # Calculate actual execution time (don't exceed remaining time)
        actual_execution = min(time_quantum, self.remaining_time)
        
        # Update remaining time
        self.remaining_time -= actual_execution
        
        # Record execution in history
        self.execution_history.append((current_time, current_time + actual_execution))
        
        # Check if process is complete
        if self.remaining_time <= 0:
            self.state = Process.TERMINATED
            self.finish_time = current_time + actual_execution
            
        return actual_execution
    
    def wait(self, time):
        """Increment waiting time for this process."""
        if self.state == Process.READY or self.state == Process.WAITING:
            self.waiting_time += time
    
    def get_turnaround_time(self):
        """Calculate turnaround time (finish time - arrival time)."""
        if self.finish_time is not None:
            return self.finish_time - self.arrival_time
        return None
    
    def get_waiting_time(self):
        """Get total waiting time."""
        return self.waiting_time
    
    def get_response_time(self):
        """Get time from arrival to first execution."""
        return self.response_time
    
    def is_arrived(self, current_time):
        """Check if the process has arrived by current_time."""
        return current_time >= self.arrival_time
    
    def is_terminated(self):
        """Check if the process has completed execution."""
        return self.state == Process.TERMINATED
    
    def reset(self):
        """Reset the process to its initial state."""
        self.remaining_time = self.burst_time
        self.start_time = None
        self.finish_time = None
        self.waiting_time = 0
        self.response_time = None
        self.state = Process.NEW
        self.execution_history = []
    
    def __str__(self):
        return f"Process {self.pid} ({self.name}): arrival={self.arrival_time}, burst={self.burst_time}, priority={self.priority}, state={self.state}"