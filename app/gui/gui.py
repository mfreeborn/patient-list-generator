import queue
from concurrent.futures import ThreadPoolExecutor

from app.gui.enums import Key, Message
from app.gui.events import EVENTS
from app.gui.layout import main_layout
from app.gui.utils import init_gui, log_gui_event, set_text_invisible, update_gui


def run_gui():
    main_window = init_gui(window_title="Patient List Generator", layout=main_layout)

    gui_queue = queue.Queue()
    with ThreadPoolExecutor(max_workers=1) as executor:
        while True:
            event, values = main_window.read(timeout=100)

            if event is None:
                # closes the program
                break

            # handle user interactions synchronously
            elif event != "__TIMEOUT__":
                log_gui_event(event, values)
                set_text_invisible(window=main_window)

                # this is a bound event
                if isinstance(event, tuple):
                    event = event[1]

                EVENTS[event](values, main_window, gui_queue, executor)

                update_gui(values=values, window=main_window)

            # check for queue messages asynchronously
            try:
                message = gui_queue.get_nowait()
            except queue.Empty:
                pass
            else:
                if message == Message.START_GENERATING_LIST:
                    main_window[Key.GENERATE_LIST_BUTTON].update(
                        "GENERATING LIST...", disabled=True
                    )

                if message == Message.ERROR_GENERATING_LIST:
                    main_window[Key.GENERATE_LIST_BUTTON].update(
                        "Generate List", disabled=False
                    )
                    main_window[Key.LIST_ERROR_TEXT].update(visible=True)

                if message == Message.FINISH_GENERATING_LIST:
                    main_window[Key.GENERATE_LIST_BUTTON].update(
                        "Generate List", disabled=False
                    )
                    main_window[Key.LIST_SUCCESS_TEXT].update(visible=True)
