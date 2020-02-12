import logging
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from core.gui import appconfig
from core.gui.dialogs.dialog import Dialog
from core.gui.themes import FRAME_PAD, PADX, PADY, scale_fonts

if TYPE_CHECKING:
    from core.gui.app import Application

WIDTH = 1000
HEIGHT = 800


class PreferencesDialog(Dialog):
    def __init__(self, master: "Application", app: "Application"):
        super().__init__(master, app, "Preferences", modal=True)
        self.gui_scale = tk.DoubleVar(value=self.app.canvas.app_scale)
        preferences = self.app.guiconfig["preferences"]
        self.editor = tk.StringVar(value=preferences["editor"])
        self.theme = tk.StringVar(value=preferences["theme"])
        self.terminal = tk.StringVar(value=preferences["terminal"])
        self.gui3d = tk.StringVar(value=preferences["gui3d"])
        self.draw()

    def draw(self):
        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(0, weight=1)
        self.draw_preferences()
        self.draw_buttons()

    def draw_preferences(self):
        frame = ttk.LabelFrame(self.top, text="Preferences", padding=FRAME_PAD)
        frame.grid(sticky="nsew", pady=PADY)
        frame.columnconfigure(1, weight=1)

        label = ttk.Label(frame, text="Theme")
        label.grid(row=0, column=0, pady=PADY, padx=PADX, sticky="w")
        themes = self.app.style.theme_names()
        combobox = ttk.Combobox(
            frame, textvariable=self.theme, values=themes, state="readonly"
        )
        combobox.set(self.theme.get())
        combobox.grid(row=0, column=1, sticky="ew")
        combobox.bind("<<ComboboxSelected>>", self.theme_change)

        label = ttk.Label(frame, text="Editor")
        label.grid(row=1, column=0, pady=PADY, padx=PADX, sticky="w")
        combobox = ttk.Combobox(
            frame, textvariable=self.editor, values=appconfig.EDITORS, state="readonly"
        )
        combobox.grid(row=1, column=1, sticky="ew")

        label = ttk.Label(frame, text="Terminal")
        label.grid(row=2, column=0, pady=PADY, padx=PADX, sticky="w")
        combobox = ttk.Combobox(
            frame,
            textvariable=self.terminal,
            values=appconfig.TERMINALS,
            state="readonly",
        )
        combobox.grid(row=2, column=1, sticky="ew")

        label = ttk.Label(frame, text="3D GUI")
        label.grid(row=3, column=0, pady=PADY, padx=PADX, sticky="w")
        entry = ttk.Entry(frame, textvariable=self.gui3d)
        entry.grid(row=3, column=1, sticky="ew")

        label = ttk.Label(frame, text="Scaling")
        label.grid(row=4, column=0, pady=PADY, padx=PADX, sticky="w")

        scale_frame = ttk.Frame(frame)
        scale_frame.grid(row=4, column=1, sticky="ew")
        scale_frame.columnconfigure(0, weight=1)
        scale = ttk.Scale(
            scale_frame,
            from_=0.5,
            to=5,
            value=1,
            orient=tk.HORIZONTAL,
            variable=self.gui_scale,
            command=self.scale_adjust,
        )
        scale.grid(row=0, column=0, sticky="ew")
        entry = ttk.Entry(
            scale_frame, textvariable=self.gui_scale, width=4, state="disabled"
        )
        entry.grid(row=0, column=1)

    def draw_buttons(self):
        frame = ttk.Frame(self.top)
        frame.grid(sticky="ew")
        for i in range(2):
            frame.columnconfigure(i, weight=1)

        button = ttk.Button(frame, text="Save", command=self.click_save)
        button.grid(row=0, column=0, sticky="ew", padx=PADX)

        button = ttk.Button(frame, text="Cancel", command=self.destroy)
        button.grid(row=0, column=1, sticky="ew")

    def theme_change(self, event: tk.Event):
        theme = self.theme.get()
        logging.info("changing theme: %s", theme)
        self.app.style.theme_use(theme)

    def click_save(self):
        preferences = self.app.guiconfig["preferences"]
        preferences["terminal"] = self.terminal.get()
        preferences["editor"] = self.editor.get()
        preferences["gui3d"] = self.gui3d.get()
        preferences["theme"] = self.theme.get()
        self.app.save_config()
        self.destroy()

    def scale_adjust(self, scale: str):
        self.gui_scale.set(round(self.gui_scale.get(), 2))
        app_scale = self.gui_scale.get()
        self.app.canvas.app_scale = app_scale
        scale_fonts(self.app.fonts_size, app_scale)
        # screen_width = self.app.master.winfo_screenwidth()
        # screen_height = self.app.master.winfo_screenheight()
        # scaled_width = WIDTH * app_scale
        # scaled_height = HEIGHT * app_scale
        # x = int(screen_width / 2 - scaled_width / 2)
        # y = int(screen_height / 2 - scaled_height / 2)
        # self.app.master.geometry(f"{int(scaled_width)}x{int(scaled_height)}+{x}+{y}")
        #
        # self.app.toolbar.scale(app_scale)
