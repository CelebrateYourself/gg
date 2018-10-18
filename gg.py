
import os
import tkinter as tk

# чтобы при создании списка режимов можно
# было использовать их имена, а не названия файлов,
# решил оставить как есть. В противном случае придется
# подключать все файлы, чтобы узнать имена модов.
from modes import modes
from view import View


class GallowsGame:

    info = 'Start programm text'
    chars_limit = 40

    def __init__(self):
        self.modes = {
            mode.get_name():mode for mode in modes
        }
        self.current_task = None
        self.window = View(tk.Tk())

        self._set_init_state()
        self._bind_events()

    def launch(self):
        modes_names = list(self.modes.keys())
        modes_combobox = self.window.widgets['modes']
        modes_combobox.config(values=modes_names)

        self.window.display.set(self.info)
        self.window.launch()

    def _bind_events(self):
        window = self.window
        # Mode Combobox
        modes_box = window.widgets['modes']
        modes_box.bind('<<ComboboxSelected>>', self._mode_select)
        # Resource Combobox
        resources_box = window.widgets['resources']
        resources_box.bind('<<ComboboxSelected>>', self._resource_select)
        # Input Entry
        input_text = window.input_text
        input_text.trace_variable('w', self._on_key_press)
        input_ = window.widgets['input']
        input_.bind('<Return>', self._input_send)
        # Run button
        run_button = window.widgets['run_button']
        run_button.bind('<Return>', self._run_task)
        run_button.bind('<space>', self._run_task)
        run_button.bind('<Button-1>', self._run_task)

    def _set_init_state(self):
        window = self.window
        widgets = window.widgets

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
        window.display.set(mode_cls.info)
        res_names = mode_cls.get_resources_names()

        resources_box = window.widgets['resources']
        resources_box.config(
            state='readonly',
            values=res_names,
        )
        resources_box.focus()
        
        if hasattr(mode_cls, 'settings'):
            settings_button = window.widgets['settings_button']
            settings_button.config(state=tk.NORMAL)

    def _on_key_press(self, *args):
        limit = self.chars_limit
        input_text = self.window.input_text
        text = input_text.get()
        if len(text) >= limit:
            input_text.set(text[:limit])

    def _resource_select(self, event=None):
        window = self.window
        run_button = window.widgets['run_button']
        run_button.config(state=tk.NORMAL)
        run_button.focus()

    def _run_task(self, event=None):
        window = self.window
        mode_name = window.selected_mode.get()
        resource_name = window.selected_resource.get()
        mode_cls = self.modes[mode_name]

        task = mode_cls(
            display=self.window.display,
            resource_name=resource_name,
            on_exit=self._show_results
        )
        self.current_task = task

        input_ = window.widgets['input']
        input_.config(state=tk.NORMAL)
        input_.focus()

        task.launch()

    def _show_results(self, result_text=''):
        self.window.display.set(result_text)

        self.current_task = None
        input_ = self.window.widgets['input']
        input_.config(state=tk.DISABLED)


if __name__ == '__main__':
    GallowsGame().launch()