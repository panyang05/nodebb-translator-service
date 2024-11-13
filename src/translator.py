from openai import AzureOpenAI
import os
import ast
 
def get_response(system : str, user : str) -> str:
    api_key = os.getenv("AZURE_API_KEY")

    client = AzureOpenAI(
        api_key=api_key,
        api_version="2024-02-15-preview",
        azure_endpoint="https://recitation-llm.openai.azure.com/"
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
            {
            "role": "system",
            "content": f"{system}"
            },
            {
                "role": "user",
                "content": f"{user}"
            }
        ]
    )
    
    return response.choices[0].message.content


def translate_content(content: str) -> tuple[bool, str]:
    try:
        systen_prompt = '''
            You are an intelligent assistant.

            You need to decide a given post is English or not, and
            a post is unintelligible or malformed. If a post is not in English,
            please give the translation of the post into English.

            Here are some examples:
            Given "Good afternoon!", you should output (True, "")
            Given "今天天气很好", you should output (False, "The weather is great today")
            Given "123f?!!!@ not clear...", you sohuld output (False, "Unintelligible post)
            Given "lksjdflkj please clarify", you should output (False, "Unintelligible post")
        '''
        response = get_response(systen_prompt, content)
        response = ast.literal_eval(response)
        
        return response
    except:
        return False, "Unable to process"