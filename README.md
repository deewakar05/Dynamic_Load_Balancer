<b>Dynamic Load Balancer Simulator 🚀</b>

Welcome to the Dynamic Load Balancer Simulator! This Python-based tool simulates task assignment and load balancing across multiple processors, helping you visualize how workloads are distributed over time. 🎉

<b>🌟 Features :</b>

1. Multiple Processors 🖥️: Simulate 2 to 8 processors handling tasks dynamically.

2. Task Assignment 📊: Assigns tasks to the least-loaded processor using a smart algorithm.

3. Load Balancing ⚖️: Re-distributes tasks between overloaded and underloaded processors.

4. Visualization 📈: Plots processor loads over time with Matplotlib (saved as load_distribution.png).

5. Random Workloads 🎲: Generates tasks with random workloads for realistic simulation.
6. User-Friendly 🖱️: Interactive CLI to set simulation parameters.

<b>🛠️ Requirements :</b>

To run this simulator, you'll need:
Python 3.x 🐍 

Libraries 📦 :

numpy (for calculations) ➡️ pip install numpy

matplotlib (for plotting) ➡️ pip install matplotlib

<b>Install them with:</b>

bash

pip install numpy matplotlib

<b>🚀 How to Run: </b>

Clone or Download this project:

bash

git clone <repository-url>

cd dynamic-load-balancer-simulator

Run the Script:

bash

python load_balancer.py

Follow the Prompts:

Enter the number of processors (2-8) 🖥️

Set the number of simulation steps (50-500) ⏳

Choose the task creation probability (0.1-0.9) 🎲

Check the Output

<b>Screenshots:</b>

input:

![WhatsApp Image 2025-03-23 at 21 52 56](https://github.com/user-attachments/assets/3a00ddef-1fc9-45c2-b34f-a0bd67e79ada)

output:

![WhatsApp Image 2025-03-23 at 21 31 01](https://github.com/user-attachments/assets/4bab40ad-8867-41c4-9285-50039dcc5b58)
![WhatsApp Image 2025-03-23 at 21 32 48](https://github.com/user-attachments/assets/43bd099e-d5de-4c3f-83d3-2c8079d0f103)
![load_distribution](https://github.com/user-attachments/assets/c8b8b15d-7618-49d0-a698-e7b8ee0dd2bc)

<b>📋 Example Usage:</b>

bash

Enter number of processors (2-8): 4
Enter number of simulation steps (50-500): 100
Enter new task probability (0.1-0.9): 0.5

Starting simulation...

Processors: 4

Steps: 100

Task probability: 0.5

Step 0: Task 0 (workload: 0.73) assigned to processor 0

Step 0: Current loads: ['0.73', '0.00', '0.00', '0.00']
...

<b>🧠 How It Works:</b>

Task Creation 🎯:

Tasks are created with random workloads (0.1 to 1.0) based on the task probability.

Assignment 📌:

Each task is assigned to the processor with the lowest current load.

Balancing ⚖️:

Every 10 steps, tasks move from overloaded processors (>110% of average load) to underloaded ones (<90% of average load).

Visualization 📉:

Processor loads are tracked and plotted over time.

<b>🌈 Code Structure</b>

Task Class: Represents a task with an ID and workload.

Processor Class: Manages tasks and tracks load history.

DynamicLoadBalancer Class: Core logic for task assignment and balancing.

main() Function: Runs the simulation loop.

<b>💡 Future Improvements: </b>

🌐 Add real-time load balancing metrics.

🎨 Enhance visualization with live updates.

⚡ Simulate task execution time and completion.

🛡️ Add error handling for edge cases.

<b> Contribution made by :</b>

Aman Kumar, Diwakar, Manoj
