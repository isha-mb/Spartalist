import tkinter as tk
from tkinter import ttk, messagebox
import re
from datetime import datetime

SCHOOL_NAME      = "Batangas State University TNEU - Alangilan Campus"
RESULTS_FILENAME = "spartalist_results_2026.txt"
ADMIN_PASSWORD   = "admin123"

POSITIONS = [
    "President",
    "Executive Vice President",
    "VP For Student Development & Government - Alangilan",
    "VP For Student Development & Government - Balayan",
]

PARTY_LISTS = {
    "Habinaya": {
        "President"                                           : "Angel Gionni S. Ornales",
        "Executive Vice President"                            : "Christopher R. Pacheco",
        "VP For Student Development & Government - Alangilan" : "Jose Reyes",
        "VP For Student Development & Government - Balayan"   : "Ana Villanueva",
    },
    "BatState United": {
        "President"                                           : "Juan dela Cruz",
        "Executive Vice President"                            : "Liza Bautista",
        "VP For Student Development & Government - Alangilan" : "Ryan Fernandez",
        "VP For Student Development & Government - Balayan"   : "Sophia Ramos",
    },
}


C = {
    "bg"         : "#FAF7F7",
    "surface"    : "#FFFFFF",
    "surface2"   : "#F2EDED",
    "border"     : "#E8D5D5",
    "accent"     : "#C0152A",
    "accent2"    : "#8B0000",
    "accent_light": "#FDECEA",
    "text"       : "#1A1A1A",
    "text_dim"   : "#7A6A6A",
    "success"    : "#1E7E34",
    "error"      : "#C0152A",
    "warning"    : "#B45309",
    "white"      : "#FFFFFF",
    "card"       : "#FFFFFF",
    "btn_hover"  : "#FFFFFF",
    "nav_bg"     : "#C0152A",
    "nav_active" : "#8B0000",
    "habinaya"   : "#1565C0",
    "batstate"   : "#6A1B9A",
    "divider"    : "#E0CCCC",
    "row_alt"    : "#FDF5F5",
    "bar_bg"     : "#F2EDED",
}

PARTY_COLORS = {
    "Habinaya"       : C["habinaya"],
    "BatState United": C["batstate"],
}

FONT_TITLE  = ("Georgia", 18, "bold")
FONT_HEAD   = ("Georgia", 13, "bold")
FONT_BODY   = ("Helvetica", 11)
FONT_BODY_B = ("Helvetica", 11, "bold")
FONT_SMALL  = ("Helvetica", 9)
FONT_BTN    = ("Georgia", 11, "bold")
FONT_LABEL  = ("Helvetica", 10)


class CandidateNode:
    def __init__(self, name, party, position):
        self.name     = name
        self.party    = party
        self.position = position
        self.votes    = 0
        self.next     = None

class CandidateLinkedList:
    def __init__(self, position):
        self.position = position
        self.head     = None

    def append(self, name, party):
        node = CandidateNode(name, party, self.position)
        if not self.head:
            self.head = node
        else:
            cur = self.head
            while cur.next: cur = cur.next
            cur.next = node

    def find(self, name):
        cur = self.head
        while cur:
            if cur.name.lower() == name.lower(): return cur
            cur = cur.next
        return None

    def add_vote(self, name):
        node = self.find(name)
        if node: node.votes += 1; return True
        return False

    def get_winner(self):
        winner, cur = None, self.head
        while cur:
            if not winner or cur.votes > winner.votes: winner = cur
            cur = cur.next
        return winner

    def all_candidates(self):
        result, cur = [], self.head
        while cur: result.append(cur); cur = cur.next
        return result

class VotingSystem:
    def __init__(self):
        self.voters:  dict[str, set] = {}
        self.ballots: dict[str, CandidateLinkedList] = {}
        self._build_ballots()

    def _build_ballots(self):
        for pos in POSITIONS:
            self.ballots[pos] = CandidateLinkedList(pos)
            for party, cands in PARTY_LISTS.items():
                if pos in cands:
                    self.ballots[pos].append(cands[pos], party)

    def register_voter(self, sid):
        sid = sid.strip().upper()
        if sid in self.voters: return False
        self.voters[sid] = set(); return True

    def is_registered(self, sid):
        return sid.strip().upper() in self.voters

    def has_voted_for(self, sid, position):
        return position in self.voters.get(sid.strip().upper(), set())

    def all_voted(self, sid):
        sid = sid.strip().upper()
        return all(self.has_voted_for(sid, p) for p in POSITIONS)

    def cast_vote(self, sid, position, candidate_name):
        sid = sid.strip().upper()
        if sid not in self.voters:
            return False, "Student ID not registered."
        if position not in self.ballots:
            return False, f"'{position}' is not a valid position."
        if position in self.voters[sid]:
            return False, f"Already voted for {position}."
        if not self.ballots[position].add_vote(candidate_name):
            return False, f"Candidate '{candidate_name}' not found."
        self.voters[sid].add(position)
        return True, f"Vote cast for {candidate_name}!"

    def get_results(self):
        results = {}
        for pos, ll in self.ballots.items():
            w = ll.get_winner()
            results[pos] = {
                "candidates": [(c.name, c.party, c.votes) for c in ll.all_candidates()],
                "winner"    : (w.name, w.party, w.votes) if w else None,
            }
        return results

    def total_votes_cast(self):
        return sum(len(v) for v in self.voters.values())

def is_valid_id(sid):
    return bool(re.match(r"^\d{2}-\d{5}$", sid.strip()))

# ─────────────────────────────────────────────
#  GUI — REUSABLE WIDGETS
# ─────────────────────────────────────────────

def styled_btn(parent, text, command, color=None, width=20, pady=8):
    bg = color or C["accent"]
    fg = C["white"]
    hover = C["btn_hover"] if bg == C["accent"] else bg
    b  = tk.Button(
        parent, text=text, command=command, font=FONT_BTN,
        bg=bg, fg=fg, activebackground=hover, activeforeground=C["white"],
        relief="flat", bd=0, padx=16, pady=pady, cursor="hand2", width=width,
    )
    b.bind("<Enter>", lambda e: b.config(bg=hover))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b

def section_label(parent, text):
    tk.Label(parent, text=text, font=FONT_HEAD, bg=C["bg"], fg=C["accent"]).pack(pady=(18,4))
    tk.Frame(parent, bg=C["accent"], height=2).pack(fill="x", padx=30)

def card_frame(parent, **kw):
    return tk.Frame(parent, bg=C["card"], relief="flat",
                    highlightbackground=C["border"], highlightthickness=1, **kw)

def scrollable(parent, bg=None):
    bg = bg or C["bg"]
    canvas = tk.Canvas(parent, bg=bg, highlightthickness=0)
    sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas, bg=bg)
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=sb.set)
    canvas.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return frame

# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────

class SpartalistApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.vs = VotingSystem()
        self.title("SPARTALIST — Student Council Voting")
        self.geometry("860x620")
        self.minsize(760, 560)
        self.configure(bg=C["bg"])
        self.resizable(True, True)

        self._build_header()
        self._build_nav()
        self._build_content()
        self.show_home()


    def _build_header(self):
        hdr = tk.Frame(self, bg=C["accent"], pady=0)
        hdr.pack(fill="x")

        inner = tk.Frame(hdr, bg=C["accent"])
        inner.pack(fill="x", padx=0)

        left = tk.Frame(inner, bg=C["accent"])
        left.pack(side="left", padx=20, pady=12)
        tk.Label(left, text="⚔️ SPARTALIST", font=("Georgia", 20, "bold"),
                 bg=C["accent"], fg=C["white"]).pack(side="left")
        tk.Label(left, text=f"  •  {SCHOOL_NAME}", font=("Helvetica", 9),
                 bg=C["accent"], fg="#FFCCCC").pack(side="left", pady=2)

        self.status_lbl = tk.Label(inner, text="", font=("Helvetica", 9),
                                   bg=C["accent"], fg="#FFEEEE")
        self.status_lbl.pack(side="right", padx=20)

    def _build_nav(self):
        nav = tk.Frame(self, bg=C["white"], pady=0)
        nav.pack(fill="x")

        tk.Frame(self, bg=C["accent"], height=3).pack(fill="x")

        self.nav_btns = {}
        tabs = [("🏠  Home", "home"), ("📋  Register", "register"),
                ("🗳️  Vote", "vote"), ("🔒  Admin", "admin")]
        for label, key in tabs:
            b = tk.Button(nav, text=label, font=("Georgia", 10, "bold"),
                          bg=C["white"], fg=C["text_dim"],
                          activebackground=C["accent_light"], activeforeground=C["accent"],
                          relief="flat", bd=0, padx=22, pady=10, cursor="hand2",
                          command=lambda k=key: self._nav(k))
            b.pack(side="left")
            self.nav_btns[key] = b

    def _build_content(self):
        self.content = tk.Frame(self, bg=C["bg"])
        self.content.pack(fill="both", expand=True)

    def _nav(self, key):
        for k, b in self.nav_btns.items():
            if k == key:
                b.config(bg=C["accent_light"], fg=C["accent"])
            else:
                b.config(bg=C["white"], fg=C["text_dim"])
        for w in self.content.winfo_children(): w.destroy()
        {"home": self.show_home, "register": self.show_register,
         "vote": self.show_vote, "admin": self.show_admin}[key]()

    def set_status(self, msg, color=None):
        self.status_lbl.config(text=msg, fg=color or C["success"])

    def clear_content(self):
        for w in self.content.winfo_children(): w.destroy()

    # ── HOME ──────────────────────────────────

    def show_home(self):
        self._nav_highlight("home")
        self.clear_content()
        f = tk.Frame(self.content, bg=C["bg"])
        f.pack(fill="both", expand=True, padx=40, pady=30)

        hero = card_frame(f)
        hero.pack(fill="x", pady=(0, 20))

        hero_inner = tk.Frame(hero, bg=C["accent"])
        hero_inner.pack(fill="x")
        tk.Label(hero_inner, text="⚔️", font=("Georgia", 42), bg=C["accent"], fg=C["white"]).pack(pady=(20,0))
        tk.Label(hero_inner, text="SPARTALIST", font=("Georgia", 26, "bold"),
                 bg=C["accent"], fg=C["white"]).pack()
        tk.Label(hero_inner, text="Student Council Election System  •  2026",
                 font=("Helvetica", 10), bg=C["accent"], fg="#FFCCCC").pack(pady=(2,18))

        stats = tk.Frame(f, bg=C["bg"])
        stats.pack(fill="x", pady=(0, 20))
        stats.columnconfigure((0,1,2), weight=1)

        def stat_card(parent, col, icon, label, val_fn):
            c = card_frame(parent, padx=20, pady=16)
            c.grid(row=0, column=col, padx=6, sticky="ew")
            tk.Label(c, text=icon, font=("Georgia", 22), bg=C["card"], fg=C["accent"]).pack()
            self._stat_labels = getattr(self, "_stat_labels", {})
            lbl = tk.Label(c, text=str(val_fn()), font=("Georgia", 22, "bold"),
                           bg=C["card"], fg=C["accent"])
            lbl.pack()
            tk.Label(c, text=label, font=FONT_SMALL, bg=C["card"], fg=C["text_dim"]).pack()
            return lbl

        self.lbl_registered = stat_card(stats, 0, "👥", "Registered Voters",
                                        lambda: len(self.vs.voters))
        self.lbl_votes      = stat_card(stats, 1, "🗳️", "Votes Cast",
                                        lambda: self.vs.total_votes_cast())
        self.lbl_positions  = stat_card(stats, 2, "📌", "Positions",
                                        lambda: len(POSITIONS))

        btns = tk.Frame(f, bg=C["bg"])
        btns.pack(pady=10)
        styled_btn(btns, "Register to Vote", lambda: self._nav("register"), width=22).pack(side="left", padx=8)
        b2 = styled_btn(btns, "Cast My Vote", lambda: self._nav("vote"), width=22, color=C["surface2"])
        b2.config(fg=C["accent"], bg=C["surface2"])
        b2.pack(side="left", padx=8)

        section_label(f, "CANDIDATES")
        cf = tk.Frame(f, bg=C["bg"])
        cf.pack(fill="x", pady=10)
        cf.columnconfigure(list(range(len(POSITIONS))), weight=1)

        for col, pos in enumerate(POSITIONS):
            card = card_frame(cf, padx=12, pady=12)
            card.grid(row=0, column=col, padx=5, sticky="nsew")
            hstrip = tk.Frame(card, bg=C["accent"], padx=8, pady=4)
            hstrip.pack(fill="x")
            short = pos.replace("VP For Student Development & Government - ", "VP ")
            tk.Label(hstrip, text=short, font=("Helvetica", 8, "bold"), bg=C["accent"],
                     fg=C["white"], wraplength=150, justify="center").pack()
            for node in self.vs.ballots[pos].all_candidates():
                pc = PARTY_COLORS.get(node.party, C["text_dim"])
                row = tk.Frame(card, bg=C["card"], pady=3)
                row.pack(fill="x")
                tk.Frame(row, bg=pc, width=3).pack(side="left", fill="y", padx=(0,6))
                info = tk.Frame(row, bg=C["card"])
                info.pack(side="left")
                tk.Label(info, text=node.name, font=("Helvetica", 8, "bold"),
                         bg=C["card"], fg=C["text"], wraplength=140, justify="left").pack(anchor="w")
                tk.Label(info, text=node.party, font=("Helvetica", 7),
                         bg=C["card"], fg=pc).pack(anchor="w")

    def _nav_highlight(self, key):
        for k, b in self.nav_btns.items():
            if k == key:
                b.config(bg=C["accent_light"], fg=C["accent"])
            else:
                b.config(bg=C["white"], fg=C["text_dim"])

    # ── REGISTER ──────────────────────────────

    def show_register(self):
        self._nav_highlight("register")
        self.clear_content()
        f = tk.Frame(self.content, bg=C["bg"])
        f.pack(fill="both", expand=True)

        
        col = tk.Frame(f, bg=C["bg"])
        col.place(relx=0.5, rely=0.5, anchor="center")

        card = card_frame(col, padx=40, pady=36)
        card.pack()

        tk.Label(card, text="📋", font=("Georgia", 36), bg=C["card"], fg=C["accent"]).pack()
        tk.Label(card, text="VOTER REGISTRATION", font=FONT_TITLE,
                 bg=C["card"], fg=C["accent"]).pack(pady=(8, 4))
        tk.Label(card, text="Enter your Student ID to register", font=FONT_BODY,
                 bg=C["card"], fg=C["text_dim"]).pack(pady=(0, 20))

        tk.Label(card, text="Student ID  (##-#####)", font=FONT_LABEL,
                 bg=C["card"], fg=C["text_dim"]).pack(anchor="w")

        entry_frame = tk.Frame(card, bg=C["accent"], padx=2, pady=2)
        entry_frame.pack(fill="x", pady=(4, 16))
        self.reg_entry = tk.Entry(entry_frame, font=("Helvetica", 14, "bold"),
                                  bg=C["white"], fg=C["text"], insertbackground=C["accent"],
                                  relief="flat", bd=8, width=22)
        self.reg_entry.pack(fill="x")
        self.reg_entry.bind("<Return>", lambda e: self._do_register())

        self.reg_msg = tk.Label(card, text="", font=FONT_BODY, bg=C["card"], fg=C["success"])
        self.reg_msg.pack(pady=(0, 12))

        styled_btn(card, "Register Now", self._do_register, width=24).pack()

        tk.Label(card, text=f"Total registered: {len(self.vs.voters)}",
                 font=FONT_SMALL, bg=C["card"], fg=C["text_dim"]).pack(pady=(16, 0))
        self.reg_count_lbl = tk.Label(card, text="", font=FONT_SMALL, bg=C["card"], fg=C["text_dim"])
        self.reg_count_lbl.pack()

    def _do_register(self):
        sid = self.reg_entry.get().strip()
        if not sid:
            self.reg_msg.config(text="⚠  Student ID cannot be empty.", fg=C["error"]); return
        if not is_valid_id(sid):
            self.reg_msg.config(text=f"⚠  Invalid format. Use ##-##### (e.g. 25-08323)", fg=C["error"]); return
        ok = self.vs.register_voter(sid)
        if ok:
            self.reg_msg.config(text=f"✓  Registered successfully! Welcome, {sid.upper()}.", fg=C["success"])
            self.reg_entry.delete(0, "end")
            self.set_status(f"{len(self.vs.voters)} voters registered")
        else:
            self.reg_msg.config(text=f"⚠  {sid.upper()} is already registered.", fg=C["warning"])

    # ── VOTE ──────────────────────────────────

    def show_vote(self):
        self._nav_highlight("vote")
        self.clear_content()
        self._vote_sid = None

        outer = tk.Frame(self.content, bg=C["bg"])
        outer.pack(fill="both", expand=True)

        top = card_frame(outer, padx=30, pady=20)
        top.pack(fill="x", padx=30, pady=(20, 10))

        tk.Label(top, text="🗳️  CAST YOUR VOTE", font=FONT_TITLE,
                 bg=C["card"], fg=C["accent"]).pack(side="left")

        right = tk.Frame(top, bg=C["card"])
        right.pack(side="right")
        tk.Label(right, text="Student ID:", font=FONT_LABEL,
                 bg=C["card"], fg=C["text_dim"]).pack(side="left", padx=(0,8))
        self.vote_id_entry = tk.Entry(right, font=FONT_BODY_B, bg=C["white"],
                                      fg=C["text"], insertbackground=C["accent"],
                                      relief="flat", bd=6, width=14,
                                      highlightbackground=C["accent"], highlightthickness=1)
        self.vote_id_entry.pack(side="left", padx=(0,8))
        self.vote_id_entry.bind("<Return>", lambda e: self._load_voter())
        styled_btn(right, "Load", self._load_voter, width=8, pady=4).pack(side="left")

        self.vote_msg = tk.Label(outer, text="Enter your Student ID to begin.",
                                 font=FONT_BODY, bg=C["bg"], fg=C["text_dim"])
        self.vote_msg.pack(pady=(0, 6))

        ballot_outer = tk.Frame(outer, bg=C["bg"])
        ballot_outer.pack(fill="both", expand=True, padx=30, pady=(0, 10))
        self.ballot_frame = scrollable(ballot_outer)

        self.submit_btn = styled_btn(outer, "Submit All Votes", self._submit_votes,
                                     color=C["success"], width=26)
        self.submit_btn.pack(pady=(0, 16))
        self.submit_btn.config(state="disabled")

        self._vote_selections = {}

    def _load_voter(self):
        sid = self.vote_id_entry.get().strip()
        if not is_valid_id(sid):
            self.vote_msg.config(text="⚠  Invalid format. Use ##-#####.", fg=C["error"]); return
        sid = sid.upper()
        if not self.vs.is_registered(sid):
            self.vote_msg.config(text="⚠  Not registered. Please register first.", fg=C["error"]); return
        if self.vs.all_voted(sid):
            self.vote_msg.config(text=f"✓  {sid} has already voted in all positions.", fg=C["warning"]); return

        self._vote_sid = sid
        self.vote_msg.config(text=f"✓  Welcome, {sid}! Select your candidates below.", fg=C["success"])
        self._build_ballot()
        self.submit_btn.config(state="normal")

    def _build_ballot(self):
        for w in self.ballot_frame.winfo_children(): w.destroy()
        self._vote_selections = {}
        sid = self._vote_sid

        for pos in POSITIONS:
            already = self.vs.has_voted_for(sid, pos)
            card = card_frame(self.ballot_frame, padx=20, pady=14)
            card.pack(fill="x", pady=6, padx=4)


            hdr = tk.Frame(card, bg=C["card"])
            hdr.pack(fill="x")
            short = pos.replace("VP For Student Development & Government - ", "VP - ")
            tk.Label(hdr, text=f"📌 {short}", font=FONT_HEAD,
                     bg=C["card"], fg=C["accent"]).pack(side="left")
            if already:
                tk.Label(hdr, text="  ✓ Already voted", font=FONT_SMALL,
                         bg=C["card"], fg=C["success"]).pack(side="left", padx=8)

            tk.Frame(card, bg=C["border"], height=1).pack(fill="x", pady=8)

            if already:
                tk.Label(card, text="You have already cast your vote for this position.",
                         font=FONT_BODY, bg=C["card"], fg=C["text_dim"]).pack(anchor="w")
                continue

            var = tk.StringVar(value="")
            self._vote_selections[pos] = var


            tk.Radiobutton(card, text="— Skip this position —", variable=var, value="",
                           font=FONT_SMALL, bg=C["card"], fg=C["text_dim"],
                           activebackground=C["card"], selectcolor=C["accent_light"],
                           relief="flat").pack(anchor="w", pady=2)

            for node in self.vs.ballots[pos].all_candidates():
                pc = PARTY_COLORS.get(node.party, C["text_dim"])
                row = tk.Frame(card, bg=C["row_alt"], pady=6, padx=8)
                row.pack(fill="x", pady=3)
                rb = tk.Radiobutton(row, variable=var, value=node.name,
                                    bg=C["row_alt"], activebackground=C["accent_light"],
                                    selectcolor=C["accent"], relief="flat")
                rb.pack(side="left")
                tk.Frame(row, bg=pc, width=4).pack(side="left", fill="y", padx=(4, 8))
                info = tk.Frame(row, bg=C["row_alt"])
                info.pack(side="left", padx=4)
                tk.Label(info, text=node.name, font=FONT_BODY_B,
                         bg=C["row_alt"], fg=C["text"]).pack(anchor="w")
                tk.Label(info, text=node.party, font=FONT_SMALL,
                         bg=C["row_alt"], fg=pc).pack(anchor="w")

    def _submit_votes(self):
        if not self._vote_sid:
            return
        sid  = self._vote_sid
        cast = 0
        msgs = []
        for pos, var in self._vote_selections.items():
            chosen = var.get()
            if not chosen: continue
            ok, msg = self.vs.cast_vote(sid, pos, chosen)
            if ok: cast += 1
            msgs.append(("✓ " if ok else "⚠ ") + msg)

        if cast == 0:
            self.vote_msg.config(text="⚠  No votes were selected.", fg=C["warning"]); return

        summary = "\n".join(msgs)
        messagebox.showinfo("Votes Recorded",
                            f"Votes recorded for {sid}:\n\n{summary}\n\n"
                            f"Total positions voted: {cast}  •  Thank you! 🎓")
        self.set_status(f"Votes cast: {self.vs.total_votes_cast()}")
        self._vote_sid = None
        self.vote_id_entry.delete(0, "end")
        self.vote_msg.config(text="Enter your Student ID to begin.", fg=C["text_dim"])
        for w in self.ballot_frame.winfo_children(): w.destroy()
        self.submit_btn.config(state="disabled")

    # ── ADMIN ─────────────────────────────────

    def show_admin(self):
        self._nav_highlight("admin")
        self.clear_content()

        gate = tk.Frame(self.content, bg=C["bg"])
        gate.place(relx=0.5, rely=0.5, anchor="center")

        card = card_frame(gate, padx=40, pady=36)
        card.pack()
        tk.Label(card, text="🔒", font=("Georgia", 36), bg=C["card"]).pack()
        tk.Label(card, text="ADMIN PANEL", font=FONT_TITLE,
                 bg=C["card"], fg=C["accent"]).pack(pady=(8,4))
        tk.Label(card, text="Enter admin password to continue", font=FONT_BODY,
                 bg=C["card"], fg=C["text_dim"]).pack(pady=(0,16))

        tk.Label(card, text="Password", font=FONT_LABEL,
                 bg=C["card"], fg=C["text_dim"]).pack(anchor="w")
        ef = tk.Frame(card, bg=C["accent"], padx=2, pady=2)
        ef.pack(fill="x", pady=(4,16))
        pwd_entry = tk.Entry(ef, font=("Helvetica", 14), show="●",
                             bg=C["white"], fg=C["text"],
                             insertbackground=C["accent"], relief="flat", bd=8, width=22)
        pwd_entry.pack(fill="x")

        err_lbl = tk.Label(card, text="", font=FONT_BODY, bg=C["card"], fg=C["error"])
        err_lbl.pack(pady=(0,8))

        def try_login(e=None):
            if pwd_entry.get() == ADMIN_PASSWORD:
                gate.destroy()
                self._show_admin_dashboard()
            else:
                err_lbl.config(text="⚠  Incorrect password.")

        pwd_entry.bind("<Return>", try_login)
        styled_btn(card, "Enter", try_login, width=24).pack()

    def _show_admin_dashboard(self):
        self.clear_content()
        outer = tk.Frame(self.content, bg=C["bg"])
        outer.pack(fill="both", expand=True)


        tab_bar = tk.Frame(outer, bg=C["surface2"])
        tab_bar.pack(fill="x")
        tk.Frame(outer, bg=C["divider"], height=1).pack(fill="x")

        tab_content = tk.Frame(outer, bg=C["bg"])
        tab_content.pack(fill="both", expand=True)

        self._admin_tabs = {}

        def switch_tab(key):
            for k, b in self._admin_tabs.items():
                b.config(bg=C["accent"] if k==key else C["surface2"],
                         fg=C["white"]  if k==key else C["text_dim"])
            for w in tab_content.winfo_children(): w.destroy()
            {"leaderboard": lambda: self._admin_leaderboard(tab_content),
             "voters"     : lambda: self._admin_voters(tab_content),
             "export"     : lambda: self._admin_export(tab_content)}[key]()

        for label, key in [("📊 Leaderboard", "leaderboard"),
                           ("👥 Voters",      "voters"),
                           ("💾 Export",      "export")]:
            b = tk.Button(tab_bar, text=label, font=FONT_BTN,
                          bg=C["surface2"], fg=C["text_dim"],
                          activebackground=C["accent"], activeforeground=C["white"],
                          relief="flat", bd=0, padx=24, pady=10, cursor="hand2",
                          command=lambda k=key: switch_tab(k))
            b.pack(side="left")
            self._admin_tabs[key] = b

        switch_tab("leaderboard")

    def _admin_leaderboard(self, parent):
        outer = tk.Frame(parent, bg=C["bg"])
        outer.pack(fill="both", expand=True, padx=20, pady=16)

        tk.Label(outer, text=f"📊  LIVE LEADERBOARD  —  Total votes: {self.vs.total_votes_cast()}",
                 font=FONT_HEAD, bg=C["bg"], fg=C["accent"]).pack(pady=(0, 12))

        scroll_outer = tk.Frame(outer, bg=C["bg"])
        scroll_outer.pack(fill="both", expand=True)
        frame = scrollable(scroll_outer)

        results = self.vs.get_results()
        for pos in POSITIONS:
            data = results[pos]
            card = card_frame(frame, padx=20, pady=14)
            card.pack(fill="x", pady=6, padx=2)

            short = pos.replace("VP For Student Development & Government - ", "VP - ")
            tk.Label(card, text=f"📌 {short}", font=FONT_HEAD,
                     bg=C["card"], fg=C["accent"]).pack(anchor="w")
            tk.Frame(card, bg=C["border"], height=1).pack(fill="x", pady=8)

            sorted_c = sorted(data["candidates"], key=lambda x: x[2], reverse=True)
            max_v = max((v for _, _, v in sorted_c), default=1) or 1

            winner_name = data["winner"][0] if data["winner"] else ""

            for name, party, votes in sorted_c:
                row = tk.Frame(card, bg=C["card"])
                row.pack(fill="x", pady=3)

                is_win = (name == winner_name and votes > 0)
                pc = PARTY_COLORS.get(party, C["text_dim"])

                lbl_frame = tk.Frame(row, bg=C["card"], width=230)
                lbl_frame.pack(side="left"); lbl_frame.pack_propagate(False)

                crown = "🏆 " if is_win else "   "
                tk.Label(lbl_frame, text=f"{crown}{name}", font=FONT_BODY_B,
                         bg=C["card"], fg=C["accent"] if is_win else C["text"]).pack(anchor="w")
                tk.Label(lbl_frame, text=f"    {party}", font=FONT_SMALL,
                         bg=C["card"], fg=pc).pack(anchor="w")

                bar_bg = tk.Frame(row, bg=C["bar_bg"], height=22, width=300)
                bar_bg.pack(side="left", padx=(10, 8), pady=2)
                bar_bg.pack_propagate(False)
                fill_w = max(4, int((votes / max_v) * 280)) if max_v > 0 else 4
                bar_fill = tk.Frame(bar_bg, bg=C["accent"] if is_win else pc,
                                    height=22, width=fill_w)
                bar_fill.place(x=0, y=0)

                tk.Label(row, text=f"{votes} vote(s)", font=FONT_SMALL,
                         bg=C["card"], fg=C["text_dim"]).pack(side="left")

        refresh_btn = styled_btn(outer, "🔄 Refresh", lambda: self._refresh_leaderboard(parent),
                                 width=18, pady=6)
        refresh_btn.pack(pady=(12, 0))

    def _refresh_leaderboard(self, parent):
        for w in parent.winfo_children(): w.destroy()
        self._admin_leaderboard(parent)

    def _admin_voters(self, parent):
        outer = tk.Frame(parent, bg=C["bg"])
        outer.pack(fill="both", expand=True, padx=20, pady=16)

        tk.Label(outer, text=f"👥  REGISTERED VOTERS  ({len(self.vs.voters)} total)",
                 font=FONT_HEAD, bg=C["bg"], fg=C["accent"]).pack(pady=(0, 12))

        thead = tk.Frame(outer, bg=C["surface2"], pady=6)
        thead.pack(fill="x")
        for txt, w in [("Student ID", 16), ("Positions Voted", 60)]:
            tk.Label(thead, text=txt, font=FONT_BODY_B, bg=C["surface2"],
                     fg=C["accent"], width=w, anchor="w").pack(side="left", padx=8)

        scroll_outer = tk.Frame(outer, bg=C["bg"])
        scroll_outer.pack(fill="both", expand=True)
        frame = scrollable(scroll_outer)

        for i, (sid, voted) in enumerate(self.vs.voters.items()):
            row_bg = C["white"] if i % 2 == 0 else C["row_alt"]
            row = tk.Frame(frame, bg=row_bg, pady=6)
            row.pack(fill="x")
            tk.Label(row, text=sid, font=FONT_BODY_B, bg=row_bg,
                     fg=C["accent"], width=16, anchor="w").pack(side="left", padx=8)
            voted_str = ", ".join(p.replace("VP For Student Development & Government - ","VP ")
                                  for p in voted) if voted else "— None yet"
            color = C["success"] if len(voted)==len(POSITIONS) else C["text_dim"]
            tk.Label(row, text=voted_str, font=FONT_SMALL, bg=row_bg,
                     fg=color, anchor="w").pack(side="left", padx=8)

    def _admin_export(self, parent):
        outer = tk.Frame(parent, bg=C["bg"])
        outer.pack(fill="both", expand=True, padx=20, pady=16)

        tk.Label(outer, text="💾  EXPORT RESULTS", font=FONT_HEAD,
                 bg=C["bg"], fg=C["accent"]).pack(pady=(0, 12))


        preview_frame = card_frame(outer, padx=16, pady=16)
        preview_frame.pack(fill="both", expand=True)

        text = tk.Text(preview_frame, font=("Courier New", 10), bg=C["surface2"],
                       fg=C["text"], relief="flat", bd=0, state="disabled",
                       wrap="none")
        sb = ttk.Scrollbar(preview_frame, command=text.yview)
        text.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        text.pack(fill="both", expand=True)

        self.result_text_widget = text
        self._refresh_preview()

        btns = tk.Frame(outer, bg=C["bg"])
        btns.pack(pady=12)
        styled_btn(btns, "🔄 Refresh Preview", self._refresh_preview, width=20, pady=6).pack(side="left", padx=8)
        styled_btn(btns, "💾 Save to File",    self._save_results,    width=20, pady=6,
                   color=C["success"]).pack(side="left", padx=8)

    def _refresh_preview(self):
        results = self.vs.get_results()
        lines   = []
        lines.append(f"SPARTALIST — {SCHOOL_NAME}")
        lines.append(f"Election Results — {datetime.now().strftime('%B %d, %Y %I:%M %p')}")
        lines.append("=" * 60)
        for pos in POSITIONS:
            data = results[pos]
            lines.append(f"\nPOSITION: {pos}")
            lines.append("-" * 40)
            sorted_c = sorted(data["candidates"], key=lambda x: x[2], reverse=True)
            for name, party, votes in sorted_c:
                tag = " <-- WINNER" if data["winner"] and name==data["winner"][0] and votes>0 else ""
                lines.append(f"  {name:<28} ({party})  --  {votes} vote(s){tag}")
        lines.append("\n" + "=" * 60)
        lines.append(f"Total registered voters : {len(self.vs.voters)}")
        lines.append(f"Total votes cast        : {self.vs.total_votes_cast()}")
        content = "\n".join(lines)

        t = self.result_text_widget
        t.config(state="normal")
        t.delete("1.0", "end")
        t.insert("1.0", content)
        t.config(state="disabled")
        return content

    def _save_results(self):
        content = self._refresh_preview()
        try:
            with open(RESULTS_FILENAME, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Saved", f"Results saved to:\n{RESULTS_FILENAME}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app = SpartalistApp()
    style = ttk.Style(app)
    style.theme_use("default")
    style.configure("Vertical.TScrollbar", background=C["surface2"],
                    troughcolor=C["bg"], arrowcolor=C["accent"])
    app.mainloop()