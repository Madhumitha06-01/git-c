from crewai import Agent, Task, Crew, Process, LLM
from crewai.knowledge.source.base_knowledge_source import BaseKnowledgeSource
import requests
from typing import Dict, Any
from pydantic import BaseModel, Field
import uuid
from dotenv import load_dotenv
load_dotenv()

class TravelKnowledgeSource(BaseKnowledgeSource):
    """Knowledge source that fetches data from both hotel and airline APIs."""
    
    hotel_api_endpoint: str = Field(description="Hotel API endpoint URL")
    airline_api_endpoint: str = Field(description="Airline API endpoint URL")
    
    def load_content(self) -> Dict[Any, str]:
        """Fetch and format both hotel and airline data from the remote APIs."""
        try:
            # Fetch hotel data
            hotel_response = requests.get(self.hotel_api_endpoint)
            hotel_response.raise_for_status()  # Ensure the request was successful
            hotel_data = hotel_response.json()  # Parse hotel data
            hotels = hotel_data.get('hotels', [])  # Extract hotels from the response

            # Fetch airline data
            airline_response = requests.get(self.airline_api_endpoint)
            airline_response.raise_for_status()  # Ensure the request was successful
            airline_data = airline_response.json()  # Parse airline data
            flights = airline_data.get('flights', [])  # Extract flights from the response

            # Format and combine the data
            formatted_data = self._format_travel_data(hotels, flights)
            return {self.hotel_api_endpoint: formatted_data}
        except Exception as e:
            raise ValueError(f"Failed to fetch travel data: {str(e)}")

    def _format_travel_data(self, hotels: list, flights: list) -> str:
        """Format both hotel and flight data into readable text."""
        formatted = "Hotel and Flight Information:\n\n"
        
        # Format hotel data
        formatted += "Hotels:\n"
        for hotel in hotels:
            formatted += f"""
                Name: {hotel.get('name', 'N/A')}
                Location: {hotel.get('location', 'N/A')}
                Price per Night: {hotel.get('price_per_night', 'N/A')}
                Rating: {hotel.get('rating', 'N/A')}
                Description: {hotel.get('description', 'No description available')}
                Amenities: {', '.join(hotel.get('amenities', []))}
                -------------------"""

        # Format flight data
        formatted += "\nFlights:\n"
        for flight in flights:
            formatted += f"""
                Airline: {flight.get('airline', 'N/A')}
                Departure: {flight.get('departure', 'N/A')}
                Arrival: {flight.get('arrival', 'N/A')}
                Price: {flight.get('price', 'N/A')}
                Duration: {flight.get('duration', 'N/A')}
                -------------------"""
                
        return formatted

    def add(self) -> None:
        """Process and store the travel data (hotels and flights)."""
        content = self.load_content()
        for _, text in content.items():
            chunks = self._chunk_text(text)
            self.chunks.extend(chunks)
        
        # Save documents with metadata
        chunks_metadata = [
            {
                "chunk_id": str(uuid.uuid4()),
                "source": self.hotel_api_endpoint,
                "description": f"Chunk {i + 1} from API response"
            }
            for i in range(len(chunks))
        ]

        # Save documents (chunks) and metadata
        self.save_documents(metadata=chunks_metadata)

# Create knowledge source for travel data (hotels + flights)
travel_knowledge = TravelKnowledgeSource(
    hotel_api_endpoint="https://mocki.io/v1/69547617-da5e-449d-8fa5-1c0c862e2890",  # Hotel API endpoint
    airline_api_endpoint="https://mocki.io/v1/b06aa388-2ab4-4b5d-ac32-f8b8e4c2a1d3"  # Airline API endpoint
)

# Create a specialized agent for handling both hotels and flights
travel_analyst = Agent(
    role="Travel Analyst",
    goal="Answer questions about hotels and flights and assist with booking",
    backstory="""You are a travel analyst with expertise in hotels, flights, pricing, and booking. You help users find accommodations, flights, and assist with bookings based on their preferences.""",
    knowledge_sources=[travel_knowledge],
    llm=LLM(model="gpt-4", temperature=0.0)
)

# Create task that handles user questions for both hotels and flights
analysis_task = Task(
    description="Answer this question about hotels or flights: {user_question}",
    expected_output="A detailed answer based on the most recent travel data (hotels and flights)",
    agent=travel_analyst
)

# Create task for booking
booking_task = Task(
    description="Assist with booking the flight and hotel based on user's preferences.",
    expected_output="Confirmation of flight and hotel bookings.",
    agent=travel_analyst
)

# Create task for canceling bookings
cancel_task = Task(
    description="Cancel the user's current booking for flight or hotel.",
    expected_output="Confirmation of cancellation.",
    agent=travel_analyst
)

# Create task for re-booking
rebook_task = Task(
    description="Assist the user with re-booking the flight and hotel after cancellation.",
    expected_output="Confirmation of re-booking.",
    agent=travel_analyst
)

# Create and run the crew with tasks (analysis, booking, cancel, re-book)
crew = Crew(
    agents=[travel_analyst],
    tasks=[analysis_task, booking_task, cancel_task, rebook_task],
    verbose=True,
    process=Process.sequential
)

# Manage booking state
booking_state = {"booked": False, "hotel": None, "flight": None}

# Chatbot loop to interact with users
def chatbot():
    print("Welcome to the Travel Assistant! Ask me about hotels, flights, or bookings.")
    while True:
        user_input = input("You: ")
        
        # Check for exit commands
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Bye Have a nice day!")
            break

        # Handle cancelation or re-booking
        elif "cancel" in user_input.lower() and booking_state["booked"]:
            print("Do you want to cancel your booking?")
            cancel_response = input("Yes or No: ")
            if cancel_response.lower() == "yes":
                result = crew.kickoff(inputs={"user_question": "Cancel the current booking."})
                print("Bot:", result)
                booking_state["booked"] = False
                booking_state["hotel"] = None
                booking_state["flight"] = None
            else:
                print("Cancellation aborted.")

        # Handle re-booking after cancellation
        elif "rebook" in user_input.lower() and not booking_state["booked"]:
            print("You don't have an active booking. Would you like to make a new booking?")
            rebook_response = input("Yes or No: ")
            if rebook_response.lower() == "yes":
                result = crew.kickoff(inputs={"user_question": "Proceed with booking."})
                print("Bot:", result)
                booking_state["booked"] = True
            else:
                print("Re-booking aborted.")

        # If the user is ready to finalize a booking
        elif "book" in user_input.lower():
            print("Let's finalize your booking!")
            result = crew.kickoff(inputs={"user_question": "Proceed with booking."})
            print("Bot:", result)
            booking_state["booked"] = True

        # Execute the crew with the user question for travel information
        else:
            result = crew.kickoff(inputs={"user_question": user_input})
            print("Bot:", result)

# Start the chatbot
chatbot()
