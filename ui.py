import tkinter as tk
import asyncio
import threading

# Importa os módulos do assistente
from app.recorder import gravar_audio
from app.transcriber import transcrever_audio
from app.brain import perguntar_ia
from app.speaker import gerar_e_tocar

# ── Paleta ────────────────────────────────────────────────────────────────────
BG           = "#161210"
SURFACE      = "#2e2822"
SURFACE2     = "#26201a"
BORDER       = "#4a4038"

BUBBLE_USER  = "#bf6c3a"
BUBBLE_IA    = "#242018"

TEXT_USER    = "#fef3e8"
TEXT_IA      = "#ddd0be"
TEXT_SYS     = "#4a4035"

TEXT         = "#cfc3b0"
TEXT_DIM     = "#7a6f62"
MUTED        = "#42392e"
ACCENT       = "#d4915a"

GREEN        = "#6dab78"
RED          = "#c94040"
AMBER        = "#d4910a"

BTN_IDLE_BG  = "#bf6c3a"
BTN_IDLE_FG  = "#fef3e8"
BTN_REC_BG   = "#c94040"
BTN_REC_FG   = "#ffffff"
BTN_PROC_BG  = "#2e2820"
BTN_PROC_FG  = "#d4910a"

FONT_UI_SM   = ("Segoe UI", 8)
FONT_TITLE   = ("Segoe UI", 16, "bold")
FONT_SUB     = ("Segoe UI", 8)
FONT_BTN     = ("Segoe UI", 10, "bold")
FONT_BUBBLE  = ("Segoe UI", 10)
FONT_LABEL   = ("Segoe UI", 7)


def rounded_rect(canvas, x1, y1, x2, y2, r, **kw):
    canvas.create_arc(x1,     y1,     x1+2*r, y1+2*r, start=90,  extent=90,  style="pieslice", **kw)
    canvas.create_arc(x2-2*r, y1,     x2,     y1+2*r, start=0,   extent=90,  style="pieslice", **kw)
    canvas.create_arc(x1,     y2-2*r, x1+2*r, y2,     start=180, extent=90,  style="pieslice", **kw)
    canvas.create_arc(x2-2*r, y2-2*r, x2,     y2,     start=270, extent=90,  style="pieslice", **kw)
    canvas.create_rectangle(x1+r, y1,   x2-r, y2,   **kw)
    canvas.create_rectangle(x1,   y1+r, x2,   y2-r, **kw)


class TypingIndicator(tk.Frame):
    def __init__(self, parent, **kwargs):
        self.bg_color  = kwargs.get('bg', BUBBLE_IA)
        self.dot_color = ACCENT
        self.dot_dim   = TEXT_DIM

        super().__init__(parent, bg=SURFACE)

        # Label remetente igual aos balões
        tk.Label(self, text="voci", font=FONT_LABEL, fg=MUTED, bg=SURFACE).pack(anchor="w", padx=18, pady=(0, 1))

        # Balão arredondado via canvas
        cw, ch, r = 72, 38, 14
        c = tk.Canvas(self, width=cw, height=ch, bg=SURFACE, highlightthickness=0, bd=0)
        c.pack(anchor="w", padx=10, pady=(0, 2))
        rounded_rect(c, 1, 1, cw - 1, ch - 1, r, fill=self.bg_color, outline="")

        # Pontinhos dentro do canvas
        dots_frame = tk.Frame(c, bg=self.bg_color)
        c.create_window(cw // 2, ch // 2, window=dots_frame)

        self.dots = []
        for _ in range(3):
            d = tk.Label(dots_frame, text="●", font=("Segoe UI", 11),
                         fg=self.dot_dim, bg=self.bg_color)
            d.pack(side="left", padx=2)
            self.dots.append(d)

        self.animating   = False
        self.current_dot = 0

    def start(self):
        self.animating   = True
        self.current_dot = 0
        self._animate()

    def _animate(self):
        if not self.animating:
            return
        for d in self.dots:
            d.config(fg=self.dot_dim)
        self.dots[self.current_dot].config(fg=self.dot_color)
        self.current_dot = (self.current_dot + 1) % 3
        self.after(500, self._animate)

    def stop(self):
        self.animating = False
        self.destroy()


class BubbleMessage(tk.Frame):
    def __init__(self, parent, text, side, bg_color, fg_color, label, **kwargs):
        super().__init__(parent, bg=SURFACE, **kwargs)

        MAX_W    = 270
        PAD_X    = 14
        PAD_Y    = 9
        RADIUS   = 14

        # Label remetente
        tk.Label(
            self, text=label,
            font=FONT_LABEL, fg=MUTED, bg=SURFACE,
        ).pack(anchor="e" if side == "right" else "w", padx=PAD_X + 4, pady=(0, 1))

        # Medir dimensões necessárias
        probe = tk.Label(self, text=text, font=FONT_BUBBLE, wraplength=MAX_W, justify="left")
        probe.update_idletasks()
        tw = min(probe.winfo_reqwidth(), MAX_W)
        th = probe.winfo_reqheight()
        probe.destroy()

        cw = tw + PAD_X * 2
        ch = th + PAD_Y * 2

        c = tk.Canvas(self, width=cw, height=ch, bg=SURFACE, highlightthickness=0, bd=0)
        c.pack(anchor="e" if side == "right" else "w", padx=10, pady=(0, 2))

        rounded_rect(c, 1, 1, cw - 1, ch - 1, RADIUS, fill=bg_color, outline="")

        inner = tk.Label(
            c, text=text,
            font=FONT_BUBBLE,
            fg=fg_color, bg=bg_color,
            wraplength=MAX_W,
            justify="left",
            padx=PAD_X, pady=PAD_Y,
        )
        c.create_window(cw // 2, ch // 2, window=inner)


class VoiceAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voci")
        self.root.configure(bg=BG)
        self.root.geometry("460x720")
        self.root.minsize(380, 560)

        self.recording  = False
        self._pulse_job = None
        self._pulse_on  = False
        self._dot_idx   = 0

        self._typing = None

        self._build_ui()
        self._animate_online()

    def _build_ui(self):
        # ── Header ────────────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=24, pady=(22, 0))

        # Avatar circular (simulado com frame quadrado)
        av = tk.Frame(header, bg=ACCENT, width=42, height=42)
        av.pack(side="left")
        av.pack_propagate(False)
        tk.Label(av, text="V", font=("Segoe UI", 17, "bold"), fg=BG, bg=ACCENT).place(relx=.5, rely=.5, anchor="center")

        info = tk.Frame(header, bg=BG)
        info.pack(side="left", padx=(12, 0))
        tk.Label(info, text="Voci", font=FONT_TITLE, fg=TEXT, bg=BG).pack(anchor="w")

        row = tk.Frame(info, bg=BG)
        row.pack(anchor="w")
        self._online_dot = tk.Label(row, text="●", font=("Segoe UI", 7), fg=GREEN, bg=BG)
        self._online_dot.pack(side="left")
        tk.Label(row, text=" online agora", font=FONT_SUB, fg=TEXT_DIM, bg=BG).pack(side="left")

        # Botão limpar no header
        tk.Button(
            header, text="✕",
            font=("Segoe UI", 12),
            fg=MUTED, bg=BG,
            activeforeground=TEXT_DIM, activebackground=BG,
            bd=0, relief="flat", cursor="hand2",
            command=self._clear_chat,
        ).pack(side="right")

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", pady=(16, 0))

        # ── Área de chat ──────────────────────────────────────────────────────
        chat_outer = tk.Frame(self.root, bg=SURFACE)
        chat_outer.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(chat_outer, bg=SURFACE, bd=0, highlightthickness=0)
        sb = tk.Scrollbar(chat_outer, orient="vertical", command=self.canvas.yview)
        sb.configure(bg=SURFACE2, troughcolor=SURFACE, width=3, relief="flat", bd=0)
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.bubble_frame = tk.Frame(self.canvas, bg=SURFACE)
        self._cw = self.canvas.create_window((0, 0), window=self.bubble_frame, anchor="nw")

        self.bubble_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",       lambda e: self.canvas.itemconfig(self._cw, width=e.width))
        self.canvas.bind_all("<MouseWheel>",  lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        tk.Frame(self.bubble_frame, bg=SURFACE, height=12).pack()
        self._append_sys("hoje")
        self._append("ia", "Olá! Pressione gravar e fale comigo. PS: Faça perguntas simples, bro! 🎙")

        # ── Status ────────────────────────────────────────────────────────────
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

        st = tk.Frame(self.root, bg=BG, pady=6)
        st.pack(fill="x", padx=24)

        self._status_dot = tk.Label(st, text="●", font=("Segoe UI", 7), fg=MUTED, bg=BG)
        self._status_dot.pack(side="left", padx=(0, 5))
        self.status_var = tk.StringVar(value="pronto para ouvir")
        self._status_lbl = tk.Label(st, textvariable=self.status_var, font=FONT_UI_SM, fg=TEXT_DIM, bg=BG)
        self._status_lbl.pack(side="left")

        # ── Input bar ─────────────────────────────────────────────────────────
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

        bar = tk.Frame(self.root, bg=BG, pady=16)
        bar.pack(fill="x", padx=20)

        self.mic_btn = tk.Button(
            bar,
            text="⏺  Gravar",
            font=FONT_BTN,
            fg=BTN_IDLE_FG, bg=BTN_IDLE_BG,
            activeforeground=BTN_IDLE_FG, activebackground=ACCENT,
            bd=0, relief="flat",
            padx=28, pady=12,
            cursor="hand2",
            command=self._on_mic_click,
        )
        self.mic_btn.pack(fill="x")

    def _show_typing(self):
        self._typing = TypingIndicator(self.bubble_frame)
        self._typing.pack(fill="x", pady=(2, 4))
        self._typing.start()
        self.root.after(60, lambda: self.canvas.yview_moveto(1.0))

    def _hide_typing(self):
        if self._typing:
            self._typing.stop()
            self._typing = None

    # ── Mensagens ─────────────────────────────────────────────────────────────
    def _append(self, tag, text):
        if tag == "user":
            BubbleMessage(self.bubble_frame, text, "right", BUBBLE_USER, TEXT_USER, "você").pack(fill="x", pady=(2, 4))
        elif tag == "ia":
            BubbleMessage(self.bubble_frame, text, "left",  BUBBLE_IA,   TEXT_IA,   "voci").pack(fill="x", pady=(2, 4))
        else:
            self._append_sys(text)
        self.root.after(60, lambda: self.canvas.yview_moveto(1.0))

    def _append_sys(self, text):
        f = tk.Frame(self.bubble_frame, bg=SURFACE, pady=5)
        f.pack(fill="x")
        tk.Label(f, text=text, font=("Segoe UI", 7, "italic"), fg=TEXT_SYS, bg=SURFACE).pack(anchor="center")

    # ── Animações ─────────────────────────────────────────────────────────────
    def _animate_online(self):
        shades = [GREEN, "#4d8a58", GREEN, "#5d9a68"]
        self._online_dot.configure(fg=shades[self._dot_idx % len(shades)])
        self._dot_idx = (self._dot_idx + 1) % len(shades)
        self.root.after(1400, self._animate_online)

    def _start_pulse(self, color):
        self._pulse_on = not self._pulse_on
        self._status_dot.configure(fg=color if self._pulse_on else MUTED)
        self._pulse_job = self.root.after(480, lambda: self._start_pulse(color))

    def _stop_pulse(self):
        if self._pulse_job:
            self.root.after_cancel(self._pulse_job)
            self._pulse_job = None
        self._status_dot.configure(fg=MUTED)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _set_status(self, msg, color=TEXT_DIM, pulse=False):
        self._stop_pulse()
        self.status_var.set(msg)
        self._status_lbl.configure(fg=color)
        if pulse:
            self._start_pulse(color)

    def _set_btn(self, text, bg, fg, state="normal"):
        self.mic_btn.configure(text=text, bg=bg, fg=fg, state=state)

    def _clear_chat(self):
        for w in self.bubble_frame.winfo_children():
            w.destroy()
        tk.Frame(self.bubble_frame, bg=SURFACE, height=12).pack()
        self._append_sys("conversa reiniciada")

    # ── Fluxo ─────────────────────────────────────────────────────────────────
    def _on_mic_click(self):
        if self.recording:
            return
        self.recording = True
        threading.Thread(target=self._run_flow, daemon=True).start()

    def _run_flow(self):
        try:
            self.root.after(0, lambda: self._set_btn("⏺  Gravando…",   BTN_REC_BG,  BTN_REC_FG,  "disabled"))
            self.root.after(0, lambda: self._set_status("gravando 5 segundos…",  RED,   pulse=True))
            arquivo = gravar_audio(duracao=5)

            self.root.after(0, lambda: self._set_btn("◌  Processando…", BTN_PROC_BG, BTN_PROC_FG, "disabled"))
            self.root.after(0, lambda: self._set_status("transcrevendo áudio…",  AMBER, pulse=True))
            texto = transcrever_audio(arquivo)

            if not texto:
                self.root.after(0, lambda: self._append("sys", "nenhum áudio detectado"))
                return

            self.root.after(0, lambda: self._append("user", texto))
            self.root.after(0, lambda: self._set_status("voci está pensando…", TEXT_DIM, pulse=True))
            self.root.after(0, self._show_typing)

            resposta = perguntar_ia(texto)
            self.root.after(0, self._hide_typing)
            self.root.after(0, lambda: self._append("ia", resposta))

            self.root.after(0, lambda: self._set_status("reproduzindo…", GREEN, pulse=True))
            asyncio.run(gerar_e_tocar(resposta))

        except Exception as e:
            self.root.after(0, lambda: self._append("sys", f"erro: {e}"))

        finally:
            self.recording = False
            self.root.after(0, self._stop_pulse)
            self.root.after(0, lambda: self._set_btn("⏺  Gravar", BTN_IDLE_BG, BTN_IDLE_FG))
            self.root.after(0, lambda: self._set_status("pronto para ouvir"))


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceAssistantApp(root)
    root.mainloop()