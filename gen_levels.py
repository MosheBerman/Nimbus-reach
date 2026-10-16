#!/usr/bin/env python3
"""Build the 12 new Nimbus-reach levels (indices 18-29) + COMBOS + THEMES.

Validation: rectangular rows, legend-only chars, exactly one 'S', >=1 gem,
locks <= keys, plus jump-aware BFS reachability (keys reachable with locks
closed; all gems/keys reachable with locks open). Paint/spring levels (27,28)
skip BFS - they need paint/spring traversal.
Emit: /tmp/nr_levels.js, /tmp/nr_combos.js, /tmp/nr_themes.js
"""
from collections import deque

LEGEND = set(".#WSkLpoFPjcialevm12346789*f")  # no '5'
SKIP_BFS = {27, 28}  # paint / spring traversal


def blank(w, h, ch="#"):
    return [[ch] * w for _ in range(h)]


def rect(g, x, y, w, h, ch):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            g[yy][xx] = ch


def hline(g, x1, x2, y, ch):
    for xx in range(min(x1, x2), max(x1, x2) + 1):
        g[y][xx] = ch


def vline(g, x, y1, y2, ch):
    for yy in range(min(y1, y2), max(y1, y2) + 1):
        g[yy][x] = ch


def put(g, x, y, ch):
    g[y][x] = ch


def rows(g):
    return ["".join(r) for r in g]


def seg(g, pts, ch):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 == x1:
            vline(g, x0, y0, y1, ch)
        else:
            hline(g, x0, x1, y0, ch)


# ---------------- L18: Room to Room (doorless rooms) ----------------
def l18():
    g = blank(24, 11)
    vline(g, 8, 0, 10, "W"); put(g, 8, 2, "#"); put(g, 8, 8, "#")
    vline(g, 16, 0, 10, "W"); put(g, 16, 2, "#"); put(g, 16, 8, "#")
    hline(g, 0, 23, 5, "W")
    for x in (4, 12, 20):
        put(g, x, 5, "#")
    put(g, 1, 1, "S")
    for x, y in [(3, 1), (5, 3), (10, 1), (13, 3), (19, 1), (21, 3),
                 (3, 7), (5, 9), (10, 7), (13, 9), (19, 7), (21, 9), (12, 2)]:
        put(g, x, y, "*")
    put(g, 14, 1, "F"); put(g, 10, 9, "F")
    put(g, 18, 3, "o"); put(g, 22, 7, "o")
    put(g, 20, 9, "e")
    return ("Room to Room", 170, True, rows(g))


# ---------------- L19: Veilwalk (invisible walls) ----------------
def l19():
    g = blank(24, 11)
    hline(g, 10, 15, 4, "v"); hline(g, 10, 15, 7, "v")
    vline(g, 10, 4, 7, "v"); vline(g, 15, 4, 7, "v")
    put(g, 10, 6, "#")  # entrance gap
    for x, y in [(12, 5), (13, 5), (12, 6), (13, 6)]:
        put(g, x, y, "*")
    put(g, 2, 9, "*"); put(g, 23, 9, "*")
    hline(g, 16, 23, 8, "v"); hline(g, 16, 23, 10, "v")  # east veil hallway
    put(g, 20, 9, ".")  # hole to jump
    vline(g, 8, 1, 3, "v")  # hidden vertical wall...
    put(g, 5, 2, "e")       # ...this patrol reveals it
    put(g, 18, 5, "f")
    put(g, 1, 1, "S")
    put(g, 21, 2, "o")
    return ("Veilwalk", 170, True, rows(g))


# ---------------- L20: Dead Ends (walled maze) ----------------
def l20():
    import random
    W, H = 25, 13
    CW, CH = 12, 6
    rnd = random.Random(20261016)
    seen = [[False] * CW for _ in range(CH)]
    vw = [[True] * (CW + 1) for _ in range(CH)]
    hw = [[True] * CW for _ in range(CH + 1)]
    stack = [(0, 0)]; seen[0][0] = True
    while stack:
        cx, cy = stack[-1]
        opts = []
        for dx, dy, tag in ((1, 0, "e"), (-1, 0, "w"), (0, 1, "s"), (0, -1, "n")):
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < CW and 0 <= ny < CH and not seen[ny][nx]:
                opts.append((nx, ny, tag))
        if not opts:
            stack.pop(); continue
        nx, ny, tag = rnd.choice(opts)
        seen[ny][nx] = True
        if tag == "e": vw[cy][cx + 1] = False
        elif tag == "w": vw[cy][cx] = False
        elif tag == "s": hw[cy + 1][cx] = False
        else: hw[cy][cx] = False
        stack.append((nx, ny))
    g = blank(W, H, "W")
    for cy in range(CH):
        for cx in range(CW):
            tx, ty = 1 + 2 * cx, 1 + 2 * cy
            put(g, tx, ty, "#")
            if not vw[cy][cx + 1]: put(g, tx + 1, ty, "#")
            if not hw[cy + 1][cx]: put(g, tx, ty + 1, "#")
    dead = []
    for cy in range(CH):
        for cx in range(CW):
            if (cx, cy) == (0, 0):
                continue
            open_n = (not vw[cy][cx]) + (not vw[cy][cx + 1]) + (not hw[cy][cx]) + (not hw[cy + 1][cx])
            if open_n == 1:
                dead.append((cx, cy))
    rnd.shuffle(dead)
    assert len(dead) >= 8, f"only {len(dead)} dead ends"
    put(g, 1, 1, "S")
    for cx, cy in dead[:2]:  # sealed treasure nooks: 1 lock each
        tx, ty = 1 + 2 * cx, 1 + 2 * cy
        if not vw[cy][cx]: lx, ly = tx - 1, ty
        elif not vw[cy][cx + 1]: lx, ly = tx + 1, ty
        elif not hw[cy][cx]: lx, ly = tx, ty - 1
        else: lx, ly = tx, ty + 1
        assert g[ly][lx] == "#", "lock tile not corridor"
        put(g, lx, ly, "L")
        put(g, tx, ty, "*")
    for cx, cy in dead[2:4]:
        put(g, 1 + 2 * cx, 1 + 2 * cy, "k")
    for cx, cy in dead[4:8]:
        put(g, 1 + 2 * cx, 1 + 2 * cy, "*")
    placed = 0
    for cy in range(CH - 1, -1, -1):
        for cx in range(CW - 1, -1, -1):
            if placed >= 2:
                break
            tx, ty = 1 + 2 * cx, 1 + 2 * cy
            if g[ty][tx] == "#" and abs(tx - 1) + abs(ty - 1) > 12:
                put(g, tx, ty, "e" if placed == 0 else "f"); placed += 1
        if placed >= 2:
            break
    return ("Dead Ends", 210, True, rows(g))


# ---------------- L21: Icewind Spiral ----------------
def l21():
    W, H = 30, 13
    g = blank(W, H)
    pts = [(1, 1), (18, 1), (18, 11), (1, 11), (1, 3), (16, 3),
           (16, 9), (3, 9), (3, 5), (14, 5), (14, 7), (5, 7), (5, 6)]
    seg(g, pts, "i")
    # corner wall stubs on the outer side of each turn
    for x, y in [(19, 1), (19, 11), (1, 12), (1, 2), (16, 2), (16, 10),
                 (3, 10), (3, 4), (14, 4), (14, 8), (5, 8)]:
        assert g[y][x] == "#", f"stub {(x, y)} hits path"
        put(g, x, y, "W")
    for x, y in [(10, 1), (18, 7), (9, 11), (10, 3), (12, 9), (9, 5)]:
        assert g[y][x] == "i", f"gem {(x, y)} not on ice"
        put(g, x, y, "*")
    put(g, 1, 1, "S")
    hline(g, 5, 19, 6, "i")   # exit east
    put(g, 19, 6, "#")
    hline(g, 20, 23, 6, "#")  # transition strip
    put(g, 21, 6, "."); put(g, 22, 6, ".")  # 2-wide hole: jump at ice speed
    put(g, 20, 5, "*"); put(g, 23, 7, "*")
    put(g, 23, 7, "e")
    # checkerboard chamber x24-29 y1-6, 2x2 ground center with 4 gems
    for yy in range(1, 7):
        for xx in range(24, 30):
            if (xx, yy) in ((26, 3), (27, 3), (26, 4), (27, 4)):
                put(g, xx, yy, "*")
            elif (xx + yy) % 2 == 0:
                put(g, xx, yy, "i")
    rect(g, 24, 8, 6, 4, "#")  # top-right plain area
    for x, y in [(24, 8), (26, 8), (28, 8), (25, 10), (27, 10), (29, 11)]:
        put(g, x, y, "*")
    return ("Icewind Spiral", 190, True, rows(g))


# ---------------- L22: Ember Holes (lava + doors) ----------------
def l22():
    W, H = 26, 12
    g = blank(W, H, "l")
    rect(g, 1, 9, 4, 3, "#"); put(g, 2, 10, "S"); put(g, 4, 9, "o")
    vline(g, 2, 5, 8, "#"); hline(g, 2, 10, 5, "#")
    vline(g, 8, 1, 4, "#"); hline(g, 8, 18, 1, "#")
    vline(g, 10, 5, 6, "#"); hline(g, 10, 16, 6, "#")
    vline(g, 16, 6, 10, "#"); hline(g, 14, 22, 10, "#")
    put(g, 5, 5, "."); put(g, 12, 6, ".")  # holes in the path
    for x, y in [(8, 2), (11, 1), (13, 6), (15, 10)]:  # keys on the path
        assert g[y][x] == "#", f"key {(x, y)} not on ground"
        put(g, x, y, "k")
    # middle-right room, 1 lock, ground outside
    for x in range(19, 25):
        put(g, x, 5, "W"); put(g, x, 9, "W")
    for y in range(5, 10):
        put(g, 19, y, "W"); put(g, 24, y, "W")
    rect(g, 20, 6, 4, 3, "#")
    put(g, 21, 9, "L")
    for x, y in [(20, 6), (22, 6), (23, 8)]:
        put(g, x, y, "*")
    # top room: vestibule + 2 subchambers, double doors on the right one
    for x in range(19, 26):
        put(g, x, 1, "W"); put(g, x, 4, "W")
    for y in range(1, 5):
        put(g, 19, y, "W"); put(g, 25, y, "W")
    vline(g, 22, 1, 4, "W")
    put(g, 22, 2, "L"); put(g, 22, 3, "L")
    put(g, 19, 2, "L")  # main door, no ground outside: jump-unlock
    rect(g, 20, 2, 2, 2, "#"); rect(g, 23, 2, 2, 2, "#")
    put(g, 20, 2, "*"); put(g, 21, 3, "*")
    for x, y in [(23, 2), (24, 2), (23, 3), (24, 3)]:
        put(g, x, y, "*")
    put(g, 6, 5, "e"); put(g, 16, 8, "f")
    return ("Ember Holes", 200, True, rows(g))


# ---------------- L23: Skipping Stones (open chambers) ----------------
def l23():
    W, H = 30, 13
    g = blank(W, H, ".")
    rect(g, 1, 9, 4, 3, "#"); put(g, 2, 10, "S")
    put(g, 1, 9, "*"); put(g, 4, 11, "*"); put(g, 3, 10, "o")
    rect(g, 7, 8, 3, 3, "#"); put(g, 7, 8, "*"); put(g, 9, 10, "*")
    rect(g, 12, 9, 4, 3, "#"); put(g, 12, 9, "j")
    put(g, 14, 9, "*"); put(g, 15, 11, "*")
    rect(g, 17, 7, 3, 3, "#"); put(g, 18, 7, "*")
    rect(g, 22, 8, 4, 3, "#"); put(g, 24, 8, "j"); put(g, 25, 9, "e")
    put(g, 23, 10, "*")
    rect(g, 26, 4, 3, 3, "#"); put(g, 27, 5, "F")
    put(g, 26, 4, "*"); put(g, 28, 6, "*")
    rect(g, 22, 5, 2, 2, "#"); put(g, 22, 5, "*")
    rect(g, 18, 4, 2, 2, "#"); put(g, 18, 4, "*")
    rect(g, 12, 2, 5, 3, "#"); put(g, 13, 2, "f")
    put(g, 12, 4, "*"); put(g, 16, 4, "*")
    return ("Skipping Stones", 180, False, rows(g))


# ---------------- L24: Arrow Run ----------------
def l24():
    W, H = 30, 11
    g = blank(W, H, ".")
    put(g, 1, 5, "S"); hline(g, 2, 3, 5, "#")
    hline(g, 4, 11, 5, "6")
    put(g, 12, 5, "3"); put(g, 13, 6, "3")  # the diagonal that throws you off
    hline(g, 15, 18, 6, "6")
    rect(g, 19, 3, 6, 4, "#")   # the 4x6 island
    hline(g, 19, 24, 7, "4")    # return arrows along the bottom
    put(g, 18, 7, "2")          # corner points down...
    rect(g, 16, 8, 3, 2, "#")   # ...onto plain tiles
    put(g, 17, 9, "o")
    hline(g, 25, 27, 4, "6")    # arrows continue right
    put(g, 28, 4, ".")          # the hole
    put(g, 29, 4, "*")          # the ONLY diamond
    return ("Arrow Run", 160, True, rows(g))


# ---------------- L25: Magnet Mile ----------------
def l25():
    W, H = 26, 13
    g = blank(W, H, ".")
    cols = [22, 19, 16, 13, 10, 7, 4]
    span = {22: (2, 10), 19: (2, 10), 16: (2, 10), 13: (4, 10),
            10: (2, 10), 7: (2, 11), 4: (2, 10)}
    for x in cols:
        y0, y1 = span[x]
        vline(g, x, y0, y1, "m")
    for a, b, y in [(22, 19, 10), (19, 16, 2), (16, 13, 4),
                    (13, 10, 10), (10, 7, 2), (7, 4, 10)]:
        hline(g, b, a, y, "m")
    put(g, 23, 11, "S"); put(g, 22, 11, "#"); put(g, 24, 11, "#")
    put(g, 4, 11, "#"); put(g, 3, 11, "#")
    put(g, 3, 11, "p")   # soup on the runway (item on ground)
    put(g, 2, 11, ".")   # the final hole
    rect(g, 0, 11, 2, 1, "#")
    put(g, 0, 11, "*"); put(g, 1, 11, "*")
    for x, y in [(22, 4), (19, 8), (16, 5), (13, 7), (10, 4), (7, 8), (4, 5)]:
        assert g[y][x] == "m", f"gem {(x, y)} not on magnet"
        put(g, x, y, "*")
    put(g, 19, 6, "f"); put(g, 17, 2, "e"); put(g, 10, 6, "f")
    return ("Magnet Mile", 180, True, rows(g))


# ---------------- L26: Patrol Hall ----------------
def l26():
    W, H = 28, 13
    g = blank(W, H, "#")
    rect(g, 2, 2, 24, 9, "W")  # interior block -> 1-wide hallway ring
    put(g, 1, 1, "S")
    hline(g, 8, 12, 1, "c"); vline(g, 26, 5, 7, "c"); hline(g, 18, 22, 11, "c")
    for x, y in [(3, 1), (14, 1), (25, 1), (26, 9), (14, 11), (3, 11), (1, 3), (1, 9)]:
        put(g, x, y, "*")
    put(g, 5, 1, "e"); put(g, 20, 11, "e")
    put(g, 26, 4, "f"); put(g, 1, 8, "f")
    put(g, 10, 11, "o")
    return ("Patrol Hall", 170, True, rows(g))


# ---------------- L27: Prism Vault (diamond paint) ----------------
def l27():
    W, H = 30, 13
    g = blank(W, H, ".")
    put(g, 26, 1, "S")
    put(g, 27, 1, "P"); put(g, 26, 2, "P")  # paint pots right and below
    rect(g, 26, 10, 2, 2, "#"); put(g, 27, 11, "k"); put(g, 26, 10, "o")
    for x, y in [(22, 5), (18, 10), (10, 10)]:  # refills within reach
        put(g, x, y, "P")
    for x in range(8, 20):  # center room, wall border...
        put(g, x, 4, "W"); put(g, x, 8, "W")
    for y in range(4, 9):
        put(g, 8, y, "W"); put(g, 19, y, "W")
    put(g, 13, 8, "L")
    rect(g, 9, 5, 10, 3, "#")
    for yy in range(5, 8):
        for xx in range(9, 19):
            if (xx, yy) not in ((11, 6), (15, 6)):
                put(g, xx, yy, "*")  # diamonds on almost every tile
    put(g, 11, 6, "e"); put(g, 15, 6, "e")  # trapped by gems until freed
    return ("Prism Vault", 230, False, rows(g))


# ---------------- L28: Springtide ----------------
def l28():
    W, H = 24, 14
    g = blank(W, H, ".")
    rect(g, 1, 11, 5, 2, "#"); put(g, 2, 12, "S"); put(g, 4, 11, "j")
    put(g, 1, 11, "*"); put(g, 5, 12, "*")
    rect(g, 8, 9, 4, 2, "#"); put(g, 9, 9, "j")
    put(g, 8, 9, "*"); put(g, 11, 10, "*")
    rect(g, 14, 7, 4, 2, "#"); put(g, 15, 7, "j"); put(g, 16, 7, "F")
    put(g, 14, 7, "*"); put(g, 17, 8, "*")
    rect(g, 7, 5, 4, 2, "#"); put(g, 8, 5, "j")
    put(g, 7, 5, "*"); put(g, 10, 6, "*")
    rect(g, 13, 3, 4, 2, "#"); put(g, 14, 3, "j"); put(g, 16, 3, "F")
    put(g, 13, 3, "*"); put(g, 16, 4, "*")
    rect(g, 19, 1, 4, 2, "#")
    for x, y in [(19, 1), (21, 1), (19, 2), (22, 2)]:
        put(g, x, y, "*")
    return ("Springtide", 180, False, rows(g))


# ---------------- L29: Daylight Run ----------------
def l29():
    W, H = 34, 11
    g = blank(W, H, ".")
    rect(g, 1, 4, 4, 3, "#"); put(g, 2, 5, "S"); put(g, 3, 6, "e")
    hline(g, 5, 30, 4, "c"); hline(g, 5, 30, 5, "c")
    for x in (12, 20, 27):
        put(g, x, 4, "."); put(g, x, 5, ".")
    for x in (10, 18, 25):
        put(g, x, 4, "o")
    for x in (8, 14, 22, 28):
        put(g, x, 5, "*")
    rect(g, 31, 3, 3, 5, "#")
    for x, y in [(31, 3), (32, 4), (33, 5), (31, 7)]:
        put(g, x, y, "*")
    return ("Daylight Run", 100, False, rows(g))


BUILDERS = [l18, l19, l20, l21, l22, l23, l24, l25, l26, l27, l28, l29]
KINGDOMS = [6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9]

COMBOS_ADD = [
    {"mon": {"puff": 2}, "pow": ["shield", "clock"]},
    {"mon": {"puff": 2}, "pow": ["freeze", "clock"]},
    {"mon": {"puff": 3}, "pow": ["shield", "soup"]},
    {"mon": {"puff": 2}, "pow": ["speed", "clock"]},
    {"mon": {"puff": 3}, "pow": ["shield", "soup"]},
    {"mon": {"puff": 2}, "pow": ["fly", "clock"]},
    {"mon": {"puff": 2}, "pow": ["speed", "shield"]},
    {"mon": {"puff": 3}, "pow": ["magnet", "soup"]},
    {"mon": {"puff": 4}, "pow": ["freeze", "clock"]},
    {"mon": {"puff": 3}, "pow": ["paint", "shield"]},
    {"mon": {"puff": 2}, "pow": ["fly", "clock"]},
    {"mon": {"puff": 2}, "pow": ["speed", "clock"]},
]

THEMES_ADD = [
    {"id": "vault", "name": "The Vaults",
     "sky": ["#1a1030", "#4a2d70", "#8a6ac0"], "ground": ["#d8d0e8", "#8a7ab0", "#5a4a80"],
     "wall": ["#6a5a9a", "#3a2d5a", "#241a3a"], "paint": "#7ef0d2", "haze": "#c0b0e8"},
    {"id": "rift", "name": "Shatter Isles",
     "sky": ["#0e2a33", "#2a6a7a", "#9adfff"], "ground": ["#dfe8e4", "#8aa8a0", "#556a64"],
     "wall": ["#e08a5a", "#a05a3a", "#5a3020"], "paint": "#ffd84a", "haze": "#cfeef2"},
    {"id": "gauntlet", "name": "The Gauntlet",
     "sky": ["#2a1a08", "#7a4a1a", "#ffb050"], "ground": ["#f0e0c0", "#b09060", "#705830"],
     "wall": ["#d0d0e8", "#7070a0", "#3a3a60"], "paint": "#ff86d0", "haze": "#ffe8c0"},
    {"id": "prism", "name": "Prism Skies",
     "sky": ["#1a3a6a", "#5aa8e8", "#e8f8ff"], "ground": ["#f8f0ff", "#c0a8e8", "#8870b8"],
     "wall": ["#ffd0e8", "#e87aa8", "#a04a78"], "paint": "#6ff0c0", "haze": "#ffffff"},
]


def bfs(map_rows, pass_locks):
    H, Wd = len(map_rows), len(map_rows[0])
    block = set(".Wv") | (set() if pass_locks else {"L"})
    start = next((x, y) for y in range(H) for x in range(Wd) if map_rows[y][x] == "S")
    seen = {start}
    dq = deque([start])
    while dq:
        x, y = dq.popleft()
        for dy in range(-2, 3):
            for dx in range(-3, 4):
                if dx == 0 and dy == 0:
                    continue
                if max(abs(dx), abs(dy)) > 2 and not (abs(dx) <= 3 and abs(dy) <= 1):
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < Wd and 0 <= ny < H and (nx, ny) not in seen \
                        and map_rows[ny][nx] not in block:
                    seen.add((nx, ny))
                    dq.append((nx, ny))
    return seen


def validate(idx, name, map_rows):
    errs = []
    widths = {len(r) for r in map_rows}
    if len(widths) != 1:
        errs.append(f"ragged rows: {sorted(widths)}")
    flat = "".join(map_rows)
    bad = set(flat) - LEGEND
    if bad:
        errs.append(f"bad chars: {sorted(bad)}")
    if flat.count("S") != 1:
        errs.append(f"S count = {flat.count('S')}")
    if flat.count("*") < 1:
        errs.append("no gems")
    if flat.count("L") > flat.count("k"):
        errs.append(f"locks {flat.count('L')} > keys {flat.count('k')}")
    if idx not in SKIP_BFS:
        gems = {(x, y) for y, r in enumerate(map_rows) for x, ch in enumerate(r) if ch == "*"}
        keys = {(x, y) for y, r in enumerate(map_rows) for x, ch in enumerate(r) if ch == "k"}
        n_locks = flat.count("L")
        r_open = bfs(map_rows, True)
        r_shut = bfs(map_rows, False)
        if not gems <= r_open:
            errs.append(f"gems unreachable even unlocked: {sorted(gems - r_open)}")
        if n_locks:
            if idx == 20:  # maze: fungible keys, one reachable key bootstraps
                if len(keys & r_shut) < 1:
                    errs.append("no key reachable before unlocking")
            elif not keys <= r_shut:
                errs.append(f"keys behind locks: {sorted(keys - r_shut)}")
        else:
            if not keys <= r_shut:
                errs.append(f"keys unreachable: {sorted(keys - r_shut)}")
        if not keys <= r_open:
            errs.append(f"keys unreachable even unlocked: {sorted(keys - r_open)}")
    return errs


def main():
    levels = []
    ok = True
    for i, b in enumerate(BUILDERS):
        name, time, walled, map_rows = b()
        idx = 18 + i
        errs = validate(idx, name, map_rows)
        flat = "".join(map_rows)
        print(f"{'OK ' if not errs else 'FAIL'} L{idx} {name!r}: "
              f"{len(map_rows[0])}x{len(map_rows)} gems={flat.count('*')} "
              f"locks={flat.count('L')} keys={flat.count('k')} "
              f"time={time} walled={walled} k={KINGDOMS[i]}")
        for r in map_rows:
            print("   |" + r + "|")
        for e in errs:
            ok = False
            print(f"   !! {e}")
        levels.append((KINGDOMS[i], name, time, walled, map_rows))
    assert ok, "VALIDATION FAILED"
    assert len(COMBOS_ADD) == 12 == len(levels)

    def js(s):
        return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"

    group_comment = {0: "The Vaults", 3: "Shatter Isles", 6: "The Gauntlet", 9: "Prism Skies"}
    lines = []
    for i, (k, name, time, walled, map_rows) in enumerate(levels):
        if i in group_comment:
            lines.append(f"\n  // ---- {group_comment[i]} ----")
        lines.append(f"  {{ k:{k}, name:{js(name)}, time:{time}, "
                     f"walled:{str(walled).lower()}, map:[")
        lines += [f"    {js(r)}," for r in map_rows]
        lines.append("  ]},")
    open("/tmp/nr_levels.js", "w").write("\n".join(lines) + "\n")

    cl = [f"  {{ mon:{{ puff:{c['mon']['puff']} }}, "
          f"pow:[{','.join(js(p) for p in c['pow'])}] }}," for c in COMBOS_ADD]
    open("/tmp/nr_combos.js", "w").write("\n".join(cl) + "\n")

    tl = []
    for t in THEMES_ADD:
        tl.append(
            '  { id:"%s", name:"%s", sky:["%s"], ground:["%s"], wall:["%s"], paint:"%s", haze:"%s" },'
            % (t["id"], t["name"], '","'.join(t["sky"]), '","'.join(t["ground"]),
               '","'.join(t["wall"]), t["paint"], t["haze"]))
    open("/tmp/nr_themes.js", "w").write("\n".join(tl) + "\n")
    print("wrote /tmp/nr_levels.js /tmp/nr_combos.js /tmp/nr_themes.js")


if __name__ == "__main__":
    main()
