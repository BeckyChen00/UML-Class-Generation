import os

import openai

from openai import OpenAI

from Parser import *
from calculation import *
from config import *
from GenPrompt import *

input_tokens = 0
output_tokens = 0
total_tokens = 0

def ask_llm(llm,message,temperature,used_tokens):
    if llm==1:
        set_openai()        
        response = openai.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages = message,
                temperature = temperature,
                max_tokens = running_params['max_tokens'],
                top_p = running_params['top_p'],
                frequency_penalty = running_params['frequency_penalty'],
                presence_penalty = running_params['presence_penalty'],
                )
        AI_answer = response.choices[0].message.content
        global input_tokens,output_tokens,total_tokens
        input_tokens += response.usage.prompt_tokens
        output_tokens += response.usage.completion_tokens
        total_tokens += response.usage.total_tokens
        print("used tokens: ", input_tokens,output_tokens,total_tokens)
        used_tokens += response.usage.total_tokens
    elif llm==2:
        set_openai()
        response = openai.chat.completions.create(
                model="gpt-4",
                messages = message,
                temperature = temperature,
                max_tokens = running_params['max_tokens'],
                top_p = running_params['top_p'],
                frequency_penalty = running_params['frequency_penalty'],
                presence_penalty = running_params['presence_penalty'],

                )
        AI_answer = response.choices[0].message.content
        # used_tokens += response.usage.total_tokens
    elif llm==3:
        client = OpenAI(
            base_url = "https://integrate.api.nvidia.com/v1",
            api_key = running_params['llama3-8b_api_key']
            )
        response = client.chat.completions.create(
            model="meta/llama3-8b-instruct",
            messages = message,
            temperature = temperature,
            max_tokens = running_params['max_tokens'],
            top_p = running_params['top_p'],
            )
        AI_answer = ''
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                AI_answer+=chunk.choices[0].delta.content
    elif llm==4:
        client = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            api_key= "sk-0ce7cd90b6074604ae473eca22fbeb69", 
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        response = client.chat.completions.create(
            model="qwen-plus", # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            messages=message,
            temperature = temperature,
            max_tokens = running_params['max_tokens'],
            top_p = running_params['top_p'],
            frequency_penalty = running_params['frequency_penalty'],
            presence_penalty = running_params['presence_penalty'],           
            )
        AI_answer = response.choices[0].message.content

    return AI_answer,used_tokens


def set_openai():
    # os.environ['http_proxy'] = running_params['http_proxy']
    # os.environ['https_proxy'] = running_params['https_proxy']
    # openai.api_key=running_params['openai_api_key']
    openai.base_url = 'https://www.DMXapi.com/v1/'
    openai.api_key='sk-HXJ9ubNKq2k13zlfTzr1xsL35CSzXeaAxkHKE0O6jOgYZ2GO'