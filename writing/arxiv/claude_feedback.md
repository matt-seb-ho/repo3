I read it closely and checked the internal arithmetic across the tables and text. The work itself hangs together well — Tables 1, 5, 6, 8, the OpenFOAM factor readout, and the speedup/variance headline numbers all reconcile when I recompute them. But there are a few concrete inconsistencies you'll want to fix before posting. Listing them by severity.

**Clear errors (should fix)**

1. **App G.3 contradicts Table 7.** The harness-less section says vanilla Claude Code "recovers +0.164 over this floor" (the 0.333 minimax floor), implying ~0.497. But Table 7 lists vanilla CC on minimax-m2.7 at **0.821**, i.e. a gain of **+0.488**, not +0.164. One of these is wrong; given the floor (0.333) and Table 7 (0.821) are each cited elsewhere, the "+0.164" looks like the stale number.

2. **Table 10 (App I) doesn't sum for the Expert 1 extended row.** GEOS docs 89 + GitHub 21 + Search 6 + Other 7 = **123**, but "Total visits" is listed as **106** (and the text says the catch-up "adds 77 navigations on top of the original 29" → 106). The other two rows (Expert 1 1h = 29, Expert 2 1h = 73) both sum correctly, so this one is off.

3. **Table 2 / §6.3: Expert 1's file-level score drops in the longer session.** Expert 1 (1h) file-level base = 0.812; Expert 1 (no cap, ~3h) file-level base = **0.689**. The base file gets *worse* in the extended session even though the deck-level rises to 0.931. That's counterintuitive and currently unexplained — either it needs a one-line explanation (e.g., base.xml was restructured to accommodate the `<Included>`/benchmark file) or it's a transcription error. A reviewer will flag it.

**Moderate**

4. **Split arithmetic in §5.2.** "The 46 tasks are split into 10 held-out-eval tasks, 18 distillation tasks, and 17 validation-selection tasks" sums to **45**. App A.1 resolves it ("one task dropped"), but §5.2 presents it as a clean partition of 46. Add the dropped-task caveat in the main text.

5. **Intro mislabels variance vs. SD.** Intro point (2) says SIGA "cuts score variance by about 16×." The 16× is the *standard-deviation* ratio (σ 0.081 → 0.005); as a variance ratio it'd be ~260×. The abstract correctly says "standard deviation by 16×." Make the intro match.

6. **§6.1 main-effects numbers don't reconcile with the cell means.** Computing straight Resolution-IV contrasts over the eight factorial cells in Table 1, I get R ≈ −0.037 (you report −0.032) and **X ≈ +0.011**, which is outside the stated "X, M, and S all fall within ±0.007." If you computed these via a regression including the extra cells (S+X+M etc.), say so; otherwise the X claim and the −0.032 need correcting.

7. **§6.6 "on Claude all effects are within ±0.5"** but App E reports R = **+0.52** for the Claude backbone — just over the bound. Either round the statement or adjust.

8. **"Outperforming" vs "matches."** The abstract says SE is "outperforming the strongest hand-designed configuration," but SE held-out (0.789 ± 0.012) vs S+X+M (0.783 ± 0.022) is within noise, and §4.3 more carefully says "matches." I'd use "matches" everywhere.

**Minor / worth a sentence**

9. Table 9: Medium and Hard show different T1/T2 drop counts (27/62 vs 26/53) even though Hard is defined as Medium + T3. Explainable by the two independent LLM rewrites, but a half-sentence would preempt the question.
10. §6.4: Hard scores slightly *higher* than Medium (0.835 vs 0.829) despite dropping more spec — fine at n=1, but maybe note it's within single-run noise.
11. Terminology: the same 10 tasks are called the "ICL pool" (App A) and "held-out-eval" (§5.3). Worth stating they're identical so readers don't suspect leakage when App G.3 draws an "ICL demonstration."
12. The "ten canonical sections" list in §3 includes *Functions* but omits *Tasks*, whereas the App M section-score breakdown lists *Tasks* and not *Functions*. Tiny taxonomic mismatch.

Items 1–3 are the ones I'd treat as blocking. Everything else is tightening. Want me to draft corrected wording for any of these?
