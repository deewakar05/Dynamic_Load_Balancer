import sys
import numpy as np

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox,
                           QPushButton, QTextEdit, QGroupBox, QScrollArea)
from PyQt6.QtCore import QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from collections import deque
from typing import List, Dict
import time

plt.switch_backend('QtAgg')

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
        self.state = "IDLE"
        self.tasks: List[Task] = []
        self.load_history = deque(maxlen=100)
        self.completed_tasks = 0
        self.total_processing_time = 0.0
        self.queue_length_history = deque(maxlen=100)
        self.processing_speed = 1.0
        self.queue_size_limit = 20
        
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

class LoadBalancerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic Load Balancer Simulator")
        self.setGeometry(100, 100, 1600, 900)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Control panel with scroll
        control_panel = QWidget()
        control_panel.setFixedWidth(400)
        control_scroll = QScrollArea()
        control_scroll.setWidget(control_panel)
        control_scroll.setWidgetResizable(True)
        
        control_layout = QVBoxLayout(control_panel)
        
        # Process Settings
        process_group = QGroupBox("Process Settings")
        process_layout = QVBoxLayout()
        
        proc_layout = QHBoxLayout()
        proc_layout.addWidget(QLabel("Processors:"))
        self.proc_spin = QSpinBox()
        self.proc_spin.setRange(2, 8)
        self.proc_spin.setValue(4)
        self.proc_spin.valueChanged.connect(self.update_process_settings)
        proc_layout.addWidget(self.proc_spin)
        process_layout.addLayout(proc_layout)
        
        self.process_settings = []
        self.process_settings_widget = QWidget()
        self.process_settings_layout = QVBoxLayout(self.process_settings_widget)
        process_layout.addWidget(self.process_settings_widget)
        
        process_group.setLayout(process_layout)
        control_layout.addWidget(process_group)
        
        # Task Settings
        task_group = QGroupBox("Task Settings")
        task_layout = QVBoxLayout()
        
        # Number of tasks
        num_tasks_layout = QHBoxLayout()
        num_tasks_layout.addWidget(QLabel("Number of Tasks:"))
        self.num_tasks_spin = QSpinBox()
        self.num_tasks_spin.setRange(10, 1000)
        self.num_tasks_spin.setValue(100)
        self.num_tasks_spin.setSingleStep(10)
        num_tasks_layout.addWidget(self.num_tasks_spin)
        task_layout.addLayout(num_tasks_layout)
        
        prob_layout = QHBoxLayout()
        prob_layout.addWidget(QLabel("Task Probability:"))
        self.prob_spin = QDoubleSpinBox()
        self.prob_spin.setRange(0.1, 0.9)
        self.prob_spin.setSingleStep(0.1)
        self.prob_spin.setValue(0.3)
        prob_layout.addWidget(self.prob_spin)
        task_layout.addLayout(prob_layout)
        
        priority_layout = QHBoxLayout()
        priority_layout.addWidget(QLabel("Priority:"))
        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(0, 5)
        self.priority_spin.setValue(0)
        priority_layout.addWidget(self.priority_spin)
        task_layout.addLayout(priority_layout)
        
        workload_layout = QHBoxLayout()
        workload_layout.addWidget(QLabel("Workload:"))
        self.workload_min = QDoubleSpinBox()
        self.workload_min.setRange(0.1, 1.0)
        self.workload_min.setSingleStep(0.1)
        self.workload_min.setValue(0.1)
        workload_layout.addWidget(self.workload_min)
        workload_layout.addWidget(QLabel("-"))
        self.workload_max = QDoubleSpinBox()
        self.workload_max.setRange(0.1, 1.0)
        self.workload_max.setSingleStep(0.1)
        self.workload_max.setValue(1.0)
        workload_layout.addWidget(self.workload_max)
        task_layout.addLayout(workload_layout)
        
        task_group.setLayout(task_layout)
        control_layout.addWidget(task_group)
        
        # Load Balancing Settings
        balance_group = QGroupBox("Load Balancing")
        balance_layout = QVBoxLayout()
        
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Threshold:"))
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0.1, 0.5)
        self.threshold_spin.setSingleStep(0.1)
        self.threshold_spin.setValue(0.2)
        threshold_layout.addWidget(self.threshold_spin)
        balance_layout.addLayout(threshold_layout)
        
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel("Frequency:"))
        self.freq_spin = QSpinBox()
        self.freq_spin.setRange(5, 50)
        self.freq_spin.setValue(10)
        freq_layout.addWidget(self.freq_spin)
        balance_layout.addLayout(freq_layout)
        
        balance_group.setLayout(balance_layout)
        control_layout.addWidget(balance_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_simulation)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_simulation)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        control_layout.addLayout(button_layout)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        self.stats_labels = {}
        stats = ['Total Tasks', 'Completed Tasks', 'Load Balance Count', 
                'Total Migrations', 'Avg Processing Time', 'Elapsed Time']
        for stat in stats:
            label = QLabel(f"{stat}: 0")
            self.stats_labels[stat] = label
            stats_layout.addWidget(label)
        stats_group.setLayout(stats_layout)
        control_layout.addWidget(stats_group)
        
        # Processor States
        states_group = QGroupBox("Processor States")
        states_layout = QVBoxLayout()
        self.state_labels = {}
        for i in range(8):
            label = QLabel(f"Processor {i}: IDLE")
            self.state_labels[i] = label
            states_layout.addWidget(label)
        states_group.setLayout(states_layout)
        control_layout.addWidget(states_group)
        
        # Log area
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        self.log_text.setMaximumHeight(300)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        control_layout.addWidget(log_group)
        
        layout.addWidget(control_scroll)
        
        # Graph area
        graph_panel = QWidget()
        graph_layout = QVBoxLayout(graph_panel)
        
        self.figure, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 8))
        self.canvas = FigureCanvas(self.figure)
        graph_layout.addWidget(self.canvas)
        
        layout.addWidget(graph_panel)
        
        # Timer for simulation
        self.timer = QTimer()
        self.timer.timeout.connect(self.simulation_step)
        
        # Initialize simulation variables
        self.balancer = None
        self.step = 0
        
        # Initialize process settings
        self.update_process_settings()
    
    def update_process_settings(self):
        for i in reversed(range(self.process_settings_layout.count())): 
            self.process_settings_layout.itemAt(i).widget().setParent(None)
        self.process_settings.clear()
        
        for i in range(self.proc_spin.value()):
            proc_group = QGroupBox(f"Processor {i} Settings")
            proc_layout = QVBoxLayout()
            
            speed_layout = QHBoxLayout()
            speed_layout.addWidget(QLabel("Processing Speed:"))
            speed_spin = QDoubleSpinBox()
            speed_spin.setRange(0.5, 2.0)
            speed_spin.setSingleStep(0.1)
            speed_spin.setValue(1.0)
            speed_layout.addWidget(speed_spin)
            proc_layout.addLayout(speed_layout)
            
            queue_layout = QHBoxLayout()
            queue_layout.addWidget(QLabel("Queue Size Limit:"))
            queue_spin = QSpinBox()
            queue_spin.setRange(5, 50)
            queue_spin.setValue(20)
            queue_layout.addWidget(queue_spin)
            proc_layout.addLayout(queue_layout)
            
            proc_group.setLayout(proc_layout)
            self.process_settings_layout.addWidget(proc_group)
            self.process_settings.append({
                'speed': speed_spin,
                'queue_size': queue_spin
            })
    
    def log_message(self, message: str):
        self.log_text.append(message)
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def update_statistics(self):
        if self.balancer:
            stats = self.balancer.get_statistics()
            self.stats_labels['Total Tasks'].setText(f"Total Tasks: {stats['total_tasks']}")
            self.stats_labels['Completed Tasks'].setText(f"Completed Tasks: {stats['completed_tasks']}")
            self.stats_labels['Load Balance Count'].setText(f"Load Balance Count: {stats['load_balance_count']}")
            self.stats_labels['Total Migrations'].setText(f"Total Migrations: {stats['total_migrations']}")
            self.stats_labels['Avg Processing Time'].setText(
                f"Avg Processing Time: {stats['avg_processing_time']:.2f}"
            )
            self.stats_labels['Elapsed Time'].setText(
                f"Elapsed Time: {stats['elapsed_time']:.1f}s"
            )
            
            for i, proc_stat in enumerate(stats['processor_stats']):
                if i < len(self.state_labels):
                    self.state_labels[i].setText(
                        f"Processor {i}: {proc_stat['state']} "
                        f"(Load: {proc_stat['avg_load']:.2f})"
                    )
    
    def start_simulation(self):
        self.balancer = DynamicLoadBalancer(self.proc_spin.value())
        
        for i, settings in enumerate(self.process_settings):
            self.balancer.processors[i].processing_speed = settings['speed'].value()
            self.balancer.processors[i].queue_size_limit = settings['queue_size'].value()
        
        self.step = 0
        self.max_tasks = self.num_tasks_spin.value()
        self.log_text.clear()
        self.log_message("Starting simulation...")
        self.log_message(f"Processors: {self.proc_spin.value()}")
        self.log_message(f"Number of Tasks: {self.max_tasks}")
        self.log_message(f"Task Probability: {self.prob_spin.value()}")
        self.log_message(f"Task Priority: {self.priority_spin.value()}")
        self.log_message(f"Workload Range: {self.workload_min.value()}-{self.workload_max.value()}")
        self.log_message(f"Load Balance Threshold: {self.threshold_spin.value()}")
        self.log_message(f"Balance Frequency: {self.freq_spin.value()} steps")
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.proc_spin.setEnabled(False)
        self.num_tasks_spin.setEnabled(False)
        self.prob_spin.setEnabled(False)
        self.priority_spin.setEnabled(False)
        self.workload_min.setEnabled(False)
        self.workload_max.setEnabled(False)
        self.threshold_spin.setEnabled(False)
        self.freq_spin.setEnabled(False)
        
        self.timer.start(100)
    
    def stop_simulation(self):
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.proc_spin.setEnabled(True)
        self.num_tasks_spin.setEnabled(True)
        self.prob_spin.setEnabled(True)
        self.priority_spin.setEnabled(True)
        self.workload_min.setEnabled(True)
        self.workload_max.setEnabled(True)
        self.threshold_spin.setEnabled(True)
        self.freq_spin.setEnabled(True)
        self.log_message("\nSimulation stopped.")
        
        if self.balancer:
            stats = self.balancer.get_statistics()
            self.log_message("\nFinal Statistics:")
            self.log_message(f"Total Tasks: {stats['total_tasks']}")
            self.log_message(f"Completed Tasks: {stats['completed_tasks']}")
            self.log_message(f"Load Balance Count: {stats['load_balance_count']}")
            self.log_message(f"Total Migrations: {stats['total_migrations']}")
            self.log_message(f"Average Processing Time: {stats['avg_processing_time']:.2f}")
            self.log_message(f"Total Elapsed Time: {stats['elapsed_time']:.1f}s")
    
    def simulation_step(self):
        if self.balancer.total_tasks < self.max_tasks:
            if np.random.random() < self.prob_spin.value():
                workload = np.random.uniform(self.workload_min.value(), self.workload_max.value())
                priority = self.priority_spin.value()
                task = self.balancer.create_task(workload, priority)
                processor = self.balancer.assign_task(task)
                self.log_message(
                    f"Step {self.step}: Task {task.task_id} "
                    f"(workload: {workload:.2f}, priority: {priority}) "
                    f"assigned to processor {processor}"
                )
        
        if self.step % self.freq_spin.value() == 0:
            self.balancer.balance_load()
            loads = self.balancer.get_processor_loads()
            self.log_message(
                f"Step {self.step}: Current loads: "
                f"{[f'{load:.2f}' for load in loads]}"
            )
        
        self.balancer.update_load_history()
        self.update_plot()
        self.update_statistics()
        
        self.step += 1
        
        # Stop simulation if all tasks are completed
        if self.balancer.total_tasks >= self.max_tasks and self.balancer.completed_tasks >= self.max_tasks:
            self.stop_simulation()
    
    def update_plot(self):
        self.ax1.clear()
        self.ax2.clear()
        
        for i, processor in enumerate(self.balancer.processors):
            self.ax1.plot(list(processor.load_history), label=f'Processor {i}')
        
        self.ax1.set_title('Processor Load Distribution Over Time')
        self.ax1.set_xlabel('Time Steps')
        self.ax1.set_ylabel('Load')
        self.ax1.legend()
        self.ax1.grid(True)
        
        for i, processor in enumerate(self.balancer.processors):
            self.ax2.plot(list(processor.queue_length_history), 
                         label=f'Processor {i}')
        
        self.ax2.set_title('Task Queue Length Over Time')
        self.ax2.set_xlabel('Time Steps')
        self.ax2.set_ylabel('Queue Length')
        self.ax2.legend()
        self.ax2.grid(True)
        
        self.figure.tight_layout()
        self.canvas.draw()

def main():
    app = QApplication(sys.argv)
    window = LoadBalancerGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
