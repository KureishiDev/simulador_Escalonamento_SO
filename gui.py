import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageGrab
from simulator import Simulator
import webbrowser

THEMES = {
    "dark": {
        "header_footer": "#23272A",
        "background": "#2C2F33",
        "canvas_bg": "#36393F",
        "text": "#FFFFFF",
        "text_axes": "#99AAB5",
        "button": "#40444B",
        "button_active": "#5C6067",
        "title_bar_mode": 1,
    },
    "light": {
        "header_footer": "#E3E5E8",
        "background": "#FFFFFF",
        "canvas_bg": "#F8F9F9",
        "text": "#060607",
        "text_axes": "#5C6773",
        "button": "#E3E5E8",
        "button_active": "#B9BBBE",
        "title_bar_mode": 0,
    },
}

TICK_WIDTH, BAR_HEIGHT, Y_OFFSET, X_OFFSET = 30, 40, 70, 60
HEADER_HEIGHT, FOOTER_HEIGHT, CANVAS_PADDING_Y = 60, 80, 10


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.id = None
        self.widget.bind("<Enter>", self.schedule_tip)
        self.widget.bind("<Leave>", self.hide_tip)
        self.widget.bind("<ButtonPress>", self.hide_tip)

    def show_tip(self):
        if self.tooltip_window or not self.widget.winfo_exists():
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", "9", "normal"),
        )
        label.pack(ipadx=1)
        self.tooltip_window.label = label

    def hide_tip(self, event=None):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

    def schedule_tip(self, event=None):
        self.hide_tip()
        self.id = self.widget.after(500, self.show_tip)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class AppGUI:
    def __init__(self, master):
        self.master = master
        self.simulator = None
        self.is_running = False
        self.task_y_positions = {}
        self.is_dark_theme = tk.BooleanVar(value=False)

        self.github_icon_light_tk = None
        self.github_icon_dark_tk = None
        self.book_icon_tk = None
        self.logo_tk = None

        self.base_title = "Simulador Interativo de Escalonamento de Processos"
        master.title(self.base_title)
        master.geometry("1200x800")
        master.resizable(True, True)
        self.style = ttk.Style(master)
        self.style.theme_use("alt")
        self.header_frame = ttk.Frame(self.master, height=HEADER_HEIGHT)
        self.header_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
        self.control_frame = ttk.Frame(self.master, padding=10)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, expand=False, pady=(0, 5))

        self.main_content_frame = ttk.Frame(self.master)
        self.main_content_frame.pack(
            side=tk.TOP, fill=tk.BOTH, expand=True, pady=CANVAS_PADDING_Y, padx=10
        )

        self.canvas_frame = ttk.Frame(self.main_content_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.legend_frame = ttk.Frame(self.main_content_frame, padding=(10, 5))
        self.legend_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))

        self.footer_frame = ttk.Frame(self.master, height=FOOTER_HEIGHT)
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=False)
        self._setup_header()
        self._setup_widgets()
        self._setup_footer()
        self._apply_theme()

    def _apply_theme(self):
        theme = "dark" if self.is_dark_theme.get() else "light"
        colors = THEMES[theme]
        self.style.configure(
            ".", background=colors["background"], foreground=colors["text"]
        )
        self.style.configure("TFrame", background=colors["background"])
        self.style.configure(
            "TLabel", background=colors["background"], foreground=colors["text"]
        )
        self.style.configure(
            "TButton",
            font=("Segoe UI", 10, "normal"),
            padding=(10, 5),
            background=colors["button"],
            foreground=colors["text"],
            borderwidth=0,
            focusthickness=0,
        )
        self.style.map("TButton", background=[("active", colors["button_active"])])
        self.master.configure(bg=colors["background"])
        self.header_frame.configure(style="Header.TFrame")
        self.style.configure("Header.TFrame", background=colors["header_footer"])
        self.footer_frame.configure(style="Footer.TFrame")
        self.style.configure("Footer.TFrame", background=colors["header_footer"])
        self.legend_frame.configure(style="Legend.TFrame")
        self.style.configure("Legend.TFrame", background=colors["header_footer"])
        self.header_label.configure(
            background=colors["header_footer"], foreground=colors["text"]
        )
        self.footer_label.configure(
            background=colors["header_footer"], foreground=colors["text"]
        )

        self.style.configure(
            "Treeview",
            background=colors["canvas_bg"],
            foreground=colors["text"],
            fieldbackground=colors["canvas_bg"],
            borderwidth=0,
        )
        self.style.configure(
            "Treeview.Heading",
            background=colors["button"],
            foreground=colors["text"],
            padding=5,
            font=("Segoe UI", 10, "bold"),
        )
        self.style.map(
            "Treeview.Heading", background=[("active", colors["button_active"])]
        )

        if hasattr(self, "logo_label") and self.logo_label:
            self.logo_label.configure(bg=colors["header_footer"])

        if hasattr(self, "github_icon_label"):
            self.github_icon_label.configure(bg=colors["header_footer"])
            if self.is_dark_theme.get():
                self.github_icon_label.config(image=self.github_icon_light_tk)
            else:
                self.github_icon_label.config(image=self.github_icon_dark_tk)

        if hasattr(self, "book_icon_label"):
            self.book_icon_label.configure(bg=colors["header_footer"])

        if hasattr(self, "canvas"):
            self.canvas.configure(bg=colors["canvas_bg"])
            self._draw_axes()

        self._set_title_bar_theme(colors["title_bar_mode"])

    def _setup_header(self):
        self.header_frame.grid_rowconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=2)
        self.header_frame.grid_columnconfigure(2, weight=1)

        left_icons_frame = ttk.Frame(self.header_frame, style="Header.TFrame")
        left_icons_frame.grid(row=0, column=0, sticky="nsw")

        center_title_frame = ttk.Frame(self.header_frame, style="Header.TFrame")
        center_title_frame.grid(row=0, column=1, sticky="nsew")

        right_empty_frame = ttk.Frame(self.header_frame, style="Header.TFrame")
        right_empty_frame.grid(row=0, column=2, sticky="nse")

        try:
            img_light = Image.open(resource_path("github-mark-white.png")).resize(
                (32, 32), Image.Resampling.LANCZOS
            )
            img_dark = Image.open(resource_path("github-mark.png")).resize(
                (32, 32), Image.Resampling.LANCZOS
            )
            self.github_icon_light_tk = ImageTk.PhotoImage(img_light)
            self.github_icon_dark_tk = ImageTk.PhotoImage(img_dark)
            self.github_icon_label = tk.Label(left_icons_frame, cursor="hand2")
            self.github_icon_label.image = self.github_icon_dark_tk
            self.github_icon_label.pack(side=tk.LEFT, padx=10, pady=10)
            self.github_icon_label.bind("<Button-1>", self._open_github_link)
            Tooltip(self.github_icon_label, "Abre o perfil do desenvolvedor no GitHub")
        except Exception as e:
            print(f"Erro ao carregar ícones do GitHub: {e}")

        try:
            img_book = Image.open(resource_path("todos.png")).resize(
                (32, 32), Image.Resampling.LANCZOS
            )
            photo_book = ImageTk.PhotoImage(img_book)
            self.book_icon_label = tk.Label(
                left_icons_frame, image=photo_book, cursor="hand2"
            )
            self.book_icon_label.image = photo_book
            self.book_icon_label.pack(side=tk.LEFT, padx=10, pady=10)
            self.book_icon_label.bind("<Button-1>", self._open_book_link)
            Tooltip(self.book_icon_label, "Abrir PDF de referência sobre escalonamento")
        except Exception as e:
            print(f"Erro ao carregar ícone do livro: {e}")

        header_text = "Ferramenta para Simulação e Análise Visual de Algoritmos de Escalonamento de Processos"
        self.header_label = ttk.Label(
            center_title_frame,
            text=header_text,
            font=("Segoe UI", 16, "bold"),
            anchor="center",
        )
        self.header_label.pack(expand=True, fill=tk.BOTH)

    def _setup_widgets(self):
        button_container = ttk.Frame(self.control_frame)
        button_container.pack()
        self.btn_load = ttk.Button(
            button_container,
            text="Carregar Arquivo...",
            command=self._load_file_clicked,
        )
        self.btn_load.pack(side=tk.LEFT, padx=5)
        Tooltip(self.btn_load, "Carrega um novo arquivo de simulação (.txt)")

        self.btn_show_data = ttk.Button(
            button_container,
            text="Ver Dados do Arquivo",
            command=self._show_data_dialog,
            state="disabled",
        )
        self.btn_show_data.pack(side=tk.LEFT, padx=5)
        Tooltip(
            self.btn_show_data,
            "Mostra os dados de entrada do arquivo de simulação carregado",
        )

        self.btn_next_step = ttk.Button(
            button_container,
            text="Próximo Passo",
            command=self._next_step_clicked,
            state="disabled",
        )
        self.btn_next_step.pack(side=tk.LEFT, padx=5)
        Tooltip(self.btn_next_step, "Avança a simulação em um único tick de tempo")
        self.btn_run_all = ttk.Button(
            button_container,
            text="Executar Tudo",
            command=self._run_all_clicked,
            state="disabled",
        )
        self.btn_run_all.pack(side=tk.LEFT, padx=5)
        Tooltip(self.btn_run_all, "Inicia ou para a execução automática da simulação")
        self.btn_save = ttk.Button(
            button_container,
            text="Salvar Imagem",
            command=self._save_canvas_as_image,
            state="disabled",
        )
        self.btn_save.pack(side=tk.LEFT, padx=5)
        Tooltip(self.btn_save, "Salva o gráfico de Gantt atual como uma imagem PNG")

        self.lbl_tick = ttk.Label(
            self.control_frame, text="Tick: --", font=("Segoe UI", 12)
        )
        self.lbl_tick.pack(side=tk.RIGHT, padx=20)
        self.lbl_algorithm = ttk.Label(
            self.control_frame, text="Algoritmo: --", font=("Segoe UI", 12)
        )
        self.lbl_algorithm.pack(side=tk.RIGHT, padx=20)
        self.canvas = tk.Canvas(
            self.canvas_frame, scrollregion=(0, 0, 5000, 2000), highlightthickness=0
        )
        hbar = ttk.Scrollbar(
            self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview
        )
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        vbar = ttk.Scrollbar(
            self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview
        )
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    def _setup_footer(self):
        left_footer = ttk.Frame(self.footer_frame, style="Footer.TFrame")
        center_footer = ttk.Frame(self.footer_frame, style="Footer.TFrame")
        right_footer = ttk.Frame(self.footer_frame, style="Footer.TFrame")

        left_footer.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0))
        right_footer.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10))
        center_footer.pack(expand=True, fill=tk.BOTH)

        self.theme_button = ttk.Button(
            left_footer, text="Ativar Modo Noturno", command=self._toggle_theme
        )
        self.theme_button.pack(expand=True, padx=10)
        Tooltip(self.theme_button, "Alterna entre o tema claro e o escuro")

        center_content = ttk.Frame(center_footer, style="Footer.TFrame")
        center_content.pack(expand=True)

        logo_path = resource_path("logo_utf.png")
        if os.path.exists(logo_path):
            try:
                logo_image = Image.open(logo_path)
                h, w = 50, int((50 / logo_image.height) * logo_image.width)
                logo_image = logo_image.resize((w, h), Image.Resampling.LANCZOS)
                self.logo_tk = ImageTk.PhotoImage(logo_image)
                self.logo_label = tk.Label(center_content, image=self.logo_tk)
                self.logo_label.image = self.logo_tk
                self.logo_label.pack(side=tk.LEFT, padx=10, pady=5)
            except Exception as e:
                print(f"Erro ao carregar a logo: {e}")

        footer_text = (
            "Simulador de Escalonamento v1.5 | 2025 Vinicius Wandembruck | Licença MIT"
        )
        self.footer_label = ttk.Label(
            center_content, text=footer_text, font=("Segoe UI", 10)
        )
        self.footer_label.pack(side=tk.LEFT, padx=10)

        self.btn_about = ttk.Button(
            right_footer, text="Sobre", command=self._show_about_dialog
        )
        self.btn_about.pack(expand=True, padx=10)
        Tooltip(self.btn_about, "Exibe informações sobre o projeto e referências")

    def _open_github_link(self, event=None):
        url = "https://github.com/KureishiDev"
        webbrowser.open_new_tab(url)

    def _open_book_link(self, event=None):
        url = (
            "https://wiki.inf.ufpr.br/maziero/lib/exe/fetch.php?media=socm:socm-06.pdf"
        )
        webbrowser.open_new_tab(url)

    def _set_title_bar_theme(self, theme_mode):
        try:
            import ctypes
            from sys import getwindowsversion

            self.master.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.master.winfo_id())
            if getwindowsversion().build >= 17763:
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                value = ctypes.c_int(theme_mode)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    DWMWA_USE_IMMERSIVE_DARK_MODE,
                    ctypes.byref(value),
                    ctypes.sizeof(value),
                )
        except Exception:
            pass

    def _toggle_theme(self):
        self.is_dark_theme.set(not self.is_dark_theme.get())
        if self.is_dark_theme.get():
            self.theme_button.config(text="Ativar Modo Claro")
        else:
            self.theme_button.config(text="Ativar Modo Noturno")
        self._apply_theme()

    def _show_data_dialog(self):
        if not self.simulator or not self.simulator.original_task_list:
            messagebox.showinfo("Informação", "Nenhum dado de simulação carregado.")
            return

        data_window = tk.Toplevel(self.master)
        data_window.title("Dados do Arquivo de Simulação")
        data_window.geometry("650x400")
        data_window.transient(self.master)
        data_window.grab_set()

        theme = "dark" if self.is_dark_theme.get() else "light"
        colors = THEMES[theme]
        data_window.configure(bg=colors["background"])

        top_frame = ttk.Frame(data_window, padding=(10, 10, 10, 0))
        top_frame.pack(fill="x")

        info_text = f"Algoritmo: {self.simulator.scheduling_algorithm_name}  |  Quantum: {self.simulator.quantum}"
        ttk.Label(top_frame, text=info_text, font=("Segoe UI", 12, "bold")).pack()

        table_frame = ttk.Frame(data_window, padding=(10, 10, 10, 5))
        table_frame.pack(expand=True, fill="both")

        columns = ("id", "color", "arrival", "duration", "priority")
        tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", style="Treeview"
        )

        tree.heading("id", text="ID da Tarefa")
        tree.heading("color", text="Cor")
        tree.heading("arrival", text="Ingresso (Tick)")
        tree.heading("duration", text="Duração")
        tree.heading("priority", text="Prioridade")

        tree.column("id", width=100, anchor=tk.CENTER)
        tree.column("color", width=100, anchor=tk.CENTER)
        tree.column("arrival", width=110, anchor=tk.CENTER)
        tree.column("duration", width=100, anchor=tk.CENTER)
        tree.column("priority", width=100, anchor=tk.CENTER)

        for task in self.simulator.original_task_list:
            tree.insert(
                "",
                tk.END,
                values=(
                    task.task_id,
                    task.color,
                    task.arrival_time,
                    task.duration,
                    task.priority,
                ),
            )

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(data_window, padding=(10, 5, 10, 10))
        button_frame.pack(fill="x")
        ok_button = ttk.Button(
            button_frame, text="OK", command=data_window.destroy, style="TButton"
        )
        ok_button.pack()

    def _show_about_dialog(self):
        about_window = tk.Toplevel(self.master)
        about_window.title("Sobre este Programa")
        about_window.geometry("550x250")
        about_window.resizable(False, False)
        about_window.transient(self.master)
        about_window.grab_set()
        theme = "dark" if self.is_dark_theme.get() else "light"
        colors = THEMES[theme]
        about_window.configure(bg=colors["background"])
        about_text = (
            "Referência principal para a confecção dos algoritmos:\n"
            "Sistemas Operacionais: Conceitos e Mecanismos\n"
            "Autor: Prof. Carlos A. Maziero (DINF - UFPR)\n\n"
            "Este projeto foi desenvolvido sob a tutela do\n"
            "Prof. Marco Aurélio Wehrmeister que ministrou a\n"
            "disciplina de Sistemas Operacionais em 2025/2."
        )
        content_frame = ttk.Frame(about_window, padding=20, style="About.TFrame")
        self.style.configure("About.TFrame", background=colors["background"])
        content_frame.pack(expand=True, fill=tk.BOTH)
        ttk.Label(
            content_frame, text=about_text, justify=tk.LEFT, font=("Segoe UI", 11)
        ).pack(pady=10)
        ok_button = ttk.Button(content_frame, text="OK", command=about_window.destroy)
        ok_button.pack(pady=(10, 0))
        self.master.update_idletasks()
        master_x, master_y, master_w, master_h = (
            self.master.winfo_x(),
            self.master.winfo_y(),
            self.master.winfo_width(),
            self.master.winfo_height(),
        )
        win_w, win_h = about_window.winfo_width(), about_window.winfo_height()
        x, y = master_x + (master_w - win_w) // 2, master_y + (master_h - win_h) // 2
        about_window.geometry(f"+{x}+{y}")

    def _load_file_clicked(self):
        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo de configuração",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os arquivos", "*.*")],
        )
        if not file_path:
            return
        self._reset_simulation_gui()
        self.simulator = Simulator(file_path)
        self.btn_next_step.config(state="normal")
        self.btn_run_all.config(state="normal")
        self.btn_show_data.config(state="normal")
        self.btn_save.config(state="disabled")
        filename = os.path.basename(file_path)
        self.master.title(f"{self.base_title} - [{filename}]")
        self.lbl_tick.config(text="Tick: 0")
        algo_name = self.simulator.scheduling_algorithm_name
        self.lbl_algorithm.config(text=f"Algoritmo: {algo_name}")

    def _reset_simulation_gui(self):
        self.is_running = False
        self.task_y_positions = {}
        self.canvas.delete("all")
        for widget in self.legend_frame.winfo_children():
            widget.destroy()
        self._draw_axes()
        self.btn_run_all.config(text="Executar Tudo")
        if hasattr(self, "btn_show_data"):
            self.btn_show_data.config(state="disabled")
        self.lbl_tick.config(text="Tick: --")
        self.lbl_algorithm.config(text="Algoritmo: --")

    def _draw_axes(self):
        self.canvas.delete("axes")
        theme = "dark" if self.is_dark_theme.get() else "light"
        colors = THEMES[theme]
        axis_color = colors["text_axes"]

        self.canvas.create_line(
            X_OFFSET,
            Y_OFFSET - 20,
            5000,
            Y_OFFSET - 20,
            arrow=tk.LAST,
            fill=axis_color,
            tags="axes",
        )
        self.canvas.create_text(
            X_OFFSET + 40,
            Y_OFFSET - 35,
            text="Tempo (ticks)",
            fill=axis_color,
            font=("Segoe UI", 9),
            tags="axes",
        )
        for i in range(0, 151):
            x = X_OFFSET + i * TICK_WIDTH
            self.canvas.create_line(
                x, Y_OFFSET - 25, x, Y_OFFSET - 15, fill=axis_color, tags="axes"
            )
            if i % 5 == 0:
                self.canvas.create_text(
                    x,
                    Y_OFFSET - 35,
                    text=str(i),
                    font=("Segoe UI", 8),
                    fill=axis_color,
                    tags="axes",
                )

        self.canvas.create_line(
            X_OFFSET,
            Y_OFFSET - 20,
            X_OFFSET,
            2000,
            arrow=tk.LAST,
            fill=axis_color,
            tags="axes",
        )
        self.canvas.create_text(
            X_OFFSET - 30,
            Y_OFFSET - 10,
            text="Tarefas",
            angle=90,
            anchor="w",
            fill=axis_color,
            font=("Segoe UI", 9),
            tags="axes",
        )

    def _draw_gantt_bar(self, current_tick, task):
        theme = "dark" if self.is_dark_theme.get() else "light"
        colors = THEMES[theme]
        if task.task_id not in self.task_y_positions:
            next_y_pos = len(self.task_y_positions)
            self.task_y_positions[task.task_id] = next_y_pos

            legend_item_frame = ttk.Frame(self.legend_frame, style="Legend.TFrame")
            legend_item_frame.pack(side=tk.LEFT, padx=10)

            color_box = tk.Frame(legend_item_frame, width=20, height=20, bg=task.color)
            color_box.pack(side=tk.LEFT)

            task_label = ttk.Label(
                legend_item_frame, text=f"- {task.task_id}", style="Legend.TLabel"
            )
            self.style.configure(
                "Legend.TLabel",
                background=colors["header_footer"],
                foreground=colors["text"],
            )
            task_label.pack(side=tk.LEFT, padx=(5, 0))

        y0 = Y_OFFSET + self.task_y_positions[task.task_id] * (BAR_HEIGHT + 5)
        y1 = y0 + BAR_HEIGHT
        x0 = X_OFFSET + (current_tick - 1) * TICK_WIDTH
        x1 = x0 + TICK_WIDTH
        self.canvas.create_rectangle(
            x0, y0, x1, y1, fill=task.color, outline=colors["background"]
        )

    def _update_gui(self, task_that_ran):
        if not self.simulator:
            return
        current_tick = self.simulator.global_tick
        self.lbl_tick.config(text=f"Tick: {current_tick}")
        if task_that_ran:
            self._draw_gantt_bar(current_tick, task_that_ran)

    def _run_simulation_step(self):
        if not self.simulator:
            return False
        task_that_ran = self.simulator.tick()
        is_complete = self.simulator._is_simulation_complete()
        self._update_gui(task_that_ran)
        if is_complete:
            self.btn_next_step.config(state="disabled")
            self.btn_run_all.config(text="Finalizado", state="disabled")
            self.btn_save.config(state="normal")
            self.is_running = False
            return False
        return True

    def _save_canvas_as_image(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG file", "*.png"), ("All files", "*.*")],
            )
            if not file_path:
                return

            # Pega as coordenadas da área que inclui o Canvas E a Legenda
            x0_main = self.master.winfo_rootx() + self.main_content_frame.winfo_x()
            y0_main = self.master.winfo_rooty() + self.main_content_frame.winfo_y()
            x1_main = x0_main + self.main_content_frame.winfo_width()
            y1_main = y0_main + self.main_content_frame.winfo_height()

            # Garante que a interface esteja atualizada antes de capturar
            self.master.update_idletasks()

            ImageGrab.grab(bbox=(x0_main, y0_main, x1_main, y1_main)).save(file_path)
            print(f"Imagem salva em: {file_path}")
        except Exception as e:
            print(f"Erro ao salvar a imagem: {e}")
            messagebox.showerror(
                "Erro ao Salvar", f"Não foi possível salvar a imagem.\nDetalhe: {e}"
            )

    def _next_step_clicked(self):
        self.is_running = False
        self.btn_run_all.config(text="Executar Tudo")
        self._run_simulation_step()

    def _run_all_clicked(self):
        if self.is_running:
            self.is_running = False
            self.btn_run_all.config(text="Executar Tudo")
        else:
            if not self.simulator:
                messagebox.showwarning(
                    "Aviso", "Por favor, carregue um arquivo de simulação primeiro."
                )
                return
            self.is_running = True
            self.btn_run_all.config(text="Parar")
            self._run_loop()

    def _run_loop(self):
        if self.is_running:
            if self._run_simulation_step():
                self.master.after(200, self._run_loop)
            else:
                self.btn_run_all.config(text="Finalizado")

    def start(self):
        self.master.mainloop()
