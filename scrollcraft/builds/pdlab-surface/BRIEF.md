# BRIEF: pdlab surface

**Self-authored, not interviewed.** The owner's standing instruction for this
project is "work autonomously, do not ask me questions". The eight answers
below are written in the project's own voice from the mission statement, the
report, and the existing app; they are a fallback, not a plan the owner signed.

## The eight answers

1. **Vibe.** Instrument, honest, cold, precise, alive. References: an
   oscilloscope face; Nowak & May's 1992 kaleidoscope plates in *Nature*;
   a Bloomberg terminal seen from across the room.
2. **The scroll journey, in order.** The payoff matrix, already running, with a
   hidden opponent waiting for my first move. Then the finite game unravelling
   backwards under my hand. Then me playing a strategy properly. Then all
   eighteen strategies ranked, sideways. Then the lattice takes the whole screen
   and grows as I scroll. Then the replicator triangle and why TFT survives.
   Then noise, and the extortioner. Then a prompt I can type into.
3. **Energy curve.** Quiet open. Rising pressure through the unravelling.
   Calm hands-on play. Brisk sideways. The one loud moment: the lattice.
   Then settle, then sober, then still.
4. **Feel, stage by stage, and the one moment.** Curiosity, unease, control,
   recognition, awe, clarity, doubt, readiness. The one moment: the screen
   fills with the blooming lattice and the number in the corner says how many
   still cooperate.
5. **One thing no site does.** The scroll wheel is the generation counter of a
   real spatial simulation. Not a video of one: the 99×99 Nowak–May lattice is
   computed in the page, and scrolling advances it.
6. **Distance from premium-minimal.** Dense. Data product. Small type, many
   real numbers, mono labels, no marketing.
7. **One world or scenes.** One live surface. Not a film, not chapters: an
   application whose panels populate as the page is operated.
8. **Assets.** No footage, no photography. The assets are the numbers in
   `results/app_payload.json` (canonical run 5) and the simulations themselves,
   ported to JavaScript and cross-checked against the Python package.

## Feeling curve (one line per act, emotion first, then the cause)

```
1  Curiosity     the payoff matrix is live and a hidden opponent has already moved;
                 behind the panel a single red cell sits in a still blue field
2  Unease        pinned: the 200-round game unravels backwards from the last round
                 as I scroll, the count of cooperative rounds falling to zero
3  Control       I choose an opponent and play, by hand or by policy; the surface answers
4  Recognition   eighteen strategies travel sideways, ranked, museum-labelled with real
                 scores: the nice ones are at the front, Gradual ahead of TFT
5  Awe  (PEAK)   the panels get out of the way and the lattice fills the viewport,
                 generation advancing under the wheel, the corner readout counting
6  Clarity       the replicator triangle: a draggable start, the neutral edge, x* = 1/17,
                 the eigenvalues that say why
7  Doubt         pinned: noise sweeps from 0 to 0.2 through the exact Markov chain
                 and TFT drops to 9/4 the instant ε > 0; the extortioner's line
8  Readiness     a prompt with a cursor in it, computing the same things on demand
```

No two adjacent acts share a feeling.

## The peak

Act 5. The sentence: *"the whole screen bloomed into a blue-and-red kaleidoscope
under my scroll wheel, and the number in the corner said 31 percent still
cooperate."* It gets the largest span on the page (3.6 viewport-heights), the
quiet act before it (the rail, act 4, has no simulation of its own and the
lattice behind it is still only a small diamond), and the only moment where the
panels recede to a single small readout.

## Authored silence

None. Every act has content at p = 0 (the panels are opaque grounds). The
"silence" before the peak is the rail act being visually quiet, not empty.

## Tell-someone sentence

"It's the site where you scroll and a cooperation simulation grows across the
whole screen, generation by generation, and every number on the page is the
real one from the paper."

## Signature move

**Scroll is the generation counter.** A fixed full-viewport canvas renders the
99×99 synchronous Nowak–May lattice (b = 1.9, one defector at the centre, 8
neighbours plus self, ties keep the incumbent), precomputed for 130 generations
in the page's own JS. Page scroll before the peak advances it from generation 0
to 6 (the diamond barely appears); the peak act's `--sc-p` advances it 6 → 130;
after the peak it holds. The status bar's readout (`gen · f_C · b`) is the same
state. The `b` handle in the peak recomputes every frame. Bespoke JS, engine
untouched.

## Grammar

Live surface. Bans honoured: no scrub, no kinetic, no spotlight, no drift past
two stops, no marketing chrome, no display type above ~2.25rem, no hero claim
over media. Nav is app chrome (a fixed status bar with a bench tab strip and the
live readout). Hero is the surface in a state. Close is a real input.
