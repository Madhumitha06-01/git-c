from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI
from langchain_community.tools.gmail import GmailSendMessage
from langchain_community.tools.gmail.utils import build_resource_service, get_gmail_credentials
import os
from dotenv import load_dotenv
import re
import logging

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@CrewBase
class EmailProposalCrew:
    """Crew for generating and sending proposal emails."""

    # LLM setup
    llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

    # Gmail API setup
    credentials = get_gmail_credentials(
        token_file="credentials/token.json",
        scopes=["https://mail.google.com/"],
        client_secrets_file="credentials/credentials.json",
    )
    api_resource = build_resource_service(credentials=credentials)
    gmail_send_tool = GmailSendMessage(api_resource=api_resource)

    def validate_emails(self, email_list):
        """Validate recipient email addresses."""
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return [email.strip() for email in email_list if re.match(email_regex, email.strip())]

    @agent
    def email_content_agent(self) -> Agent:
        """Agent responsible for generating email content."""
        return Agent(
            config={
                "name": "Email Content Creator",
                "description": "Generates email content for proposals using LLM.",
            },
            tools=[],
            llm=self.llm,
            verbose=True,
        )

    @agent
    def email_validation_agent(self) -> Agent:
        """Agent responsible for validating recipient emails."""
        return Agent(
            config={
                "name": "Email Validator",
                "description": "Validates recipient email addresses.",
            },
            tools=[],
            llm=self.llm,
            verbose=True,
        )

    @agent
    def email_sender_agent(self) -> Agent:
        """Agent responsible for sending emails."""
        return Agent(
            config={
                "name": "Email Sender",
                "description": "Sends emails using Gmail API.",
            },
            tools=[self.gmail_send_tool],
            llm=self.llm,
            verbose=True,
        )

    @task
    def generate_email_task(self) -> Task:
        """Task to generate email content for a proposal topic."""
        return Task(
            config={
                "name": "Generate Email Content",
                "description": "Generate email content for the given proposal topic.",
                "expected_output": "Draft email content with a subject, introduction, benefits, and next steps.",
            },
            agent=self.email_content_agent(),
            callback=lambda _, task: task.agent.run(
                input("Enter the proposal topic (e.g., AI Analytics Tool): ").strip()
            ),
        )

    @task
    def validate_emails_task(self) -> Task:
        """Task to validate recipient email addresses."""
        return Task(
            config={
                "name": "Validate Recipient Emails",
                "description": "Validate email addresses provided by the user.",
                "expected_output": "List of valid email addresses.",
            },
            agent=self.email_validation_agent(),
            callback=lambda _, task: self.validate_emails(
                input("Enter recipient email(s) (comma-separated): ").split(",")
            ),
        )

    @task
    def send_email_task(self) -> Task:
        """Task to send emails to the validated recipients."""
        return Task(
            config={
                "name": "Send Email",
                "description": "Send the generated email to validated recipients.",
                "expected_output": "Confirmation that emails have been sent successfully.",
            },
            agent=self.email_sender_agent(),
            callback=lambda email_content, task: task.agent.run(
                message=email_content,
                to=self.validate_emails_task().output,
                subject="Proposal: AI Analytics Tool",
            ),
        )

    @crew
    def crew(self) -> Crew:
        """Define the workflow for the email proposal crew."""
        return Crew(
            agents=[
                self.email_content_agent(),
                self.email_validation_agent(),
                self.email_sender_agent(),
            ],
            tasks=[
                self.generate_email_task(),
                self.validate_emails_task(),
                self.send_email_task(),
            ],
            process=Process.sequential,
            verbose=True,
        )