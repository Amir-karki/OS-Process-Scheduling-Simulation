import time
from abc import ABC, abstractmethod

class Scheduler(ABC):
        
    def __init__(self, name):
        self.name = name
        self.processes = []
        self.current_time = 0
        self.time_slice = 1  # Default time slice for simulation
        self.context_switch_overhead = 0  # Default context switch overhead
        self.current_process = None
        self.completed_processes = []
        
        # For Gantt chart data
        self.execution_log = []
    
    def add_process(self, process):
        """Add a process to be scheduled."""
        self.processes.append(process)
    
    def add_processes(self, processes):
        """Add multiple processes to be scheduled."""
        self.processes.extend(processes)
    
    def set_context_switch_overhead(self, overhead):
        """Set the context switch overhead."""
        self.context_switch_overhead = overhead
    
    def reset(self):
        """Reset the scheduler to its initial state."""
        self.current_time = 0
        self.current_process = None
        self.completed_processes = []
        self.execution_log = []
        
        # Reset all processes
        for process in self.processes:
            process.reset()
    
    @abstractmethod
    def get_next_process(self, ready_processes):
        pass
    
    def run(self, until_time=None):
        """
        Run the simulation until all processes complete or until_time is reached.
        
        Args:
            until_time (int, optional): Maximum simulation time
        
        Returns:
            list: Completed processes
        """
        # Reset the simulation
        self.reset()
        
        # Continue until all processes are completed or until_time is reached
        while (len(self.completed_processes) < len(self.processes) and 
               (until_time is None or self.current_time < until_time)):
            
            # Get processes that have arrived and are not completed
            ready_processes = [p for p in self.processes 
                              if p.is_arrived(self.current_time) and not p.is_terminated()]
            
            if not ready_processes:
                # No processes ready, advance time to next arrival
                next_arrival = min([p.arrival_time for p in self.processes 
                                    if not p.is_terminated() and p.arrival_time > self.current_time], 
                                   default=None)
                if next_arrival is None:
                    # All processes have arrived and completed
                    break
                
                # Log idle time in execution log
                if self.current_time < next_arrival:
                    self.execution_log.append(("IDLE", self.current_time, next_arrival))
                
                # Advance time to next arrival
                self.current_time = next_arrival
                continue
            
            # Get the next process to execute based on the scheduling algorithm
            next_process = self.get_next_process(ready_processes)
            
            # Handle context switch if needed
            if self.context_switch_overhead > 0 and self.current_process != next_process and self.current_process is not None:
                # Add context switch to execution log
                self.execution_log.append(("CS", self.current_time, self.current_time + self.context_switch_overhead))
                
                # Update waiting times for all ready processes during context switch
                for p in ready_processes:
                    if p != next_process:
                        p.wait(self.context_switch_overhead)
                
                # Advance time for context switch
                self.current_time += self.context_switch_overhead
            
            # Set the current process
            self.current_process = next_process
            
            # Execute the process for the time slice
            execution_time = next_process.execute(self.current_time, self.time_slice)
            
            # Add to execution log
            self.execution_log.append((next_process.pid, self.current_time, self.current_time + execution_time))
            
            # Update current time
            self.current_time += execution_time
            
            # Update waiting time for all other ready processes
            for p in ready_processes:
                if p != next_process:
                    p.wait(execution_time)
            
            # Check if process is complete
            if next_process.is_terminated():
                self.completed_processes.append(next_process)
                self.current_process = None
        
        return self.completed_processes
    
    def get_average_waiting_time(self):
        """Calculate the average waiting time for all processes."""
        if not self.completed_processes:
            return 0
        return sum(p.get_waiting_time() for p in self.completed_processes) / len(self.completed_processes)
    
    def get_average_turnaround_time(self):
        """Calculate the average turnaround time for all processes."""
        if not self.completed_processes:
            return 0
        return sum(p.get_turnaround_time() for p in self.completed_processes) / len(self.completed_processes)
    
    def get_average_response_time(self):
        """Calculate the average response time for all processes."""
        if not self.completed_processes:
            return 0
        return sum(p.get_response_time() for p in self.completed_processes) / len(self.completed_processes)
    
    def get_cpu_utilization(self):
        """Calculate CPU utilization percentage."""
        if self.current_time == 0:
            return 0
        
        # Calculate total idle time
        idle_time = sum(end - start for pid, start, end in self.execution_log if pid == "IDLE")
        context_switch_time = sum(end - start for pid, start, end in self.execution_log if pid == "CS")
        
        # Calculate utilization
        utilization = (self.current_time - idle_time - context_switch_time) / self.current_time * 100
        return utilization
    
    def get_execution_log(self):
        """Get the execution log for creating Gantt charts."""
        return self.execution_log
    
    def __str__(self):
        return f"{self.name} Scheduler"