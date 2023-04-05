# This code is licensed under the terms of the GNU Lesser General Public License v2.1
import asyncio
import functools
import os
import shutil
from typing import Callable

import openai
from nicegui import ui
from nicegui.events import UploadEventArguments


async def io_bound(callback: Callable, *args: any, **kwargs: any):
    """Makes a blocking function awaitable;
    pass function as first parameter and its arguments as the rest"""
    return await asyncio.get_event_loop().run_in_executor(None, functools.partial(callback, *args, **kwargs))


with ui.row().classes("ml-12 lg:w-full w-2/3") as box_text:
    ui.textarea().classes("lg:w-full w-3/4 font-mono text-white bg-transparent rounded-lg").props(
        "filled borderless hide-bottom-space autogrow").style("display: none;")


class AUDIO_State:
    def __init__(self):
        self.upload_dialog = ui.dialog()
        with ui.row().classes("ml-12 lg:w-full w-2/3") as self.text_box:
            ui.textarea().classes("lg:w-full w-3/4 font-mono text-white bg-transparent rounded-lg").props(
                "filled borderless hide-bottom-space autogrow").style("display: none;")

    async def transcribe_audio(self, e: UploadEventArguments):
        # Assume `temp_file` is a SpooledTemporaryFile object
        # with open(e.name, 'wb') as f:
        # transcription.classes("bg-gray-800")
        # spinner.style('display: block')
        # home_column.classes('border-2 border-gray-800')
        print("Transcribing audio...")

        self.text_box.props(add="loading")
        self.upload_dialog.close()
        file_name = e.name
        with open(e.name, 'wb') as f:
            shutil.copyfileobj(e.content, f)

        e.content.close()

        file = open(file_name, 'rb')
        try:
            result = await io_bound(openai.Audio.transcribe, "whisper-1", file=file)
            self.text_box.value = result.text
        except openai.error.InvalidRequestError as e:
            pass
        finally:
            # Delete file
            file.close()
            os.remove(file_name)
            self.text_box.props(remove="loading")
        #


async def content(au: AUDIO_State) -> None:
    # Upload button
    with ui.dialog() as au.upload_dialog, ui.card().classes("p-6 shadow-none font-mono"):
        ui.label('Upload an audio or video file')
        ui.label(
            "Formats supported:"
            " mp3, mp4, wav").classes(
            "text-sm text-gray-400")

        with ui.row().classes("justify-end"):
            with ui.upload(on_upload=au.transcribe_audio) as upload:
                upload.props("color=grey-10 flat hide-upload-btn auto-upload no-thumbnails")
        with ui.row().classes("justify-end"):
            ui.button('Cancel', on_click=au.upload_dialog.close).props("color=red").classes(
                "capitalize")

    with ui.row().classes("absolute inset-0 max-w-md mx-auto h-80 blur-[118px] sm:h-72").style(
            "background: linear-gradient(152.92deg, rgba(192, 132, 252, 0.2) 4.54%, "
            "rgba(232, 121, 249, 0.26) 34.2%, rgba(192, 132, 252, 0.1) 77.55%)"):
        with ui.label() as index_title_header:
            index_title_header.text = "Speakscribe"
            index_title_header.classes("text-4xl font-bold text-white")

    with ui.column():
        with ui.row().classes("ml-12"):
            ui.label("Audio Transcription").classes("text-4xl font-bold text-white font-mono")
        with ui.row().classes("ml-12 lg:w-full w-2/3"):
            ui.label(
                "Upload an audio file to transcribe it. You can either upload audio or video files.").classes(
                "text-white text-md font-mono")
        with ui.row().classes("ml-12 lg:w-full w-11/12"):
            au.text_box = ui.textarea().classes("lg:w-full w-11/12 font-mono text-white bg-transparent rounded-lg").props(
                "filled borderless hide-bottom-space autogrow")

        with ui.row().classes("ml-12 lg:w-full w-3/4"):
            ui.button("Upload an audio file", on_click=au.upload_dialog.open).props(
                "icon=upload white flat unelevated xs").classes(
                "bg-transparent border-2 rounded-lg border-white text-white font-mono")