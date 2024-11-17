from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List
import instructor
import json
import os

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
    if i == 1:
        return 1, ["pandas"] 
    elif i == 2:
        return 2, ["pandas", "numpy"] 
    elif i == 3:
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


def create_first_prompt(propriedade):    
        resp = client.chat.completions.create(
            model="gemma2:2b",
            messages=[
                {
                    "role": "user",
                    "content":  f"Imagine you are a human asking a LLM to assume a role of a code reviewer. \
                        Create a prompt to that purpose. The code is a attempt to clean a csv database, and the \
                        prompt needs to say what our llm have to do when it receives the code (it doesn have to \
                        include things like 'code goes here', etc). Start the prompt with things like 'I need \
                        you to act as a code reviewer...'. The a prompt needs to have a poor {propriedade} \
                        (rated 1 on a scale of 5)."
                }
            ],
            response_model=Prompts,
        )
        
        prompt = resp.prompt
        prompts_formated = {"propriedade": propriedade, "valor": 1, "prompt": prompt}

        return prompts_formated

def create_following_prompts(previous_prompt, message):  
    resp = client.chat.completions.create(
        model="gemma2:2b",
        messages=[
            {
                "role": "user",
                "content": f"{message}: {previous_prompt["prompt"]}",  
            }
        ],
        response_model=Prompts,
    )
    prompt = resp.prompt
    prompts_formated = {"propriedade": previous_prompt["propriedade"], "valor": previous_prompt["valor"] + 1, "prompt": prompt}

    return prompts_formated

def create_complexity_prompts(i):
    libraries = get_difficulty(i)
    resp = client.chat.completions.create(
        model="gemma2:2b",
        messages=[  
            {
                "role": "user",
                "content": f"Imagine you are a human asking a LLM to assume a role of a code reviewer. \
                        Create a prompt to that purpose. The code is a attempt to clean a csv database, and the \
                        prompt needs to say what our llm have to do when it receives the code (the prompt doesn need \
                        to include the code itself). Start the prompt with things like 'I need \
                        you to act as a code reviewer... {i, libraries}"
            }
        ],
        response_model=Prompts,
    )

    prompt = resp.prompt
    prompts_formated = {"propriedade": "complexity", "valor": i, "prompt": prompt}

    return prompts_formated

    
def add_prompt_to_json(propriedade, prompts):
    directory = os.path.join(os.path.dirname(__file__), '../prompts_reviewer/')
    os.makedirs(directory, exist_ok=True)
    json_filename = os.path.join(directory, f'prompts_{propriedade}_reviewer.json')
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(prompts, json_file, ensure_ascii=False, indent=2)