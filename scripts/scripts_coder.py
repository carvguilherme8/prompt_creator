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


def get_difficulty(i):
    if i == 1:
        return ["pandas"] 
    elif i == 2:
        return ["pandas", "numpy"] 
    elif i == 3:
        return ["pandas", "pyjanitor"]  
    elif i == 4:
        return ["pandas", "dask"]
    elif i == 5:
        return ["pandas", "dask", "sqlalchemy"]  
    else:
        return None


def create_first_prompt(propriedade):
    prompts = []
    resp = client.chat.completions.create(
        model="gemma2:2b",
        messages=[  
            {
                "role": "user",
                "content": f"Imagine you are a human asking a language model to return Python code for cleaning a \
                    dirty CSV file. Create a prompt to request this code with a poor {propriedade} \
                    (rated 1 on a scale of 5). Do not include examples or fields to complete; focus on \
                    delivering a prompt that reflects a poor {propriedade} as described."
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
    resp = client.chat.completions.create(
        model="gemma2:2b",
        messages=[  
            {
                "role": "user",
                "content": f"Imagine you are a human asking a language model to return Python code for cleaning a \
                    dirty CSV file. Create a prompt to request this code and also request that it must contain\
                    the following libraries {get_difficulty(i)}."
            }
        ],
        response_model=Prompts,
    )

    prompt = resp.prompt
    prompts_formated = {"propriedade": "complecity", "valor": i, "prompt": prompt}

    return prompts_formated

    
def add_prompt_to_json(propriedade, prompts):
    directory = os.path.join(os.path.dirname(__file__), '../prompts_coder/')
    os.makedirs(directory, exist_ok=True)
    json_filename = os.path.join(directory, f'prompts_{propriedade}_coder.json')
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(prompts, json_file, ensure_ascii=False, indent=2)