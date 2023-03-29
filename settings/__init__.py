# This code is licensed under the terms of the GNU Lesser General Public License v2.1
import toml
import openai

open_ai_api_key = toml.load('settings.toml')['openai']['api_key']
default_prompt = toml.load('settings.toml')['openai']['prompt']

openai.api_key = open_ai_api_key

# Test the API key
try:
    openai.Completion.create(engine="text-curie-001", prompt="Hello, World!", max_tokens=5)
except openai.error.AuthenticationError as e:
    raise Exception('Invalid OpenAI API Key, please check your settings.toml file.')

