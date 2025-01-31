# Import necessary libraries
import panel as pn
from crewai.tasks import task, Task  # Make sure 'crewai' is in the Python path
from crewai.tasks.task_output import TaskOutput  # Check this path as well

# Initialize the chat interface
chat_interface = pn.chat.ChatInterface()

# Assuming Mycrew is a custom class that interacts with the chat interface
class Mycrew:
    def __init__(self, chat_interface):
        self.chat_interface = chat_interface

    def process_task(self, task):
        # Logic to process the task and send a message to the chat interface
        print(f"Processing task: {task.name}")
        self.chat_interface.send(f"Task {task.name} is in progress...")

# Instantiate the Mycrew object
mycrew_instance = Mycrew(chat_interface)

# Function to print task output to chat
def print_output(output: TaskOutput):
    """
    Sends the output of the task to the chat interface.
    """
    message = output.raw  # Extract the raw message
    chat_interface.send(message, user=output.agent, respond=False)

# Define the research_task with callback for output
@task
def research_task(self) -> Task:
    """
    Handles research tasks and sends the output via the print_output function.
    """
    mycrew_instance.process_task(self)  # Use Mycrew instance to process the task
    return Task(
        name="Research Task",
        description="This task handles research based on input parameters.",
        callback=print_output  # Callback for sending output to the chat interface
    )

# Define the reporting_task with callback for output and human input flag
@task
def reporting_task(self) -> Task:
    """
    Handles reporting tasks that require human input for feedback.
    """
    mycrew_instance.process_task(self)  # Use Mycrew instance to process the task
    return Task(
        name="Reporting Task",
        description="This task handles reporting and requests human feedback.",
        callback=print_output,  # Callback to print the output
        human_input=True  # Flag indicating that human input is required
    )

# If you want to run the tasks, you would trigger them like so:
# This will initiate the research and reporting tasks (Example usage)
research_task()
reporting_task()
