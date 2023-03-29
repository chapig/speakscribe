# This code is licensed under the terms of the GNU Lesser General Public License v2.1

from nicegui import ui

from components import audio_transcriber
from components import chat

ui_state = chat.UIState()
au_state = audio_transcriber.AUDIO_State()

@ui.page('/')
async def index_page() -> None:
    # Chat component is in components/chat.py
    await chat.content(ui_state)
    await audio_transcriber.content(au_state)

    # Footer
    with ui.footer().classes("font-mono bg-zinc-900"):
        ui.label(
            'Copyright © 2023 Luis Chaparro. This website was built using OpenAI and NiceGUI. All rights reserved.')


ui.run(dark=True, title='Speakscribe')
