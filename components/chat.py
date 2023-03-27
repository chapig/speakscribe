# This code is licensed under the terms of the GNU Lesser General Public License v2.1
import asyncio
import functools
from datetime import datetime
from typing import Callable

import openai
from nicegui import ui

from database import handler
from settings import default_prompt
from settings import open_ai_api_key

database_handler = handler.Database()

openai.api_key = open_ai_api_key


async def io_bound(callback: Callable, *args: any, **kwargs: any):
    """Makes a blocking function awaitable;
    pass function as first parameter and its arguments as the rest"""
    return await asyncio.get_event_loop().run_in_executor(None, functools.partial(callback, *args, **kwargs))


async def message_timestamp():
    datenow = str(datetime.now()).split(' ')
    date = datenow[0]
    time = datenow[1].split(":")
    time = f'{time[0]}:{time[1]}' + ' '
    return date, time


async def get_chatbot_response(prompt):
    response = await io_bound(openai.Completion.create,
                              engine="text-davinci-003",
                              prompt=prompt,
                              temperature=0.9,
                              max_tokens=1000,
                              top_p=1,
                              frequency_penalty=0,
                              presence_penalty=0.6,
                              )
    return response.choices[0].text


class UIState:
    def __init__(self):
        self.delete_dialog = ui.dialog()
        self.loading_spinner = ui.spinner('dots', size='lg', color='white').style('display: none')
        self.text_input = ui.input(value='').classes("w-full")
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

            messages = await database_handler.get_messages()
            # Format the messages
            prompt = ''
            for message in messages:
                prompt += f'{message[1]}\n{message[2]}\n'

            prompt += f'You: {self.text_input.value}\n'
            print(default_prompt + prompt)

            response = await get_chatbot_response(default_prompt + prompt)
            response = response.replace('Chatbot:', '')
            print("Chatbot: " + response)

            await database_handler.insert_message(self.text_input.value, response, str(datetime.now()))

            self.text_input.value = ''
            with ui.label(response).classes("bg-white text-black rounded-lg p-2"):
                date, time = await message_timestamp()
                ui.label(time + " " + date).classes("text-xs text-gray-400").tooltip(f"Message received at this time.")
            self.spinner.style('display: none')


async def notify_message_cleared():
    await database_handler.delete_messages()
    ui.notify(type="positive", message="Messages cleared successfully.", position="top")


async def toggle_drawer(ui_state: UIState) -> None:
    ui_state.right_menu.toggle()


async def content(ui_state: UIState) -> None:
    with ui.header(elevated=False).style('background-color: #1d1d1d').classes(
            'items-center justify-between') as ui_state.header:
        ui.label('Speakscribe').classes("text-white text-md font-medium")

        ui.button(on_click=lambda: ui_state.right_menu.toggle()).props(
            f'flat color=white icon=chat')

        with ui.right_drawer(value=True, fixed=False, top_corner=True).style("background-color: none;").props(
                ':width="500"').classes("") as ui_state.right_menu:
            with ui.column().classes('bg-blue-700 shadow-2xl rounded-md p-8 text-white relative'):
                ui.label('Chat').classes("text-lg text-white font-medium")
                ui.label('Chat with ChatGPT.').classes(
                    "text-white text-sm font-normal")

                with ui.dialog() as ui_state.delete_dialog, ui.card().classes("p-6 shadow-none"):
                    ui.label('Clear all messages')
                    ui.label(
                        "Note that this action can't be undone and will erase the chatbot's memory, "
                        "therefore the chatbot won't be able to respond based on previous messages.").classes(
                        "text-sm text-gray-400")
                    with ui.row().classes("justify-end"):
                        ui.button('Cancel', on_click=ui_state.delete_dialog.close).props("color=red").classes(
                            "capitalize")
                        ui.button('Clear', on_click=ui_state.delete_dialog.close).props("color=white").classes(
                            "capitalize text-black").on('click',
                                                        notify_message_cleared)
                ui.button(on_click=ui_state.delete_dialog.open).props("icon=delete color=red unelevated")

                with ui.column().classes("bg-blue-600 rounded-lg w-full p-6 shadow-lg") as ui_state.chat:
                    ui.label(
                        "Hello, type something to start a conversation!").classes(
                        "bg-white text-black rounded-lg p-2")

                with ui.row().classes("w-full"):
                    ui_state.text_input = ui.input().classes("w-full block").on("keydown.enter",
                                                                                ui_state.update_chat_row)
