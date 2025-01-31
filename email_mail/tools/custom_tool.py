import os
from exa_py import Exa
from langchain.agents import tool

class YourCustomTool:
    # Initialize Exa with the API key
    @staticmethod
    def _exa():
        return Exa(api_key=os.environ["EXA_API_KEY"])

    @tool
    def search(query: str):
        """Search for a webpage based on the query."""
        # Using the Exa instance to perform the search
        return YourCustomTool._exa().search(f"{query}", use_autoprompt=True, num_results=3)

    @tool
    def find_similar(url: str):
        """Search for webpages similar to a given URL.
        The URL passed in should be a URL returned from search.
        """
        return YourCustomTool._exa().find_similar(url, num_results=3)

    @tool
    def get_contents(ids: str):
        """Get the contents of a webpage.
        The ids must be passed in as a list, which is returned from the search.
        """
        # Convert the string representation of list to an actual list
        ids = eval(ids)
        
        # Get the contents of the web pages using Exa
        contents = str(YourCustomTool._exa().get_contents(ids))
        
        # Limit content length and format it
        contents = contents.split("URL:")
        contents = [content[:1000] for content in contents]  # Limit each content to 1000 characters
        return "\n\n".join(contents)

    @staticmethod
    def tools():
        """Return the tools that can be used for the Langchain agent."""
        return [YourCustomTool.search, YourCustomTool.find_similar, YourCustomTool.get_contents]
