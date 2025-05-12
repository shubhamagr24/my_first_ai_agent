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


from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from youtube_transcript_api import YouTubeTranscriptApi
from pytube import extract

import asyncio
from playwright.async_api import async_playwright

from openai import OpenAI


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


class math_toolkit:
    def get_tools(self):
        return [
            multiply,
            add,
            subtract,
            divide,
            modulus,
            power,
            largest,
            smallest,
            average
        ]


math_toolkit=math_toolkit()
math_tools=math_toolkit.get_tools()

# --- Advanced operations --- #

# duckduckgo search tool
simple_search_tool = Tool(
    name="DuckDuckGo_simple_Search",
    func=DuckDuckGoSearchRun().run,
    description=(
        "Search the web using DuckDuckGo and return a list of relevant results. "
        "Useful for answering general knowledge questions or finding recent news."
    )
)


# duckduckgo search tool returns snipeet,title,link
duckduckgo_search_tool = Tool(
    name="DuckDuckGo_Search",
    func=DuckDuckGoSearchResults(output_format="list").run,
    description=(
        "Search the web using DuckDuckGo and return a list of relevant results. "
        "Useful for answering general knowledge questions or finding recent news."
        "The output is a list of dictionaries, each containing 'title', 'snippet', and 'link' keys."
        "The 'link' key contains the URL of the result, which can be used to fetch more information."
    )
)


# google search tool 
search = GoogleSerperAPIWrapper()
# Need to explicitly convert search function to a tool
google_search_tool = Tool(
    name="Google_Search",
    func=lambda q: search.results(q)['organic'][:4], # Limit to top 3 results
    description=(
        "Search web using Google and get structured results that includes links. which can be used to fetch more information. "
        "Try formulating the search query in a way that it captures all the available context"),
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
            return text[:20000]  # Truncate for safety

        # Else assume it's HTML
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return text[:20000]

    except Exception as e:
        return f"Error fetching content: {e}"
    
get_webpage_content = Tool(
    name="get_webpage_content",
    func=get_webpage_content,
    description=(
        "Use this tool to fetch metadata or links from a webpage or PDF URL. "
        "Returns the first 5000 characters of webpage or PDF content. "
        # "DO NOT use this tool to load or analyze large files (CSV, PDF, Excel, etc.). "
        # "Instead, if the page contains a downloadable file link, extract just the file URL and pass it to the Python tool."
    )
)




# --- advance Webpage content extraction --- #
async def get_webpage_content_async(url: str) -> str:
    try:
        # --- PDF Handling --- #
        head = requests.head(url, timeout=5)
        if url.lower().endswith(".pdf") or "application/pdf" in head.headers.get("Content-Type", "").lower():
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            pdf = PdfReader(BytesIO(response.content))
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text[:20000] or "No readable text extracted from PDF."

        # --- Webpage Handling with Playwright --- #
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                java_script_enabled=True,
                viewport={"width": 1280, "height": 800}
            )
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(5000)

            content = await page.content()
            await browser.close()

        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return text[:20000] or "No readable text extracted from webpage."

    except Exception as e:
        return f"Error fetching content: {e}"


# --- Sync wrapper for LangChain Tool --- #
def advanced_get_webpage_content(url: str) -> str:
    return asyncio.run(get_webpage_content_async(url))


# --- LangChain Tool --- #
advanced_get_webpage_content = Tool(
    name="advanced_get_webpage_content",
    func=advanced_get_webpage_content,
    description=(
        "Use this tool only if get_webpage_content fails. "
        "Use this tool to fetch content from a webpage or PDF URL. "
        "Returns the first 20,000 characters of the visible text content. "
        "Handles PDFs and Cloudflare-protected sites using headful browser emulation."
    )
)




#python interpreter
python_repl = PythonREPL()
python_interpreter_tool = Tool(
    name="python_repl",
    func=python_repl.run,
    description=(
        """A Python REPL shell (Read-Eval-Print Loop).
    Use this to execute single or multi-line python commands.
    Input should be syntactically valid Python code.
    Always end your code with `print(...)` to see the output.
    Do NOT execute code that could be harmful to the host system.
    You are allowed to download files from URLs.
    Do NOT send commands that block indefinitely (e.g., `input()`)."""
    )
)

# --- Wikipedia search tool --- #
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

wikipedia_search=Tool(
    name="wikipedia_search",
    func=wikipedia.run,
    description=("Fetches summaries from Wikipedia. Useful for general knowledge or factual questions about entities, events, concepts, etc."
    "Prioritze this wikipedia search tool over web search and get web content for general knowledge questions. "
    )

)


# audio transcription tool

@tool
def automatic_speech_recognition(file_url: str, file_extension: str) -> str:
    """Transcribe an audio file to text
    Args:
        file_url (str): the URL to the audio file
        file_extension (str): the file extension, e.g. mp3
    """
    try:
        
        response = requests.get(file_url)
        response.raise_for_status()
        # write to disk
        file_extension = file_extension.replace('.','')
        with open(f'tmp.{file_extension}', 'wb') as file:
            file.write(response.content)

        audio_file = open(f'tmp.{file_extension}', "rb")
        client = OpenAI()
        transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        return transcription.text

        # return 'sample'

    except Exception as e:
        return f"automatic_speech_recognition failed: {e}"
    



# --- YouTube transcript tool --- #

@tool
def get_youtube_transcript(page_url: str) -> str:
    """Get the transcript of a YouTube video
    Args:
        page_url (str): YouTube URL of the video
    """
    try:
        # get video ID from URL
        video_id = extract.video_id(page_url)

        # get transcript
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)

        # keep only text
        txt = '\n'.join([s.text for s in transcript.snippets])
        return txt[:20000]
    except Exception as e:
        return f"get_youtube_transcript failed: {e}"



tool_list=[
    # simple_search_tool,
    # duckduckgo_search_tool,
    google_search_tool,
    wikipedia_search,
    automatic_speech_recognition
    get_youtube_transcript,
    get_webpage_content,
    advanced_get_webpage_content,
    python_interpreter_tool
]+ math_tools