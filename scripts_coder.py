from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List
import instructor
import json

class Prompts(BaseModel):
    response: str 

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

def create_recursive(prompts, property, previous_prompt, message, num_responses):
    if num_responses > 5:
        return
    
    resp = client.chat.completions.create(
        model="gemma2:2b",
        messages=[
            {
                "role": "user",
                "content": f"{message}: {previous_prompt}",  
            }
        ],
        response_model=Prompts,
    )
    previous_prompt = resp.response
    prompts.append({"propriedade": property, "valor": num_responses, "prompt": previous_prompt})
    
    create_recursive(prompts, property, previous_prompt, message, num_responses+1)

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

    previous_prompt = resp.response
    prompts.append({"propriedade": propriedade, "valor": 1, "prompt": previous_prompt})
    print(prompts)

    # create_recursive(prompts, propriedade, previous_prompt, message_to_improve, 2)
        
    # json_filename = f'prompts_{propriedade}_coder.json'
    # with open(json_filename, 'w', encoding='utf-8') as json_file:
    #     json.dump(prompts, json_file, ensure_ascii=False, indent=2)


# create_json("clarity", "make the following prompt a little more clear. Prompt:")