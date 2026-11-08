#!/usr/bin/env python3
"""Draw gate-level schematics for worksheets from a netlist (schemdraw, black and white).

Needs: pip install schemdraw matplotlib

    import sys; sys.path.insert(0, "<skill>/scripts")   # or copy this file next to wslib.py
    from logic_fig import circuit
    circuit("figs/redundant.svg",
            inputs=["a", "b", "c"],
            gates=[("g1", "AND", "a b"),
                   ("g2", "AND", "~a c"),          # ~x = inversion bubble on that input
                   ("g3", "AND", "b c"),
                   ("z",  "OR",  "g1 g2 g3")],
            marks={"g3": "s-a-0"})                  # x on a net (stem) with a label

Gate types: AND OR NAND NOR XOR XNOR NOT BUF. Every net is named after the gate that drives it.
Layout is automatic: column = logic level, row = average height of the gate's sources,
vertical wire tracks in the gaps are ordered to minimise crossings, junction dots are added
where wires branch. Optional arguments:
    outputs     nets drawn as primary outputs (default: nets that drive no gate)
    marks       {"net": "s-a-1"} marks the stem right after its driver;
                {"net>gate": "s-a-0"} marks the fan-out branch of net into gate
    bridges     [("p", "q", "bridge")] dashed short between two nets, with a label
    gate_labels {"g1": "G1"} instance name printed inside/above a gate
    net_labels  True (default) prints internal net names on gate outputs
    y           {"name": y} position hints for inputs or gates (larger y = higher)
    level       {"gate": column} force a gate into a later column
Any wire that runs through a gate is reported as a warning: fix it with `y` hints.
Always look at the result (open the PNG, or render the sheet page) before using it.
Write .svg for crisp print output (Typst embeds it), or .png (dpi argument).
"""
import itertools
import matplotlib
matplotlib.use("Agg")
import schemdraw
import schemdraw.elements as elm
import schemdraw.logic as logic

_TYPES = {"AND": logic.And, "OR": logic.Or, "NAND": logic.Nand, "NOR": logic.Nor,
          "XOR": logic.Xor, "XNOR": logic.Xnor, "NOT": logic.Not, "BUF": logic.Buf}
ROW = 1.0      # spacing of primary inputs
VGAP = 0.55    # minimum free space between gates in a column
TRACK = 0.32   # spacing of vertical wire tracks
NOTW = 1.0    # drawn length of NOT/BUF
EPS = 1e-6


def _parse(ins):
    out = []
    for s in (ins.split() if isinstance(ins, str) else ins):
        out.append((s[1:], True) if s.startswith("~") else (s, False))
    return out


def _proto(t, n, nots):
    t = t.upper()
    if t in ("NOT", "BUF"):
        return _TYPES[t]().length(NOTW)
    kw = {"inputs": n}
    if nots:
        kw["inputnots"] = nots
    return _TYPES[t](**kw)


def circuit(fname, inputs, gates, outputs=None, marks=None, bridges=None, gate_labels=None,
            net_labels=True, y=None, level=None, dpi=250, fontsize=13):
    marks, bridges = marks or {}, bridges or []
    gate_labels, yh, lvh = gate_labels or {}, y or {}, level or {}
    G = {}
    for out, t, ins in gates:
        pins = _parse(ins)
        nots = [i + 1 for i, (_, inv) in enumerate(pins) if inv]
        p = _proto(t, len(pins), nots)
        an = {k: tuple(v) for k, v in p.anchors.items()}
        bb = p.get_bbox()
        if t.upper() in ("NOT", "BUF"):      # two-terminal elements: drop the default leads
            an, bb = {"in1": (0.0, 0.0), "out": (NOTW, 0.0)}, type(bb)(0, -0.45, NOTW, 0.45)
        G[out] = dict(t=t.upper(), pins=[n for n, _ in pins], nots=nots, an=an,
                      w=an["out"][0], top=bb.ymax, bot=bb.ymin)
    for n in list(G):
        for s in G[n]["pins"]:
            if s not in G and s not in inputs:
                raise ValueError(f"net {s!r} (input of {n}) is neither an input nor a gate")
    consumers = {}
    for n, g in G.items():
        for k, s in enumerate(g["pins"]):
            consumers.setdefault(s, []).append((n, k))
    if outputs is None:
        outputs = [n for n in G if n not in consumers]

    # levels
    lv = {i: 0 for i in inputs}

    def L(n):
        if n not in lv:
            lv[n] = max([1 + L(s) for s in G[n]["pins"]] + [lvh.get(n, 0)])
        return lv[n]
    for n in G:
        L(n)
    ncol = max(lv.values())

    # vertical placement
    Y = {}
    for i, n in enumerate(inputs):
        Y[n] = yh.get(n, -i * ROW)

    def pin_dy(n, k):
        return G[n]["an"][f"in{k + 1}"][1]
    for c in range(1, ncol + 1):
        col = [n for n in G if lv[n] == c]
        want = {}
        for n in col:
            if n in yh:
                want[n] = yh[n]
            else:   # centre the gate so its pins line up with their sources on average
                ps = G[n]["pins"]
                want[n] = sum(Y[s] - pin_dy(n, k) for k, s in enumerate(ps)) / len(ps)
        col.sort(key=lambda n: -want[n])
        pos = {}
        prev = None
        for n in col:          # top to bottom, push down to avoid overlaps
            yy = want[n]
            if prev is not None and n not in yh:
                yy = min(yy, pos[prev] + G[prev]["bot"] - VGAP - G[n]["top"])
            pos[n] = yy
            prev = n
        free = [n for n in col if n not in yh]
        if free:               # shift the block back towards its wanted centre
            sh = sum(want[n] - pos[n] for n in free) / len(free)
            if sh > 0:         # moving up must not collide with a pinned gate above
                for a, b in zip(col, col[1:]):
                    if b in free and a not in free:
                        sh = min(sh, pos[a] + G[a]["bot"] - VGAP - G[b]["top"] - pos[b])
            for n in free:
                pos[n] += sh
        Y.update(pos)

    # move an input that feeds a single pin onto that pin's height (no jog), keeping order
    for i, n in enumerate(inputs):
        cons = consumers.get(n, [])
        if n in yh or len(cons) != 1:
            continue
        g, k = cons[0]
        ty = Y[g] + pin_dy(g, k)
        lo = Y[inputs[i + 1]] + 0.5 if i + 1 < len(inputs) else -1e9
        hi = Y[inputs[i - 1]] - 0.5 if i > 0 else 1e9
        if lo <= ty <= hi:
            Y[n] = ty

    # wire tracks per gap (gap c lies just left of column c)
    src_col = {n: lv[n] for n in Y}
    segs_needed = {}   # gap -> {net: [dest y, ...]}
    direct = set()
    for s, cons in consumers.items():
        for (n, k) in cons:
            dy = Y[n] + pin_dy(n, k)
            if len(cons) == 1 and abs(dy - Y[s]) < EPS and lv[n] == src_col[s] + 1:
                direct.add((n, k))
                continue
            segs_needed.setdefault(lv[n], {}).setdefault(s, []).append(dy)

    def order_tracks(nets):
        nets = list(nets)
        def span(s):
            ys = segs_needed_g[s] + [Y[s]]
            return min(ys), max(ys)
        def cost(perm):
            c = 0
            for i, a in enumerate(perm):
                for b in perm[i + 1:]:      # a is left of b
                    lo, hi = span(b)
                    if lo + EPS < Y[a] < hi - EPS:          # a's source wire crosses b
                        c += 1
                    lo, hi = span(a)
                    c += sum(lo + EPS < d < hi - EPS for d in segs_needed_g[b])
            return c
        if len(nets) <= 7:
            return list(min(itertools.permutations(nets), key=cost))
        return sorted(nets, key=lambda s: Y[s])
    tracks = {}
    for gcol, d in segs_needed.items():
        segs_needed_g = d
        tracks[gcol] = order_tracks(d)

    # horizontal positions
    lab_w = 0.25
    colx = {0: 0.0}
    colw = {0: 0.0}
    for c in range(1, ncol + 1):
        colw[c] = max(G[n]["w"] for n in G if lv[n] == c)
        nt = len(tracks.get(c, []))
        gap = 0.5 + TRACK * (nt + 1) + (0.35 if net_labels and c > 1 else 0)
        colx[c] = colx[c - 1] + colw[c - 1] + gap
    trackx = {}
    for c, ts in tracks.items():
        left = colx[c - 1] + colw[c - 1] + (0.35 if net_labels and c > 1 else 0) + 0.25
        for i, s in enumerate(ts):
            trackx[(c, s)] = left + TRACK * (i + 1)

    X = {n: (0.0, Y[n]) for n in inputs}      # source point of each net
    PIN = {}
    for n, g in G.items():
        x0 = colx[lv[n]]
        X[n] = (x0 + g["an"]["out"][0], Y[n])
        for k in range(len(g["pins"])):
            a = g["an"][f"in{k + 1}"]
            PIN[(n, k)] = (x0 + a[0], Y[n] + a[1])

    # wires as segments
    segs = []
    def seg(p, q):
        if abs(p[0] - q[0]) > EPS or abs(p[1] - q[1]) > EPS:
            segs.append((p, q))
    reach = {}                                   # net -> rightmost x of its source wire
    for s, cons in consumers.items():
        sx, sy = X[s]
        for (n, k) in cons:
            px, py = PIN[(n, k)]
            if (n, k) in direct:
                seg((sx, sy), (px, py))
                continue
            tx = trackx[(lv[n], s)]
            reach[s] = max(reach.get(s, sx), tx)
            seg((tx, sy), (tx, py))
            seg((tx, py), (px, py))
    for s, rx in reach.items():
        seg(X[s], (rx, X[s][1]))
    right = max(colx[c] + colw[c] for c in colx) + 0.5
    out_end = {}
    for o in outputs:
        ox, oy = X[o]
        out_end[o] = max(ox + 0.7, reach.get(o, ox) + 0.5)
    for (p, q, *_) in bridges:
        bx = max(X[p][0], X[q][0]) + 0.45
        for n in (p, q):
            out_end[n] = max(out_end.get(n, X[n][0]), bx + (0.5 if n in outputs else 0.15))
    for o, ex in out_end.items():
        seg(X[o], (ex, X[o][1]))

    # junction dots: points where 3 or more wire directions meet
    pts = {}
    def key(p):
        return (round(p[0], 4), round(p[1], 4))
    allp = set(key(p) for sg in segs for p in sg)
    for P in allp:
        dirs = set()
        for (a, b) in segs:
            a, b = key(a), key(b)
            if a == P:
                dirs.add((round(b[0] - a[0] > 0) - round(b[0] - a[0] < 0), (b[1] > a[1]) - (b[1] < a[1])))
            elif b == P:
                dirs.add(((a[0] > b[0]) - (a[0] < b[0]), (a[1] > b[1]) - (a[1] < b[1])))
            elif _on(P, a, b):
                if abs(a[0] - b[0]) < EPS:
                    dirs |= {(0, 1), (0, -1)}
                else:
                    dirs |= {(1, 0), (-1, 0)}
        if len(dirs) >= 3:
            pts[P] = True

    # warnings: wires running through gate bodies
    warns = []
    for n, g in G.items():
        x0, x1 = colx[lv[n]] + 0.05, colx[lv[n]] + g["w"] - 0.05
        y0, y1 = Y[n] + g["bot"], Y[n] + g["top"]
        for (a, b) in segs:
            if (min(a[0], b[0]) < x1 and max(a[0], b[0]) > x0 and
                    min(a[1], b[1]) < y1 - 0.02 and max(a[1], b[1]) > y0 + 0.02):
                if not (abs(a[1] - b[1]) < EPS and (abs(b[0] - x0 + 0.05) < 0.05 or abs(a[0] - x0 + 0.05) < 0.05)
                        and abs(max(a[0], b[0]) - (x0 - 0.05)) < 0.05):
                    warns.append(f"wire {a}->{b} crosses gate {n}")

    # draw
    schemdraw.config(fontsize=fontsize, lw=1.3)
    d = schemdraw.Drawing(show=False)
    for n, g in G.items():
        el = _proto(g["t"], len(g["pins"]), g["nots"])
        if g["t"] in ("NOT", "BUF"):
            el = el.at((colx[lv[n]], Y[n])).anchor("start")
        else:
            el = el.at((colx[lv[n]] + g["an"]["in1"][0], Y[n] + g["an"]["in1"][1])).anchor("in1")
        d.add(el)
        if n in gate_labels:
            cx = colx[lv[n]] + g["w"] * (0.42 if g["t"] not in ("NOT", "BUF") else 0.4)
            cy = Y[n] if g["t"] not in ("NOT", "BUF") else Y[n] + g["top"] + 0.15
            d.add(elm.Label().at((cx, cy)).label(gate_labels[n], fontsize=fontsize - 3))
    for (a, b) in segs:
        d.add(elm.Line().at(a).to(b))
    for P in pts:
        d.add(elm.Dot(radius=0.065).at(P))
    for n in inputs:
        d.add(elm.Label().at((-0.12, Y[n])).label(n, loc="left", halign="right"))
    for o in outputs:
        d.add(elm.Label().at((out_end[o] + 0.1, X[o][1])).label(o, loc="right", halign="left"))
    if net_labels:
        for n in G:
            if n not in outputs:
                d.add(elm.Label().at((X[n][0] + (0.65 if n in marks else 0.18), X[n][1] + 0.03))
                      .label(n, loc="top", halign="left", fontsize=fontsize - 2))
    for k, txt in marks.items():
        if ">" in k:
            s, gname = k.split(">")
            ks = [kk for kk, ss in enumerate(G[gname]["pins"]) if ss == s]
            if not ks:
                raise ValueError(f"mark {k!r}: {s} is not an input of {gname}")
            px, py = PIN[(gname, ks[0])]
            mx, my = px - 0.22, py
        else:
            mx, my = X[k][0] + 0.3, X[k][1]
        d.add(elm.Label().at((mx, my)).label("×", fontsize=fontsize + 3))
        d.add(elm.Label().at((mx, my - 0.12)).label(txt, loc="bottom", fontsize=fontsize - 3))
    for (p, q, *rest) in bridges:
        bx = max(X[p][0], X[q][0]) + 0.45
        d.add(elm.Line().at((bx, X[p][1])).to((bx, X[q][1])).linestyle("--"))
        d.add(elm.Dot(radius=0.065).at((bx, X[p][1])))
        d.add(elm.Dot(radius=0.065).at((bx, X[q][1])))
        if rest and rest[0]:
            d.add(elm.Label().at((bx + 0.1, (X[p][1] + X[q][1]) / 2))
                  .label(rest[0], loc="right", halign="left", fontsize=fontsize - 3))
    d.save(fname, dpi=dpi)
    for w in warns:
        print(f"[logic_fig] {fname}: {w}")
    return warns


def _on(P, a, b):
    if abs(a[0] - b[0]) < EPS and abs(P[0] - a[0]) < EPS:
        return min(a[1], b[1]) + EPS < P[1] < max(a[1], b[1]) - EPS
    if abs(a[1] - b[1]) < EPS and abs(P[1] - a[1]) < EPS:
        return min(a[0], b[0]) + EPS < P[0] < max(a[0], b[0]) - EPS
    return False


if __name__ == "__main__":
    import os, sys
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    circuit(os.path.join(out, "demo_redundant.png"), ["a", "b", "c"],
            [("g1", "AND", "a b"), ("g2", "AND", "~a c"), ("g3", "AND", "b c"),
             ("z", "OR", "g1 g2 g3")], marks={"g3": "s-a-0"})
    circuit(os.path.join(out, "demo_bridge.png"), ["a", "b", "c"],
            [("p", "AND", "a b"), ("q", "NOT", "c")], bridges=[("p", "q", "short")])
    circuit(os.path.join(out, "demo_recon.png"), ["A", "B", "C", "D"],
            [("e", "NAND", "A B"), ("f", "OR", "B C"), ("g", "NOT", "D"),
             ("h", "AND", "e f"), ("z", "NOR", "h g")], marks={"B>f": "s-a-1"},
            gate_labels={"e": "G1", "f": "G2"})
    print("demo figures written to", out)
