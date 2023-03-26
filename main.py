import asyncio
import functools
import os
import shutil
from typing import Callable

import openai  # very nice API to run AI models; see https://replicate.com/
from nicegui import ui
from nicegui.events import UploadEventArguments

from components import chat

openai.api_key = "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"

messages = []

ui_state = chat.UIState()


@ui.page('/')
async def index_page() -> None:
    # Chat component is in components/chat.py
    await chat.content(ui_state)





async def update_animation(object, animation):
    object.classes(animation)


async def update_border_color(object, color):
    object.classes('border-2' + color)


async def transcribe(e: UploadEventArguments):
    # Assume `temp_file` is a SpooledTemporaryFile object

    transcription.classes("bg-gray-800")
    spinner.style('display: block')
    home_column.classes('border-2 border-gray-800')
    file_name = e.name
    with open(e.name, 'wb') as f:
        shutil.copyfileobj(e.content, f)

    e.content.close()

    file = open(file_name, 'rb')
    try:
        result = await io_bound(openai.Audio.transcribe, "whisper-1", file=file)
        transcription.text = result.text
        await update_border_color(home_column, ' border-green-300')
        await update_animation(transcription, 'animate-none')
    except openai.error.InvalidRequestError as e:
        await update_border_color(home_column, ' border-red-500')
        await update_animation(transcription, 'animate-none')
        return
    finally:
        spinner.style('display: none')
        copy_button.style('display: block')
        file.close()
        os.remove(file_name)


# Header


# Footer
with ui.footer().style('background-color: #3874c8'):
    ui.label('Copyright © 2023 Luis Chaparro. This website was built using OpenAI and NiceGUI. All rights reserved.')

    # transcription = ui.markdown("Transcript:\n").classes("text-white text-sm")

ui.run(dark=True, title='NiceGUI Demo')
