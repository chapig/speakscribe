# `Speakscribe`
Speakscribe is a web application that allows users to transcribe audios using OpenAI and also interact with a chat bot. The web application is created in Python using NiceGUI.

![image](https://user-images.githubusercontent.com/46666572/228412224-4534eb88-2b9d-4713-ac62-3ed1d3b10788.png)


## Requirements
To use this web application, you will need to have the following installed on your machine:

- Python 3.6 or higher
- NiceGUI
- OpenAI API key

## Installation

- Clone this repository to your local machine.
- Open the settings.toml file and insert your OpenAI API key.
- Modify the chatbot prompt if desired.

### Example of settings.toml
```toml
[openai]
api_key = "sk-openai_api_key"
prompt = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\n"
```

- Run `pip install -r requirements.txt` to install the required libraries.
- Run the application by executing speakscribe.py on your machine.

## Deployment
To deploy your NiceGUI app on a server, you will need to execute your main.py (or whichever file contains your ui.run(...)) on your cloud infrastructure. You can, for example, just install the NiceGUI python package via pip and use systemd or similar service to start the main script. In most cases, you will set the port to 80 (or 443 if you want to use HTTPS) with the ui.run command to make it easily accessible from the outside. Check [NiceGUI - Server Hosting](https://nicegui.io/documentation#server_hosting) for more information.

## Credits
This project was created by Luis C. Gomez using [NiceGUI](https://github.com/zauberzeug/nicegui/)
