import tkinter as tk
from tkinter import ttk
import os
import sys

def set_autostart(enable):
    try:
        startup_dir = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
        batch_file = os.path.join(startup_dir, "Moupenix_Autostart.bat")
        
        if enable:
            if getattr(sys, "frozen", False):
                target = f'start "" "{sys.executable}"'
            else:
                main_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
                target = f'start pythonw "{main_py}"'
                
            with open(batch_file, "w", encoding="utf-8") as f:
                f.write(f"@echo off\n{target}\n")
        else:
            if os.path.exists(batch_file):
                os.remove(batch_file)
    except Exception as e:
        print("Erro ao configurar autostart:", e)

class ControlPanel(tk.Toplevel):
    def __init__(self, master, config, themes, on_config_change, on_toggle_pause, on_exit):
        super().__init__(master)
        self.cfg = config
        self.themes = themes
        self.on_config_change = on_config_change
        self.on_toggle_pause = on_toggle_pause
        self.on_exit = on_exit
        
        self.title("Moupenix - Painel de Controle")
        self.geometry("380x560")
        self.resizable(False, False)
        self.configure(bg="#1E1E2E")
        self.attributes("-topmost", True)
        
        # Intercepta o botão 'X' da janela para apenas minimizar/ocultar
        self.protocol("WM_DELETE_WINDOW", self.hide)
        
        self.create_widgets()
        
    def create_widgets(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # Cores e estilos modernos
        style.configure("TLabel", background="#1E1E2E", foreground="#CDD6F4", font=("Segoe UI", 9))
        style.configure("Title.TLabel", background="#1E1E2E", foreground="#F5C2E7", font=("Segoe UI", 14, "bold"))
        style.configure("Sub.TLabel", background="#1E1E2E", foreground="#A6ADC8", font=("Segoe UI", 8))
        style.configure("TCheckbutton", background="#1E1E2E", foreground="#CDD6F4", font=("Segoe UI", 9))
        style.configure("TCombobox", fieldbackground="#313244", background="#45475A", foreground="#CDD6F4")
        
        # Cabeçalho
        header = ttk.Label(self, text="🍆 Moupenix Settings", style="Title.TLabel")
        header.pack(pady=(15, 2))
        sub = ttk.Label(self, text="Ponteiro Animado Personalizado para Windows", style="Sub.TLabel")
        sub.pack(pady=(0, 15))
        
        frame = tk.Frame(self, bg="#1E1E2E", padx=20)
        frame.pack(fill="both", expand=True)
        
        # 1. Tamanho do Cursor
        ttk.Label(frame, text="Tamanho Base (Escala):").pack(anchor="w")
        self.scale_var = tk.DoubleVar(value=self.cfg.get("scale", 1.0))
        scale_slider = tk.Scale(
            frame, from_=0.5, to=2.2, resolution=0.1, orient="horizontal",
            variable=self.scale_var, command=self.update_values,
            bg="#313244", fg="#F5C2E7", highlightthickness=0, troughcolor="#45475A"
        )
        scale_slider.pack(fill="x", pady=(2, 10))
        
        # 2. Sensibilidade de Estiramento por Velocidade
        ttk.Label(frame, text="Alongamento por Velocidade:").pack(anchor="w")
        self.speed_var = tk.DoubleVar(value=self.cfg.get("speed_stretch", 1.5))
        speed_slider = tk.Scale(
            frame, from_=0.0, to=3.0, resolution=0.1, orient="horizontal",
            variable=self.speed_var, command=self.update_values,
            bg="#313244", fg="#F5C2E7", highlightthickness=0, troughcolor="#45475A"
        )
        speed_slider.pack(fill="x", pady=(2, 10))
        
        # 3. Alongamento ao Clicar / Segurar
        ttk.Label(frame, text="Alongamento ao Clicar (Hold):").pack(anchor="w")
        self.click_var = tk.DoubleVar(value=self.cfg.get("click_stretch", 1.4))
        click_slider = tk.Scale(
            frame, from_=1.0, to=2.5, resolution=0.1, orient="horizontal",
            variable=self.click_var, command=self.update_values,
            bg="#313244", fg="#F5C2E7", highlightthickness=0, troughcolor="#45475A"
        )
        click_slider.pack(fill="x", pady=(2, 10))
        
        # 4. Tema de Cores
        ttk.Label(frame, text="Tema Visual:").pack(anchor="w")
        self.theme_var = tk.StringVar(value=self.cfg.get("theme", "Cartoon Rosa"))
        theme_combo = ttk.Combobox(
            frame, textvariable=self.theme_var, values=list(self.themes.keys()), state="readonly"
        )
        theme_combo.pack(fill="x", pady=(2, 10))
        theme_combo.bind("<<ComboboxSelected>>", self.update_values)
        
        # 5. Checkboxes
        self.part_var = tk.BooleanVar(value=self.cfg.get("particles_enabled", True))
        chk_part = tk.Checkbutton(
            frame, text="Partículas / Gotículas ao soltar clique", variable=self.part_var,
            command=self.update_values, bg="#1E1E2E", fg="#CDD6F4", selectcolor="#313244",
            activebackground="#1E1E2E", activeforeground="#F5C2E7"
        )
        chk_part.pack(anchor="w", pady=(0, 5))
        
        self.sound_var = tk.BooleanVar(value=self.cfg.get("sound_effects", False))
        chk_sound = tk.Checkbutton(
            frame, text="Som cômico (Pop ao soltar clique)", variable=self.sound_var,
            command=self.update_values, bg="#1E1E2E", fg="#CDD6F4", selectcolor="#313244",
            activebackground="#1E1E2E", activeforeground="#F5C2E7"
        )
        chk_sound.pack(anchor="w", pady=(0, 5))

        self.autostart_var = tk.BooleanVar(value=self.cfg.get("autostart", False))
        chk_auto = tk.Checkbutton(
            frame, text="Iniciar automaticamente com o Windows", variable=self.autostart_var,
            command=self.update_values, bg="#1E1E2E", fg="#CDD6F4", selectcolor="#313244",
            activebackground="#1E1E2E", activeforeground="#F5C2E7"
        )
        chk_auto.pack(anchor="w", pady=(0, 5))

        self.hide_native_var = tk.BooleanVar(value=self.cfg.get("hide_native_cursor", False))
        chk_native = tk.Checkbutton(
            frame, text="Ocultar ponteiro original do Windows", variable=self.hide_native_var,
            command=self.update_values, bg="#1E1E2E", fg="#CDD6F4", selectcolor="#313244",
            activebackground="#1E1E2E", activeforeground="#F5C2E7"
        )
        chk_native.pack(anchor="w", pady=(0, 15))
        
        # Botões de Ação
        btn_frame = tk.Frame(frame, bg="#1E1E2E")
        btn_frame.pack(fill="x", pady=5)
        
        self.pause_btn = tk.Button(
            btn_frame, text="⏸ Pausar Cursor", command=self.on_toggle_pause,
            bg="#F38BA8", fg="#11111B", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=5
        )
        self.pause_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        hide_btn = tk.Button(
            btn_frame, text="👁 Ocultar Menu (F9)", command=self.hide,
            bg="#89B4FA", fg="#11111B", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=5
        )
        hide_btn.pack(side="right", expand=True, fill="x", padx=(5, 0))
        
        exit_btn = tk.Button(
            frame, text="🛑 Encerrar Moupenix (ESC)", command=self.on_exit,
            bg="#45475A", fg="#CDD6F4", font=("Segoe UI", 9), relief="flat", pady=5
        )
        exit_btn.pack(fill="x", pady=(10, 5))
        
        # Dicas de Teclado
        info = ttk.Label(
            frame, text="Atalhos: F9 (Menu) | ESC (Sair com segurança)", style="Sub.TLabel", justify="center"
        )
        info.pack(pady=(5, 0))

    def update_values(self, *args):
        self.cfg["scale"] = self.scale_var.get()
        self.cfg["speed_stretch"] = self.speed_var.get()
        self.cfg["click_stretch"] = self.click_var.get()
        self.cfg["theme"] = self.theme_var.get()
        self.cfg["particles_enabled"] = self.part_var.get()
        self.cfg["sound_effects"] = self.sound_var.get()
        self.cfg["autostart"] = self.autostart_var.get()
        self.cfg["hide_native_cursor"] = self.hide_native_var.get()
        set_autostart(self.cfg["autostart"])
        self.on_config_change(self.cfg)

    def toggle_pause_button(self, is_paused):
        if is_paused:
            self.pause_btn.config(text="▶ Retomar Cursor", bg="#A6E3A1")
        else:
            self.pause_btn.config(text="⏸ Pausar Cursor", bg="#F38BA8")

    def toggle_visibility(self):
        if self.state() == "normal":
            self.hide()
        else:
            self.show()

    def hide(self):
        self.withdraw()

    def show(self):
        self.deiconify()
        self.lift()
        self.focus_force()

