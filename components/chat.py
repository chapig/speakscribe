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
                              stop=["You:", "Chatbot:"]
                              )
    return response.choices[0].text


class UIState:
    def __init__(self):
        self.transcription = ui.button()
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
            with ui.row().classes("bg-blue-500 text-md text-white shadow-md font-normal text-center rounded-lg p-3"):
                ui.label(self.text_input.value.capitalize())
                date, time = await message_timestamp()
                ui.label(time + " " + date).classes("text-xs text-white").tooltip(
                    f"Message received at this time.")
            self.spinner = ui.spinner('dots', size='lg', color='black').style('display: block').classes(
                "bg-white text-white rounded-lg p-2")

            messages = await database_handler.get_messages()
            # Format the messages
            prompt = ''
            for message in messages:
                prompt += f'{message[1]}\n{message[2]}\n'

            prompt += f'You: {self.text_input.value}\nChatbot:'

            response = await get_chatbot_response(default_prompt + prompt)
            response = response.replace('AI Assistant:', '').strip()

            await database_handler.insert_message(self.text_input.value, response, str(datetime.now()))

            self.text_input.value = ''
            with ui.row().classes(
                    "bg-white text-md text-black font-normal text-left rounded-lg p-2 shadow-lg") as self.chat_box:
                ui.label(response).classes("text-sm text-black")
                date, time = await message_timestamp()
                ui.label(time + " " + date).classes("text-xs text-gray-400").tooltip(
                    f"Message received at this time.")

            self.spinner.style('display: none')

    async def children_chat(self):
        self.chat.clear()


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

        with ui.dialog() as ui_state.delete_dialog, ui.card().classes("p-6 shadow-none"):
            ui.label('Clear all messages')
            ui.label(
                "Note that this action can't be undone and will erase the chatbot's memory, "
                "therefore the chatbot won't be able to respond based on previous messages.").classes(
                "text-sm text-gray-400")

            with ui.row().classes("justify-end"):
                ui.button('Cancel', on_click=ui_state.delete_dialog.close).props("color=red").classes(
                    "capitalize")
                ui.button('Clear', on_click=ui_state.children_chat).props("color=white").classes(
                    "capitalize text-black").on('click',
                                                notify_message_cleared).on('click', ui_state.delete_dialog.close)

        with ui.right_drawer(value=True, fixed=False, top_corner=True).style("background-color: none;").props(
                ':width="500"').classes(
            "bg-gray-900 shadow-2xl rounded-md p-8 text-white relative h-full") as ui_state.right_menu:
            with ui.row().classes(
                    "grid grid-cols-1 md:grid-cols-1 lg:grid-cols-1 gap-2 md:gap-4 lg:gap-6 p-5"):
                ui.label('Chatbot Assistance').classes("text-xl text-white font-medium")
                with ui.row():
                    ui.label(
                        'Connect with ChatGPT to chat and have personalized recommendations.').classes(
                        "text-white text-md font-normal")
                with ui.row():
                    ui.button(on_click=ui_state.delete_dialog.open).props("icon=delete color=red unelevated").classes(
                        "mb-2")

            with ui.row().classes(
                    "grid grid-cols-1 md:grid-cols-1 lg:grid-cols-1 gap-2 md:gap-4 lg:gap-6 p-5 bg-gray-800 rounded-lg") as ui_state.chat:
                with ui.row().classes("bg-white text-md text-black font-normal text-center rounded-lg p-2 shadow-lg"):
                    ui.label("Hello, type something to start a conversation!")
                    date, time = await message_timestamp()
                    ui.label(time + " " + date).classes("text-xs text-gray-400").tooltip(
                        f"Message received at this time.")

            with ui.row().classes("w-full mt-4"):
                with ui.input().classes("w-full text-black bg-black").props(
                        'filled label-color=primary dark standout="bg-primary text-white').on("keydown.enter",
                                                                                              ui_state.update_chat_row) as ui_state.text_input:
                    ui.button(on_click=ui_state.update_chat_row).props(
                        "icon=send color=white unelevated flat").classes("w-12 h-12 bg-transparent text")
