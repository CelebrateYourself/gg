
import tkinter as tk
import tkinter.ttk as ttk


class View(ttk.Frame):

    def __init__(self, root):
        super().__init__(root)

        self.widgets = {}
        self.display = tk.StringVar()
        self.selected_mode = tk.StringVar()
        self.selected_resource = tk.StringVar()
        self.input_text = tk.StringVar()

        self._create_widgets()

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

        display = tk.Label(
            frame,
            anchor='nw',
            bg='#eee',
            height=10,
            justify='left',
            textvariable=self.display,
            wraplength=425,
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
        ).grid(row=1, column=6, sticky='nes', pady=5)
        self.widgets['scrollbar'] = scrollbar

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
