# Run 3 search for pair-produced neutral long-lived particles decaying in the hadronic calorimeter

Search for a scalar boson decaying to two neutral long-lived particles (LLPs), each reconstructed as a trackless, hadronic-energy-dominated jet.
Constrain scalar production times branching fraction as a function of LLP proper decay length, using a data-driven ABCD estimate of QCD multijet background.

## Source and Scope

* Analysis mode: source-derived analysis with requested changes.
* Primary source: supplied `1501.04020v2.pdf`, ATLAS, "Search for pair-produced long-lived neutral particles decaying to jets in the ATLAS hadronic calorimeter in pp collisions at sqrt(s) = 8 TeV", arXiv:1501.04020v2. Section references below refer to this local PDF's numbered analysis sections, not PDF page numbers.
* Target realization: ATLAS Run 3, explicitly requested; pp collisions at 13.6 TeV. Select certified periods with suitable trigger coverage; neither the data-taking years nor the luminosity have been specified.
* Physics intent: gluon-fusion production of a scalar Phi (including a Higgs-like benchmark), followed by Phi -> pi_v pi_v in a Hidden Valley model. The neutral pseudoscalar pi_v decays preferentially to heavy fermions. Both LLPs decay near the outer ECal or in the HCal, each producing one narrow calorimeter jet with little electromagnetic energy and no associated good ID tracks. No reconstructed displaced vertex is required.
* Historical realization: 2012 data at 8 TeV, 20.3 fb^-1, a dedicated CalRatio trigger, and exactly two jets satisfying the displaced-candidate selection. These are historical data conditions, not Run 3 normalization inputs.
* Requested deviations: Run 3 adaptation and replacement of the QCD estimate by ABCD. The user's statement that the original method failed motivates the replacement; the paper itself reports successful validation and no significant excess. Do not attribute the user's diagnosis to the publication.
* Added elements: explicit tag/probe assignment, ABCD controls and validation, joint signal/background inference across four regions, and Run 3 performance requirements. The ABCD axes below are a proposed concrete baseline, not an experimentally validated result.
* Supporting research: the [ATLAS Run 3 trigger paper](https://arxiv.org/abs/2401.06630) documents 13.6 TeV operation and major trigger changes. It does not establish the particular CalRatio chain, plateau, or exposure needed here. These require period-specific confirmation. The later [ATLAS calorimeter LLP search, Section 5](https://arxiv.org/pdf/1902.03094) provides a precedent for ABCD with signal contamination included in a simultaneous fit; it uses different discriminants and does not validate the axes proposed here.

## Data Samples

| Data sample | Role(s) in analysis |
| --- | --- |
| Certified Run 3 pp data with a suitable single-candidate CalRatio-like trigger | Nominal A/B/C/D regions and controls; effective luminosity determined from actual trigger availability and data quality |
| Independent inclusive-jet triggered Run 3 data, including prescaled triggers where useful | Calorimeter response, trigger efficiency, QCD correlations, independent closure; retain trigger prescales and exposure |
| Empty-bunch data with appropriate calorimeter triggers | Cosmic-ray and instrumental-background estimates |
| Unpaired isolated-bunch data with appropriate calorimeter triggers | Beam-induced background (BIB) estimate and veto validation |
| Zero-bias/random collision data | Accidental-track and collision-overlay corrections for non-collision samples |
| Run 3 detector-simulated signal at the mass pairs below | Acceptance, all-region signal leakage, efficiency maps and lifetime-dependent predictions |
| Run 3 QCD multijet simulation, with heavy-flavour components represented | Diagnostic closure, composition and response studies; not the nominal QCD normalization |
| Run 3 W/Z+jets, ttbar, single-top and diboson simulation | Audit prompt collision contamination in every ABCD region; constrain any non-negligible contribution separately |

The source simulated gluon fusion with PYTHIA 8.165 and MSTW2008, full GEANT4 response, and pile-up reweighting. These versions and the source's 8 TeV cross sections are historical only. Run 3 requires validated generation, detector simulation, reconstruction and 13.6 TeV normalization. No dataset or derivation identifiers are supplied; do not assume PHYSLITE retains the necessary calorimeter, track, timing, and trigger information.

Preserve these actual source benchmark combinations, in GeV; entries within a row are the only LLP masses paired with that parent mass:

| Parent mass | LLP masses |
| --- | --- |
| 100 | 10, 25 |
| 126 (source Higgs benchmark) | 10, 25, 40 |
| 140 | 10, 20, 40 |
| 300 | 50 |
| 600 | 50, 150 |
| 900 | 50, 150 |

There are 13 mass pairs, not a Cartesian product. Preserve the 126 GeV point as a source benchmark; do not silently relabel it as a modern Higgs mass point. Any additional Higgs mass or mass-grid extension is a separate model choice. Retain gluon fusion only for the baseline interpretation.

Source pi_v branching fractions (percent), from Table 1:

| pi_v mass [GeV] | bb | tau+tau- | cc |
| --- | --- | --- | --- |
| 10 | 70.0 | 16.4 | 13.4 |
| 20 | 86.3 | 8.0 | 5.6 |
| 25 | 86.6 | 8.1 | 5.3 |
| 40 | 86.5 | 8.5 | 5.0 |
| 50 | 86.2 | 8.8 | 4.9 |
| 150 | 84.8 | 10.2 | 4.8 |

Use the benchmark decay model, not a pure bb approximation. The published fractions are rounded and do not all sum exactly to 100%; establish the complete decay configuration before generation rather than inventing missing fractions. Generated lifetimes must cover the efficiency-map domain; exact source generated lifetimes are not specified in the paper. Source comparisons use c*tau = 1.5 m.

## Backgrounds

* QCD multijets: expected dominant background, including neutral-rich jets, heavy flavour and misreconstruction. Replace the source's fitted per-jet P/Q probabilities, combinatorial event weights, and extrapolated inter-jet correction by the ABCD model below. Neither the historical 1.8 correction factor nor the 23.2 +/- 8.0 event estimate is an input to Run 3.
* Cosmic rays: source-subdominant, but remeasure for Run 3. Use empty crossings with vertex and timing cuts relaxed for measurement; restore joint two-jet timing acceptance, trigger live-time normalization, collision-overlap/PV probability and accidental-track isolation effects. The historical 0.3 +/- 0.2 events, 5% timing fraction and 2.9 exposure ratio are not transferable.
* Beam-induced backgrounds: use unpaired isolated crossings and muon-segment/jet alignment information. Preserve timing and BIB rejection intent. The source used artificial jet pairs and MET acceptance to estimate 0.07 +/- 0.07 events; any reuse of this construction requires Run 3 validation of pairing and exposure. Do not assume the old negligible yield persists.
* Prompt electroweak/top backgrounds: not separately quantified in the source. Audit W/Z+jets (including invisible and tau decays), ttbar, single top and dibosons in A, B, C and D with simulation and suitable data controls. Low MET and two unusual jets suppress them but do not prove they vanish. No new lepton veto is imposed by default.
* Instrumental effects: audit calorimeter noise, dead/problematic channels, coherent bursts, timing anomalies and reconstruction failures using detector-quality controls. Exclude bad periods and validate dedicated cleaning; an instrumental population need not obey QCD factorization.
* Mixed backgrounds: test BIB/cosmic plus collision jets, and accidental overlapping non-collision deposits. Include or bound them using measured overlap rates. Avoid counting the same component both in QCD and in an additive non-QCD model.

Only QCD is constrained by the ABCD transfer relation. Other components require region-specific estimates or demonstrated negligible upper bounds.

## Data Required

### Collision data and reconstructed simulation

* Run, luminosity block, event identifier, bunch category, data-quality and detector-status information; integrated and effective luminosities, live time, trigger prescales and overlap information.
* Trigger decisions, available online objects and offline matching information, including whether the tag alone satisfies the complete trigger path.
* All relevant calorimeter jets before track-isolation and energy-ratio cuts: four-momentum, ET, eta, phi, E_H and E_EM (or equivalent validated sampling information), cleaning inputs, energy-weighted cell timing, and associated muon segments/BIB flags.
* ID tracks, momenta, positions/directions, quality and hit information sufficient to reproduce the good-track selection and count tracks within DeltaR < 0.2 of each jet. Retain pile-up tracks; do not silently change to PV-only isolation.
* Reconstructed vertices and their tracks; MET and inputs needed to assess its response to unusual jets; pile-up observables and additional-jet multiplicity.
* Information to distinguish non-positive or invalid calorimeter energy measurements from valid near-zero electromagnetic energy. Define a common, calibrated treatment before freezing regions; never silently turn invalid ratios into high-ratio candidates.

### Signal simulation

* Parent and both LLP truth four-momenta, decay positions, proper decay times, decay modes, and matching to reconstructed objects.
* Generator weights, cross section, filter efficiency, sums of weights, pile-up and performance corrections; generated-lifetime and geometry metadata.
* Event-level efficiencies and correlations for the complete selection, including timing, MET, tag assignment and region migrations.

### Non-collision and auxiliary samples

* The same object-level information as collision data, plus bunch-pattern occupancy, trigger live times, timing beyond the nominal window, and muon-segment information.
* Zero-bias measurements of accidental tracks and collision overlap as functions of eta, pile-up and period.

## Triggers

* Historical CalRatio signal trigger (source Section 4): L1 ET >= 40 GeV in a narrow 0.2 x 0.2 region; L2 log10(E_H/E_EM) > 1.2 and no tracks with pT > 1 GeV in a 0.2 x 0.2 region; final-level anti-kt R = 0.4 jet with minimum ET 35 GeV. The source reports the L1 threshold fully efficient at offline ET = 60 GeV; this does not mean the entire trigger is fully efficient for LLPs.
* Run 3 signal trigger requirement: a verified single-candidate CalRatio-like path, supported by the fully selected tag alone. Establish menu, prescales, matching, turn-on and response versus decay position, energy, eta, timing and pile-up in each period. A path requiring two unusual jets cannot populate the proposed probe fail regions in the required way.
* Define T_tag(period) = max(60 GeV, validated offline energy threshold for the selected Run 3 path). Its numerical value is unresolved. Retain residual trigger efficiency explicitly in signal acceptance. The probe baseline remains ET > 40 GeV unless measured trigger/event correlations require a documented adaptation.
* Never require the probe to trigger, nor veto events where it also triggers. A fully accepted tag is required in every ABCD region; study residual global-trigger and tag/probe correlations. The tag may be subleading among all reconstructed jets.
* Inclusive-jet and random triggers provide independent performance/control data. Their historical 15 GeV thresholds and exposures are not Run 3 requirements. Correct their sampling and overlaps explicitly.
* Empty/unpaired-bunch triggers require separate exposures and efficiency validation.

## Object Definitions and Roles

* Jets: calorimeter-based anti-kt R = 0.4 jets, preserving the source topology. Historical inputs were locally weighted clusters with energy/eta-dependent calibration. Use Run 3 validated calorimeter reconstruction and low-EMF response; ordinary prompt-jet or particle-flow calibration is not automatically valid for this signature.
* Loose candidate: ET > 40 GeV, |eta| < 2.5, dedicated good-jet cleaning that permits small EMF, and -1 < t < 5 ns. Do not apply isolation or calorimeter-ratio cuts at this stage. Additional reconstructed jets are allowed.
* Tight candidate: a loose candidate also satisfying h = log10(E_H/E_EM) > 1.2 and n = 0 good tracks with pT > 1 GeV within DeltaR < 0.2. These retain the source thresholds as the proposed Run 3 baseline, subject to detector-performance validation.
* Good track: source definition is at least two pixel hits and at least nine pixel+SCT hits in total. Its Run 3 translation must be fixed consistently in signal, controls and simulation after validating efficiencies/fakes. Until then this is a reference selection, not an assertion of an approved Run 3 working point.
* Timing: energy-weighted average of jet-cell times relative to a beta = 1 particle from the IP. Preserve the source window, but quantify late LLP inefficiency versus mass and lifetime. The source's at-worst 1.5% loss is not a Run 3 guarantee.
* Tag: highest-ET tight candidate that matches and independently satisfies the signal trigger and has ET > T_tag(period). Among multiple eligible tags choose only one; define a stable tie-breaker. Highest ET is among eligible tags, not among all jets. This preserves the source requirement that the trigger-matched candidate, rather than an unrelated leading jet, satisfies the higher threshold.
* Probe: after tag assignment and the common tight-candidate multiplicity veto below, select the remaining tight candidate if one exists; otherwise select the highest-ET remaining loose candidate. Count each event once. This tight-first rule preserves the source's exactly-two-selected-candidates signal acceptance even when ordinary jets have larger ET than a signal candidate.

The probe assignment is a new analysis convention needed to make a single event-level ABCD table explicit. Because it uses the tight selection, it can induce correlations, especially with several possible probes. It is not an innocuous ranking rule: validate the full assignment, including the multiplicity veto, in closure tests. Do not use an independence claim measured on unselected individual jets. If this convention prevents reliable closure, the ABCD definition must be revised before use; silently restricting the analysis to exactly two reconstructed jets is not an acceptable fix.

## Analysis Regions

Common preselection, applied identically before ABCD assignment:

* Certified collision data and the approved signal trigger, with tag-supported acceptance.
* A primary vertex with at least three tracks of pT > 1 GeV (source baseline, to be validated for Run 3).
* Veto an event if any reconstructed jet exhibits the defined BIB signature, including relevant endcap muon-segment alignment. Require MET < 50 GeV. Use full-event information for these cuts, not just the chosen pair.
* At least two loose candidates, and at least one eligible tag.
* At most two tight candidates in the entire loose-candidate pool. This is a veto on a third tight candidate, not on ordinary extra jets.
* Assign tag and probe as defined above. No DeltaPhi > 2 requirement is applied: in the source that cut belonged to background-measurement samples, not the signal selection.

Proposed ABCD axes: X = probe h, Y = probe n. The nominal pass boundary h > 1.2 and n = 0 retains the source's signal criteria; h = 1.2 is fail. All valid low-h jets and all n >= 1 jets are initially retained for fail regions, with population and boundary stability tested before finalization.

| Region | Purpose | Additional requirements on the probe |
| --- | --- | --- |
| A / SR | Signal and pass/pass | h > 1.2, n = 0 |
| B | High-h, non-isolated control | h > 1.2, n >= 1 |
| C | Low-h, isolated control | h <= 1.2, n = 0 |
| D | Fail/fail control | h <= 1.2, n >= 1 |
| VR-H plane | Closure below nominal h boundary | Restrict h <= 1.2; split X at h = 0 (pass: 0 < h <= 1.2; fail: h <= 0), Y at n = 0 versus n >= 1 |
| VR-N plane | Closure with nonzero track multiplicity | Restrict n >= 1; X split at h = 1.2; Y split at n = 1 versus n >= 2 |

VR splits are proposed validation definitions, not source cuts. They reuse the nominal event assignment without reranking when VR boundaries change. Both exclude A, but share some events with B/C/D and each other; use their covariance and do not add them as independent Poisson data alongside the same events. Reserve disjoint data subsets if using VR information to constrain fit nuisances and assess held-out closure.

Equivalence check: A contains the tight tag and a tight probe, while the common veto excludes a third tight candidate. Conversely, every event passing the translated source selection has exactly two tight candidates, at least one eligible tag, and the tight-first probe selects the other. Thus A is exactly the translated source SR, including events with additional ordinary jets. There are no further A-only cuts. The comparison assumes the stated Run 3 trigger and object translation; it is not equality of Run 1 and Run 3 efficiencies.

## Histograms

1. Event cutflow and region yields: one entry per event; include trigger, vertex, BIB, MET, loose candidates, tag, tight multiplicity, and A/B/C/D. Provide signal efficiency, weighted yields, raw data counts and effective exposure by period.
2. ABCD plane: probe h versus integer n, one entry per selected event; mark all boundaries, include low-h and high-n tails, show QCD diagnostics and signal leakage. Keep A blinded until validation is frozen.
3. Tag/probe kinematics: ET [GeV], eta, h, n, time [ns]; one entry per named role per event, split by region and period. Also plot MET [GeV], DeltaPhi(tag,probe), loose/tight jet multiplicities and pile-up.
4. Closure: observed/predicted yield and kappa in validation planes versus candidate ET/eta, detector region, extra-jet multiplicity, pile-up and period. Include uncertainty and any control overlap covariance.
5. Trigger and reconstruction efficiency: efficiency versus LLP decay radius r [m], |z| [m], boost and reconstructed ET; distinguish single-LLP efficiencies from the two-LLP event acceptance.
6. Lifetime response: event acceptance and expected signal yields in all four regions versus c*tau [m], separately for each mass pair; compare generated and map-predicted points.
7. Final interpretation: observed 95% CL upper limits on sigma(gg -> Phi) x BR(Phi -> pi_v pi_v) [pb] versus c*tau [m]; normalized Higgs-like limits where a defined Run 3 reference cross section exists. Expected median and bands are a declared addition.

No arbitrary production histogram binning is fixed here. Preserve exact cut boundaries and discrete track counts; choose remaining bins using resolution and available control statistics before unblinding.

## Analysis Steps

1. Establish certified Run 3 exposure and required trigger/object performance. Retain fail regions through every extraction and cleaning stage; apply common event requirements.
2. Form loose and tight candidates, apply the global tight-multiplicity veto, assign the tag/probe exactly once, and construct A/B/C/D flags. Check trigger support in all four regions.
3. Estimate each non-QCD component in each region. For diagnostic transfers define q_R = N_R - b_R(other); final fits use raw counts and additive backgrounds, not Gaussian errors on subtracted counts.
4. Specify the QCD transfer as q_A = kappa * q_B * q_C / q_D, where kappa = q_A*q_D/(q_B*q_C) for the true QCD population. Independence corresponds to kappa = 1. Neither independence nor a numerical kappa is established by this specification.
5. Measure closure in VR-H, VR-N and independent jet-triggered data; use QCD simulation for auxiliary composition and higher-dimensional checks. Condition on tag requirements and examine the tight-first ranking explicitly. Assess correlations from neutral fraction, charged multiplicity, calorimeter material, shared pile-up, flavour, energy balance, extra jets, MET, and trigger selection.
6. Define any necessary exclusive period/kinematic/multiplicity categories before unblinding, and constrain each category's kappa from independent validation with an extrapolation uncertainty. Do not infer kappa freely from SR data: four unconstrained QCD yields would destroy the background prediction. Do not transplant the source correction or later analyses' closure uncertainties.
7. Predict signal versus lifetime using the source mechanism: generate a large ensemble of LLP decays over the 0-50 m proper-decay-length study range and use boost-dependent efficiency maps to obtain yields. Rebuild maps for Run 3; retain decay-position dependence, both LLP kinematics and event-level cuts/correlations. The paper does not specify all map axes or sampling details, so these need validation rather than reconstruction by guesswork. Include correct decay probabilities; never condition away decays outside the detector. Validate at directly simulated lifetimes and restrict reported limits to supported coverage. Simple interpolation of the historical yield curve is not sufficient.
8. Normalize signal as N_R = L * [sigma(gg -> Phi) * BR(Phi -> pi_v pi_v)] * acceptance_R(c*tau), with the LLP decay mixture included in acceptance and generator/filter normalization consistently handled. Do not double-count LLP branching fractions. Repeat for A/B/C/D to retain signal leakage.
9. Freeze selections, validation and uncertainty model before inspecting A; then fit and report the final inference. Unresolved trigger coverage or failed closure prevents a numerical physics result, not writing this specification.

## Workflow

1. Data extraction and skimming
   * Retain all loose candidates, tracks, trigger information, timing and background flags; never prefilter on probe h > 1.2 or n = 0. Preserve separately the relaxed vertex/timing selections required by non-collision controls.
   * Record exposure, weights, truth and detector-performance metadata described under Data Required.
2. Data analysis and histogramming
   * Apply common selection, deterministic roles and mutually exclusive region flags. Fill cutflows, diagnostics, signal efficiency maps and validation planes.
3. Background estimation and model construction
   * Derive non-collision and prompt-background constraints, perform conditional QCD closure studies, and establish kappa with uncertainty. Propagate shared control samples and nuisance correlations.
4. Statistical model construction
   * Use disjoint A/B/C/D event counts for each validated category; include signal in all regions, constrained non-QCD backgrounds and the QCD transfer relation. Produce a pre-unblinding background prediction from B/C/D and external constraints, then the post-unblinding inference.

## Validation and Cross-checks

* Verify source-fidelity cutflow logic separately from Run 3 performance. Source Section 4 requires exactly two selected candidates, not exactly two reconstructed jets, and imposes no signal DeltaPhi cut.
* Confirm probe fail regions are populated with tag-supported trigger acceptance. Measure efficiencies and correlations in independent data; tag matching alone does not establish a plateau or independence.
* Evaluate closure after the complete selection, ranking and third-tight-jet veto. Compare single-probe and multiple-probe events explicitly. A small linear correlation coefficient is insufficient evidence of tail factorization.
* Require held-out closure pulls consistent with the assigned uncertainties, stable transfer factors under controlled boundary variations and enough data to constrain the extrapolation to A. Freeze a quantitative criterion using expected precision before unblinding; no precision target is supplied here.
* If validation shows a material unstable correlation, redesign or decorrelate axes/selection with explicit documentation of any SR change. Do not conceal nonclosure in an arbitrary uncertainty or revert to the rejected P/Q method.
* Audit non-QCD fractions separately in each region; mixtures can violate ABCD even when each individual component appears well behaved.
* Validate calorimeter-jet energy response specifically for low EMF, track isolation versus pile-up, timing tails, detector-region dependence, and MET response to displaced energy deposits.
* Validate non-collision transfers, including two-jet timing correlation and collision-overlap effects, with dedicated samples. A single-jet timing probability squared is not justified automatically.
* Test signal contamination across all mass/lifetime points and use injection tests for bias and interval coverage. Test lifetime maps against fully simulated points and quantify finite-map statistics and extrapolation.

## Systematic Uncertainties

### Source-analysis uncertainties

These identify source provenance, not Run 3 numerical assignments (Section 6 and Table 2).

* Luminosity 2.8%; scalar production theory roughly 10%, mass dependent; PDF acceptance 2.1%; pile-up acceptance 10%; ISR +2.9/-1.2%; finite signal simulation statistics.
* Dedicated low-EMF JES from dijet balance versus EMF and eta; source signal-yield shifts depend on the mass pair. Preserve the need for a non-standard-jet response study.
* Trigger ET, calorimeter ratio and isolation mismodelling; jet timing; MET scale/resolution. Source Table 2 gives sample-dependent shifts rather than universal errors.
* ISR affects both jet multiplicity/overlap and scalar boost; the source combined those effects as correlated. FSR was assessed as negligible for its selection, which is not proof for a changed reconstruction.
* The removed QCD method had P/Q fit statistics, ET-eta factorization, DeltaPhi-control selection and inter-jet extrapolation uncertainties. Record these as historical only; do not carry them into the ABCD likelihood.

### New-method uncertainties

* Finite B/C/D statistics through their count likelihoods, not a duplicate normalization nuisance.
* kappa uncertainty from residual h/n dependence, tight-first probe assignment, multiplicity veto and validation-to-SR extrapolation; allow category dependence where supported. Central value and width remain to be measured.
* Control-boundary stability, flavour/kinematic composition, conditional trigger correlations and sampling/exposure corrections.
* Region-specific non-QCD subtraction/constraint uncertainties, including shared samples; signal leakage and migration uncertainties in the joint fit.
* Limited validation statistics must be separated from evidence of nonclosure to avoid counting the same uncertainty twice.

### Modernization/adaptation uncertainties

* Run 3 luminosity and trigger exposure; period-dependent trigger efficiencies and matching; actual calibration uncertainties replace historical percentages.
* Calorimeter response and resolution for displaced low-EMF jets, energy-ratio response near threshold, jet cleaning, timing calibration and detector geometry/material description.
* Track reconstruction, fakes, quality translation and accidental pile-up tracks. Evaluate increased occupancy and endcap effects explicitly rather than reusing the historical 10% assignment.
* MET scale/resolution and response to non-standard jets; pile-up modelling; contemporary generator, PDF, scale and radiation variations at 13.6 TeV.
* Lifetime-map statistics, interpolation/extrapolation, event-level correlations, and changes in timing acceptance with lifetime.

Propagate variations through selection, role assignment and every affected region, not just the SR yield. Use correlations only when the same physical source is shared across periods/regions. For a limit on an absolute cross section, keep the reference production-rate theory uncertainty distinct from acceptance errors; include it when interpreting a signal strength or branching fraction relative to a theory prediction.

## Statistical Analysis

* Historical procedure (Section 7): one event-count Poisson term, profile-likelihood-ratio test statistic, frequentist toy data and CLs upper limits at 95% confidence; Gaussian-constrained systematic uncertainties and finite signal statistics. The source presents observed limit curves, not expected-limit bands. Its historical observation was 24 events against 23.5 +/- 8.0 expected, not a Run 3 prediction.
* Requested-method adaptation: a simultaneous count likelihood over A/B/C/D, keeping profile-likelihood CLs with toys as the baseline. Expected median limits and bands are added for the Run 3 analysis; do not claim asymptotic inference reproduces the source.
* For category k and region R, expected counts are lambda_Rk = mu*s_Rk(theta) + q_Rk + b_Rk(other,theta). Here mu is signal strength relative to an explicitly stated sigma x BR reference; equivalently fit the absolute cross section times branching fraction directly.
* Positive QCD parameterization: q_D = d, q_B = d*r_h, q_C = d*r_n, q_A = kappa*d*r_h*r_n. Fit d, r_h and r_n as nonnegative parameters, with kappa externally constrained by validation. This avoids literal division by an observed zero D count. Sparse controls require the Poisson fit and toy coverage tests; do not insert arbitrary pseudocounts.
* Include all signal-region and control-region signal yields, finite MC statistics and experimental uncertainties. Use positive nuisance parameterizations for rates and transfer factors; this is an explicit refinement of the historical Gaussian treatment where positivity requires it.
* Fit non-QCD contributions separately with auxiliary constraints. Avoid treating weighted, prescale-corrected counts as ordinary Poisson integers; use raw counts with exposure in the expectation or an appropriate sampling likelihood.
* Before unblinding, exclude A's observed count and predict its background using B/C/D and external constraints. After unblinding, report the prediction and the simultaneous fit distinctly.
* Outputs: observed and expected 95% CL limits on sigma(gg -> Phi) x BR(Phi -> pi_v pi_v) versus c*tau for each supported mass pair, with expected bands. For the Higgs-like benchmark also show normalization to a stated 13.6 TeV gluon-fusion reference and, where supported, excluded lifetimes at 10% and 30% branching fractions as in the source. No numerical limit or sensitivity is asserted without data and validated efficiencies.

## For Review

* Proposed ABCD choice: use the tagged-event probe h/n plane. The user specified ABCD but not its axes; this is a concrete proposal awaiting performance validation. Tight-first assignment preserves the signal selection but may create significant correlations. A validated kappa and transferable control samples are essential, not optional implementation details.
* Run 3 inputs still required before execution: certified years/periods and luminosity, available single-candidate trigger paths with tag-only support, T_tag per period, data format retaining required information, and approved track/jet/timing/MET definitions. The public trigger overview does not resolve these analysis-specific inputs.
* Baseline assumptions retained for review: source kinematic/ratio/isolation/timing/MET thresholds, 13 source mass pairs including 126 GeV, and gluon fusion only. Do not change these merely to match convenient modern samples.
* Generator decay configuration must resolve rounded branching fractions and generated lifetime coverage; a contemporary Higgs mass point would be an explicitly added benchmark.
* Validation boundaries are proposed. Their adequacy, non-QCD contamination, statistical power and quantitative closure criterion require Run 3 samples. No data-driven quantities have been measured in preparing this document.
* Source-fidelity and consistency review completed against Sections 3-7 and Tables 1-3: checked strict offline inequalities, trigger-matched role, track cone, exact selected-candidate multiplicity, no imported background-only DeltaPhi cut, A/SR equivalence, all 13 benchmark pairs, efficiency-map lifetime extrapolation, systematics provenance, and toy-based observed-limit procedure. Run 1 luminosity, yields, calibrations and trigger thresholds are explicitly historical; Run 3 unresolved inputs remain identified rather than fabricated.
