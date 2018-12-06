INFO = """Welcome to GallowsGame.

The application allows you to create and solve
simple tasks with text of the form of question-
answer, like guessing words, tests, translating
word and more.

You can use existing modes and resources for them,
or create your own. 

To continue, select the mode you need in the Mode
list. Then, select the resource in the list of 
resources. If possible, configure the settings 
(Setting button) and press Run button for start.
"""

import os
import tkinter as tk

from modes import modes
from view import SettingsDialog, View


class GallowsGame:

    INIT = 'init'
    MODE = 'mode'
    RESOURCE = 'resource'
    TASK = 'task'

    title = 'Gallows Game'
    info = INFO #'Start programm text'
    chars_limit = 50

    def __init__(self):
        
        # dict of pairs 'mode_name': ModeClass
        self.modes = {
            mode.get_name():mode for mode in modes
        }
        self.window = View(tk.Tk())
        self.window.master.title(self.title)
        self.window.master.resizable(False, False)

        self._set_state(self.INIT)
        self._bind_events()

    def launch(self):
        """ launch app 
        
        Load mode names into the Mode widget,
        display app info and launch Tk mainloop
        
        """
        modes_names = list(self.modes.keys())
        modes_combobox = self.window.widgets['modes']
        modes_combobox.config(values=modes_names)

        self.window.display = self.info
        self.window.launch()

    def _bind_events(self):
        window = self.window
        # Mode Combobox
        modes_box = window.widgets['modes']
        modes_box.bind('<<ComboboxSelected>>', self._mode_select)
        # Resource Combobox
        resources_box = window.widgets['resources']
        resources_box.bind('<<ComboboxSelected>>', self._resource_select)
        # Settings Button
        s_button = window.widgets['settings_button']
        s_button.bind('<Return>', self._open_settings)
        s_button.config(command=self._open_settings)
        # Input Entry
        input_text = window.input_text
        input_text.trace_variable('w', self._on_key_press)
        input_ = window.widgets['input']
        input_.bind('<Return>', self._input_send)
        # Reset Button
        reset_button = window.widgets['reset_button']
        reset_button.bind('<Return>', self._reset)
        reset_button.config(command=self._reset)
        # Run Button
        run_button = window.widgets['run_button']
        run_button.bind('<Return>', self._run_task)
        run_button.config(command=self._run_task)

    def _set_state(self, state):
        window = self.window
        widgets = window.widgets

        if state == self.INIT:
            self.current_mode = None
            self.current_settings = None
            self.current_task = None

            window.selected_mode.set('')
            window.selected_resource.set('')

            widgets['modes'].config(state='readonly')
            widgets['resources'].config(state=tk.DISABLED)
            widgets['settings_button'].config(state=tk.DISABLED)
            widgets['run_button'].config(state=tk.DISABLED)
            widgets['input'].config(state=tk.DISABLED)
            widgets['modes'].focus()

        elif state == self.MODE:
            mode = self.current_mode

            self.current_settings = None
            self.current_task = None

            window.selected_resource.set('')

            widgets['modes'].config(state='readonly')
            widgets['resources'].config(state='readonly')
            if hasattr(mode, 'settings') and mode.settings:
                widgets['settings_button'].config(state=tk.NORMAL)
            else:
                widgets['settings_button'].config(state=tk.DISABLED)
            widgets['run_button'].config(state=tk.DISABLED)
            widgets['input'].config(state=tk.DISABLED)
            widgets['resources'].focus()

        elif state == self.RESOURCE:
            widgets['run_button'].config(state=tk.NORMAL)
            widgets['run_button'].focus()

        elif state == self.TASK:
            widgets['modes'].config(state=tk.DISABLED)
            widgets['resources'].config(state=tk.DISABLED)
            widgets['settings_button'].config(state=tk.DISABLED)
            widgets['run_button'].config(state=tk.DISABLED)
            widgets['input'].config(state=tk.NORMAL)
            widgets['input'].focus()

        else:
            raise ValueError()

    ####### Actions ########
    def _input_send(self, event=None):
        input_text = self.window.input_text
        input_value = input_text.get()
        if not input_value:
            return
        input_text.set('')
        self.current_task.on_answer(input_value)

    def _mode_select(self, event=None):
        window = self.window
        mode_name = window.selected_mode.get()
        mode_cls = self.modes[mode_name]
        self.current_mode = mode_cls

        window.display = mode_cls.info
        res_names = mode_cls.get_resources_names()

        resources_box = window.widgets['resources']
        resources_box.config(values=res_names)

        self._set_state(self.MODE)

    def _on_key_press(self, *args):
        limit = self.chars_limit
        input_text = self.window.input_text
        text = input_text.get()
        if len(text) >= limit:
            input_text.set(text[:limit])

    def _open_settings(self, event=None):
        frame = self.window.master
        mode = self.current_mode
        title = 'Settings | {}'.format(mode.get_name())
        dialog = SettingsDialog(frame, title, settings=mode.settings)
        if dialog.result:
            self.current_settings = dialog.result

    def _reset(self, event=None):
        self._set_state(self.INIT)
        self.window.display = self.info

    def _resource_select(self, event=None):
        self._set_state(self.RESOURCE)

    def _run_task(self, event=None):
        mode_cls = self.current_mode
        window = self.window
        resource_name = window.selected_resource.get()
        settings = None

        if self.current_settings:
            settings = self.current_settings
        elif hasattr(mode_cls, 'settings') and mode_cls.settings:
            settings = {
                k:v.get() for k,v in mode_cls.settings.items()
            }

        task = mode_cls(
            # Because display now is a property object in window
            window=self.window,
            resource_name=resource_name,
            settings=settings,
            on_exit=self._show_results
        )
        self.current_task = task

        self._set_state(self.TASK)
        task.launch()

    def _show_results(self, result_text=''):
        self.window.display = result_text
        self._set_state(self.INIT)


if __name__ == '__main__':
    GallowsGame().launch()
