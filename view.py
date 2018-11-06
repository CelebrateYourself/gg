
import tkinter as tk
import tkinter.ttk as ttk

import tkinter.simpledialog as dialogs


class View(ttk.Frame):

    def __init__(self, root):
        super().__init__(root)

        self.widgets = {}
        self.selected_mode = tk.StringVar()
        self.selected_resource = tk.StringVar()
        self.input_text = tk.StringVar()

        self._create_widgets()

    @property
    def display(self):
        widget = self.widgets['display']
        return widget.get(1.0, tk.END)

    @display.setter
    def display(self, text):
        widget = self.widgets['display']
        widget.config(state=tk.NORMAL)
        widget.delete(1.0, tk.END)
        widget.insert(tk.END, text)
        widget.config(state=tk.DISABLED)

    def _create_widgets(self):
        frame = self.master
        frame.config(pady=5, padx=5, bg='#bbb')

        ttk.Label(
            frame,
            text='Mode',
        ).grid(row=0, column=0, sticky='nw', pady=(3,0))

        modes = ttk.Combobox(
            frame,
            state='readonly',
            textvariable=self.selected_mode,
            values=[],
        )
        modes.grid(
            row=0,
            column=1,
            sticky='nw',
            padx=(0, 5),
            pady=(2,0)
        )
        self.widgets['modes'] = modes

        ttk.Label(
            frame,
            text='Resource',
        ).grid(row=0, column=2, sticky='nw', pady=(3,0))

        resources = ttk.Combobox(
            frame,
            state='readonly',
            textvariable=self.selected_resource,
        )
        resources.grid(
            row=0,
            column=4,
            sticky='nw',
            padx=(0, 5),
            pady=(2,0)
        )
        self.widgets['resources'] = resources

        settings_button = ttk.Button(
            frame,
            text='Settings',
        )
        settings_button.grid(
            row=0,
            column=5,
            columnspan=2,
            sticky='ne'
        )
        self.widgets['settings_button'] = settings_button

        display = tk.Text(
            frame,
            #font=('Courier', 11),
            bg='#eee',
            borderwidth=1,
            height=10,
            padx=7,
            pady=2,
            width=1, # :D maybe, that width may be ~width of second column
            wrap=tk.WORD,
        )
        display.grid(
            row=1,
            column=0,
            columnspan=7,
            sticky='nwse',
            pady=5,
            padx=(1, 23)
        )
        self.widgets['display'] = display

        scrollbar = ttk.Scrollbar(
            frame,
            command=display.yview,
        )
        scrollbar.grid(row=1, column=6, sticky='nes', pady=5)
        self.widgets['scrollbar'] = scrollbar
        display.config(yscrollcommand=scrollbar.set)

        input_ = ttk.Entry(
            frame,
            textvariable=self.input_text,
        )
        input_.grid(
            row=2,
            column=0,
            columnspan=4,
            sticky='wse',
            pady=(0, 1)
        )
        self.widgets['input'] = input_
        
        reset_button = ttk.Button(
            frame,
            text='Reset'
        )
        reset_button.grid(row=2, column=4, sticky='es', padx=(0, 5))
        self.widgets['reset_button'] = reset_button

        run_button = ttk.Button(
            frame,
            text='Run'
        )
        run_button.grid(row=2, column=5, columnspan=2, sticky='es')
        self.widgets['run_button'] = run_button

    def launch(self):
        self.master.mainloop()


class SettingsDialog(dialogs.Dialog):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args)
        self.settings = kwargs['settings']
        self._create_widgets()

    def body(self, master):
        self.result = None

    def apply(self):
        # on OK exit
        pass

    def _create_widgets(self):
        print(self.settings)
        # for line,setting in enumerate(settings)
        # label = Label
        # s_widget = self._widgets_factory(setting)
        # label.grid(row=line, column=0)
        # s_widget.grid(row=line, column=1)

