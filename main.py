import tkinter as tk
import win32api
import win32gui
import win32con
import ctypes
import atexit
import sys
import time

# Habilita DPI awareness para garantir precisão de pixel em monitores com escala (125%, 150%, 4K)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

from config import load_config, save_config, THEMES
from cursor_renderer import CursorRenderer
from cursor_hider import CursorHider
from control_panel import ControlPanel

class MoupenixApp:
    def __init__(self):
        self.cfg = load_config()
        self.themes = THEMES
        self.is_paused = False
        self.is_running = True
        
        # Virtual desktop bounds
        self.vx = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        self.vy = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
        self.vw = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        self.vh = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        
        # Criação da janela overlay transparente
        self.root = tk.Tk()
        self.root.title("Moupenix_Overlay")
        self.root.overrideredirect(True)
        self.root.geometry(f"{self.vw}x{self.vh}+{self.vx}+{self.vy}")
        self.root.attributes("-topmost", True)
        
        # Cor de transparência absoluta
        self.trans_color = "#010101"
        self.root.config(bg=self.trans_color)
        self.root.wm_attributes("-transparentcolor", self.trans_color)
        
        self.canvas = tk.Canvas(
            self.root, width=self.vw, height=self.vh,
            bg=self.trans_color, highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Aplica estilos Win32 para click-through total
        self.setup_click_through()
        
        # Ocultador de cursor e renderizador
        self.hider = CursorHider()
        self.renderer = CursorRenderer(self.cfg, self.themes)
        
        # Atualiza estado do cursor nativo se configurado
        if self.cfg.get("hide_native_cursor", False):
            self.hider.hide()
            
        # Painel de controle
        self.panel = ControlPanel(
            self.root, self.cfg, self.themes,
            on_config_change=self.on_config_change,
            on_toggle_pause=self.toggle_pause,
            on_exit=self.exit_app
        )
        
        # Estado de hotkeys para evitar disparos repetidos instantâneos
        self.last_f9_press = 0.0
        self.last_esc_press = 0.0
        
        atexit.register(self.cleanup)
        
        # Inicia loop de renderização (~60 FPS)
        self.root.after(16, self.loop)

    def setup_click_through(self):
        try:
            self.root.update()
            hwnd = win32gui.GetParent(self.root.winfo_id())
            if hwnd == 0:
                hwnd = self.root.winfo_id()
                
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(
                hwnd, win32con.GWL_EXSTYLE,
                ex_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT |
                win32con.WS_EX_TOOLWINDOW | win32con.WS_EX_NOACTIVATE
            )
        except Exception as e:
            print("Erro ao configurar click-through:", e)

    def on_config_change(self, new_cfg):
        self.cfg = new_cfg
        save_config(self.cfg)
        
        if self.cfg.get("hide_native_cursor", False):
            self.hider.hide()
        else:
            self.hider.restore()

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.panel.toggle_pause_button(self.is_paused)
        if self.is_paused:
            self.canvas.delete("cursor_element")
            self.hider.restore()
        else:
            if self.cfg.get("hide_native_cursor", False):
                self.hider.hide()

    def loop(self):
        if not self.is_running:
            return
            
        now = time.time()
        
        # Atalho F9: Abrir/Fechar Menu de Configurações
        if win32api.GetAsyncKeyState(win32con.VK_F9) & 0x8000:
            if now - self.last_f9_press > 0.35:
                self.last_f9_press = now
                self.panel.toggle_visibility()
                
        # Atalho ESC: Sair do programa com segurança (somente se painel estiver visível ou apertar intencionalmente)
        if win32api.GetAsyncKeyState(win32con.VK_ESCAPE) & 0x8000:
            if self.panel.state() == "normal":
                self.panel.hide()
                time.sleep(0.15)
                
        if not self.is_paused:
            try:
                # Posição global do mouse
                mx, my = win32api.GetCursorPos()
                
                # Ajusta para coordenadas relativas da janela/canvas
                cx = mx - self.vx
                cy = my - self.vy
                
                # Estado dos botões do mouse
                l_down = (win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000) != 0
                r_down = (win32api.GetAsyncKeyState(win32con.VK_RBUTTON) & 0x8000) != 0
                
                # Física e Renderização
                self.renderer.update_physics(cx, cy, l_down, r_down)
                self.renderer.render(self.canvas, cx, cy)
                
            except Exception as e:
                pass
                
        # Reagenda próximo quadro (~16ms = 60 FPS)
        self.root.after(16, self.loop)

    def cleanup(self):
        self.hider.restore()
        save_config(self.cfg)

    def exit_app(self):
        self.is_running = False
        self.cleanup()
        try:
            self.root.destroy()
        except Exception:
            pass
        sys.exit(0)

    def run(self):
        try:
            self.root.mainloop()
        finally:
            self.cleanup()

if __name__ == "__main__":
    app = MoupenixApp()
    app.run()

