import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.patches import Patch
import io
import base64

class Visualizer:
    """
    Utility class for visualizing scheduling algorithm results.
    """
    
    def __init__(self):
        """Initialize the visualizer with default settings."""
        # Define a color map for processes and special blocks
        self.colors = plt.cm.tab10.colors
        self.special_colors = {
            'IDLE': 'lightgray',
            'CS': 'darkgray'
        }
    
    def gantt_chart(self, execution_log, title="Process Execution Gantt Chart", figsize=(12, 6)):
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Sort execution log by start time
        execution_log = sorted(execution_log, key=lambda x: x[1])
        
        # Get unique process IDs (excluding special states)
        process_ids = sorted(set(pid for pid, _, _ in execution_log if pid not in self.special_colors))
        
        # Create y-position mapping
        y_positions = {}
        current_y = 0
        
        # Add special states first
        for special in self.special_colors:
            if any(pid == special for pid, _, _ in execution_log):
                y_positions[special] = current_y
                current_y += 1
        
        # Add process positions
        for pid in process_ids:
            y_positions[pid] = current_y
            current_y += 1
        
        # Plot each execution segment
        for pid, start, end in execution_log:
            duration = end - start
            color = self.special_colors.get(pid, self.colors[hash(str(pid)) % len(self.colors)])
            
            # Draw the execution block
            ax.barh(y_positions[pid], duration, left=start, height=0.5, 
                    color=color, alpha=0.8, edgecolor='black')
            
            # Add label for segments with enough width
            if duration > (execution_log[-1][2] - execution_log[0][1]) / 50:  # Only label wider segments
                ax.text(start + duration/2, y_positions[pid], str(pid), 
                        ha='center', va='center', color='black', fontweight='bold')
        
        # Set chart properties
        ax.set_title(title)
        ax.set_xlabel('Time')
        ax.set_yticks(list(y_positions.values()))
        ax.set_yticklabels(list(y_positions.keys()))
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Add legend
        legend_elements = []
        for pid in y_positions:
            if pid in self.special_colors:
                color = self.special_colors[pid]
                name = "Idle" if pid == "IDLE" else "Context Switch" if pid == "CS" else pid
                legend_elements.append(Patch(facecolor=color, edgecolor='black', label=name))
        
        # Add regular process legend entries (limit to avoid overcrowding)
        for i, pid in enumerate(process_ids[:10]):  # Limit to first 10 processes
            color = self.colors[hash(str(pid)) % len(self.colors)]
            legend_elements.append(Patch(facecolor=color, edgecolor='black', label=f"Process {pid}"))
        
        # Add "+ more" if there are more processes
        if len(process_ids) > 10:
            legend_elements.append(Patch(facecolor='white', edgecolor='white', label="+ more..."))
        
        ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.1),
                  ncol=min(5, len(legend_elements)), frameon=True)
        
        plt.tight_layout()
        return fig
    
    def metrics_comparison_chart(self, metrics_df, title="Scheduler Performance Comparison", figsize=(14, 8)):
        """
        Generate charts comparing metrics across different schedulers.
        
        Args:
            metrics_df (pd.DataFrame): DataFrame containing metrics for different schedulers
            title (str): Title for the chart
            figsize (tuple): Figure size (width, height)
            
        Returns:
            plt.Figure: The comparison chart figure
        """
        if metrics_df.empty:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, "No data available for comparison", 
                    ha='center', va='center', fontsize=14)
            return fig
        
        # Create figure with subplots
        fig, axs = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle(title, fontsize=16)
        
        metrics = ['avg_waiting_time', 'avg_turnaround_time', 'avg_response_time', 'cpu_utilization']
        titles = ['Average Waiting Time', 'Average Turnaround Time', 
                 'Average Response Time', 'CPU Utilization (%)']
        
        # Plot each metric
        for i, (metric, subplot_title) in enumerate(zip(metrics, titles)):
            row, col = i // 2, i % 2
            ax = axs[row, col]
            
            # Sort by the current metric
            sorted_df = metrics_df.sort_values(metric)
            
            # Create bar chart
            bars = ax.bar(sorted_df.index, sorted_df[metric], color=self.colors[:len(sorted_df)])
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{height:.2f}', ha='center', va='bottom', fontsize=8)
            
            # Set subplot properties
            ax.set_title(subplot_title)
            ax.set_ylabel('Time' if 'time' in metric else 'Percentage')
            ax.tick_params(axis='x', rotation=45)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust for suptitle
        return fig
    
    def timeline_chart(self, processes, title="Process Timeline", figsize=(12, 8)):
        """
        Generate a timeline chart showing when processes arrive, execute, and complete.
        
        Args:
            processes (list): List of Process objects
            title (str): Title for the chart
            figsize (tuple): Figure size (width, height)
            
        Returns:
            plt.Figure: The timeline chart figure
        """
        if not processes:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, "No processes available for timeline", 
                    ha='center', va='center', fontsize=14)
            return fig
        
        # Sort processes by arrival time
        processes = sorted(processes, key=lambda p: p.arrival_time)
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Get max finish time for x-axis limit
        max_finish = max(p.finish_time if p.finish_time is not None else p.arrival_time 
                          for p in processes)
        
        # Plot each process
        y_positions = {}
        for i, process in enumerate(processes):
            y_pos = len(processes) - i
            y_positions[process.pid] = y_pos
            
            # Plot arrival point
            ax.scatter(process.arrival_time, y_pos, marker='o', color='green', s=100, 
                      label='Arrival' if i == 0 else "")
            
            # Plot waiting periods
            if process.execution_history:
                # Plot first waiting period (from arrival to first execution)
                first_start = process.execution_history[0][0]
                if first_start > process.arrival_time:
                    ax.hlines(y_pos, process.arrival_time, first_start, colors='orange', 
                             linestyles='--', linewidth=2)
                    ax.text((process.arrival_time + first_start)/2, y_pos + 0.1, 
                           f"Wait ({first_start - process.arrival_time})", ha='center', fontsize=8)
                
                # Plot execution periods
                for j, (start, end) in enumerate(process.execution_history):
                    ax.hlines(y_pos, start, end, colors=self.colors[i % len(self.colors)], 
                             linewidth=4, label='Execution' if i == 0 and j == 0 else "")
                    
                    # Add execution duration label for longer segments
                    if end - start >= max_finish * 0.05:
                        ax.text((start + end)/2, y_pos - 0.1, f"CPU ({end - start})", 
                               ha='center', va='top', fontsize=8)
                    
                    # Plot waiting periods between executions
                    if j < len(process.execution_history) - 1:
                        next_start = process.execution_history[j+1][0]
                        if next_start > end:
                            ax.hlines(y_pos, end, next_start, colors='orange', 
                                     linestyles='--', linewidth=2)
                            ax.text((end + next_start)/2, y_pos + 0.1, 
                                   f"Wait ({next_start - end})", ha='center', fontsize=8)
            
            # Plot finish point if process is completed
            if process.finish_time is not None:
                ax.scatter(process.finish_time, y_pos, marker='x', color='red', s=100,
                          label='Finish' if i == 0 else "")
            
            # Add process label
            ax.text(0, y_pos, f"P{process.pid}: {process.name}", ha='right', va='center',
                   fontweight='bold', fontsize=10)
        
        # Set chart properties
        ax.set_title(title)
        ax.set_xlabel('Time')
        ax.set_ylabel('Processes')
        ax.set_yticks([])  # Hide y-axis ticks
        ax.set_xlim(-1, max_finish + 1)
        ax.set_ylim(0, len(processes) + 1)
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Create custom legend
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='upper center', 
                 bbox_to_anchor=(0.5, -0.1), ncol=3)
        
        plt.tight_layout()
        return fig
    
    def save_figure(self, fig, filename):
        """
        Save a figure to a file.
        
        Args:
            fig (plt.Figure): The figure to save
            filename (str): The filename to save to
            
        Returns:
            str: The path to the saved file
        """
        fig.savefig(filename, bbox_inches='tight', dpi=300)
        plt.close(fig)
        return filename
    
    def figure_to_base64(self, fig):
        """
        Convert a figure to a base64-encoded string.
        
        Args:
            fig (plt.Figure): The figure to convert
            
        Returns:
            str: Base64-encoded string of the figure
        """
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return img_str