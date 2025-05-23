# from toolkit import python_interpreter_tool,duckduckgo_search_tool

# print(python_interpreter_tool.invoke("print(1+1)"))



from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from toolkit import tool_list  # List of Tool objects with structured input support
from sample_ques import ques  # Import the question dictionary

# System prompt for the agent
system_prompt = (
    """
You are a helpful assistant tasked with answering questions using a set of tools. 
Now, I will ask you a question. Report your thoughts, and finish your answer with the following template: 
FINAL ANSWER: [YOUR FINAL ANSWER]. 
Make sure to follow the template exactly and end with final answer.
YOUR FINAL ANSWER should only be a number OR as few words as possible OR a comma separated list of numbers and/or strings. 
If you are asked for a number, don't use commas, units like $ or % unless specified.
If you are asked for a string, avoid abbreviations and articles or any other unnecessary words or anotations
If you are asked for a list, apply the above rules to each element.
"""
)

# Initialize Chat Model
llm = ChatOpenAI(model="gpt-4.1-mini",max_tokens=2000)

# Create the agent executor (handles multi-input tools via OpenAI Functions)
agent_executor = initialize_agent(
    tools=tool_list,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    agent_kwargs={
        "system_message": system_prompt,
    },
    max_iterations=7
)

load_file_ques="""Below is a youtube video url, help me list the countries that are mentioned in the video. 
youtube URL: "https://www.youtube.com/watch?v=nnXs1ngaJXo
"""


# Run the agent
response = agent_executor.invoke(
    {"input": load_file_ques}
    )

print(response['output'].split("FINAL ANSWER:")[-1].strip())


