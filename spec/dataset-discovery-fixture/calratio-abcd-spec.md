# Run 1 CalRatio displaced-jet search with an ABCD QCD estimate

Search for gg -> Phi -> pi_v pi_v, with both long-lived neutral particles decaying near the outer electromagnetic calorimeter or in the hadronic calorimeter.
Retain the published 8 TeV analysis and replace only its QCD estimate and the statistical treatment needed to support that replacement.

## Source and Scope

* Analysis mode: Source-derived with requested changes.
* Authoritative source: ATLAS, "Search for pair-produced long-lived neutral particles decaying to jets in the ATLAS hadronic calorimeter in pp collisions at sqrt(s) = 8 TeV", arXiv:1501.04020v2, supplied as [1501.04020v2.pdf](1501.04020v2.pdf). Section references below refer to this version.
* Analysis intent: identify two displaced, narrow, trackless, hadronic-energy-dominated jets and constrain scalar production times branching fraction versus LLP proper decay length.
* Source realization: 2012 ATLAS data, 20.3 fb^-1, sqrt(s) = 8 TeV, dedicated CalRatio trigger and Run 1 calorimeter/tracking reconstruction.
* Requested deviation: replace the single-jet P/Q fake-probability prediction and its extrapolated correlation correction with a data-driven ABCD estimate. The user's report that the previous method failed motivates the replacement; the paper itself reports closure and agreement with data.
* Added elements: explicit tag/probe sidebands, ABCD closure requirements, correlation nuisance and simultaneous region-count likelihood. These are proposed analysis choices, not results from the source. Their validity must be established with control data before producing limits.
* Technique context: a later [ATLAS CalRatio search](https://cds.cern.ch/record/2657638/files/1902.03094.pdf?version=1) also uses a data-driven ABCD method. Its Run 2 selections and discriminants are not imported here; it does not establish closure for the proposed Run 1 axes.

## Data Samples

| Data Sample | Role(s) In Analysis |
| --- | --- |
| 2012 pp collision data at 8 TeV, 20.3 fb^-1 after quality requirements | CalRatio-triggered signal and ABCD control regions |
| 2012 prescaled single-jet data, thresholds of 15 GeV or higher | Independent QCD characterization, trigger studies and closure validation; source effective luminosities 14.8-454.1 nb^-1 |
| Empty-crossing data with a CalRatio-like trigger | Cosmic-ray estimate |
| Unpaired isolated-crossing data with a CalRatio-like trigger | Beam-halo estimate |
| Random collision-trigger data | Probability for incidental tracks to spoil cosmic-jet isolation |
| Source Hidden Valley signal simulations listed below | Acceptance, trigger efficiency, lifetime dependence and signal contamination in ABCD regions |
| Inclusive multijet simulation used for detector-performance studies | Data/MC response and pile-up checks; not the nominal QCD normalization |
| Additional electroweak/top simulation or control data, if needed by the audit | Bound non-QCD collision contamination in all four regions; no fixed yield assumed |

Concrete dataset/derivation identifiers and generated sample lifetimes are not given in the paper. No modern data-format default is imposed.

Source signal generation: PYTHIA 8.165 with MSTW2008, gluon fusion only, GEANT4 detector simulation, data-equivalent reconstruction and pile-up reweighting. The scalar has SM-Higgs-like production at each mass and 100% generated branching fraction to pi_v pi_v. Preserve these actual benchmark combinations:

| Parent mass [GeV] | pi_v mass [GeV] | Source ggF cross section [pb] |
| --- | --- | --- |
| 100 | 10, 25 | 29.7 |
| 126 (Higgs) | 10, 25, 40 | 19.0 |
| 140 | 10, 20, 40 | 15.4 |
| 300 | 50 | 3.59 |
| 600 | 50, 150 | 0.52 |
| 900 | 50, 150 | 0.06 |

Each comma-separated entry denotes a separate benchmark at that row's parent mass, not a Cartesian product across rows. Low-mass samples have parent mass below 300 GeV; the remainder are high-mass samples. Source pi_v branching fractions are:

| pi_v mass [GeV] | bb [%] | tau+ tau- [%] | cc [%] |
| --- | --- | --- | --- |
| 10 | 70.0 | 16.4 | 13.4 |
| 20 | 86.3 | 8.0 | 5.6 |
| 25 | 86.6 | 8.1 | 5.3 |
| 40 | 86.5 | 8.5 | 5.0 |
| 50 | 86.2 | 8.8 | 4.9 |
| 150 | 84.8 | 10.2 | 4.8 |

Small deficits from 100% in the displayed source fractions must not be silently renormalized.

## Backgrounds

* QCD multijets: dominant; infer from CalRatio collision-data regions B, C and D using the ABCD relation below. Do not reuse the source 23.2 +/- 8.0 prediction, the P/Q fits, or their 1.8 +/- 0.5 correction as a prior, normalization or ABCD correlation factor.
* Cosmic rays: retain the source empty-crossing method (Section 5). Apply the selection except primary-vertex and timing requirements, then account for timing acceptance, trigger exposure and incidental collision tracks. Source reference values: about 5% double-jet timing acceptance, 2.9 exposure scaling, isolation weights 0.55-0.63, and 0.3 +/- 0.2 events in the signal region. Estimate contamination separately in B/C/D using their actual pass/fail definitions; the signal-region isolation correction cannot simply be copied to track-fail regions.
* Beam halo: retain timing rejection and the veto on endcap muon segments aligned in phi with jets. Use unpaired isolated crossings and artificial jet pairs as in Section 5, applying the missing-momentum requirement and correcting cosmic contamination. The source estimates 0.07 +/- 0.07 signal-region events and treats this as negligible. Retain that source treatment in A only if reproduced; reassess in sidebands.
* Mixed noncollision/collision events: the source found combinations such as halo plus multijet or halo plus cosmic negligible. Check this conclusion in the newly introduced sidebands.
* Background audit additions: check W/Z+jets, top, prompt photons/electrons, heavy-flavor jets, instrumental noise and calorimeter pathologies. Heavy-flavor and prompt-QCD components belong in the inclusive multijet estimate, not a second additive QCD component. Other collision processes must be bounded or modeled separately if significant. The source does not provide their individual yields. Low missing momentum and jet quality suppress several of these contributions but are not proof of negligible contamination.

## Data Required

### Collision data and background control samples

* Event identity, data quality, luminosity/exposure, bunch category, trigger decisions and prescales, trigger-object matching, pile-up indicators, primary-vertex tracks and missing transverse momentum.
* All relevant jets, not just two leading jets: calibrated ET, eta, phi, hadronic and electromagnetic energies or EMF, modified jet-quality flags, energy-weighted cell timing and beam-halo rejection information.
* Tracks: pT, eta, phi, pixel hits and combined pixel/SCT hits; retain tracks needed for the offline cone and trigger comparisons.
* Empty/unpaired/random-crossing exposures and timing/track information needed for the noncollision corrections.

### Signal and performance simulation

* The corresponding reconstructed quantities, trigger emulation, event weights, generated cross sections, generated proper lifetime and normalization metadata.
* LLP identities, decay modes, four-momenta/boosts and truth decay positions; parent kinematics and ISR information for source systematic studies.
* Acceptance and uncertainty information in A/B/C/D for every benchmark and lifetime considered.
* No specific container names, calibration releases or missing metadata values are assumed.

## Triggers

* CalRatio, signal and nominal ABCD sample (source Section 4): first level requires at least 40 GeV ET in a 0.2 x 0.2 region using topological jets; this threshold is fully efficient at offline jet ET = 60 GeV. Second level requires log10(EH/EEM) > 1.2 and no tracks with pT > 1 GeV in a 0.2 x 0.2 window. Third level reconstructs anti-kt R = 0.4 jets with minimum ET of 35 GeV.
* Require a qualified offline jet that fired CalRatio with ET > 60 GeV. The companion jet requires ET > 40 GeV. If multiple selected jets fired, the leading such jet supplies the >60 GeV requirement. Do not assume the matched jet is the leading reconstructed jet.
* The ET plateau statement does not establish full-chain efficiency for track or energy-ratio requirements.
* Prescaled single-jet triggers provide independent diagnostic data; account for exposure and trigger bias. The source's DeltaPhi > 2.0 requirement belongs to its probability-measurement sample, not to the nominal event or ABCD selection.
* Apply ABCD variables to the companion probe, not the trigger tag. Do not require the probe to fail trigger matching: that would remove valid double-trigger signal events. Residual trigger-OR and tag-choice biases must be included in closure studies.

## Object Definitions and Roles

* Jets: anti-kt R = 0.4 from locally weighted calorimeter clusters, followed by the source energy/eta-dependent simulation calibration. Apply standard source good-jet criteria with the low-EMF-rejecting requirements removed. Do not add an offline narrowness cut absent from the paper.
* Base jet: ET > 40 GeV, |eta| < 2.5, modified good-jet criteria and -1 < t < 5 ns. Time is the energy-weighted calorimeter-cell time relative to a beta = 1 particle from the interaction point.
* Define h = log10(EH/EEM), equivalently log10((1-EMF)/EMF) when defined, and n = number of good tracks within DeltaR < 0.2 of the jet axis. A good track has pT > 1 GeV, at least two pixel hits and at least nine combined pixel/SCT hits. No additional primary-vertex association cut is introduced. The superscript footnote after 0.2 in the PDF is not a cone size of 0.22.
* Full candidate: base jet with h > 1.2 and n = 0.
* Tag: the highest-ET full candidate matched to a fired CalRatio object with ET > 60 GeV. This deterministic assignment is a new bookkeeping choice; it does not require that tag to lead all jets.
* Probe pool: all other base jets. To preserve the original inclusive treatment of extra ordinary jets, choose a single probe by smallest n, then largest h, then largest ET, with a stable final tie-break. Undefined calorimeter ratios need the source reconstruction convention before this ordering can be used; do not substitute arbitrary numerical ratios.
* This proposed ordering deliberately ensures that a full candidate, if present, is chosen as probe. It can create correlations and must be validated as part of the ABCD method. Choosing the two leading reconstructed jets or requiring exactly two base jets instead would change the source signal region.

## Analysis Regions

Common preselection, applied identically in A/B/C/D:

* Good-quality collision data with a primary vertex having at least three tracks with pT > 1 GeV.
* Reject events with any reconstructed jet identified as beam halo; require missing transverse momentum < 50 GeV.
* Require a tag and at least one other base jet, and assign the probe as above.
* Require no more than two full candidates in the event. This common veto preserves the published rejection of three or more full candidates. Additional jets failing full-candidate requirements are allowed.

Proposed ABCD axes are X = h(probe) and Y = n(probe). Initial sidebands use the complete complement of each pass requirement; no unsupported numerical lower h cut or upper track-count cut is invented.

| Region | Purpose | Requirements beyond common preselection |
| --- | --- | --- |
| A / signal region | Signal count; pass/pass | X > 1.2 and Y = 0 |
| B | Hadronic-energy-pass, track-fail | X > 1.2 and Y >= 1 |
| C | Hadronic-energy-fail, track-pass | X <= 1.2 and Y = 0 |
| D | Double fail | X <= 1.2 and Y >= 1 |
| Validation families | Test transfer without using A | Auxiliary rectangles within X <= 1.2 or Y >= 1, defined before examining A; examples below |

Equivalence check: an original selected event has exactly two full candidates and an eligible trigger-matched >60 GeV candidate. The tag is one of them; the minimum-n/maximum-h probe ordering selects the other even when additional ordinary jets are present. Conversely, A contains a tag and a full-candidate probe, and the common multiplicity veto excludes a third full candidate. Thus A is the published signal selection, with no added DeltaPhi or reconstructed-jet-multiplicity restriction.

All events contribute once. B/C/D contain one full candidate, the tag. That multiplicity change, the ranking, and the trigger requirement can generate nonfactorization; the ABCD formula is a hypothesis to validate, not a consequence of the region definitions.

## Histograms

1. Source-comparison cutflow: counts after collision quality/vertex, trigger, missing momentum/halo rejection, base jets, candidate identification and exactly-two full candidates. One entry per event per cut stage.
2. ABCD occupancy: two-dimensional X versus Y and the four event counts; X is dimensionless, Y is an integer. Include the 1.2 and zero-track boundaries and preserve the high-track tail.
3. Tag and probe diagnostic distributions: ET [GeV], eta, h, n and time [ns], plus event missing momentum [GeV], DeltaPhi [rad], base-jet multiplicity and pile-up. One entry per named object or event, split by region and trigger multiplicity.
4. Closure summaries: measured/predicted validation yields, pulls and kappa versus probe ET/eta, pile-up, tag kinematics and jet multiplicity.
5. Signal acceptance and yield versus c*tau [m], per actual benchmark, with the c*tau = 1.5 m reference table and uncertainty components.
6. Observed 95% CL upper limits versus c*tau: sigma(gg -> Phi) times BR(Phi -> pi_v pi_v) [pb], and the Higgs normalized quantity divided by 19.0 pb. Include the 10% and 30% branching-fraction interpretations.

Diagnostic histogram binning is not fixed by the paper; choose it to resolve selection boundaries and permit meaningful uncertainties. The final inference is a counting analysis, not a histogram-shape fit.

## Analysis Steps

1. Apply event requirements and build base jets, good-track counts and full candidates without discarding jets needed for sidebands or multiplicity counting.
2. Assign tag/probe once, apply the common candidate veto and classify A/B/C/D.
3. Estimate cosmic, halo and any significant additional non-QCD contributions in each region. Define q_R as the underlying QCD yield, not the total observed count N_R.
4. Use the ABCD transfer relation q_A = kappa * q_B * q_C / q_D. For exact conditional factorization kappa = 1. Non-QCD-subtracted control counts provide a diagnostic estimate, but the nominal inference uses Poisson counts with additive contamination components.
5. Determine whether kappa = 1 is supported by independent validation. Any correction and its uncertainty require a justified extrapolation from control data; never determine kappa by forcing agreement with A or by borrowing the old P/Q correction. If nonclosure cannot be bounded, the proposed ABCD axes do not support a reliable limit and must be revised within the requested ABCD method.
6. Preserve the source lifetime procedure (Section 7): generate a large ensemble of pi_v decays spanning 0-50 m and use an efficiency map dependent on LLP boost to evaluate efficiencies at different proper decay lengths. Retain the decay-position, geometry, kinematic and timing acceptance. The paper does not specify the full map binning or sampling implementation; obtain or reconstruct these and validate against the generated samples. Do not silently substitute mass interpolation or pure event lifetime reweighting for the stated procedure.
7. Normalize signal using luminosity, the appropriate row's production cross section and branching fraction, and evaluate leakage in all four regions at each lifetime.
8. Validate and freeze the background construction before using A to obtain the observed result.

## Workflow

1. Data Extraction and NTuple Skimming
   * Preserve all base jets and their track/energy information, trigger matching and event metadata. Do not skim on probe h, zero tracks, exactly two reconstructed jets or a back-to-back requirement. Noncollision streams need separate skims that retain events failing vertex/timing cuts.
2. Data Analysis and Histogramming
   * Construct derived quantities, count full candidates, assign roles and fill region flags, cutflows and diagnostics consistently.
3. Background Estimation
   * Derive noncollision corrections, audit other contamination, test ABCD closure and produce control yields and the justified kappa constraint.
4. Statistical Model Construction
   * Construct the four-region counting model including signal in controls, correlated detector uncertainties and the non-QCD constraints. Propagate lifetime-dependent acceptance to limits.

## Validation and Cross-checks

* Source fidelity: reproduce the signal-region selection and compare the published 24 selected events if the identical dataset/reconstruction is available. This number is a historical reference, not a new measurement or a target for background tuning.
* At c*tau = 1.5 m the source expected signal yields are 536, 941, 365 for (126,10/25/40); 440, 424 for (100,10/25); 525, 900, 641 for (140,10/20/40); 444 for (300,50); 35, 41 for (600,50/150); and 3.5, 4.6 for (900,50/150), at 100% branching fraction. Validate statistical precision against source Table 3.
* Test ABCD with auxiliary four-bin rectangles wholly outside A. Proposed examples: in X <= 1.2 split X at 0 and Y into 0 versus >=1; in Y >=1 split X at 1.2 and Y into 1 versus >=2. Apply the same tag/probe algorithm and common selection. These are new validation choices, not published regions. Assess signal leakage before calling them signal depleted.
* Test additional adjacent sideband splits, not just the broad tails. Compare closure versus kinematics, detector region, pile-up, run period, base-jet multiplicity and number of trigger-matched jets. A small linear correlation alone is insufficient evidence of tail factorization.
* Use independent single-jet data to examine trigger bias and selection-induced correlations, with prescale/exposure accounting. Its lower luminosity may limit this check. Ensure validation samples overlapping B/C/D are not counted as statistically independent constraints without accounting for overlap.
* Test signal injection and contamination for each benchmark/lifetime; model signal in controls even when it is small.
* Validate the efficiency map at generated lifetimes and across barrel/endcap and LLP boosts. Preserve the loss from delayed timing and missing momentum; the source quotes at most 1.5% timing inefficiency for its considered samples.
* No closure result, numerical kappa, background yield or new exclusion is claimed by this specification. If available controls cannot constrain the extrapolation to A, document that limitation before inference.

## Systematic Uncertainties

### Source-analysis uncertainties

* Luminosity: 2.8%. Signal production cross-section uncertainty: approximately 10%, with benchmark-dependent asymmetric values in source Table 2.
* Signal PDF acceptance: 2.1%; source reweights MSTW2008nlo68cl, CT10 and NNPDF2.3 and their error sets.
* Pile-up acceptance: 10%, especially incidental tracks spoiling isolation; retain source comparisons of ET, EMF, eta, phi, tracks and timing versus pile-up.
* JES: use the source low-EMF-specific response study with dijet balancing versus eta and EMF, not an ordinary-jet JES assumption. Retain benchmark-dependent variations from Table 2 for source reproduction.
* Trigger, missing momentum and timing: source Table 2 variations; trigger checks separately vary ET, energy ratio and track requirements. Missing momentum and timing studies smear the relevant cut response.
* ISR acceptance: +2.9/-1.2%; source halves/doubles the ISR-jet population and varies ISR jet pT by 5% for the parent-boost effect, adding those two correlated effects. Source FSR acceptance effects are negligible.
* Signal MC statistics: source Table 3; propagate finite efficiency-map precision as well when reconstructed.
* Source noncollision statistical errors and exposure/isolation corrections remain relevant. Original QCD P/Q fit, ET/eta-factorization and DeltaPhi-selection errors are retired with that estimator.
* Retain component uncertainties, not the Table 2 total in addition to its components. Source Table 2 is the authoritative per-benchmark numerical prescription; new control-region responses require reevaluation rather than assigning A's percentage to every region.

### New-method uncertainties

* Finite B/C/D counts, included directly as Poisson information.
* ABCD nonclosure and extrapolation of kappa into A; selection/ranking, calorimeter-track correlations, trigger effects and stability under sideband changes. Quantify from independent validation; no fixed percentage is assumed.
* Non-QCD contamination and its subtraction/modeling in all regions; signal leakage and acceptance migrations.
* Correlate shared physical effects across regions. Propagate effects on both yields and the transfer relation without double counting validation statistics as a separate systematic.

### Modernization/adaptation uncertainties

* None imposed: this remains a Run 1 analysis. A future change of run, trigger, reconstruction or calibration would require a separate acceptance and systematic reevaluation and is outside the requested scope.

## Statistical Analysis

* Source treatment (Section 7): a single signal-region event count, profile-likelihood-ratio test statistic, frequentist toy experiments and CLs upper limits at 95% CL; systematic nuisance effects with assumed Gaussian constraints. The paper reports observed limit curves. Do not relabel them as expected limits or use asymptotic formulae as a source reproduction.
* Requested-method extension: a simultaneous product of Poisson terms for A, B, C and D, with mean lambda_R = mu*s_R(theta) + q_R + b_R(theta). Here mu scales a specified reference signal, b_R contains non-QCD contributions, and all yields are nonnegative.
* A convenient positive QCD parameterization is q_D = d, q_B = r_X*d, q_C = r_Y*d and q_A = kappa*r_X*r_Y*d. Constrain kappa from validated auxiliary information; leaving it free alongside mu removes the useful ABCD prediction. Preserve Gaussian constraints for appropriate source effects; any positive multiplicative constraint for kappa is a new-method choice.
* Sparse or zero control counts are treated in the likelihood, not by dividing by zero or inserting pseudocounts. If the controls fail to identify the transfer, report the lack of sensitivity.
* Parameters of interest: sigma(gg -> Phi)*BR(Phi -> pi_v pi_v), and the corresponding ratio to sigma_SM = 19.0 pb at mH = 126 GeV, separately for each actual mass pair and lifetime. Track the reference theory uncertainty consistently when mapping mu to a cross section; do not add the same production uncertainty twice.
* Preserve toy-based profile-likelihood CLs inference. Historical 23.5 +/- 8.0 total background and published exclusion intervals are comparison results only and must be recalculated with the new estimate.
* Required outputs: observed 95% CL limits and the 10%/30% Higgs branching-fraction excluded lifetime intervals. Expected-limit bands may be added later but are not claimed as source outputs here.

## For Review

* Proposed ABCD choices, pending control-data validation: probe h versus good-track count, full-complement sidebands, and minimum-track/maximum-h probe ranking. These preserve the original A selection but do not guarantee factorization. The optional user question about preferred axes/boundaries remains open to revision.
* Dataset identifiers, generated lifetimes, complete efficiency-map construction and exact trigger matching/quality conventions are not supplied in the paper. Recover them from the original analysis metadata; do not fabricate modern replacements.
* The physical treatment of zero/negative calibrated EM or hadronic energy in h is not documented in the paper. Recover its convention before populating or ordering those jets; preserve the original treatment for A and quantify any sideband sensitivity.
* The paper's multiple-trigger wording does not enumerate cases where a trigger-matched jet fails offline candidate cuts. This specification interprets the trigger requirement as needing a matched selected candidate, consistent with the stated final jet selection. Compare against original selection code if available.
* No collision data, control counts or simulation files were supplied beyond the paper. The specification is complete as a proposed analysis definition, but ABCD closure, contamination, uncertainties and new limits have not been measured.
