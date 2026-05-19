"""
╔═══════════════════════════════════════════════════╗
║    💱  Real-Time Currency Converter  v3.0         ║
║    Python · Tkinter · ExchangeRate-API (free)     ║
╠═══════════════════════════════════════════════════╣
║  Install  ➜  pip install requests                 ║
║  Run      ➜  python currency_converter.py         ║
╚═══════════════════════════════════════════════════╝

FIXED in v3:
  ✅  Always fetches USD-base rates ONCE
  ✅  Cross-rate formula — no re-fetch on pair change
      result = amount × (rate_TO / rate_FROM)
  ✅  Multiple API fallbacks (BDT / PKR / SAR fully supported)

UI in v3:
  🎨  Canvas gradient header (indigo → violet)
  🃏  Drop-shadow cards
  🔘  Hover-animated buttons
  💊  Live rate pill with ▲▼ trend arrow
  🌙  Dark / Light mode toggle
  📋  Scrollable conversion history (15 entries)
  📤  Export history to CSV
  ⌨   Keyboard shortcuts
"""

# ── stdlib ──────────────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import csv
from datetime import datetime

# ── third-party (auto-install if missing) ───────────────────────────────────
try:
    import requests
except ImportError:
    import sys, subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests


#  CONSTANTS & DATA

WIN_W, WIN_H    = 560, 900
HDR_H           = 148
HISTORY_MAX     = 15
AUTO_REFRESH_MS = 30 * 60 * 1000

# Two free APIs tried in order — both support BDT, INR, SAR, PKR etc.
APIS = [
    "https://open.er-api.com/v6/latest/USD",
    "https://api.exchangerate-api.com/v4/latest/USD",
]

# code → (flag emoji, full name, currency symbol)
CURRENCIES = {
    "USD": ("🇺🇸", "US Dollar",          "$"),
    "EUR": ("🇪🇺", "Euro",               "€"),
    "GBP": ("🇬🇧", "British Pound",      "£"),
    "BDT": ("🇧🇩", "Bangladeshi Taka",   "৳"),
    "INR": ("🇮🇳", "Indian Rupee",       "₹"),
    "JPY": ("🇯🇵", "Japanese Yen",       "¥"),
    "CAD": ("🇨🇦", "Canadian Dollar",    "C$"),
    "AUD": ("🇦🇺", "Australian Dollar",  "A$"),
    "CHF": ("🇨🇭", "Swiss Franc",        "Fr"),
    "CNY": ("🇨🇳", "Chinese Yuan",       "¥"),
    "SAR": ("🇸🇦", "Saudi Riyal",        "SR"),
    "AED": ("🇦🇪", "UAE Dirham",         "AED"),
    "SGD": ("🇸🇬", "Singapore Dollar",   "S$"),
    "MYR": ("🇲🇾", "Malaysian Ringgit",  "RM"),
    "NZD": ("🇳🇿", "New Zealand Dollar", "NZ$"),
    "KRW": ("🇰🇷", "South Korean Won",   "₩"),
    "THB": ("🇹🇭", "Thai Baht",          "฿"),
    "PKR": ("🇵🇰", "Pakistani Rupee",    "Rs"),
    "NOK": ("🇳🇴", "Norwegian Krone",    "kr"),
    "SEK": ("🇸🇪", "Swedish Krona",      "kr"),
}
CODES   = list(CURRENCIES.keys())
DISPLAY = [f"{v[0]} {k}  —  {v[1]}" for k, v in CURRENCIES.items()]


#  COLOUR PALETTES

def _P(**kw):
    """Readable palette factory."""
    return kw

LIGHT = _P(
    bg       = "#EEF2FF",
    grad1    = "#4F46E5",   grad2   = "#7C3AED",
    card     = "#FFFFFF",   shadow  = "#C7D2FE",
    border   = "#E0E7FF",
    text     = "#1E1B4B",   text2   = "#4338CA",   text3 = "#818CF8",
    hdr_txt  = "#FFFFFF",   hdr_sub = "#C4B5FD",
    primary  = "#4F46E5",   pri_hv  = "#4338CA",
    accent   = "#10B981",   acc_hv  = "#059669",
    swap     = "#F59E0B",   swp_hv  = "#D97706",
    danger   = "#EF4444",   dan_hv  = "#DC2626",
    inp_bg   = "#F5F3FF",   inp_bd  = "#A5B4FC",  inp_foc = "#4F46E5",
    res_bg   = "#EEF2FF",   res_bd  = "#818CF8",  res_txt = "#312E81",
    pill_bg  = "#E0E7FF",   pill_fg = "#3730A3",
    rate_bg  = "#F0FDF4",   rate_fg = "#059669",
    sep      = "#C7D2FE",
    hist_bg  = "#F5F3FF",   hist_alt= "#EDE9FE",   hist_fg = "#3730A3",
    sb_bg    = "#E0E7FF",   sb_trk  = "#A5B4FC",
    mode_bg  = "#7C3AED",   mode_fg = "#FFFFFF",
    foot     = "#818CF8",
)

DARK = _P(
    bg       = "#0F0A2A",
    grad1    = "#312E81",   grad2   = "#4C1D95",
    card     = "#1E1B4B",   shadow  = "#050212",
    border   = "#3730A3",
    text     = "#EDE9FE",   text2   = "#C4B5FD",   text3 = "#6D28D9",
    hdr_txt  = "#EDE9FE",   hdr_sub = "#A78BFA",
    primary  = "#818CF8",   pri_hv  = "#6366F1",
    accent   = "#34D399",   acc_hv  = "#10B981",
    swap     = "#FCD34D",   swp_hv  = "#F59E0B",
    danger   = "#F87171",   dan_hv  = "#EF4444",
    inp_bg   = "#0F0A2A",   inp_bd  = "#4338CA",  inp_foc = "#818CF8",
    res_bg   = "#1E1B4B",   res_bd  = "#6D28D9",  res_txt = "#C4B5FD",
    pill_bg  = "#312E81",   pill_fg = "#C4B5FD",
    rate_bg  = "#064E3B",   rate_fg = "#34D399",
    sep      = "#3730A3",
    hist_bg  = "#1E1B4B",   hist_alt= "#2D2B69",   hist_fg = "#C4B5FD",
    sb_bg    = "#1E1B4B",   sb_trk  = "#4338CA",
    mode_bg  = "#4C1D95",   mode_fg = "#EDE9FE",
    foot     = "#6D28D9",
)


#  UTILITIES

def code_of(display: str) -> str:
    """'🇺🇸 USD  — US Dollar' → 'USD'"""
    return display.split()[1]


def fmt(n: float) -> str:
    """Pretty-format a float: commas + trim trailing zeros."""
    if n == 0:
        return "0"
    s = f"{n:,.4f}" if abs(n) >= 1 else f"{n:.6f}"
    return s.rstrip("0").rstrip(".")


def lerp(c1: str, c2: str, t: float) -> str:
    """Blend two '#RRGGBB' hex colours by fraction t ∈ [0, 1]."""
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1 + (r2 - r1) * t),
        int(g1 + (g2 - g1) * t),
        int(b1 + (b2 - b1) * t),
    )


#  HOVER BUTTON — tk.Button with automatic enter/leave colour change

class HBtn(tk.Button):
    """A flat button that changes colour on mouse hover."""

    def __init__(self, parent, nbg, hbg, nfg="#FFFFFF", hfg="#FFFFFF", **kw):
        super().__init__(
            parent,
            bg=nbg, fg=nfg,
            activebackground=hbg, activeforeground=hfg,
            relief="flat", bd=0, cursor="hand2",
            **kw,
        )
        self._nbg, self._hbg = nbg, hbg
        self._nfg, self._hfg = nfg, hfg
        self.bind("<Enter>", lambda _: self.config(bg=self._hbg, fg=self._hfg))
        self.bind("<Leave>", lambda _: self.config(bg=self._nbg, fg=self._nfg))

    def recolor(self, nbg, hbg, nfg="#FFFFFF", hfg="#FFFFFF"):
        """Update colours after a theme switch."""
        self._nbg, self._hbg = nbg, hbg
        self._nfg, self._hfg = nfg, hfg
        self.config(bg=nbg, fg=nfg,
                    activebackground=hbg, activeforeground=hfg)


#  SHADOW CARD
#  Simulates a drop-shadow by placing the card frame inside a slightly
#  larger coloured outer frame.

class Card:
    def __init__(self, parent, padx=18, pady=16):
        self.outer = tk.Frame(parent)           # shadow layer
        self.outer.pack(fill="x", padx=10, pady=(0, 10))
        self.frame = tk.Frame(self.outer, padx=padx, pady=pady)
        self.frame.pack(fill="x", pady=(0, 3))   # 3px shadow at bottom

    def recolor(self, card_bg: str, shadow_bg: str):
        self.outer.config(bg=shadow_bg)
        self.frame.config(bg=card_bg)
        # Repaint direct Label/Frame children
        for w in self.frame.winfo_children():
            try:
                if isinstance(w, tk.Label):
                    w.config(bg=card_bg)
                elif isinstance(w, tk.Frame):
                    w.config(bg=card_bg)
            except Exception:
                pass


#  MAIN APPLICATION CLASS

class App:
    """
    Real-Time Currency Converter.

    Conversion logic (always correct — no re-fetch when pair changes):
        All rates stored as usd_rates[X] = "X per 1 USD",  with USD = 1.0
        cross_rate = usd_rates[TO] / usd_rates[FROM]
        result     = amount × cross_rate
    """

    # ── Initialise ────────────────────────────────────────────────────────────
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("💱  Currency Converter  —  Live Rates")
        root.resizable(False, False)

        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{WIN_W}x{WIN_H}+{(sw - WIN_W)//2}+{(sh - WIN_H)//2}")

        # ── app state ──────────────────────────────────────────────────────
        self.usd_rates    : dict  = {}     # {code: rate_vs_USD}
        self.last_updated : str   = ""
        self.prev_cross   : float = 0.0   # for ▲▼ trend arrow
        self.dark         : bool  = False
        self.history      : list  = []
        self._loading     : bool  = False

        # ── Tk string variables ────────────────────────────────────────────
        self.sv_amount = tk.StringVar()
        self.sv_from   = tk.StringVar(value=DISPLAY[0])   # USD
        self.sv_to     = tk.StringVar(value=DISPLAY[3])   # BDT
        self.sv_result = tk.StringVar(value="0.00")
        self.sv_rate   = tk.StringVar(value="Fetching live rates…")

        # ── build UI, apply initial theme ──────────────────────────────────
        self._build_ui()
        self._apply_theme()

        # ── keyboard shortcuts ─────────────────────────────────────────────
        root.bind("<Return>",    lambda _: self._convert())
        root.bind("<KP_Enter>",  lambda _: self._convert())
        root.bind("<Control-w>", lambda _: self._swap())
        root.bind("<Control-l>", lambda _: self._clear())
        root.bind("<F5>",        lambda _: self._fetch_start())

        # ── first fetch + auto-refresh schedule ───────────────────────────
        root.after(200,          self._fetch_start)
        root.after(AUTO_REFRESH_MS, self._auto_refresh)


    #  UI CONSTRUCTION

    def _build_ui(self):
        """Create every widget. Called once at startup."""
        T = LIGHT    # initial theme; _apply_theme() will style properly

        # ── outermost wrapper
        self.outer = tk.Frame(self.root)
        self.outer.pack(fill="both", expand=True)

        
        # GRADIENT HEADER              
    
        self.hdr = tk.Canvas(
            self.outer, height=HDR_H, width=WIN_W,
            bd=0, highlightthickness=0)
        self.hdr.pack(fill="x")
        self._paint_gradient()

        # Text items drawn on canvas
        self.id_icon  = self.hdr.create_text(
            26, 28, anchor="nw",
            text="💱", font=("Segoe UI Emoji", 30))

        self.id_title = self.hdr.create_text(
            72, 26, anchor="nw",
            text="Currency Converter",
            font=("Segoe UI", 20, "bold"), fill="#FFFFFF")

        self.id_sub   = self.hdr.create_text(
            72, 60, anchor="nw",
            text="Real-time rates  ·  20 currencies  ·  Free API",
            font=("Segoe UI", 9), fill="#C4B5FD")

        self.id_status = self.hdr.create_text(
            26, 96, anchor="nw",
            text="⏳  Connecting to exchange-rate server…",
            font=("Segoe UI", 9, "italic"), fill="#FCD34D")

        self.id_updated = self.hdr.create_text(
            26, 118, anchor="nw",
            text="",
            font=("Segoe UI", 8), fill="#A78BFA")

        # Dark-mode toggle button — placed on canvas via create_window
        self.btn_mode = HBtn(
            self.hdr,
            nbg=T["mode_bg"], hbg=T["grad1"],
            nfg=T["mode_fg"],
            text="🌙", font=("Segoe UI Emoji", 15),
            padx=8, pady=4,
            command=self._toggle_theme)
        self.hdr.create_window(WIN_W - 12, 12, anchor="ne",
                               window=self.btn_mode)

        # ── body (everything below the header)
        self.body = tk.Frame(self.outer)
        self.body.pack(fill="both", expand=True, pady=(6, 0))

        
        # CARD 1 — Amount Input
        
        self.card_amt = Card(self.body, padx=18, pady=16)
        fa = self.card_amt.frame

        hrow = tk.Frame(fa)
        hrow.pack(fill="x", pady=(0, 8))
        self.lbl_amt_ttl = tk.Label(
            hrow, text="Enter Amount",
            font=("Segoe UI", 10, "bold"), anchor="w")
        self.lbl_amt_ttl.pack(side="left")
        self.lbl_sym_hint = tk.Label(
            hrow, text="( $ USD )",
            font=("Segoe UI", 9), anchor="e")
        self.lbl_sym_hint.pack(side="right")

        # entry frame with focus-ring border
        self.ef = tk.Frame(fa, highlightthickness=2)
        self.ef.pack(fill="x")

        self.lbl_sym = tk.Label(
            self.ef, text="$",
            font=("Segoe UI", 24, "bold"), padx=12)
        self.lbl_sym.pack(side="left")

        self.sep_v = tk.Frame(self.ef, width=1)
        self.sep_v.pack(side="left", fill="y", padx=(0, 6), pady=8)

        self.entry = tk.Entry(
            self.ef, textvariable=self.sv_amount,
            font=("Segoe UI", 24, "bold"),
            bd=0, relief="flat", justify="right", width=14)
        self.entry.pack(side="right", fill="x", expand=True, padx=10, pady=8)
        self.entry.bind("<FocusIn>",  self._focus_in)
        self.entry.bind("<FocusOut>", self._focus_out)

        
        # CARD 2 — Currency Selectors           

        self.card_cur = Card(self.body, padx=18, pady=16)
        fc2 = self.card_cur.frame

        sel = tk.Frame(fc2)
        sel.pack(fill="x")
        sel.columnconfigure(0, weight=1)
        sel.columnconfigure(2, weight=1)

        # FROM column
        col_from = tk.Frame(sel)
        col_from.grid(row=0, column=0, sticky="ew")
        self.lbl_from_ttl = tk.Label(
            col_from, text="From Currency",
            font=("Segoe UI", 9, "bold"), anchor="w")
        self.lbl_from_ttl.pack(fill="x", pady=(0, 5))
        self.cb_from = ttk.Combobox(
            col_from, textvariable=self.sv_from,
            values=DISPLAY, state="readonly",
            font=("Segoe UI", 10), width=20)
        self.cb_from.pack(fill="x")
        self.cb_from.bind("<<ComboboxSelected>>", self._on_pair_change)

        # SWAP button (centre)
        col_swap = tk.Frame(sel)
        col_swap.grid(row=0, column=1, padx=8)
        tk.Label(col_swap, text="", font=("Segoe UI", 9)).pack()  # spacer
        self.btn_swap = HBtn(
            col_swap,
            nbg=T["swap"], hbg=T["swp_hv"],
            text="⇄", font=("Segoe UI", 16, "bold"),
            padx=10, pady=6,
            command=self._swap)
        self.btn_swap.pack(pady=(2, 0))

        # TO column
        col_to = tk.Frame(sel)
        col_to.grid(row=0, column=2, sticky="ew")
        self.lbl_to_ttl = tk.Label(
            col_to, text="To Currency",
            font=("Segoe UI", 9, "bold"), anchor="w")
        self.lbl_to_ttl.pack(fill="x", pady=(0, 5))
        self.cb_to = ttk.Combobox(
            col_to, textvariable=self.sv_to,
            values=DISPLAY, state="readonly",
            font=("Segoe UI", 10), width=20)
        self.cb_to.pack(fill="x")
        self.cb_to.bind("<<ComboboxSelected>>", self._on_pair_change)

        # Store sub-frames for recolouring
        self._cur_cols = [col_from, col_swap, col_to]

        # Live rate pill
        self.pill_wrap = tk.Frame(fc2)
        self.pill_wrap.pack(fill="x", pady=(14, 0))
        self.pill = tk.Label(
            self.pill_wrap, textvariable=self.sv_rate,
            font=("Segoe UI", 9, "bold"),
            padx=14, pady=6, anchor="center")
        self.pill.pack()

       
        # ACTION BUTTONS ROW  
     
        self.btn_row = tk.Frame(self.body)
        self.btn_row.pack(fill="x", padx=10, pady=(0, 4))

        self.btn_convert = HBtn(
            self.btn_row,
            nbg=T["primary"], hbg=T["pri_hv"],
            text="🔄  Convert",
            font=("Segoe UI", 13, "bold"),
            padx=20, pady=12,
            command=self._convert)
        self.btn_convert.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.btn_clear = HBtn(
            self.btn_row,
            nbg=T["danger"], hbg=T["dan_hv"],
            text="✕  Clear",
            font=("Segoe UI", 13, "bold"),
            padx=18, pady=12,
            command=self._clear)
        self.btn_clear.pack(side="right", padx=(5, 0))

        #  CARD 3 — Result
        self.card_res = Card(self.body, padx=18, pady=20)
        fr = self.card_res.frame

        self.lbl_res_ttl = tk.Label(
            fr, text="Converted Result",
            font=("Segoe UI", 9, "bold"), anchor="center")
        self.lbl_res_ttl.pack()

        self.lbl_result = tk.Label(
            fr, textvariable=self.sv_result,
            font=("Segoe UI", 36, "bold"), anchor="center")
        self.lbl_result.pack(pady=(6, 6))

        self.lbl_detail = tk.Label(
            fr, text="—",
            font=("Segoe UI", 8), anchor="center",
            wraplength=500, justify="center")
        self.lbl_detail.pack()

        # ┌───────────────────────────────────────┐
        # │  HISTORY                              │
        # └───────────────────────────────────────┘
        self.sep_line = tk.Frame(self.body, height=1)
        self.sep_line.pack(fill="x", padx=10, pady=(8, 6))

        self.hist_hdr = tk.Frame(self.body)
        self.hist_hdr.pack(fill="x", padx=10, pady=(0, 6))

        self.lbl_hist_ttl = tk.Label(
            self.hist_hdr, text="📋  Conversion History",
            font=("Segoe UI", 10, "bold"), anchor="w")
        self.lbl_hist_ttl.pack(side="left")

        self.btn_export = HBtn(
            self.hist_hdr,
            nbg=T["pill_bg"], hbg=T["border"],
            nfg=T["pill_fg"], hfg=T["text2"],
            text="⬇  Export CSV",
            font=("Segoe UI", 8, "bold"),
            padx=10, pady=4,
            command=self._export_csv)
        self.btn_export.pack(side="right")

        # Listbox with scrollbar
        self._lf = tk.Frame(self.body, highlightthickness=1)
        self._lf.pack(fill="x", padx=10, pady=(0, 4))

        self._sb = tk.Scrollbar(self._lf)
        self._sb.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            self._lf, yscrollcommand=self._sb.set,
            font=("Segoe UI", 9), bd=0, relief="flat",
            selectmode="single", activestyle="none",
            height=6)
        self.listbox.pack(fill="both", expand=True)
        self._sb.config(command=self.listbox.yview)

        self.lbl_empty = tk.Label(
            self._lf,
            text="No conversions yet — start converting!",
            font=("Segoe UI", 9), pady=12)
        self.lbl_empty.pack()

        # ── footer keyboard hint ───────────────────────────────────────────
        self.lbl_foot = tk.Label(
            self.body,
            text="⌨  Enter = Convert  ·  Ctrl+W = Swap  ·  Ctrl+L = Clear  ·  F5 = Refresh Rates",
            font=("Segoe UI", 7), anchor="center")
        self.lbl_foot.pack(pady=(2, 8))


    #  GRADIENT HEADER

    def _paint_gradient(self):
        """Fill header canvas with smooth indigo → violet horizontal stripes."""
        T = DARK if self.dark else LIGHT
        self.hdr.delete("gradient")
        for i in range(HDR_H):
            c = lerp(T["grad1"], T["grad2"], i / HDR_H)
            self.hdr.create_line(0, i, WIN_W, i, fill=c, tags="gradient")
        self.hdr.tag_lower("gradient")     # push gradient behind text


    #  THEMING

    def _apply_theme(self):
        """Re-colour every widget for the current Light / Dark theme."""
        T = DARK if self.dark else LIGHT

        # root, outer, body
        self.root.config(bg=T["bg"])
        self.outer.config(bg=T["bg"])
        self.body.config(bg=T["bg"])

        # header
        self._paint_gradient()
        self.hdr.config(bg=T["grad1"])
        self.hdr.itemconfig(self.id_title,   fill=T["hdr_txt"])
        self.hdr.itemconfig(self.id_sub,     fill=T["hdr_sub"])
        self.hdr.itemconfig(self.id_updated, fill=T["hdr_sub"])
        self.btn_mode.recolor(T["mode_bg"], T["grad1"], T["mode_fg"], T["hdr_txt"])
        self.btn_mode.config(text="☀" if self.dark else "🌙")

        # CARD 1 — amount
        self.card_amt.recolor(T["card"], T["shadow"])
        for w in (self.lbl_amt_ttl,):
            w.config(bg=T["card"], fg=T["text"])
        self.lbl_sym_hint.config(bg=T["card"], fg=T["text3"])
        self.ef.config(bg=T["inp_bg"],
                       highlightbackground=T["inp_bd"],
                       highlightcolor=T["inp_foc"])
        self.lbl_sym.config(bg=T["inp_bg"], fg=T["primary"])
        self.sep_v.config(bg=T["inp_bd"])
        self.entry.config(bg=T["inp_bg"], fg=T["text"],
                          insertbackground=T["text"],
                          selectbackground=T["primary"],
                          selectforeground="#FFFFFF")

        # CARD 2 — currency selectors
        self.card_cur.recolor(T["card"], T["shadow"])
        for lbl in (self.lbl_from_ttl, self.lbl_to_ttl):
            lbl.config(bg=T["card"], fg=T["text2"])
        for col in self._cur_cols:
            col.config(bg=T["card"])
        self.pill_wrap.config(bg=T["card"])
        self.pill.config(bg=T["rate_bg"], fg=T["rate_fg"])
        self.btn_swap.recolor(T["swap"], T["swp_hv"])

        # Combobox styling via ttk.Style
        sty = ttk.Style()
        sty.theme_use("clam")
        sty.configure("TCombobox",
            fieldbackground=T["inp_bg"],
            background=T["card"],
            foreground=T["text"],
            arrowcolor=T["text2"],
            bordercolor=T["inp_bd"],
            lightcolor=T["inp_bd"],
            darkcolor=T["inp_bd"],
            selectbackground=T["inp_bg"],
            selectforeground=T["text"],
            padding=6)
        sty.map("TCombobox",
            fieldbackground=[("readonly", T["inp_bg"])],
            foreground=[("readonly", T["text"])],
            selectbackground=[("readonly", T["inp_bg"])],
            selectforeground=[("readonly", T["text"])])

        # action buttons row
        self.btn_row.config(bg=T["bg"])
        self.btn_convert.recolor(T["primary"], T["pri_hv"])
        self.btn_clear.recolor(T["danger"], T["dan_hv"])

        # CARD 3 — result
        self.card_res.recolor(T["res_bg"], T["res_bd"])
        self.lbl_res_ttl.config(bg=T["res_bg"], fg=T["text2"])
        self.lbl_result.config(bg=T["res_bg"], fg=T["res_txt"])
        self.lbl_detail.config(bg=T["res_bg"], fg=T["text2"])

        # history
        self.sep_line.config(bg=T["sep"])
        self.hist_hdr.config(bg=T["bg"])
        self.lbl_hist_ttl.config(bg=T["bg"], fg=T["text"])
        self.btn_export.recolor(T["pill_bg"], T["border"],
                                T["pill_fg"], T["text2"])
        self._lf.config(bg=T["hist_bg"],
                        highlightbackground=T["border"])
        self.listbox.config(bg=T["hist_bg"], fg=T["hist_fg"],
                            selectbackground=T["pill_bg"],
                            selectforeground=T["pill_fg"])
        self.lbl_empty.config(bg=T["hist_bg"], fg=T["text3"])
        self._sb.config(bg=T["sb_bg"], troughcolor=T["sb_trk"],
                        activebackground=T["primary"])

        # footer
        self.lbl_foot.config(bg=T["bg"], fg=T["foot"])

        # re-colour existing history rows
        self._recolour_rows()

    def _toggle_theme(self):
        self.dark = not self.dark
        self._apply_theme()

    def _focus_in(self, _=None):
        T = DARK if self.dark else LIGHT
        self.ef.config(highlightbackground=T["inp_foc"])

    def _focus_out(self, _=None):
        T = DARK if self.dark else LIGHT
        self.ef.config(highlightbackground=T["inp_bd"])


    #  FETCH RATES  (runs in background thread)

    def _fetch_start(self):
        """Start background fetch if not already running."""
        if self._loading:
            return
        self._loading = True
        self.btn_convert.config(state="disabled")
        self._set_status("⏳  Fetching live exchange rates…", "#FCD34D")
        threading.Thread(target=self._fetch_worker, daemon=True).start()

    def _fetch_worker(self):
        """
        Worker thread: try each API in APIS list until one succeeds.
        Both APIs return JSON with a top-level 'rates' dict keyed by
        ISO-4217 code, values = units of that currency per 1 USD.
        Posts results back via root.after() to stay thread-safe.
        """
        for url in APIS:
            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                data = resp.json()

                # Both APIs use key "rates"; v6 also has "conversion_rates"
                raw = (data.get("rates")
                       or data.get("conversion_rates")
                       or {})
                if not raw:
                    continue

                # Extract only the currencies we support
                rates = {c: float(raw[c]) for c in CODES if c in raw}
                rates["USD"] = 1.0      # base is USD

                if len(rates) < 5:      # sanity-check: too few → wrong format
                    continue

                self.usd_rates    = rates
                self.last_updated = datetime.now().strftime("%d %b %Y  %H:%M:%S")
                self.root.after(0, self._fetch_ok)
                return

            except Exception:
                continue    # try next API

        # All APIs failed — post error to main thread
        self.root.after(0, lambda: self._fetch_fail(
            "All exchange-rate servers unreachable.\n"
            "Please check your internet connection and press F5 to retry."
        ))

    def _fetch_ok(self):
        self._loading = False
        self._set_status("✅  Live rates loaded successfully", "#34D399")
        self.hdr.itemconfig(self.id_updated,
                            text=f"Last updated: {self.last_updated}")
        self.btn_convert.config(state="normal")
        self._update_pill()

    def _fetch_fail(self, msg: str):
        self._loading = False
        first_line = msg.splitlines()[0]
        self._set_status(f"⚠  {first_line}", "#F87171")
        self.btn_convert.config(state="normal")
        if not self.usd_rates:
            messagebox.showerror("Connection Error", msg)

    def _set_status(self, text: str, colour: str = "#FCD34D"):
        self.hdr.itemconfig(self.id_status, text=text, fill=colour)

    def _auto_refresh(self):
        self._fetch_start()
        self.root.after(AUTO_REFRESH_MS, self._auto_refresh)


    #  CONVERSION  ← THE FIXED CORE LOGIC

    def _convert(self):
        """
        Validate amount, compute result using the cross-rate formula,
        update the result card, and log the conversion to history.
        """

        # ── Step 1: validate amount ──────────────────────────────────────────
        raw = self.sv_amount.get().strip().replace(",", "")
        if not raw:
            self._flash_entry()
            messagebox.showwarning("Missing Amount",
                "Please enter an amount to convert.")
            return
        try:
            amount = float(raw)
            if amount < 0:
                raise ValueError("negative amount")
        except ValueError:
            self._flash_entry()
            messagebox.showerror("Invalid Input",
                "Please enter a valid positive number.\n"
                "Examples:  100    or    1250.75")
            return

        # ── Step 2: check that rates are loaded ─────────────────────────────
        if not self.usd_rates:
            messagebox.showwarning("Still Loading",
                "Exchange rates are still loading.\n"
                "Please wait a moment, then try again.\n"
                "(Or press F5 to force a refresh.)")
            return

        # ── Step 3: get selected currency codes ──────────────────────────────
        fc = code_of(self.sv_from.get())
        tc = code_of(self.sv_to.get())

        missing = [c for c in (fc, tc) if c not in self.usd_rates]
        if missing:
            messagebox.showerror("Missing Rate",
                f"No rate data available for: {', '.join(missing)}\n"
                "Press F5 to refresh.")
            return

        # ── Step 4: CROSS-RATE FORMULA ───────────────────────────────────────
        #
        #   usd_rates[X] = "how many X buys 1 USD"
        #
        #   Step A — convert amount FROM → USD:
        #       usd_val = amount / usd_rates[fc]
        #
        #   Step B — convert USD → TO:
        #       result  = usd_val × usd_rates[tc]
        #
        #   Combined in one line:
        #       cross  = usd_rates[tc] / usd_rates[fc]   (1 FC = cross TC)
        #       result = amount × cross
        #
        cross  = self.usd_rates[tc] / self.usd_rates[fc]
        result = amount * cross

        # ── Step 5: update result card ───────────────────────────────────────
        ff, fn, fs = CURRENCIES[fc]
        tf, tn, ts = CURRENCIES[tc]

        self.sv_result.set(f"{ts} {fmt(result)}")

        detail = (
            f"{ff} {fmt(amount)} {fc}  →  {tf} {fmt(result)} {tc}"
            f"     |     Rate: 1 {fc} = {fmt(cross)} {tc}"
            f"     |     {self.last_updated}"
        )
        self.lbl_detail.config(text=detail)

        # ── Step 6: update rate pill with ▲▼ trend ──────────────────────────
        arrow = ""
        if self.prev_cross:
            arrow = "  ▲" if cross > self.prev_cross else (
                    "  ▼" if cross < self.prev_cross else "")
        self.prev_cross = cross
        self.sv_rate.set(
            f"💹  1 {ff} {fc}  =  {fmt(cross)} {tf} {tc}{arrow}")

        # ── Step 7: visual feedback ──────────────────────────────────────────
        self._pulse_result()
        T = DARK if self.dark else LIGHT
        self.btn_convert.config(bg=T["accent"])
        self.root.after(300, lambda: self.btn_convert.config(bg=T["primary"]))

        # ── Step 8: add to history ───────────────────────────────────────────
        self.history.insert(0, dict(
            time=datetime.now().strftime("%H:%M:%S"),
            amount=amount, fc=fc, ff=ff, fn=fn,
            tc=tc, tf=tf, tn=tn,
            result=result, cross=cross,
        ))
        if len(self.history) > HISTORY_MAX:
            self.history.pop()
        self._refresh_history()


    #  SWAP  /  CLEAR

    def _swap(self):
        """Swap the FROM and TO currencies."""
        a, b = self.sv_from.get(), self.sv_to.get()
        self.sv_from.set(b)
        self.sv_to.set(a)
        self._on_pair_change()
        T = DARK if self.dark else LIGHT
        self.btn_swap.config(bg=T["accent"])
        self.root.after(250, lambda: self.btn_swap.config(bg=T["swap"]))

    def _clear(self):
        """Reset amount and result."""
        self.sv_amount.set("")
        self.sv_result.set("0.00")
        self.lbl_detail.config(text="—")
        self.prev_cross = 0.0
        self.entry.focus_set()


    #  UI HELPERS

    def _on_pair_change(self, _=None):
        """Called whenever either combobox selection changes."""
        fc = code_of(self.sv_from.get())
        sym = CURRENCIES[fc][2]
        self.lbl_sym.config(text=sym)
        self.lbl_sym_hint.config(text=f"( {sym} {fc} )")
        self._update_pill()

    def _update_pill(self):
        """Show the live rate between the currently selected currencies."""
        if not self.usd_rates:
            self.sv_rate.set("⏳  Fetching live rates…")
            return
        fc = code_of(self.sv_from.get())
        tc = code_of(self.sv_to.get())
        if fc in self.usd_rates and tc in self.usd_rates:
            cross = self.usd_rates[tc] / self.usd_rates[fc]
            ff = CURRENCIES[fc][0]
            tf = CURRENCIES[tc][0]
            self.sv_rate.set(
                f"💹  1 {ff} {fc}  =  {fmt(cross)} {tf} {tc}")
        else:
            self.sv_rate.set("Rate unavailable — press F5 to refresh")

    def _flash_entry(self):
        """Briefly redden the entry border to signal bad input."""
        T = DARK if self.dark else LIGHT
        self.ef.config(highlightbackground=T["danger"])
        self.root.after(600,
            lambda: self.ef.config(highlightbackground=T["inp_bd"]))

    def _pulse_result(self):
        """Briefly flash the result card bright blue on each conversion."""
        T = DARK if self.dark else LIGHT
        for w in (self.card_res.frame, self.lbl_res_ttl,
                  self.lbl_result, self.lbl_detail):
            try:
                w.config(bg=T["primary"])
            except Exception:
                pass
        self.lbl_result.config(fg="#FFFFFF")

        def _restore():
            for w in (self.card_res.frame, self.lbl_res_ttl, self.lbl_detail):
                try:
                    w.config(bg=T["res_bg"])
                except Exception:
                    pass
            self.lbl_result.config(bg=T["res_bg"], fg=T["res_txt"])
            self.lbl_res_ttl.config(fg=T["text2"])
            self.lbl_detail.config(fg=T["text2"])

        self.root.after(350, _restore)


    #  HISTORY

    def _refresh_history(self):
        """Rebuild the listbox from self.history."""
        self.listbox.delete(0, "end")
        if not self.history:
            self.lbl_empty.pack()
            return
        self.lbl_empty.pack_forget()
        for h in self.history:
            line = (
                f"  [{h['time']}]  "
                f"{h['ff']} {fmt(h['amount'])} {h['fc']}"
                f"  →  "
                f"{h['tf']} {fmt(h['result'])} {h['tc']}"
                f"     (1 {h['fc']} = {fmt(h['cross'])} {h['tc']})"
            )
            self.listbox.insert("end", line)
        self._recolour_rows()

    def _recolour_rows(self):
        """Apply alternating background colours to listbox rows."""
        T = DARK if self.dark else LIGHT
        for i in range(self.listbox.size()):
            bg = T["hist_alt"] if i % 2 == 0 else T["hist_bg"]
            self.listbox.itemconfig(i, background=bg, foreground=T["hist_fg"])

    def _export_csv(self):
        """Write the conversion history to a user-chosen CSV file."""
        if not self.history:
            messagebox.showinfo("Nothing to Export",
                "Make at least one conversion first!")
            return
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"currency_history_{ts}.csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Conversion History")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as fh:
                fieldnames = ["time", "amount", "from_currency",
                              "to_currency", "result", "rate"]
                w = csv.DictWriter(fh, fieldnames=fieldnames)
                w.writeheader()
                for h in self.history:
                    w.writerow({
                        "time":          h["time"],
                        "amount":        h["amount"],
                        "from_currency": h["fc"],
                        "to_currency":   h["tc"],
                        "result":        h["result"],
                        "rate":          h["cross"],
                    })
            messagebox.showinfo("Exported ✅", f"History saved to:\n{path}")
        except OSError as e:
            messagebox.showerror("Export Failed", str(e))


#  ENTRY POINT

def main():
    root = tk.Tk()
    try:
        root.iconbitmap("")    # suppress default Tk icon silently
    except Exception:
        pass
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()