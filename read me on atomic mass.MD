Status acknowledged

Nice work — the commit and merge are in place. This is a solid, reproducible repo state you can point people to and build from.

---

Immediate deliverables I’m providing now

Item	Why it helps	**Action included below	
README snippet	Explains the analysis and how to reproduce it	Ready‑to‑paste text	
Outreach email	Short, professional note to beamlines / university groups	Copy‑paste template	
Experimental checklist	What an accredited lab will need to validate your claim	Practical, safety‑aware steps	
CI / test suggestions	Make the repo easier to review and run automatically	Commands and test ideas	
Run instructions	How to run the analysis locally and produce CSV/plots	pip + python commands	


---

README snippet (paste into your repo)

Title
27Al(p,α)24Mg — Q-values, α kinematics, and lab thresholds (reproducible)

Summary
This repository documents a reproducible analysis showing that the observed \(^{24}\)Mg can be produced by the reaction \(^{27}\mathrm{Al}(p,\alpha)^{24}\mathrm{Mg}\). It includes Q‑value calculations (AME2020 masses embedded), two‑body kinematics, α energy vs proton energy plots, and CSV exports for numeric tables.

Files

• analysis_27Al_p_alpha.py — script that computes Q‑values, α partitioning, CM→lab kinematics, (p,n) threshold, plots, and CSV exports.
• results/ — generated CSVs and PNGs (alpha energy vs proton energy, tables).


How to run

1. Install dependencies:pip install numpy pandas matplotlib scipy

2. Run the script:python analysis_27Al_p_alpha.py

3. Optional: place mass_1.mas20 (AME2020 ASCII) next to the script and set USE_AME_FILE = True in the script to override embedded masses.


Notes & assumptions

• Non‑relativistic two‑body kinematics are used (appropriate for MeV energies).
• Cross sections and resonance structure are not modeled; use EXFOR/TALYS for yield predictions.
• Safety: any irradiation experiments must be performed in accredited facilities with radiation‑safety oversight.


---

Outreach email (copy‑paste)

Subject: Request for collaboration / beam time — validation of 27Al(p,α)24Mg identification

Body:
Hello [Name / Facility],

My name is Leif Sogge (GitHub: GuardianNinja). I have a reproducible analysis (public repo: GuardianNinja/GuardianNinja) showing that observed \(^{24}\)Mg can be produced by the reaction \(^{27}\mathrm{Al}(p,\alpha)^{24}\mathrm{Mg}\). The repo contains Q‑value calculations (AME2020 masses embedded), two‑body kinematics, α energy predictions, and a small script to reproduce the numbers and plots.

I’m seeking an accredited lab or beamline to perform a controlled proton irradiation of Al and measure α spectra, γ lines, and activation products to validate the channel and quantify cross sections at a few MeV. I can provide the analysis, data files, and a proposed experimental checklist; I’m looking for collaborators to run the irradiation and spectroscopy under proper safety protocols.

If this is of interest, I can share a short experimental plan and the reproducible notebook. Thank you for considering this collaboration.

Best regards,
Leif Sogge (GuardianNinja)
[link to repo]

---

Experimental checklist for an accredited facility

Administrative & safety

• Institutional approval and radiation‑safety signoff.
• Beamline reservation and experiment proposal submitted.


Target & beam

• High‑purity Al target (thin foil and thicker backing for comparison).
• Proton beam energies: recommended set: 3 MeV, 5 MeV, 8 MeV, 12 MeV (covers below/near Coulomb barrier and above (p,n) threshold).
• Fluence logs and beam current integration.


Detectors & diagnostics

• Silicon α spectrometer(s) with energy calibration (MeV range).
• High‑resolution γ spectrometer (HPGe) for prompt and delayed lines.
• Neutron monitor (if available) for (p,n) confirmation.
• Blank/control targets and background runs.


Measurements

• Pre‑ and post‑irradiation isotopic analysis of target surface (mass spec) for 24Mg enrichment.
• Time‑tagged α spectra during irradiation and after (to separate prompt vs delayed).
• Gamma spectra during and after irradiation.
• Record environmental and background radiation.


Data & reproducibility

• Provide raw detector files, calibration runs, beam logs, and processed spectra.
• Re-run analysis script with measured fluence to estimate yields.


---

CI / test suggestions for the repo

• Unit test: small test that verifies Q‑value arithmetic for a known reaction (e.g., 1+1→2 trivial check).
• Smoke test: run python analysis_27Al_p_alpha.py in CI and assert CSVs are produced and plots saved.
• Formatting: add requirements.txt with pinned versions for reproducibility.
• Action: GitHub Action that runs the script on push to main and uploads results/ as artifacts (CI should run in a safe, non‑radiation context — only code).


---

How I’ll proceed next (I already inferred the most useful steps)

I will prepare: (A) a short preprint‑style one‑page summary you can attach to outreach emails, (B) alpha energy vs angle plots and a CSV of numeric tables ready to paste into the repo, and (C) a concise “methods & assumptions” paragraph for the README. These will be formatted so you can paste them directly into your repo and outreach messages.

You’re set — I’ll generate those artifacts now and paste them into the chat so you can copy them into GitHub.