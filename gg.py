TEST_INFO = (
'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed '
'aliquam gravida augue, vel luctus risus accumsan in. Ut '
'efficitur et lacus eget feugiat. Donec eu ipsum turpis. '
'Praesent a diam sed lacus congue rhoncus sed eget nisi. '
'Mauris tempor tempus lorem, ac luctus sem rutrum id. '
'Duis auctor cursus fringilla. Sed interdum neque vitae '
'tellus lacinia hendrerit. Duis est libero, pulvinar vitae '
'hendrerit in, cursus a augue. Integer iaculis, nisi at '
'bibendum facilisis, tellus elit aliquam mi, id volutpat sem '
'lectus quis risus. Sed in dui id quam bibendum hendrerit. '
'Sed efficitur erat et ultrices mattis. Ut ultricies dolor '
'nec risus lobortis, sit amet varius est volutpat. Suspendisse '
'sodales ligula efficitur commodo tincidunt. Sed dictum velit '
'quis lectus elementum pretium. Integer scelerisque, urna in '
'elementum luctus, urna massa molestie tellus, non molestie '
'metus metus sit amet enim.'
)

import os
import tkinter as tk

from modes import modes
from view import SettingsDialog, View


class GallowsGame:

    title = 'Gallows Game'
    info = TEST_INFO #'Start programm text'
    chars_limit = 50

    def __init__(self):
        self.modes = {
            mode.get_name():mode for mode in modes
        }
        self.window = View(tk.Tk())
        self.window.master.title(self.title)
        self.window.master.resizable(False, False)

        self.current_mode = None
        self.current_settings = None
        self.current_task = None

        self._set_init_state()
        self._bind_events()

    def launch(self):
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
        # Run Button
        run_button = window.widgets['run_button']
        run_button.bind('<Return>', self._run_task)
        run_button.config(command=self._run_task)

    def _set_init_state(self):
        window = self.window
        widgets = window.widgets

        window.selected_mode.set('')
        window.selected_resource.set('')

        widgets['input'].config(state=tk.DISABLED)
        widgets['resources'].config(state=tk.DISABLED)
        widgets['run_button'].config(state=tk.DISABLED)
        widgets['settings_button'].config(state=tk.DISABLED)
        widgets['modes'].focus()

    ####### Actions ########
    def _input_send(self, event=None):
        input_ = self.window.widgets['input']
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
        resources_box.config(
            state='readonly',
            values=res_names,
        )
        resources_box.focus()
        
        if hasattr(mode_cls, 'settings') and mode_cls.settings:
            settings_button = window.widgets['settings_button']
            settings_button.config(state=tk.NORMAL)

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

    def _resource_select(self, event=None):
        window = self.window
        run_button = window.widgets['run_button']
        run_button.config(state=tk.NORMAL)
        run_button.focus()

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

        self._set_init_state()

        input_ = window.widgets['input']
        input_.config(state=tk.NORMAL)
        input_.focus()

        task.launch()

    def _show_results(self, result_text=''):
        self.window.display = result_text
        self._set_init_state()
        self.current_mode = None
        self.current_settings = None
        self.current_task = None


if __name__ == '__main__':
    GallowsGame().launch()