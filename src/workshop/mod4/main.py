import os
from dotenv import load_dotenv
import datetime

from fastapi import FastAPI, HTTPException
import traceback

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from pydantic import BaseModel

# Load .env only if it exists (for local use)
if os.path.exists(".env"):
  load_dotenv()

# Environment variables
SAMPLE_ENV_VAR = os.getenv("SAMPLE_ENV_VAR", "default_value")
PROJECT_CONNECTION_STRING = os.getenv("PROJECT_CONNECTION_STRING", None)
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", None)

################################################################################
#
# Reuseable Functions
#
################################################################################

# Function to Connect Client
def connect_client():
  try:
    project_client = AIProjectClient.from_connection_string(
      credential=DefaultAzureCredential(), conn_str=PROJECT_CONNECTION_STRING
    )
    return project_client
  except Exception as e:
    print(e)
    return None

# Function to Create Agent
def create_agent(
  agent_name = f"Agent {datetime.datetime.now().strftime("%Y%m%d%H%M")}",
  agent_instructions = "You are a helpful AI agent.",
  agent_model = MODEL_DEPLOYMENT_NAME,
  agent_toolset = None,
):
  try:
    project_client = connect_client()
    return project_client.agents.create_agent(
      name = agent_name,
      instructions = agent_instructions,
      model = agent_model,
      toolset = agent_toolset,
    )
  except Exception as e:
    print(e)
    return None

# Function to List Agents
def list_agents():
  try:
    project_client = connect_client()
    return project_client.agents.list_agents()
  except Exception as e:
    print(e)
    return None

# Function to Ask Agent
def ask_agent(agent_id, prompt):
  print(f"Asking agent '{agent_id}'...")

  # Default AI Response
  ai_response = "I don't know what to say."

  # Connect Project Client
  project_client = connect_client()

  # Validate project client
  if project_client:
    # Create thread for communication
    thread = None
    try:
      thread = project_client.agents.create_thread()
      # print(f"Created thread, ID: {thread.id}")
    except Exception as e:
      print(e)
      # return None

    # Validate thread
    if thread and thread.id:
      # Create message to thread
      message = None
      try:
        message = project_client.agents.create_message(
          thread_id=thread.id,
          role="user",
          content=prompt,
        )
        # print(f"Created message, ID: {message.id}")
      except Exception as e:
        print(e)
        # return None

      # Validate message
      if message and message.id:
        # Create and process agent run in thread
        try:
          run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent_id)
          # print(f"Run finished with status: {run.status}")
          if run.status == "failed":
            print(f"Run failed: {run.last_error}")
            # return None
        except Exception as e:
          print(e)
          # return None

        # Get all messages in thread
        messages = None
        try:
          messages = project_client.agents.list_messages(thread_id=thread.id)
        except Exception as e:
          print(e)
          # return None

        # Validate messages
        if messages and messages.data:
          # Get latest message
          latest_content = None
          try:
            latest_content = messages.data[0].content[0]
          except (IndexError, AttributeError, TypeError):
            print("Error accessing latest content.")

          # Handle text messages
          if (
            latest_content
            and latest_content.type == "text"
            and latest_content.text
            and latest_content.text.value
          ):
            ai_response = latest_content.text.value

  return ai_response

################################################################################
#
# FastAPI Application
#
################################################################################

# Initialize FastAPI
app = FastAPI()

start_datetime = datetime.datetime.now().strftime("%m-%d-%Y at %H:%M:%S")

# API Root
@app.get("/")
def read_root():
  current_datetime = datetime.datetime.now().strftime("%m-%d-%Y at %H:%M:%S")
  return {
    "version": "2025-03-28 9:48",
    "date_start": start_datetime,
    "date_request": current_datetime,
    "env_var": SAMPLE_ENV_VAR,
    "model": MODEL_DEPLOYMENT_NAME,
  }

# # Class for Create Request
# class CreateRequest(BaseModel):
#     agent_name: str
#     agent_instructions: str
#     agent_model: str
#     agent_toolset: None

# # Create New Agent
# @app.post("/agents/create")
# def api_create(request: CreateRequest):
#   try:
#     new_agent = create_agent(
#       agent_name = request.agent_name,
#       agent_instructions = request.agent_instructions,
#       agent_model = request.agent_model,
#       agent_toolset = request.agent_toolset,
#     )
#     return { "status": 200, "data": new_agent }
#   except Exception as e:
#     print(e)
#     raise HTTPException(status_code=500, detail="Error creating agent.")

# # List Agents
# @app.post("/agents/list")
# def api_list():
#   try:
#     agents = list_agents()
#     return { "status": 200, "data": agents.data }
#   except Exception as e:
#     print(e)
#     traceback.print_exc()
#     raise HTTPException(status_code=500, detail=str(e))

# Class for Ask Request
class AskRequest(BaseModel):
  agent_id: str
  user_input: str

# Ask Agent
@app.post("/agents/ask")
def api_ask(request: AskRequest):
  try:
    agent_response_content = ask_agent( request.agent_id, request.user_input )
    return { "status": 200, "data": agent_response_content }
  except Exception as e:
    print(e)
    traceback.print_exc()
    raise HTTPException(status_code=500, detail=str(e))

# TEMP: Chat Agent
@app.post("/agents/chat")
def api_ask(request: AskRequest):
  return { "status": 200, "data": f"This is a temporary response from the Azure AI Agent for {request.agent_id}." }
