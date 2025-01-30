import os
import re
import logging
from langchain_openai import ChatOpenAI
from langchain_community.tools.gmail import GmailSendMessage
from langchain_community.tools.gmail.utils import (
    get_gmail_credentials,
    build_resource_service,
)
from dotenv import load_dotenv
from tools.ExaSearchTool import ExaSearchTool

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------- Email Agent Class -----------------
class EmailAgent:
    """Base class for Email-related agents."""

    def __init__(self, llm, api_resource):
        """
        Initialize the agent with the LLM and Gmail API resource.
        - llm: Language model for generating email content.
        - api_resource: Gmail API resource object.
        """
        self.llm = llm
        self.api_resource = api_resource

    def generate_email_content(self, proposal_topic, company_details):
        """Generate email content for a given proposal topic."""
        logger.info(f"Generating email content for topic: {proposal_topic} with company details.")
        system_message = (
            "You are an AI assistant that generates email content for proposals. "
            "Ensure the email includes an introduction, benefits of the proposal, and clear next steps. "
            "Additionally, incorporate relevant company details to personalize the proposal."
        )
        input_text = f"Write an email for a proposal topic: {proposal_topic}. Here are the company details: {company_details}"

        # Invoke the LLM
        response = self.llm.invoke(
            [{"role": "system", "content": system_message},
             {"role": "user", "content": input_text}]
        )
        return response.content

    def send_email(self, content, recipient_emails, subject="Proposal"):
        """Send the email using Gmail API."""
        logger.info(f"Sending email to {recipient_emails}")
        send_tool = GmailSendMessage(api_resource=self.api_resource)
        try:
            send_tool._run(
                message=content,
                to=recipient_emails,
                subject=subject,
            )
            return "Email sent successfully!"
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return f"Error: {e}"

# ----------------- Task Class -----------------
class Task:
    """A single task performed by an agent."""

    def __init__(self, name, agent, function, *args, **kwargs):
        """
        Initialize a task.
        - name: The name of the task.
        - agent: The agent responsible for the task.
        - function: The function the agent will perform.
        - args/kwargs: Arguments for the function.
        """
        self.name = name
        self.agent = agent
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def execute(self):
        """Execute the task and return the result."""
        logger.info(f"Executing task: {self.name}")
        result = self.function(*self.args, **self.kwargs)
        logger.info(f"Task '{self.name}' result: {result}")
        return result

# ----------------- Crew Class -----------------
class Crew:
    """A crew that manages tasks and agents."""

    def __init__(self, name, tasks):
        """
        Initialize the crew.
        - name: Name of the crew.
        - tasks: List of Task objects.
        """
        self.name = name
        self.tasks = tasks

    def run(self):
        """Run all tasks sequentially and return results."""
        logger.info(f"Starting crew: {self.name}")
        results = []
        for task in self.tasks:
            result = task.execute()
            results.append(result)
        logger.info(f"Crew '{self.name}' execution completed.")
        return results

# ----------------- Email Validation Function -----------------
def validate_emails(email_list):
    """Validate and clean email addresses."""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return [email.strip() for email in email_list if re.match(email_regex, email.strip())]

# ----------------- Main Function -----------------
def main():
    # Step 1: Ensure the 'credentials' directory exists
    credentials_dir = "credentials"
    if not os.path.exists(credentials_dir):
        os.makedirs(credentials_dir)

    # Step 2: Load Gmail credentials and resource
    credentials = get_gmail_credentials(
        token_file=os.path.join(credentials_dir, "token.json"),  # Ensure this path is correct
        scopes=["https://mail.google.com/"],
        client_secrets_file="email_test/src/email_test/credentials/credentials.json",
    )
    api_resource = build_resource_service(credentials=credentials)

    # Step 3: Initialize the LLM and Email Agent
    llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    email_agent = EmailAgent(llm=llm, api_resource=api_resource)

    # Step 4: Gather user input for company name
    company_name = input("Enter the company name (e.g., XYZ Corp): ").strip()

    # Step 5: Research company details using ExaSearchTool
    logger.info(f"Researching company details for: {company_name}")
    research_tool = ExaSearchTool()
    company_details = research_tool.search(company_name)  # Assuming `search` method is defined
    print(company_details)

    if not company_details:
        print("No company details found. Exiting.")
        return

    # Step 6: Gather user input for proposal topic/project name
    proposal_topic = input("Enter the proposal project name (e.g., AI Analytics Tool): ").strip()

    # Step 7: Define tasks
    task_generate_email = Task(
        name="Generate Email Content",
        agent=email_agent,
        function=email_agent.generate_email_content,
        proposal_topic=proposal_topic,
        company_details=company_details
    )

    task_send_email = Task(
        name="Send Email",
        agent=email_agent,
        function=email_agent.send_email,
        content=None,  # Placeholder
        recipient_emails=None,  # Placeholder, will be updated later
    )

    # Step 8: Run the tasks using crews
    crew_generate = Crew(name="Email Content Generation Crew", tasks=[task_generate_email])
    generated_content = crew_generate.run()[0]  # Retrieve the generated email content

    # Step 9: Preview generated email
    print("\nGenerated Email Content:")
    print(generated_content)

    # Step 10: Gather recipient emails from the user
    recipient_emails_input = input("Enter recipient email(s) (comma-separated): ").split(",")
    recipient_emails = validate_emails(recipient_emails_input)

    if not recipient_emails:
        print("No valid email addresses provided. Exiting.")
        return

    # Step 11: Ask for confirmation to send the email
    confirm = input("Do you want to send this email? (yes/no): ").strip().lower()
    if confirm == "yes":
        task_send_email.kwargs['content'] = generated_content  # Update task with generated content
        task_send_email.kwargs['recipient_emails'] = recipient_emails  # Add recipient emails
        crew_send = Crew(name="Send Email Crew", tasks=[task_send_email])
        crew_send.run()
    else:
        print("Email sending cancelled.")

if __name__ == "__main__":
    main()







