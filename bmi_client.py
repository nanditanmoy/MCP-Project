import asyncio
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import json

server_params = StdioServerParameters(
    command="/Users/tanmoynandi/projects/MCP Project/.venv/bin/python",
    args=["/Users/tanmoynandi/projects/MCP Project/bmi_server.py"]
)

def llm_client(message:str):
    """
    Send the msg to LLM and return the response.
    """
    # Initialize OpenAI Client
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Send the message to LLM
    response = openai_client.chat.completions.create(
        model = "gpt-4",
        messages = [
            {"role": "system", "content": "You are an intelligent assistant. You will execute task as prompted"},
            {"role": "user", "content": message}
        ],
        max_tokens=250,
        temperature=0.2
    )

    # Extract and return the response content
    return response.choices[0].message.content.strip()


def get_prompt_to_identify_tools_and_arguments(height_m: float, weight_kg: float) -> dict:
    """Create a simple BMI calculation request without using LLM"""
    return {
        "tool": "calculateBMI",
        "arguments": {
            "weight_kg": weight_kg,
            "height_m": height_m
        }
    }

async def run(height_m: float, weight_kg: float):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Create the tool call parameters
            tool_call = get_prompt_to_identify_tools_and_arguments(height_m, weight_kg)
            
            # Call the BMI calculation tool
            result = await session.call_tool(tool_call["tool"], arguments=tool_call["arguments"])
            return result.content[0].text



def convert_height_to_meters(feet, inches):
    """Convert height from feet and inches to meters"""
    total_inches = feet * 12 + inches
    return total_inches * 0.0254

if __name__ == "__main__":
    import asyncio
    
    # Input values (5ft 10inch = 1.78m, 80kg)
    feet, inches = 5, 10
    weight_kg = 80.0
    
    # Convert height to meters
    height_m = convert_height_to_meters(feet, inches)
    print(f"Converting {feet}ft {inches}inch to {height_m:.2f}m")
    print(f"Calculating BMI for height: {height_m:.2f}m, weight: {weight_kg}kg")
    
    try:
        result = asyncio.run(run(height_m, weight_kg))
        print(f"BMI Result: {result}")
    except Exception as e:
        print(f"Error calculating BMI: {str(e)}")
