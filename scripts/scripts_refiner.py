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


def create_first_prompt(propriedade):    
        resp = client.chat.completions.create(
            model="gemma2:2b",
            messages=[
                {
                    "role": "user",
                    "content":  f"I need you to act as a prompt designer and create an initialization prompt for \
                        a 'code refiner' agent within a reinforcement learning environment. The purpose of this \
                        agent is to receive code and a list of modifications, then apply these changes \
                        accurately. When designing this prompt, start with a statement like 'I need \
                        you to act as a code refiner,' and continue with instructions on how the agent \
                        should refine code using the provided list of changes. However, ensure that \
                        the prompt has a poor {propriedade}, (rated 1 on a scale of 5)."
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

    
def add_prompt_to_json(propriedade, prompts):
    directory = os.path.join(os.path.dirname(__file__), '../prompts_refiner/')
    os.makedirs(directory, exist_ok=True)
    json_filename = os.path.join(directory, f'prompts_{propriedade}_code_refiner.json')
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(prompts, json_file, ensure_ascii=False, indent=2)