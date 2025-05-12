from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from toolkit import tool_list  # List of Tool objects with structured input support
from sample_ques import ques  # Import the question dictionary
from system_prompt import system_prompt  # Import the system prompt
import json

with open("config.json", "r") as f:
    config = json.load(f)


# Initialize Chat Model
if config['is_reasoning_model']:
    llm = ChatOpenAI(model=config['model'],max_tokens=2000)
else:
    llm = ChatOpenAI(model=config['model'], temperature=0,max_tokens=2000)

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

# Run the agent
# response = agent_executor.invoke(
#     {"input": ques["Question"]}
#     )

# print(response['output'].split("FINAL ANSWER:")[-1].strip())