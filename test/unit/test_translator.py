from src.translator import translate_content
import json
from src.translator import get_response
import multiprocessing
from mock import patch
import os
from openai import AzureOpenAI
import ast

CPU_COUNT = multiprocessing.cpu_count()

def have_same_meaning(sentence1, sentence2) -> bool:
    system_prompt = '''
    You need to decide if two given sentences have the meaning. 
    If the two sentences have the same meaning, please output True.
    If the two sentences do not have the same meaning, please output False.
    '''

    user_prompt = f'''
    Here's the first sentence: {sentence1} \n
    Here's the second sentence: {sentence2}
    '''

    response = bool(get_response(system_prompt, user_prompt))
    return response
    

def test_chinese():
    is_english, translated_content = translate_content("这是一条中文消息")
    assert is_english == False
    assert translated_content == "This is a Chinese message"

def process_item(item):
    post = item["post"]
    is_english, translated_content = translate_content(post)
    print(post, is_english, translated_content)
    assert is_english == item["expected_answer"]["is_english"]
    assert have_same_meaning(translated_content, item["expected_answer"]["translated_content"])

def test_llm_normal_response():
    with open('test/unit/normal_response.json', 'r') as file:
        data = json.load(file)
        data = data["normal_response"]
        with multiprocessing.Pool(CPU_COUNT) as pool:
            pool.map(process_item, data)

def test_llm_gibberish_response():
    with open('test/unit/gibberish_response.json', 'r') as file:
        data = json.load(file)
        data = data["gibberish_response"]
        with multiprocessing.Pool(CPU_COUNT) as pool:
            pool.map(process_item, data)

api_key = os.getenv("AZURE_API_KEY")
client = AzureOpenAI(
    api_key=api_key,
    api_version="2024-02-15-preview",
    azure_endpoint="https://recitation-llm.openai.azure.com/"
)

@patch.object(client.chat.completions, 'create')
def test_unexpected_language(mocker):
  def translate_content(content: str) -> tuple[bool, str]:
    try:
        system_prompt = '''
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
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {
                "role": "system",
                "content": f"{system_prompt}"
                },
                {
                    "role": "user",
                    "content": f"{content}"
                }
            ]
        )
    
        response = response.choices[0].message.content
        response = ast.literal_eval(response)
        
        return response
    except:
        return False, "Unable to process"
  # we mock the model's response to return a random message
  mocker.return_value.choices[0].message.content = "I don't understand your request"

  assert translate_content("Hier ist dein erstes Beispiel.") == (False, "Unable to process")
