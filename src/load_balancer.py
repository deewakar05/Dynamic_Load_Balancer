import numpy as np
import time
from typing import List, Dict
import matplotlib.pyplot as plt
from collections import deque

class Task:
    def __init__(self, task_id: int, workload: float, priority: int = 0):
        self.task_id = task_id
        self.workload = workload
        self.priority = priority
        self.assigned_processor = None
        self.creation_time = time.time()
        self.completion_time = None
        self.migration_count = 0

class Processor:
    def __init__(self, processor_id: int):
        self.processor_id = processor_id
        self.current_load = 0.0
        self.state = "IDLE"  # IDLE, BUSY, OVERLOADED
        self.tasks: List[Task] = []
        self.load_history = deque(maxlen=100)
        self.completed_tasks = 0
        self.total_processing_time = 0.0
        self.queue_length_history = deque(maxlen=100)
        self.processing_speed = 1.0  # Configurable processing speed
        self.queue_size_limit = 20   # Configurable queue limit
        
    def update_state(self):
        if self.current_load == 0:
            self.state = "IDLE"
        elif self.current_load > 0.8:
            self.state = "OVERLOADED"
        else:
            self.state = "BUSY"
            
    def update_metrics(self):
        self.queue_length_history.append(len(self.tasks))
        self.update_state()
        
    def can_accept_task(self) -> bool:
        return len(self.tasks) < self.queue_size_limit
        
    def process_task(self, task: Task) -> float:
        return task.workload / self.processing_speed

class DynamicLoadBalancer:
    def __init__(self, num_processors: int):
        self.processors = [Processor(i) for i in range(num_processors)]
        self.task_counter = 0
        self.start_time = time.time()
        self.total_tasks = 0
        self.completed_tasks = 0
        self.load_balance_count = 0
        self.total_migrations = 0
        
    def create_task(self, workload: float, priority: int = 0) -> Task:
        task = Task(self.task_counter, workload, priority)
        self.task_counter += 1
        self.total_tasks += 1
        return task
    
    def get_processor_loads(self) -> List[float]:
        return [p.current_load for p in self.processors]
    
    def assign_task(self, task: Task) -> int:
        loads = self.get_processor_loads()
        available_processors = [i for i, p in enumerate(self.processors) 
                              if p.can_accept_task()]
        
        if not available_processors:
            return -1
            
        target_processor = min(available_processors, 
                             key=lambda i: loads[i])
        
        self.processors[target_processor].tasks.append(task)
        self.processors[target_processor].current_load += task.workload
        task.assigned_processor = target_processor
        
        return target_processor
    
    def balance_load(self):
        loads = self.get_processor_loads()
        avg_load = np.mean(loads)
        std_load = np.std(loads)
        
        upper_threshold = avg_load + std_load
        lower_threshold = avg_load - std_load
        
        overloaded = [i for i, load in enumerate(loads) if load > upper_threshold]
        underloaded = [i for i, load in enumerate(loads) 
                      if load < lower_threshold and self.processors[i].can_accept_task()]
        
        if overloaded and underloaded:
            self.load_balance_count += 1
        
        for over_idx in overloaded:
            for under_idx in underloaded:
                if len(self.processors[over_idx].tasks) > 0:
                    tasks = sorted(self.processors[over_idx].tasks, 
                                 key=lambda x: x.priority, reverse=True)
                    task = tasks[0]
                    
                    self.processors[over_idx].tasks.remove(task)
                    self.processors[over_idx].current_load -= task.workload
                    
                    self.processors[under_idx].tasks.append(task)
                    self.processors[under_idx].current_load += task.workload
                    task.assigned_processor = under_idx
                    task.migration_count += 1
                    self.total_migrations += 1
    
    def update_load_history(self):
        for processor in self.processors:
            processor.load_history.append(processor.current_load)
            processor.update_metrics()
            
            if processor.tasks:
                task = processor.tasks.pop(0)
                processing_time = processor.process_task(task)
                processor.completed_tasks += 1
                processor.total_processing_time += processing_time
                self.completed_tasks += 1
                task.completion_time = time.time()
    
    def get_statistics(self) -> Dict:
        elapsed_time = time.time() - self.start_time
        return {
            'total_tasks': self.total_tasks,
            'completed_tasks': self.completed_tasks,
            'load_balance_count': self.load_balance_count,
            'total_migrations': self.total_migrations,
            'elapsed_time': elapsed_time,
            'avg_processing_time': np.mean([p.total_processing_time for p in self.processors]) if self.completed_tasks > 0 else 0,
            'processor_stats': [
                {
                    'id': p.processor_id,
                    'state': p.state,
                    'completed_tasks': p.completed_tasks,
                    'avg_load': np.mean(list(p.load_history)) if p.load_history else 0,
                    'avg_queue_length': np.mean(list(p.queue_length_history)) if p.queue_length_history else 0
                }
                for p in self.processors
            ]
        }

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
            num_tasks = int(input("\nEnter number of tasks (10-1000): "))
            if 10 <= num_tasks <= 1000:
                break
            print("Please enter a number between 10 and 1000")
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
    
    return num_processors, num_tasks, task_probability

def main():
    # Get user input
    num_processors, num_tasks, task_probability = get_user_input()
    
    # Initialize load balancer
    balancer = DynamicLoadBalancer(num_processors)
    
    print(f"\nStarting simulation...")
    print(f"Processors: {num_processors}")
    print(f"Total Tasks: {num_tasks}")
    print(f"Task probability: {task_probability}")
    
    step = 0
    while balancer.total_tasks < num_tasks:
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
        step += 1
    
    # Final visualization
    balancer.visualize_loads()
    print("\nSimulation complete! Graph saved in 'load_distribution.png'.")

if __name__ == "__main__":
    main() 
