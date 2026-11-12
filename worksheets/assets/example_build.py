"""Minimal example content script. Copy into the project's worksheets/sources/ dir together
with scripts/wslib.py, rename, and fill in. Run from sources/: python3 build_<topic>.py
Outputs: ../questions/<slug>-worksheet.pdf and ../answers/<slug>-answer-key.pdf"""
from wslib import Sheet

s = Sheet("Cache Coherence", "coherence", course="CS471")
P, Q = s.part, s.q

P("Part A: Foundations", "Cache properties every coherence protocol relies on.")

Q(r'''Define write-through and write-back caches. Why does write-back make coherence harder?''', "3cm",
r'''Write-through updates memory on every store; write-back only on eviction (dirty bit). With
write-back the only up-to-date copy may sit in one private cache, so the protocol must find it.''')

Q(r'''Complete the MSI controller table (next state / action).
#align(center)[#ft(("State", "PrRd", "PrWr", "BusRd", "BusRdX"), ("I", "S", "M"), h: 2em)]
#ex("2024 Q7")''', "0.6cm",
r'''#align(center)[#at(("State", "PrRd", "PrWr", "BusRd", "BusRdX"),
  [*I*], [S / BusRd], [M / BusRdX], [I / -], [I / -],
  [*S*], [S / -], [M / BusInv], [S / -], [I / -],
  [*M*], [M / -], [M / -], [S / BusWB], [I / BusWB])]''')

Q(r'''Bus cycle = 2× core cycle; cores at 3 GHz; one 64 B block per bus cycle; each core needs
6 GB/s; utilization ≤ 50%.
(a) What is the bus bandwidth?
(b) How many cores can it support?''', "3cm",
r'''(a) 64 B / 0.667 ns = 96 GB/s. (b) 50% → 48 GB/s; 48 / 6 = 8 cores.''')

s.build()
