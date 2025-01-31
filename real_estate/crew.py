import panel as pn
from crewai.tasks import task, Task
from crewai.tasks.task_output import TaskOutput

# Initialize chat interface
chat_interface = pn.chat.ChatInterface()

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
    return Task(
        name="Reporting Task",
        description="This task handles reporting and requests human feedback.",
        callback=print_output,  # Callback to print the output
        human_input=True  # Flag indicating that human input is required
    )
