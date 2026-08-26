# Candidate abstract openings

Each option is a self-contained replacement for the first ~3 sentences of the
abstract (current version: "Applying AI agents to scientific disciplines is an
increasingly important direction... deserves attention before agents are turned
loose..."). Each then pivots into the existing "We study how far this bottleneck
can be reduced by adapting an off-the-shelf coding agent (Claude Code)..."

Commentary follows each option.

---

## Option A — Cut to the chase: tools as the bottleneck

> Advanced scientific software, from multiphysics simulators to molecular
> dynamics engines, is now indispensable to working scientists, but the more
> expressive a tool's capabilities, the more elaborate the configuration
> language one must master to use it. Setting up a single simulation campaign
> routinely costs trained domain scientists hours to days, before any actual
> science begins. This *tool-setup* bottleneck is a natural early target for
> agentic AI: it sits between a researcher's intent and a runnable experiment,
> and reducing it would deliver immediate value to working scientists before
> agents are entrusted with deeper scientific reasoning.

**Commentary.** Closest to your own suggestion. Reads as a direct, no-frills
problem statement. The "before any actual science begins" beat is the most
engaging line and frames the cost in terms a reviewer feels. The third sentence
does the "AI before end-to-end" framing in one breath. Risk: the third sentence
is still doing a lot — could be trimmed. Strength: makes the application angle
the lead, which fits the dual application/AI4Science framing.

---

## Option B — Inversion: the powerful-tools paradox

> Powerful scientific software demands expressive configuration: the more a
> simulator can do, the more elaborate the domain-specific language a user must
> learn to drive it. The result is a quiet but persistent bottleneck in modern
> scientific workflows, where trained researchers spend hours to days per study
> translating intent into the simulator's idiom. We argue this *tool-operating*
> bottleneck is the natural first target for agentic AI in science: a concrete,
> well-scoped translation problem that, if solved reliably, returns hours per
> week to working scientists before any harder questions of automated discovery
> are on the table.

**Commentary.** My favorite for engagement. Opens with a small paradox ("the
more powerful, the harder to use") that earns attention. "Quiet but persistent"
gives texture; "translating intent into the simulator's idiom" is more vivid
than "configuration." The "first target" framing is sharper than "before
end-to-end" because it positions our work rather than just deferring AI4Science.
Risk: slightly more rhetorical than a NeurIPS-style abstract usually goes.

---

## Option C — Concrete and economic: the cost as the hook

> Modern science increasingly runs on advanced simulators and other
> highly-configurable software tools, but operating them is an expert skill in
> its own right: a single multiphysics simulation campaign can cost a trained
> researcher hours to days of setup before the first numerical result is
> produced. Reducing this configuration bottleneck is a concrete, near-term
> target for agentic AI, and a precondition for trusting agents with the harder
> open-ended scientific reasoning that has drawn most current attention.

**Commentary.** Lean — two sentences instead of three. The "before the first
numerical result is produced" beat is the strongest single phrase. The second
sentence does the application + AI4Science framing compactly. Risk: leaves
slightly less room to set up the "operating tools is itself hard" angle, which
is a key piece of your framing.

---

## Option D — Researcher's voice / lived experience

> Any scientist who has tried to run an advanced simulator knows the gap
> between deciding what experiment to run and getting the software to actually
> run it: modern simulators encode their full capability in expressive,
> often unforgiving configuration languages, and translating a paragraph of
> intent into a working input deck routinely costs hours to days of expert
> time. This translation step is a natural early target for agentic AI: it is
> concrete, repetitive, and gates access to the science it precedes.

**Commentary.** Two sentences, voice-driven. The "any scientist who has tried"
opener is unusual and grabs attention — but may read as too informal for a
NeurIPS abstract. The "concrete, repetitive, and gates access to the science"
ending is the cleanest one-line framing of the dual application/AI4Science
angle in any of these options. Risk: tone may be too narrative for the venue;
strength: most memorable if you can sell the voice.

---

## Option E — Position-setting / contrastive

> Much of the current excitement about AI agents for science targets the
> hardest parts of the scientific process: hypothesis generation, experimental
> design, automated discovery. Far less attention has gone to the prosaic but
> universal bottleneck that precedes any of these, which is operating the
> scientific software itself. Modern simulators encode their capability in
> expressive configuration languages whose setup routinely costs domain
> scientists hours to days per study.

**Commentary.** Most explicitly positioned against the prevailing AI4Science
narrative. The first sentence flatters the reader by naming what they're
already excited about; the second pivots to your contribution; the third
grounds it. This is the most rhetorically structured opener. Risk: spends a
sentence on prior work before stating the problem; some reviewers prefer
direct openers. Strength: the contrast lands the "operating tools is its own
problem" message harder than any other option.

---

## Option F — Minimal / two-sentence

> Advanced simulators and other powerful scientific software ship with
> correspondingly expressive configuration languages, and learning to operate
> them costs domain scientists hours to days per study. This *tool-operating*
> bottleneck is a concrete, near-term target for agentic AI, and a precondition
> for trusting agents with the open-ended scientific reasoning that has drawn
> most current attention.

**Commentary.** The most compressed option. Two sentences, no preamble, no
rhetorical setup. Reads efficient and confident. Risk: may feel undersold for
a paper this large; some abstracts benefit from a beat of context before
diving in. Strength: leaves the most room for the rest of the abstract (SIGA,
ablations, findings) to breathe.

---

# My recommendation

If I had to pick one, **Option B** for engagement / framing strength, or
**Option C** for a more conventional NeurIPS tone. Option E is the option
to pick if you want to most explicitly position the work against the
end-to-end-automation strand of AI4Science.

A reasonable hybrid: take Option B's first sentence (the paradox), follow with
Option C's second sentence (the cost beat), and end with Option E's third
sentence (the "much attention has gone to harder things; this is the
precondition" positioning). Roughly:

> Powerful scientific software demands expressive configuration: the more a
> simulator can do, the more elaborate the domain-specific language a user
> must learn to drive it. A single multiphysics simulation campaign can cost a
> trained researcher hours to days of setup before the first numerical result.
> Much of the current excitement about AI agents for science targets harder
> problems further downstream — hypothesis generation, automated discovery —
> but reducing this prosaic tool-operating bottleneck is a concrete, near-term
> target that delivers immediate value to working scientists, and a
> precondition for trusting agents with the rest.

This hybrid is the option I'd actually recommend, but I'm flagging it
separately rather than as one of A–F because it's an *integration* across
them rather than a distinct angle. (It uses one em dash; happy to remove.)
