import argparse
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Import models
from models.process import Process
from models.scheduler import Scheduler

# Import scheduling algorithms
from algorithms.fcfs import FCFSScheduler
from algorithms.sjf import SJFScheduler, SRTFScheduler
from algorithms.round_robin import RoundRobinScheduler
from algorithms.priority import PriorityScheduler
from algorithms.multilevel import MultilevelQueueScheduler

# Import utilities
from utils.metrics import PerformanceMetrics
from utils.visualizer import Visualizer
from utils.file_handler import FileHandler

def create_sample_processes(count=5, random_seed=None):
    """
    Create a sample set of processes for testing.
    
    Args:
        count (int): Number of processes to create
        random_seed (int): Random seed for reproducibility
        
    Returns:
        list: List of Process objects
    """
    import random
    if random_seed is not None:
        random.seed(random_seed)
    
    processes = []
    for i in range(count):
        arrival_time = random.randint(0, 10) if i > 0 else 0
        burst_time = random.randint(2, 20)
        priority = random.randint(0, 5)
        process = Process(
            pid=i+1,
            name=f"Process-{i+1}",
            arrival_time=arrival_time,
            burst_time=burst_time,
            priority=priority
        )
        processes.append(process)
    
    return processes

def load_processes_from_file(filename):
    """
    Load processes from a JSON file.
    
    Args:
        filename (str): Path to the JSON file
        
    Returns:
        list: List of Process objects
    """
    data = FileHandler.load_processes_from_json(filename)
    processes = []
    
    for p_data in data:
        process = Process(
            pid=p_data['pid'],
            name=p_data['name'],
            arrival_time=p_data['arrival_time'],
            burst_time=p_data['burst_time'],
            priority=p_data.get('priority', 0)
        )
        processes.append(process)
    
    return processes

def run_simulation(processes, schedulers, visualize=True, save_results=True):
    """
    Run scheduling simulation with the given processes and schedulers.
    
    Args:
        processes (list): List of Process objects
        schedulers (list): List of Scheduler objects
        visualize (bool): Whether to generate visualizations
        save_results (bool): Whether to save results to files
        
    Returns:
        dict: Dictionary containing simulation results
    """
    # Initialize containers for results
    metrics_list = []
    process_details = {}
    execution_logs = {}
    figures = {}
    
    # Create visualizer if needed
    visualizer = Visualizer() if visualize else None
    
    # Run each scheduler
    for scheduler in schedulers:
        print(f"\nRunning simulation with {scheduler.name}...")
        
        # Reset processes for this scheduler
        for process in processes:
            process.reset()
        
        # Add processes to the scheduler
        scheduler.add_processes(processes)
        
        # Run the simulation
        completed = scheduler.run()
        
        # Get metrics
        metrics = {
            'scheduler': scheduler.name,
            'avg_waiting_time': scheduler.get_average_waiting_time(),
            'avg_turnaround_time': scheduler.get_average_turnaround_time(),
            'avg_response_time': scheduler.get_average_response_time(),
            'cpu_utilization': scheduler.get_cpu_utilization()
        }
        metrics_list.append(metrics)
        
        # Get process details
        process_df = PerformanceMetrics.process_details_table(completed)
        process_details[scheduler.name] = process_df
        
        # Get execution log
        execution_logs[scheduler.name] = scheduler.get_execution_log()
        
        # Print summary
        print(f"  Average Waiting Time: {metrics['avg_waiting_time']:.2f}")
        print(f"  Average Turnaround Time: {metrics['avg_turnaround_time']:.2f}")
        print(f"  Average Response Time: {metrics['avg_response_time']:.2f}")
        print(f"  CPU Utilization: {metrics['cpu_utilization']:.2f}%")
        
        # Generate visualizations if requested
        if visualize:
            # Gantt chart
            gantt_fig = visualizer.gantt_chart(
                scheduler.get_execution_log(),
                title=f"{scheduler.name} - Gantt Chart"
            )
            
            # Timeline chart
            timeline_fig = visualizer.timeline_chart(
                completed,
                title=f"{scheduler.name} - Process Timeline"
            )
            
            figures[f"{scheduler.name}_gantt"] = gantt_fig
            figures[f"{scheduler.name}_timeline"] = timeline_fig
    
    # Create comparison metrics DataFrame
    metrics_df = pd.DataFrame(metrics_list)
    metrics_df = metrics_df.set_index('scheduler')
    
    # Generate comparison chart if multiple schedulers
    if visualize and len(schedulers) > 1:
        comparison_fig = visualizer.metrics_comparison_chart(
            metrics_df, 
            title="Scheduler Performance Comparison"
        )
        figures["comparison"] = comparison_fig
    
    # Save results if requested
    saved_paths = None
    if save_results:
        saved_paths = FileHandler.save_simulation_results(
            metrics_df, 
            process_details,
            execution_logs
        )
        
        # Save figures if visualizations were generated
        if visualize:
            os.makedirs(os.path.join(saved_paths["base_path"], "figures"), exist_ok=True)
            for name, fig in figures.items():
                path = os.path.join(saved_paths["base_path"], "figures", f"{name}.png")
                visualizer.save_figure(fig, path)
    
    return {
        "metrics": metrics_df,
        "process_details": process_details,
        "execution_logs": execution_logs,
        "figures": figures,
        "saved_paths": saved_paths
    }

def main():
    """Main function for running the process scheduler simulator."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process Scheduling Simulator')
    parser.add_argument('--processes', type=int, default=5, help='Number of random processes to create')
    parser.add_argument('--file', type=str, help='JSON file containing process definitions')
    parser.add_argument('--seed', type=int, help='Random seed for reproducibility')
    parser.add_argument('--algorithm', type=str, default='all', 
                        choices=['fcfs', 'sjf', 'srtf', 'rr', 'priority', 'multilevel', 'all'],
                        help='Scheduling algorithm to use')
    parser.add_argument('--quantum', type=int, default=4, help='Time quantum for Round Robin scheduler')
    parser.add_argument('--no-visualize', action='store_true', help='Disable visualization')
    parser.add_argument('--no-save', action='store_true', help='Disable saving results')
    
    args = parser.parse_args()
    
    # Load or create processes
    if args.file:
        processes = load_processes_from_file(args.file)
        print(f"Loaded {len(processes)} processes from {args.file}")
    else:
        processes = create_sample_processes(args.processes, args.seed)
        print(f"Created {len(processes)} random processes")
    
    # Print process details
    print("\nProcess Details:")
    for p in processes:
        print(f"  {p}")
    
    # Create schedulers based on the selected algorithm
    schedulers = []
    if args.algorithm in ['fcfs', 'all']:
        schedulers.append(FCFSScheduler())
    if args.algorithm in ['sjf', 'all']:
        schedulers.append(SJFScheduler())
    if args.algorithm in ['srtf', 'all']:
        schedulers.append(SRTFScheduler())
    if args.algorithm in ['rr', 'all']:
        schedulers.append(RoundRobinScheduler(args.quantum))
    if args.algorithm in ['priority', 'all']:
        schedulers.append(PriorityScheduler(preemptive=False))
        schedulers.append(PriorityScheduler(preemptive=True))
    if args.algorithm in ['multilevel', 'all']:
        schedulers.append(MultilevelQueueScheduler())
    
    # Run the simulation
    results = run_simulation(
        processes, 
        schedulers, 
        visualize=not args.no_visualize, 
        save_results=not args.no_save
    )
    
    # Print comparison results
    print("\nScheduler Comparison:")
    print(results["metrics"].sort_values('avg_waiting_time'))
    
    # Print path to saved results if applicable
    if not args.no_save and results["saved_paths"]:
        print(f"\nResults saved to: {results['saved_paths']['base_path']}")
    
    # Show figures if visualizations were generated and not in headless mode
    if not args.no_visualize and os.environ.get('DISPLAY', '') != '':
        for fig in results["figures"].values():
            plt.figure(fig.number)
        plt.show()

if __name__ == "__main__":
    main()