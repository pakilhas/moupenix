import math
import random
import time
import threading
import winsound

def play_cartoon_pop():
    try:
        winsound.Beep(650, 25)
        winsound.Beep(950, 30)
    except Exception:
        pass

class Particle:
    def __init__(self, x, y, vx, vy, color, radius=3.5, life=0.35):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.radius = radius
        self.max_life = life
        self.life = life

    def update(self, dt):
        self.life -= dt
        self.x += self.vx * (dt * 60)
        self.y += self.vy * (dt * 60)
        # Gravidade suave
        self.vy += 0.15 * (dt * 60)
        # Desaceleração
        self.vx *= 0.95
        self.vy *= 0.95
        # Reduz raio conforme vida acaba
        return self.life > 0

    def draw(self, canvas):
        if self.life <= 0:
            return
        r = self.radius * (self.life / self.max_life)
        if r > 0.5:
            canvas.create_oval(
                self.x - r, self.y - r, self.x + r, self.y + r,
                fill=self.color, outline="", tags="cursor_element"
            )

class CursorRenderer:
    def __init__(self, config, themes):
        self.cfg = config
        self.themes = themes
        
        # Dimensões base
        self.base_len = 55.0
        self.base_width = 22.0
        
        # Estado dinâmico
        self.curr_len = self.base_len
        self.len_vel = 0.0
        self.curr_width = self.base_width
        
        # Ângulo padrão (apontando para cima e esquerda ~-135 graus)
        self.default_angle = -math.pi * 0.75
        self.curr_angle = self.default_angle
        
        # Posições e velocidades
        self.prev_x = 0
        self.prev_y = 0
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 0.0
        
        # Inércia dos testículos (jiggle)
        self.ball_lag_x = 0.0
        self.ball_lag_y = 0.0
        
        # Detecção de agitação (shake)
        self.shake_history = []
        self.shake_wobble = 0.0
        
        # Cliques
        self.prev_lbutton = False
        self.prev_rbutton = False
        self.click_pulse_time = 0.0
        self.right_click_twitch = 0.0
        self.idle_time = 0.0
        
        # Partículas
        self.particles = []
        self.last_time = time.time()

    def update_physics(self, mouse_x, mouse_y, lbutton_down, rbutton_down):
        now = time.time()
        dt = max(0.001, min(0.05, now - self.last_time))
        self.last_time = now
        
        scale = self.cfg.get("scale", 1.0)
        target_base_len = self.base_len * scale
        target_base_width = self.base_width * scale
        
        # Cálculo de velocidade
        self.vx = mouse_x - self.prev_x
        self.vy = mouse_y - self.prev_y
        self.speed = math.hypot(self.vx, self.vy)
        
        # Modo ocioso (Idle breathing)
        if self.speed < 1.0 and not lbutton_down:
            self.idle_time += dt
        else:
            self.idle_time = 0.0
            
        # Reação ao botão direito (twitch / piscada rápida)
        if rbutton_down and not self.prev_rbutton:
            self.right_click_twitch = 0.35
        if self.right_click_twitch > 0:
            self.right_click_twitch -= dt
            
        # Detecção de agitação (mudanças rápidas de direção)
        if abs(self.vx) > 8:
            sign = 1 if self.vx > 0 else -1
            self.shake_history.append((now, sign))
        # Limpa histórico antigo (> 0.4s)
        self.shake_history = [(t, s) for t, s in self.shake_history if now - t < 0.4]
        
        reversals = 0
        for i in range(1, len(self.shake_history)):
            if self.shake_history[i][1] != self.shake_history[i-1][1]:
                reversals += 1
                
        is_shaking = reversals >= 4
        if is_shaking:
            self.shake_wobble = math.sin(now * 30.0) * (14.0 * scale)
        else:
            self.shake_wobble *= 0.8
            
        # Orientação e ângulo
        if self.speed > 4.0:
            target_angle = math.atan2(self.vy, self.vx)
            blend_speed = min(0.35, self.speed * 0.025)
        else:
            target_angle = self.default_angle
            blend_speed = 0.15
            
        # Se estiver em repouso > 1s, respira suavemente
        if self.idle_time > 1.0:
            breath = math.sin(self.idle_time * 2.5) * 0.08
            target_angle += breath
            
        # Twitch do botão direito
        if self.right_click_twitch > 0:
            target_angle += math.sin(self.right_click_twitch * 30.0) * 0.25
            
        # Interpolação angular suave (menor caminho)
        diff = (target_angle - self.curr_angle + math.pi) % (2 * math.pi) - math.pi
        self.curr_angle += diff * blend_speed
        
        # Estiramento por velocidade
        speed_factor = min(self.cfg.get("speed_stretch", 1.5), self.speed * 0.035)
        target_len = target_base_len * (1.0 + speed_factor)
        
        # Estiramento e pulsação por clique (quando pressionado)
        if lbutton_down:
            self.click_pulse_time += dt * 10.0
            click_mult = self.cfg.get("click_stretch", 1.4)
            pulse = math.sin(self.click_pulse_time) * (3.0 * scale)
            target_len = target_len * click_mult + pulse
            target_width = target_base_width * 1.15
        else:
            self.click_pulse_time = 0.0
            target_width = target_base_width
            
        # Inércia/Física de mola no comprimento
        k = self.cfg.get("elasticity", 0.25)
        self.len_vel += (target_len - self.curr_len) * k
        self.len_vel *= 0.72  # amortecimento
        self.curr_len += self.len_vel
        
        self.curr_width += (target_width - self.curr_width) * 0.2
        
        # Inércia dos testículos
        jiggle_intensity = self.cfg.get("jiggle_amount", 1.0)
        self.ball_lag_x += (-self.vx * 0.3 * jiggle_intensity - self.ball_lag_x) * 0.3
        self.ball_lag_y += (-self.vy * 0.3 * jiggle_intensity - self.ball_lag_y) * 0.3
        
        # Detecção de soltar o clique para disparar partículas
        theme_name = self.cfg.get("theme", "Cartoon Rosa")
        theme = self.themes.get(theme_name, self.themes["Cartoon Rosa"])
        
        if self.prev_lbutton and not lbutton_down:
            if self.cfg.get("sound_effects", False):
                threading.Thread(target=play_cartoon_pop, daemon=True).start()
                
            if self.cfg.get("particles_enabled", True):
                dir_x = math.cos(self.curr_angle)
            dir_y = math.sin(self.curr_angle)
            # Cria 5 gotículas animadas
            for _ in range(5):
                spread = random.uniform(-0.5, 0.5)
                p_speed = random.uniform(4.0, 9.0)
                p_vx = (dir_x + spread * (-dir_y)) * p_speed
                p_vy = (dir_y + spread * dir_x) * p_speed
                self.particles.append(Particle(
                    mouse_x, mouse_y, p_vx, p_vy,
                    color=theme["particle"],
                    radius=random.uniform(2.5, 4.5) * scale,
                    life=random.uniform(0.25, 0.45)
                ))
                
        self.prev_lbutton = lbutton_down
        self.prev_rbutton = rbutton_down
        self.prev_x = mouse_x
        self.prev_y = mouse_y
        
        # Atualiza partículas
        self.particles = [p for p in self.particles if p.update(dt)]

    def render(self, canvas, mouse_x, mouse_y):
        canvas.delete("cursor_element")
        
        theme_name = self.cfg.get("theme", "Cartoon Rosa")
        theme = self.themes.get(theme_name, self.themes["Cartoon Rosa"])
        
        # Vetor do ponteiro (da base para a ponta)
        dir_x = math.cos(self.curr_angle)
        dir_y = math.sin(self.curr_angle)
        
        # Vetor perpendicular
        perp_x = -dir_y
        perp_y = dir_x
        
        tip_x = mouse_x
        tip_y = mouse_y
        
        length = self.curr_len
        width = self.curr_width
        
        # Base (com efeito de wobble/agitação se houver)
        base_x = tip_x - dir_x * length + perp_x * self.shake_wobble
        base_y = tip_y - dir_y * length + perp_y * self.shake_wobble
        
        # Comprimento da cabeça (glande)
        head_len = min(length * 0.36, 26.0 * self.cfg.get("scale", 1.0))
        neck_x = tip_x - dir_x * head_len + perp_x * (self.shake_wobble * 0.4)
        neck_y = tip_y - dir_y * head_len + perp_y * (self.shake_wobble * 0.4)
        
        # 1. TESTÍCULOS (Desenhados atrás da haste)
        ball_r = width * 0.70
        ball_offset = width * 0.50
        
        # Posições com inércia (jiggle lag)
        b1_x = base_x + perp_x * ball_offset - dir_x * (ball_r * 0.25) + self.ball_lag_x
        b1_y = base_y + perp_y * ball_offset - dir_y * (ball_r * 0.25) + self.ball_lag_y
        
        b2_x = base_x - perp_x * ball_offset - dir_x * (ball_r * 0.25) + self.ball_lag_x
        b2_y = base_y - perp_y * ball_offset - dir_y * (ball_r * 0.25) + self.ball_lag_y
        
        # Testículo 1 (Esquerdo)
        canvas.create_oval(
            b1_x - ball_r, b1_y - ball_r, b1_x + ball_r, b1_y + ball_r,
            fill=theme["shaft"], outline=theme["outline"], width=2, tags="cursor_element"
        )
        # Ruguinhas sutis
        canvas.create_arc(
            b1_x - ball_r*0.6, b1_y - ball_r*0.6, b1_x + ball_r*0.6, b1_y + ball_r*0.6,
            start=45, extent=90, style="arc", outline=theme["wrinkle"], width=1.5, tags="cursor_element"
        )
        
        # Testículo 2 (Direito)
        canvas.create_oval(
            b2_x - ball_r, b2_y - ball_r, b2_x + ball_r, b2_y + ball_r,
            fill=theme["shaft"], outline=theme["outline"], width=2, tags="cursor_element"
        )
        canvas.create_arc(
            b2_x - ball_r*0.6, b2_y - ball_r*0.6, b2_x + ball_r*0.6, b2_y + ball_r*0.6,
            start=225, extent=90, style="arc", outline=theme["wrinkle"], width=1.5, tags="cursor_element"
        )
        
        # 2. HASTE (Corpo cilíndrico / shaft)
        sw = width * 0.50
        shaft_pts = [
            base_x + perp_x * sw, base_y + perp_y * sw,
            neck_x + perp_x * sw, neck_y + perp_y * sw,
            neck_x - perp_x * sw, neck_y - perp_y * sw,
            base_x - perp_x * sw, base_y - perp_y * sw
        ]
        canvas.create_polygon(
            shaft_pts, fill=theme["shaft"], outline=theme["outline"], width=2, tags="cursor_element"
        )
        
        # Veia animada / flexível na lateral da haste
        mid_x = (base_x + neck_x) * 0.5 + perp_x * (sw * 0.3 + math.sin(time.time() * 4) * 1.5)
        mid_y = (base_y + neck_y) * 0.5 + perp_y * (sw * 0.3 + math.sin(time.time() * 4) * 1.5)
        vein_pts = [
            base_x + perp_x * (sw * 0.1), base_y + perp_y * (sw * 0.1),
            mid_x, mid_y,
            neck_x - perp_x * (sw * 0.2), neck_y - perp_y * (sw * 0.2)
        ]
        canvas.create_line(
            vein_pts, smooth=True, fill=theme["vein"], width=1.8, tags="cursor_element"
        )
        
        # 3. CABEÇA / GLANDE (Formato anatômico/cartoon com crista coronal)
        hw = width * 0.68  # crista coronal mais larga que a haste
        mid_head_dist = head_len * 0.45
        mid_hx = tip_x - dir_x * mid_head_dist
        mid_hy = tip_y - dir_y * mid_head_dist
        
        head_pts = [
            neck_x + perp_x * hw, neck_y + perp_y * hw,            # crista esquerda
            mid_hx + perp_x * (hw * 0.95), mid_hy + perp_y * (hw * 0.95), # abaulado esquerdo
            tip_x, tip_y,                                         # PONTA EXATA (Hotspot de clique)
            mid_hx - perp_x * (hw * 0.95), mid_hy - perp_y * (hw * 0.95), # abaulado direito
            neck_x - perp_x * hw, neck_y - perp_y * hw,            # crista direita
            neck_x, neck_y                                        # centro base da cabeça
        ]
        canvas.create_polygon(
            head_pts, smooth=True, fill=theme["head"], outline=theme["outline"], width=2, tags="cursor_element"
        )
        
        # Fenda vertical na ponta (hotspot do cursor)
        slit_len = 5.0 * self.cfg.get("scale", 1.0)
        canvas.create_line(
            tip_x, tip_y,
            tip_x - dir_x * slit_len, tip_y - dir_y * slit_len,
            fill=theme["outline"], width=1.8, tags="cursor_element"
        )
        
        # 4. PARTÍCULAS
        for p in self.particles:
            p.draw(canvas)

