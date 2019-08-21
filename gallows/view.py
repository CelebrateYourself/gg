import tkinter as tk
import tkinter.ttk as ttk
import tkinter.simpledialog as dialogs

from functools import partial


class View(ttk.Frame):
    """ GG app main window
    
    Class variables:   
    - display: const property 
      : provides a simple Text widget interface (get/set text)
    
    - launch() -> None
      : launch Tk mainloop
    
    """

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
            # font=('Courier', 11),
            bg='#eee',
            borderwidth=1,
            height=10,
            padx=7,
            pady=2,
            width=1, # :D maybe, that width must be ~width of second column
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


class SettingsDialog:
    """ Mode settings dialog """

    def __init__(self, master, title, settings):
        self.master = master
        self.window = tk.Toplevel(master)
        self.frame = ttk.Frame(self.window)
        self.exit_frame = ttk.Frame(self.window)
        self.window.title(title)
        self.window.resizable(False, False)
        self.settings = settings
        self.variables = {}
        self.result = {}

        self.frame.grid(row=0, padx=5, pady=(5,0))
        self.exit_frame.grid(row=1, pady=5, padx=5)

        self.window.focus()
        self.window.grab_set()

        self.window.geometry(
            "+{}+{}".format(
                self.master.winfo_rootx()+50,
                self.master.winfo_rooty()+50
            )
        )

        self._create_widgets()
        self.window.wait_window(self.window)

    def _on_apply(self):
        results = {k:v.get() for k,v in self.variables.items()}
        self.result.update(results)
        self.variables.clear()
        self.master.focus()
        self.window.destroy()

    def _on_cancel(self):
        self.variables.clear()
        self.master.focus()
        self.window.destroy()

    def _create_widgets(self):
        frame = self.frame
        exit_frame = self.exit_frame

        ttk.Button(
            exit_frame,
            text='Ok',
            command=self._on_apply,
        ).grid(row=0, column=0, sticky='se', padx=(0,2))

        ttk.Button(
            exit_frame,
            command=self._on_cancel,
            text='Cancel',
        ).grid(row=0, column=1, sticky='sw', padx=(2,0))

        ######## Settings #########

        settings = self.settings

        for line,(key,setting) in enumerate(settings.items()):
            label_text = (
                setting.label 
                if hasattr(setting, 'label') 
                else key.lower().title()
            )
            ttk.Label(
                frame,
                text=label_text,
            ).grid(row=line, column=0, sticky='ne', padx=(0,2), pady=2)

            s_widget = self._widgets_factory(frame, key, setting)
            s_widget.grid(row=line, column=1, sticky='nw', padx=(2,0), pady=2)

    def _widgets_factory(self, frame, key, setting):
        w_name = setting.widget
        widget = None

        if w_name == 'entry':  # Not tested
            def validate(setting, var, *args):
                text = var.get()
                if not setting.is_valid(text):
                    var.set(setting.get())

            variable = tk.StringVar()
            widget = ttk.Entry(
                frame,
                textvariable=variable,
            )
            widget.bind(
                '<FocusOut>',
                partial(validate, setting, variable)
            )

        elif w_name == 'bool':
            variable = tk.BooleanVar()
            widget = tk.Checkbutton(
                frame,
                variable=variable,
            )

        elif w_name == 'range':
            variable = tk.IntVar()
            widget = ttk.Frame(frame)
            ttk.Scale(
                widget, 
                from_=setting.from_,
                to=setting.to,
                variable=variable,
                command=partial(
                    lambda var,val: var.set(int(float(val))),
                    variable
                )
            ).pack()
            ttk.Label(
                widget,
                textvariable=variable,
            ).pack()

        else:
            msg = 'Widget name "{}" is not implemented'.format(setting.widget)
            raise TypeError(msg)

        variable.set(setting.get())
        self.variables[key] = variable
        return widget
