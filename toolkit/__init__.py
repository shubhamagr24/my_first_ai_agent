#basic imports
from langchain.tools import Tool
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

import os

# special imports
from langchain_community.tools import DuckDuckGoSearchRun ###simple search tool
from langchain_community.tools import DuckDuckGoSearchResults ### returns snipeet,title,link
from langchain_community.utilities import GoogleSerperAPIWrapper
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from io import BytesIO
import requests
from langchain_experimental.utilities import PythonREPL


load_dotenv() 


# --- Basic operations --- #

@tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers.
    Args:
        a (float): the first number
        b (float): the second number
    """
    return a * b


@tool
def add(a: float, b: float) -> float:
    """Adds two numbers.
    Args:
        a (float): the first number
        b (float): the second number
    """
    return a + b


@tool
def subtract(a: float, b: float) -> int:
    """Subtracts two numbers.
    Args:
        a (float): the first number
        b (float): the second number
    """
    return a - b


@tool
def divide(a: float, b: float) -> float:
    """Divides two numbers.
    Args:
        a (float): the first float number
        b (float): the second float number
    """
    if b == 0:
        raise ValueError("Cannot divided by zero.")
    return a / b


@tool
def modulus(a: int, b: int) -> int:
    """Get the modulus of two numbers.
    Args:
        a (int): the first number
        b (int): the second number
    """
    return a % b


@tool
def power(a: float, b: float) -> float:
    """Get the power of two numbers.
    Args:
        a (float): the first number
        b (float): the second number
    """
    return a**b


@tool
def largest(a:list[float]) -> float:
    """Get the largest number in a list.
    Args:
        a (list[float]): the list of numbers
    """
    return max(a)

@tool
def smallest(a:list[float]) -> float:
    """Get the smallest number in a list.
    Args:
        a (list[float]): the list of numbers
    """
    return min(a)
@tool
def average(a:list[float]) -> float:
    """Get the average of a list of numbers.
    Args:
        a (list[float]): the list of numbers
    """
    return sum(a)/len(a)


# --- Advanced operations --- #

# duckduckgo search tool
simple_search_tool = Tool(
    name="DuckDuckGo Search",
    func=DuckDuckGoSearchRun().run,
    description=(
        "Search the web using DuckDuckGo and return a list of relevant results. "
        "Useful for answering general knowledge questions or finding recent news."
    )
)


# duckduckgo search tool returns snipeet,title,link
duckduckgo_search_tool = Tool(
    name="DuckDuckGo Search",
    func=DuckDuckGoSearchResults(output_format="list").run,
    description=(
        "Search the web using DuckDuckGo and return a list of relevant results. "
        "Useful for answering general knowledge questions or finding recent news."
    )
)


# google search tool 
search = GoogleSerperAPIWrapper()
# Need to explicitly convert search function to a tool
google_search_tool = Tool(
    name="Google Search",
    func=lambda q: str(search.results(q)),  # returns list of dicts with 'link'
    description="Search Google and get structured results including links.",
)



# --- Webpage content extraction --- #
def get_webpage_content(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()

        # Check if it's a PDF
        if "application/pdf" in content_type or url.lower().endswith(".pdf"):
            pdf = PdfReader(BytesIO(response.content))
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            return text[:2000]  # Truncate for safety

        # Else assume it's HTML
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return text[:2000]

    except Exception as e:
        return f"Error fetching content: {e}"
    
webpage_tool = Tool(
    name="get_webpage_content",
    func=get_webpage_content,
    description="Fetches and returns main text from a webpage or a PDF URL."
)


#python interpreter
python_repl = PythonREPL()
python_interpreter_tool = Tool(
    name="python_repl",
    description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`.",
    func=python_repl.run,
)
