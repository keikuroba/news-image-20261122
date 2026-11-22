# Sunday 22 November 2026 — the world in one image

A drawn broadsheet that sums up Sunday 22 November 2026 in five stories
plus a ticker:

- **Poland / NATO (lead).** Russia fired 400+ drones and 110 missiles at
  Ukraine — its biggest attack of the year, killing 8. Two missiles and a
  drone then fell inside Poland. PM Tusk calls it a deliberate
  provocation; NATO vows to defend "every inch" of allied land.
- **Climate / Antalya.** COP31 deadlocks over fossil fuels: talks run into
  a second day of overtime as the draft drops all mention of coal, oil
  and gas. 130+ nations demand a phase-out; oil producers refuse.
- **Middle East / Gulf.** Houthi missiles target Riyadh; defences
  intercept them. Iran claims strikes on US Patriot radars.
- **Mexico / Cartels.** Mexico captures 'El Chapo Isidro', the FBI's
  most-wanted drug lord, in Sinaloa — then deadly cartel violence erupts.
- **Sport / Tennis.** Carlos Alcaraz fights back past Ben Shelton to set
  up an ATP Finals decider against world No. 1 Alexander Zverev.
- **Ticker.** Norway court voids disputed oil licences; Kenya clears its
  last Ebola patient as the DRC toll passes 5,300; EU hunts a new ECB
  chief as Lagarde resigns; M4.1 quake in Myanmar; Smith out for
  Australia v South Africa.

## How it works

`tools/make_image.py` draws the 1024x1024 PNG with Pillow from fixed
coordinates (no photos, no network, no clock), and `main.py` copies it to
`/output/entry.png` after validating that it is a whole, well-formed PNG
inside the size limits. Re-running either program produces identical bytes.

## Entry

- Competition: [news-image-20261122](https://make.fun/c/news-image-20261122)
- `main.py` — Python 3.13, standard library only
- `assets/entry.png` — 1024x1024 PNG
