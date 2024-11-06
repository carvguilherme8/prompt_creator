from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List
import instructor
import json

class Prompts(BaseModel):
    prompt: str 

client = instructor.from_openai(
    OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  
    ),
    mode=instructor.Mode.JSON,
)

prompts = []

def get_difficulty(i):
    if 0 <= i <= 19:
        return 1, ["pandas"] 
    elif 20 <= i <= 39:
        return 2, ["pandas", "numpy"] 
    elif 40 <= i <= 59:
        return 3, ["pandas", "pyjanitor"]  
    elif 60 <= i <= 79:
        return 4, ["pandas", "dask"]
    elif 80 <= i <= 99:
        return 5, ["pandas", "dask", "sqlalchemy"]  
    else:
        return None

def generate_prompt(difficulty, libraries):
    base_prompt = f"Imagine you are a human asking a LLM to assume a role of a code reviewer. Create a prompt to that purpose. The code is a attempt to clean a csv database, and the prompt needs to say what our llm have to do when it receives the code (it doesn have to include things like 'code goes here', etc). Start the prompt with things like 'I need you to act as a code reviewer...'. You must ensure the review process considers the use of {', '.join(libraries)}."

    if difficulty == 1:
        return f"{base_prompt} Keep it simple and focus on correctness and syntax related to the use of {libraries[0]}."
    
    elif difficulty == 2:
        return f"{base_prompt} Ensure that the review also covers performance optimizations and basic handling of {libraries[0]} and {libraries[1]}. Focus on both accuracy and performance."
    
    elif difficulty == 3:
        return f"{base_prompt} In addition to checking the use of {libraries[0]}, include best practices and advanced use cases involving {libraries[1]}. The review should emphasize optimization and scalability."

    elif difficulty == 4:
        return f"{base_prompt} Your role also involves ensuring that the code is scalable and efficient for large datasets using {libraries[0]} and {libraries[1]}. Look out for advanced optimizations and modularity in the code."

    elif difficulty == 5:
        return f"{base_prompt} As a high-level reviewer, examine advanced features like distributed computing with {libraries[1]} and database integrations with {libraries[2]}. Ensure the code is optimized for both large-scale processing and database interactions."

for i in range(81, 100):
    difficulty, libraries = get_difficulty(i)
    
    if difficulty:
        prompt = generate_prompt(difficulty, libraries)
        resp = client.chat.completions.create(
            model="gemma2:2b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_model=Prompts,
        )
        
        prompts.append({"complexity": difficulty, "prompt": resp.prompt})

json_filename = 'prompts_reviewer_difficulty_5.json'
with open(json_filename, 'w', encoding='utf-8') as json_file:
    json.dump(prompts, json_file, ensure_ascii=False, indent=2)
