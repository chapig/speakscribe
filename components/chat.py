# This code is licensed under the terms of the GNU Lesser General Public License v2.1
import asyncio, functools, os
from typing import Callable

import openai
from nicegui import ui

from database import handler

database_handler = handler.Database()

# Get environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")


async def io_bound(callback: Callable, *args: any, **kwargs: any):
    """Makes a blocking function awaitable;
    pass function as first parameter and its arguments as the rest"""
    return await asyncio.get_event_loop().run_in_executor(None, functools.partial(callback, *args, **kwargs))


async def get_chatbot_response(prompt):
    response = await io_bound(openai.Completion.create,
                              engine="text-davinci-003",
                              prompt=prompt,
                              temperature=0.9,
                              max_tokens=150,
                              top_p=1,
                              frequency_penalty=0,
                              presence_penalty=0.6,
                              )
    return response.choices[0].text


class UIState:
    def __init__(self):
        self.loading_spinner = ui.spinner('dots', size='lg', color='white').style('display: none')
        self.text_input = ui.input(value='')
        self.chat = ui.column().classes("w-full")
        self.right_menu = ui.right_drawer(value=True, fixed=False, top_corner=True).style(
            "background-color: none;").props(
            ':width="500"').classes("")
        self.icon = "icon=cancel"
        self.spinner = None

    async def update_chat_row(self) -> None:
        if self.text_input.value == '':
            self.text_input.classes('border-2 border-red-500')
            return

        with self.chat:
            ui.label(self.text_input.value.capitalize()).classes("bg-stone-700 text-white rounded-lg p-2")
            self.spinner = ui.spinner('dots', size='lg', color='black').style('display: block').classes(
                "bg-white text-white rounded-lg p-2")
            response = await get_chatbot_response(self.text_input.value)
            ui.label(response).classes("bg-white text-black rounded-lg p-2")
            self.spinner.style('display: none')
        self.text_input.value = ''


async def toggle_drawer(ui_state: UIState) -> None:
    ui_state.right_menu.toggle()
    print("toggle_drawer")


async def content(ui_state: UIState) -> None:
    with ui.header(elevated=False).style('background-color: #1d1d1d').classes(
            'items-center justify-between') as ui_state.header:
        ui.label('ChatGPT').classes("text-white text-lg font-medium")

        ui.button(on_click=lambda: ui_state.right_menu.toggle()).props(
            f'flat color=white icon=chat')

        with ui.right_drawer(value=True, fixed=False, top_corner=True).style("background-color: none;").props(
                ':width="500"').classes("") as ui_state.right_menu:
            with ui.column().classes('bg-blue-700 shadow-2xl rounded-md p-8 text-white relative'):
                ui.label('Chat').classes("text-lg text-white font-medium")
                ui.label('Chat with ChatGPT.').classes(
                    "text-white text-sm font-normal")

                with ui.column() as ui_state.chat:
                    ui.label(
                        "Hello, type something to start a conversation!").classes(
                        "bg-white text-black rounded-lg p-2")

                with ui.row():
                    ui_state.text_input = ui.input().classes("w-full").on("keydown.enter", ui_state.update_chat_row)