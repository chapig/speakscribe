# This code is licensed under the terms of the GNU Lesser General Public License v2.1

from nicegui import ui

from components import audiotranscriber
from components import chat

ui_state = chat.UIState()
au_state = audiotranscriber.AUDIO_State()

@ui.page('/')
async def index_page() -> None:
    # Chat component is in components/chat.py
    await chat.content(ui_state)
    await audiotranscriber.content(au_state)

    # Footer
    with ui.footer().style('background-color: #3874c8'):
        ui.label(
            'Copyright © 2023 Luis Chaparro. This website was built using OpenAI and NiceGUI. All rights reserved.')


ui.run(dark=True, title='Speakscribe')
