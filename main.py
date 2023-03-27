# This code is licensed under the terms of the GNU Lesser General Public License v2.1
import asyncio
import functools
from typing import Callable

import pyperclip, openai, os, shutil, sqlite3
from nicegui import ui
from nicegui.events import UploadEventArguments

from components import chat

ui_state = chat.UIState()


@ui.page('/')
async def index_page() -> None:
    # Chat component is in components/chat.py
    await chat.content(ui_state)

    async def io_bound(callback: Callable, *args: any, **kwargs: any):
        """Makes a blocking function awaitable;
        pass function as first parameter and its arguments as the rest"""
        return await asyncio.get_event_loop().run_in_executor(None, functools.partial(callback, *args, **kwargs))
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

    with ui.tab_panel('Home').style('background-color: #121212'):
        with ui.row().style('gap: 3rem'):
            with ui.column().classes(
                    'bg-gray-900 shadow-2xl rounded-md p-8 text-white border-2 border-blue-500 w-full') as home_column:
                ui.label('Audio Transcription').classes("text-lg text-white font-medium")
                ui.label(
                    'Upload an audio file to transcribe it. You can either upload audio or video files.').classes(
                    "text-white text-sm font-normal")
                audio_button_upload = ui.upload(on_upload=transcribe, auto_upload=True, multiple=False).classes(
                    'text-white text-sm shadow-transparent shadow-none bg-gray-800 w-full')
                with ui.row():
                    with ui.label(text='').classes(
                            "rounded p-6 text-white text-md shadow-md relative pt-10 pb-10") as transcription:
                        spinner = ui.spinner('dots', size='lg', color='white').style('display: none')
                        copy_button = ui.button(on_click=
                                                lambda: pyperclip.copy(transcription.text)).props(
                            'icon=copy_all').classes(
                            'shadow-none bg-transparent top-0 right-0 absolute').tooltip("Copy to clipboard").style(
                            "display: none")


# Footer
with ui.footer().style('background-color: #3874c8'):
    ui.label('Copyright © 2023 Luis Chaparro. This website was built using OpenAI and NiceGUI. All rights reserved.')


ui.run(dark=True, title='Speakscribe')
