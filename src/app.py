import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import json
import os
from datetime import datetime
import base64
from io import BytesIO
import numpy as np

# Import functionality from provided modules
# Note: In a real application, you would import these classes
# Here we're redefining the necessary functionality

class Process:
    """Simplified Process class for visualization purposes"""
    def __init__(self, pid, name, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.start_time = None
        self.finish_time = None
        self.waiting_time = 0
        self.response_time = None
        self.execution_history = []

    def get_turnaround_time(self):
        if self.finish_time is None:
            return 0
        return self.finish_time - self.arrival_time

    def get_waiting_time(self):
        return self.waiting_time

    def get_response_time(self):
        return self.response_time if self.response_time is not None else 0

# Simplified FileHandler for loading results
class FileHandler:
    @staticmethod
    def load_processes_from_json(filename):
        if not os.path.exists(filename):
            return []
        
        with open(filename, 'r') as f:
            try:
                data = json.load(f)
                return data
            except json.JSONDecodeError:
                return []
    
    @staticmethod
    def load_simulation_results(result_path):
        if not os.path.exists(result_path):
            return None
        
        metrics_path = os.path.join(result_path, "metrics.csv")
        if not os.path.exists(metrics_path):
            return None
            
        metrics = pd.read_csv(metrics_path)
        
        process_details = {}
        execution_logs = {}
        
        # Find all CSV files for process details
        for filename in os.listdir(result_path):
            if filename.endswith("_process_details.csv"):
                scheduler_name = filename.replace("_process_details.csv", "").replace("_", " ")
                file_path = os.path.join(result_path, filename)
                process_details[scheduler_name] = pd.read_csv(file_path)
        
        # Find all JSON files for execution logs
        for filename in os.listdir(result_path):
            if filename.endswith("_execution_log.json"):
                scheduler_name = filename.replace("_execution_log.json", "").replace("_", " ")
                file_path = os.path.join(result_path, filename)
                with open(file_path, 'r') as f:
                    execution_logs[scheduler_name] = json.load(f)
        
        return {
            "metrics": metrics,
            "process_details": process_details,
            "execution_logs": execution_logs,
            "base_path": result_path
        }

# Visualizer class (similar to your provided code)
class Visualizer:
    def __init__(self):
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
            if pid not in y_positions:
                continue  # Skip if process ID not in our mapping
                
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
        
        if legend_elements:
            ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.1),
                    ncol=min(5, len(legend_elements)), frameon=True)
        
        plt.tight_layout()
        return fig
    
    def metrics_comparison_chart(self, metrics_df, title="Scheduler Performance Comparison", figsize=(14, 8)):
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
            
            if metric not in metrics_df.columns:
                ax.text(0.5, 0.5, f"No data for {subplot_title}", 
                      ha='center', va='center', fontsize=10)
                continue
                
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
        if not processes:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, "No processes available for timeline", 
                    ha='center', va='center', fontsize=14)
            return fig
        
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
    
    def figure_to_base64(self, fig):
        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return img_str

# Main Streamlit application
def main():
    st.set_page_config(page_title="CPU Scheduling Visualizer", layout="wide")
    
    st.title("CPU Scheduling Algorithm Visualizer")
    st.write("""
    This application visualizes and compares the performance of different CPU scheduling algorithms.
    Upload your simulation results or use the sample data to explore metrics and visualizations.
    """)
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Metrics Comparison", "Gantt Charts", "Process Timeline", "Raw Data"])
    
    # Initialize data container
    if 'data' not in st.session_state:
        st.session_state.data = None
    
    # File uploader for results directory
    st.sidebar.header("Load Data")
    uploaded_file = st.sidebar.file_uploader("Upload a metrics.csv file", type=["csv"])
    
    # Load data button
    if uploaded_file is not None and st.sidebar.button("Load Data"):
        # Create a temporary directory to store uploaded files
        temp_dir = "temp_results_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save the metrics file
        metrics_path = os.path.join(temp_dir, "metrics.csv")
        with open(metrics_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Create sample data in case additional files are missing
        metrics_df = pd.read_csv(metrics_path)
        
        # Create sample execution log
        sample_execution_log = {}
        for scheduler in metrics_df['scheduler'].values:
            sample_execution_log[scheduler] = [(0, 0, 2), (1, 2, 5), (2, 5, 8), ('IDLE', 8, 10)]
        
        # Create sample process details
        sample_process_details = {}
        for scheduler in metrics_df['scheduler'].values:
            sample_details = pd.DataFrame({
                'PID': [0, 1, 2],
                'Name': [f'Process{i}' for i in range(3)],
                'Arrival Time': [0, 1, 2],
                'Burst Time': [2, 3, 3],
                'Start Time': [0, 2, 5],
                'Finish Time': [2, 5, 8],
                'Waiting Time': [0, 1, 3],
                'Turnaround Time': [2, 4, 6],
                'Response Time': [0, 1, 3]
            })
            sample_process_details[scheduler] = sample_details
        
        # Store data in session state
        st.session_state.data = {
            "metrics": metrics_df,
            "process_details": sample_process_details,
            "execution_logs": sample_execution_log,
            "base_path": temp_dir
        }
        
        st.sidebar.success("Data loaded successfully!")
    
    # Use sample data button
    if st.sidebar.button("Use Sample Data"):
        # Create sample metrics DataFrame
        sample_metrics = pd.DataFrame({
            'scheduler': ['FCFS', 'SJF', 'RR', 'Priority'],
            'avg_waiting_time': [5.2, 4.1, 6.3, 5.8],
            'avg_turnaround_time': [8.7, 7.2, 9.5, 9.0],
            'avg_response_time': [2.1, 1.8, 1.5, 2.5],
            'throughput': [0.12, 0.14, 0.11, 0.12],
            'cpu_utilization': [92.5, 94.1, 89.7, 91.3]
        })
        
        # Create sample execution logs
        sample_execution_logs = {
            'FCFS': [(1, 0, 5), (2, 5, 9), (3, 9, 15), ('IDLE', 15, 17), (4, 17, 20)],
            'SJF': [(2, 0, 4), (1, 4, 9), (4, 9, 12), (3, 12, 18)],
            'RR': [(1, 0, 2), (2, 2, 4), (3, 4, 6), (1, 6, 8), (2, 8, 9), (3, 9, 12), (4, 12, 14), (4, 14, 16)],
            'Priority': [(3, 0, 6), (1, 6, 11), (2, 11, 15), (4, 15, 18)]
        }
        
        # Create process details for each scheduler
        sample_process_details = {}
        for scheduler in sample_metrics['scheduler']:
            # Create unique process details for each scheduler
            processes = []
            for i in range(1, 5):
                p = Process(i, f"Process{i}", i-1, 5-i%2, i)
                p.start_time = i
                p.finish_time = i + 5
                p.waiting_time = 2*i
                p.response_time = i
                
                # Add execution history based on the logs
                if scheduler in sample_execution_logs:
                    p.execution_history = [(start, end) for pid, start, end in sample_execution_logs[scheduler] if pid == i]
                
                processes.append(p)
            
            # Convert to DataFrame
            df = pd.DataFrame({
                'PID': [p.pid for p in processes],
                'Name': [p.name for p in processes],
                'Arrival Time': [p.arrival_time for p in processes],
                'Burst Time': [p.burst_time for p in processes],
                'Priority': [p.priority for p in processes],
                'Start Time': [p.start_time for p in processes],
                'Finish Time': [p.finish_time for p in processes],
                'Waiting Time': [p.waiting_time for p in processes],
                'Turnaround Time': [p.get_turnaround_time() for p in processes],
                'Response Time': [p.response_time for p in processes]
            })
            
            sample_process_details[scheduler] = df
        
        # Store sample data in session state
        st.session_state.data = {
            "metrics": sample_metrics,
            "process_details": sample_process_details,
            "execution_logs": sample_execution_logs,
            "base_path": "sample_data"
        }
        
        st.sidebar.success("Sample data loaded!")
    
    # Check if data is loaded
    if st.session_state.data is None:
        st.info("Please load data using the sidebar options to view visualizations.")
        return
    
    # Display different pages based on selection
    if page == "Metrics Comparison":
        display_metrics_page(st.session_state.data)
    elif page == "Gantt Charts":
        display_gantt_charts(st.session_state.data)
    elif page == "Process Timeline":
        display_process_timeline(st.session_state.data)
    elif page == "Raw Data":
        display_raw_data(st.session_state.data)

def display_metrics_page(data):
    st.header("Scheduler Performance Metrics Comparison")
    
    metrics_df = data["metrics"]
    
    if metrics_df.empty:
        st.warning("No metrics data available.")
        return
    
    # Ensure 'scheduler' is set as index if it exists as a column
    if 'scheduler' in metrics_df.columns:
        metrics_df = metrics_df.set_index('scheduler')
    
    # Display metrics table
    st.subheader("Performance Metrics")
    st.dataframe(metrics_df.style.highlight_max(axis=0, color='lightgreen')
                          .highlight_min(axis=0, color='lightcoral'))
    
    # Create metrics comparison chart
    visualizer = Visualizer()
    metrics_fig = visualizer.metrics_comparison_chart(metrics_df.reset_index())
    
    # Display chart
    st.subheader("Metrics Comparison")
    st.pyplot(metrics_fig)
    
    # Add download button for chart
    chart_image = visualizer.figure_to_base64(metrics_fig)
    st.markdown(f"""
    <a href="data:image/png;base64,{chart_image}" download="metrics_comparison.png">
        <button style="background-color:#4CAF50; color:white; border:none; padding:10px 24px; cursor:pointer; border-radius:4px;">
            Download Chart
        </button>
    </a>
    """, unsafe_allow_html=True)

def display_gantt_charts(data):
    st.header("Process Execution Gantt Charts")
    
    execution_logs = data["execution_logs"]
    
    if not execution_logs:
        st.warning("No execution logs available.")
        return
    
    # Select scheduler
    scheduler = st.selectbox("Select Scheduler", list(execution_logs.keys()))
    
    # Display Gantt chart for selected scheduler
    if scheduler in execution_logs:
        visualizer = Visualizer()
        gantt_fig = visualizer.gantt_chart(
            execution_logs[scheduler], 
            title=f"{scheduler} Scheduler - Process Execution"
        )
        
        st.pyplot(gantt_fig)
        
        # Add download button for chart
        chart_image = visualizer.figure_to_base64(gantt_fig)
        st.markdown(f"""
        <a href="data:image/png;base64,{chart_image}" download="{scheduler}_gantt.png">
            <button style="background-color:#4CAF50; color:white; border:none; padding:10px 24px; cursor:pointer; border-radius:4px;">
                Download Chart
            </button>
        </a>
        """, unsafe_allow_html=True)
        
        # Display execution log details
        st.subheader("Execution Log Details")
        
        # Convert execution log to DataFrame for better display
        log_df = pd.DataFrame(execution_logs[scheduler], columns=['Process ID', 'Start Time', 'End Time'])
        log_df['Duration'] = log_df['End Time'] - log_df['Start Time']
        
        st.dataframe(log_df)

def display_process_timeline(data):
    st.header("Process Timeline Visualization")
    
    process_details = data["process_details"]
    execution_logs = data["execution_logs"]
    
    if not process_details:
        st.warning("No process details available.")
        return
    
    # Select scheduler
    scheduler = st.selectbox("Select Scheduler", list(process_details.keys()))
    
    if scheduler in process_details:
        # Create Process objects from the details
        processes = []
        
        df = process_details[scheduler]
        for _, row in df.iterrows():
            process = Process(
                pid=row['PID'] if 'PID' in row else 0,
                name=row['Name'] if 'Name' in row else f"Process{row['PID'] if 'PID' in row else 0}",
                arrival_time=row['Arrival Time'] if 'Arrival Time' in row else 0,
                burst_time=row['Burst Time'] if 'Burst Time' in row else 0,
                priority=row['Priority'] if 'Priority' in row else 0
            )
            
            # Set additional attributes
            process.start_time = row['Start Time'] if 'Start Time' in row else None
            process.finish_time = row['Finish Time'] if 'Finish Time' in row else None
            process.waiting_time = row['Waiting Time'] if 'Waiting Time' in row else 0
            process.response_time = row['Response Time'] if 'Response Time' in row else None
            
            # Set execution history from logs if available
            if scheduler in execution_logs:
                process.execution_history = [
                    (start, end) for pid, start, end in execution_logs[scheduler] 
                    if str(pid) == str(process.pid)
                ]
            
            processes.append(process)
        
        # Create timeline chart
        visualizer = Visualizer()
        timeline_fig = visualizer.timeline_chart(
            processes, 
            title=f"{scheduler} Scheduler - Process Timeline"
        )
        
        st.pyplot(timeline_fig)
        
        # Add download button for chart
        chart_image = visualizer.figure_to_base64(timeline_fig)
        st.markdown(f"""
        <a href="data:image/png;base64,{chart_image}" download="{scheduler}_timeline.png">
            <button style="background-color:#4CAF50; color:white; border:none; padding:10px 24px; cursor:pointer; border-radius:4px;">
                Download Chart
            </button>
        </a>
        """, unsafe_allow_html=True)

def display_raw_data(data):
    st.header("Raw Data")
    
    # Tabs for different data types
    tab1, tab2, tab3 = st.tabs(["Metrics", "Process Details", "Execution Logs"])
    
    with tab1:
        st.subheader("Scheduler Metrics")
        if "metrics" in data and not data["metrics"].empty:
            st.dataframe(data["metrics"])
        else:
            st.warning("No metrics data available.")
    
    with tab2:
        st.subheader("Process Details")
        if "process_details" in data and data["process_details"]:
            scheduler = st.selectbox("Select Scheduler for Process Details", 
                                     list(data["process_details"].keys()),
                                     key="pd_scheduler")
            
            if scheduler in data["process_details"]:
                st.dataframe(data["process_details"][scheduler])
            else:
                st.warning("No process details available for the selected scheduler.")
        else:
            st.warning("No process details available.")
    
    with tab3:
        st.subheader("Execution Logs")
        if "execution_logs" in data and data["execution_logs"]:
            scheduler = st.selectbox("Select Scheduler for Execution Logs", 
                                     list(data["execution_logs"].keys()),
                                     key="el_scheduler")
            
            if scheduler in data["execution_logs"]:
                # Convert execution log to DataFrame for better display
                log_df = pd.DataFrame(data["execution_logs"][scheduler], 
                                     columns=['Process ID', 'Start Time', 'End Time'])
                log_df['Duration'] = log_df['End Time'] - log_df['Start Time']
                
                st.dataframe(log_df)
            else:
                st.warning("No execution logs available for the selected scheduler.")
        else:
            st.warning("No execution logs available.")

if __name__ == "__main__":
    main()