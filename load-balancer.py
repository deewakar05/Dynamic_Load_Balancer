import numpy as np
import time
from typing import List, Dict
import matplotlib.pyplot as plt
from collections import deque

class Task:
    def __init__(self, task_id: int, workload: float):
        self.task_id = task_id
        self.workload = workload  # Simulated CPU intensive work
        self.assigned_processor = None

class Processor:
    def __init__(self, processor_id: int):
        self.processor_id = processor_id
        self.current_load = 0.0
        self.tasks: List[Task] = []
        self.load_history = deque(maxlen=100)

class DynamicLoadBalancer:
    def __init__(self, num_processors: int):
        self.processors = [Processor(i) for i in range(num_processors)]
        self.task_counter = 0
        
    def create_task(self, workload: float) -> Task:
        """Create a new task with given workload"""
        task = Task(self.task_counter, workload)
        self.task_counter += 1
        return task
    
    def get_processor_loads(self) -> List[float]:
        """Get current load of all processors"""
        return [p.current_load for p in self.processors]
    
    def assign_task(self, task: Task) -> int:
        """Assign task to least loaded processor"""
        loads = self.get_processor_loads()
        target_processor = np.argmin(loads)
        
        # Assign task to the chosen processor
        self.processors[target_processor].tasks.append(task)
        self.processors[target_processor].current_load += task.workload
        task.assigned_processor = target_processor
        
        return target_processor
    
    def balance_load(self):
        """Perform load balancing by moving tasks between processors"""
        loads = self.get_processor_loads()
        avg_load = np.mean(loads)
        
        # Find overloaded and underloaded processors
        overloaded = [i for i, load in enumerate(loads) if load > avg_load * 1.1]
        underloaded = [i for i, load in enumerate(loads) if load < avg_load * 0.9]
        
        for over_idx in overloaded:
            for under_idx in underloaded:
                if len(self.processors[over_idx].tasks) > 0:
                    # Move task from overloaded to underloaded processor
                    task = self.processors[over_idx].tasks.pop()
                    self.processors[over_idx].current_load -= task.workload
                    
                    self.processors[under_idx].tasks.append(task)
                    self.processors[under_idx].current_load += task.workload
                    task.assigned_processor = under_idx
    
    def update_load_history(self):
        """Update load history for visualization"""
        for processor in self.processors:
            processor.load_history.append(processor.current_load)
    
    def visualize_loads(self):
        """Visualize processor loads over time"""
        plt.figure(figsize=(12, 6))
        for i, processor in enumerate(self.processors):
            plt.plot(list(processor.load_history), label=f'Processor {i}')
        
        plt.title('Processor Load Distribution Over Time')
        plt.xlabel('Time Steps')
        plt.ylabel('Load')
        plt.legend()
        plt.grid(True)
        plt.savefig('load_distribution.png')
        plt.close()

def get_user_input():
    """Get simulation parameters from user"""
    print("\n=== Dynamic Load Balancer Simulator ===")
    while True:
        try:
            num_processors = int(input("\nEnter number of processors (2-8): "))
            if 2 <= num_processors <= 8:
                break
            print("Please enter a number between 2 and 8")
        except ValueError:
            print("Please enter a valid number")
    
    while True:
        try:
            num_steps = int(input("\nEnter number of simulation steps (50-500): "))
            if 50 <= num_steps <= 500:
                break
            print("Please enter a number between 50 and 500")
        except ValueError:
            print("Please enter a valid number")
    
    while True:
        try:
            task_probability = float(input("\nEnter new task probability (0.1-0.9): "))
            if 0.1 <= task_probability <= 0.9:
                break
            print("Please enter a number between 0.1 and 0.9")
        except ValueError:
            print("Please enter a valid number")
    
    return num_processors, num_steps, task_probability

def main():
    # Get user input
    num_processors, num_steps, task_probability = get_user_input()
    
    # Initialize load balancer
    balancer = DynamicLoadBalancer(num_processors)
    
    print(f"\nStarting simulation...")
    print(f"Processors: {num_processors}")
    print(f"Steps: {num_steps}")
    print(f"Task probability: {task_probability}")
    
    for step in range(num_steps):
        # Create random tasks
        if np.random.random() < task_probability:
            workload = np.random.uniform(0.1, 1.0)
            task = balancer.create_task(workload)
            processor = balancer.assign_task(task)
            print(f"\nStep {step}: Task {task.task_id} (workload: {workload:.2f}) assigned to processor {processor}")
        
        # Periodically balance load
        if step % 10 == 0:
            balancer.balance_load()
            loads = balancer.get_processor_loads()
            print(f"\nStep {step}: Current loads: {[f'{load:.2f}' for load in loads]}")
        
        # Update and visualize
        balancer.update_load_history()
        
        # Simulate work
        time.sleep(0.1)
    
    # Final visualization
    balancer.visualize_loads()
    print("\nSimulation complete! Graph saved in 'load_distribution.png'.")

if __name__ == "__main__":
    main() 
