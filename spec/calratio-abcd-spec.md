# Run 1 CalRatio Search for Pair-Produced Long-Lived Neutral Particles with an ABCD QCD Estimate

Search for a scalar boson decaying to two long-lived neutral valley pions, each reconstructed as a narrow, trackless, hadronic-calorimeter-dominated jet. Reproduce the Run 1 ATLAS analysis selection and signal interpretation while replacing its multijet (QCD) estimate with an ABCD method.

## Source and Scope

* Analysis mode: Source-derived analysis with requested changes.
* Source: ATLAS Collaboration, *Search for pair-produced long-lived neutral particles decaying to jets in the ATLAS hadronic calorimeter in pp collisions at sqrt(s) = 8 TeV*, arXiv:1501.04020v2, Phys. Lett. B 743 (2015) 15-34; local source `1501.04020v2.pdf`.
* Analysis intent: Select pair-produced neutral long-lived particles (LLPs) that decay near the outer electromagnetic calorimeter or in the hadronic calorimeter, producing two narrow jets with high hadronic-to-electromagnetic energy ratio and no associated inner-detector tracks. Set limits on scalar production times branching ratio as a function of LLP proper lifetime.
* Source realization: Use 2012 ATLAS 8 TeV collision data, the dedicated CalRatio trigger, Run 1 anti-kt R=0.4 calorimeter jets, and the source object/event selections below.
* Requested deviation from the source: Replace only the source multijet probability-and-correlation-correction method with the ABCD estimate defined here. Do not use the source raw prediction, fitted correlation scale factor, or quoted multijet yield as the new prediction.
* Added or modernized elements: A simultaneous four-region ABCD likelihood, an explicit ABCD correlation parameter kappa, signal/non-QCD contamination treatment in all four regions, and ABCD closure and stability tests. These are consequences of the requested background-method change and are not claims about the source analysis.

## Data Samples

| Data Sample | Role(s) In Analysis |
| --- | --- |
| 2012 ATLAS pp collision data at sqrt(s) = 8 TeV, 20.3 fb^-1 after data-quality requirements, selected with the unprescaled CalRatio trigger | Signal region and ABCD regions A-D |
| Empty-crossing data selected with the empty-crossing CalRatio-like trigger | Cosmic-ray background estimate and timing template |
| Random-collision-trigger data | Pile-up/underlying-event track-overlap correction for the cosmic-ray estimate |
| Unpaired-isolated-crossing data selected with the corresponding CalRatio trigger | Beam-halo estimate and non-collision validation |
| Hidden Valley signal MC generated with PYTHIA 8.165 and MSTW2008, followed by detailed GEANT4 detector simulation and standard data reconstruction | Signal acceptance, region contamination, trigger studies, and lifetime extrapolation |
| Run 1 multijet data and MC control samples | Signal-systematic studies and ABCD closure diagnostics only; the source prescaled-single-jet probability method is not used for the nominal QCD yield |

Generated signal benchmarks are the actual `(m_Phi, m_pi_v)` tuples below; masses are in GeV. The quoted source gluon-fusion cross section for each parent mass is shown in pb.

| Parent mass and cross section | Generated LLP masses | Benchmark tuples |
| --- | --- | --- |
| 100, 29.7 pb | 10, 25 | (100, 10), (100, 25) |
| 126, 19.0 pb | 10, 25, 40 | (126, 10), (126, 25), (126, 40) |
| 140, 15.4 pb | 10, 20, 40 | (140, 10), (140, 20), (140, 40) |
| 300, 3.59 pb | 50 | (300, 50) |
| 600, 0.52 pb | 50, 150 | (600, 50), (600, 150) |
| 900, 0.06 pb | 50, 150 | (900, 50), (900, 150) |

The source simulates `gg -> Phi`, with `BR(Phi -> pi_v pi_v) = 100%`. The pi_v decays preferentially to heavy fermions. Its simulated branching fractions `(bb, tau tau, cc)` in percent are: 10 GeV `(70.0, 16.4, 13.4)`, 20 GeV `(86.3, 8.0, 5.6)`, 25 GeV `(86.6, 8.1, 5.3)`, 40 GeV `(86.5, 8.5, 5.0)`, 50 GeV `(86.2, 8.8, 4.9)`, and 150 GeV `(84.8, 10.2, 4.8)`. Each generated sample has a fixed lifetime chosen to populate decays throughout ATLAS. Samples are pile-up reweighted to data.

## Backgrounds

* Standard Model multijet (QCD) production
    * Importance: Dominant.
    * Estimation method: Data-driven ABCD method in the CalRatio-triggered collision sample. The two axes are the probe jet's calorimeter energy ratio and track multiplicity.
    * Control/validation samples: Regions B-D and the validation subdivisions specified below. Prescaled single-jet data may be used only for closure diagnostics, not nominal normalization.
* Cosmic-ray showers
    * Importance: Subdominant; the source predicted 0.3 +/- 0.2 events in its signal region.
    * Estimation method: Preserve the source empty-crossing method, including trigger live-time scaling, timing-window extrapolation, and track-overlap weights from random collision events.
    * Control/validation samples: Empty crossings and timing sidebands.
* Beam-halo interactions
    * Importance: Negligible after the timing and beam-halo vetoes; the source cross-check predicted 0.07 +/- 0.07 events and included cosmic contamination.
    * Estimation method: Preserve the source artificial-event method using pairs of jets from unpaired isolated crossings.
    * Control/validation samples: Unpaired isolated crossings and the beam-halo tag/veto sideband.
* Other collision backgrounds
    * Importance: Included in the data-driven QCD component unless a demonstrably non-QCD process is separately modeled. Avoid double counting.

The source result of `23.2 +/- 8.0` multijet events must not be used as the ABCD prediction; new A-D yields must be measured from the selected data.

## Data Required

### CalRatio-triggered collision data

* Run and luminosity-block data-quality status; trigger decision and trigger-object matching.
* Primary-vertex track multiplicity and track pT.
* Anti-kt R=0.4 calorimeter-jet four-vectors, local-cluster inputs/calibration state, modified good-jet decision, and beam-halo jet flag.
* Per-jet electromagnetic and hadronic calorimeter energies, `log10(E_H/E_EM)`, EMF, eta, phi, transverse energy, and energy-weighted cell time.
* Good-track multiplicity for tracks with pT > 1 GeV within DeltaR < 0.2 of each jet; the source good-track definition requires at least two pixel hits and at least nine total pixel-plus-SCT hits.
* Missing transverse momentum and the information needed to apply its source selection and variations.
* Deterministic tag/probe role, extra nominal LLP-jet count, and A-D region flag.

### Empty-, random-, and unpaired-crossing data

* Bunch-crossing category, trigger live time or exposure, jet quantities listed above, event timing, missing transverse momentum, and beam-halo tags.
* For random collision events, the probability versus eta of a pT > 1 GeV track falling in a DeltaR < 0.2 cone.

### Hidden Valley signal MC

* Reconstructed quantities matching collision data, event weights, pile-up information, and generated `(m_Phi, m_pi_v, tau_pi_v)`.
* Truth LLP four-vector, boost, and decay position in cylindrical radius and z.
* Nominal production cross section and branching fractions, generator weights, and systematic variations.

## Triggers

* Dedicated Run 1 CalRatio trigger
    * Role: Select signal-region and ABCD-region collision events.
    * Selection: Level 1 requires at least one narrow calorimeter jet with ET > 40 GeV in a 0.2 x 0.2 `(Delta eta x Delta phi)` region. Level 2 requires `log10(E_H/E_EM) > 1.2` and no pT > 1 GeV tracks in a 0.2 x 0.2 region around the jet axis. Level 3 reconstructs anti-kt R=0.4 jets and requires ET > 35 GeV.
    * Offline requirement: The trigger-matched tag jet has ET > 60 GeV, where the source reports the Level-1 threshold as fully efficient. A second jet has ET > 40 GeV.
    * Interaction with analysis variables: The trigger directly sculpts calorimeter ratio and track isolation for the tag jet. Therefore the ABCD axes are defined only from the independently reconstructed probe jet; no ABCD fail region is defined by failing the tag's trigger-level requirements.
* Empty-crossing CalRatio-like trigger
    * Role: Cosmic-ray control sample.
    * Selection: Source-equivalent CalRatio logic active in empty crossings; preserve recorded trigger configuration.
* Unpaired-isolated-crossing CalRatio trigger
    * Role: Beam-halo control sample.
    * Selection: Preserve the source trigger configuration.
* Prescaled single-jet triggers with thresholds of 15 GeV or higher
    * Role: Optional closure diagnostics only.
    * Interaction with analysis variables: Their effective luminosities and prescales must be retained if used; they do not determine the nominal ABCD normalization.

## Object Definitions and Roles

* Baseline jet
    * Analysis intent: A reconstructed calorimeter jet eligible to define the two-jet topology without applying either ABCD discriminant.
    * Source realization: Anti-kt R=0.4 jet built from locally calibrated calorimeter clusters and subsequently calibrated with the source energy- and eta-dependent scheme.
    * Requirements: ET > 40 GeV, |eta| < 2.5, modified ATLAS good-jet criteria that omit the normal rejection of small-EMF jets, and energy-weighted time `-1 < t < 5 ns`.
* Nominal LLP-jet candidate
    * Requirements: A baseline jet with `log10(E_H/E_EM) > 1.2` and zero source-defined good tracks with pT > 1 GeV in DeltaR < 0.2.
* Tag jet
    * Role: The CalRatio-trigger-matched jet. It must be a nominal LLP-jet candidate and have ET > 60 GeV.
    * Assignment: If more than one jet is trigger matched, choose the leading-ET matched jet as the tag; this implements the source statement that only the leading jet is subject to ET > 60 GeV when multiple jets fire the trigger.
* Probe jet
    * Role: Supplies both ABCD variables and is the second jet in the LLP pair.
    * Assignment: The highest-ET non-tag baseline jet. It must have ET > 40 GeV. This rule is fixed before examining its calorimeter ratio or track multiplicity.
* Additional jets
    * Other reconstructed jets are allowed, but events containing an additional nominal LLP-jet candidate beyond the tag and probe are vetoed in every A-D region. This keeps region A aligned with the source requirement of exactly two jets satisfying the complete LLP-jet selection.

## Analysis Regions

Common preselection:

* Pass 2012 data-quality requirements and the unprescaled CalRatio trigger.
* Require a reconstructed primary vertex with at least three tracks having pT > 1 GeV.
* Reject the event if any reconstructed jet is tagged as beam halo.
* Require missing transverse momentum < 50 GeV.
* Assign the tag and probe as specified above. Require the tag to pass the full nominal LLP-jet definition and the trigger-matched ET > 60 GeV condition.
* Apply the same `-1 < t < 5 ns` timing requirement to the tag and probe.
* Veto any additional nominal LLP-jet candidate beyond the tag and probe.

Define the ABCD axes on the probe jet:

* `X` (CalRatio): pass if `log10(E_H/E_EM) > 1.2`; fail if `log10(E_H/E_EM) <= 1.2`.
* `Y` (track isolation): pass if `n_track = 0`; fail if `n_track >= 1`, where tracks use the source good-track and cone definitions.

| Region | Purpose | Additional requirements |
| --- | --- | --- |
| A (signal region) | Final source-equivalent two-LLP-jet selection | Probe passes X and Y. Thus tag and probe are both nominal LLP-jet candidates, and exactly two jets satisfy that definition. Keep blinded while finalizing the ABCD procedure. |
| B | QCD control region | Probe passes X and fails Y. |
| C | QCD control region | Probe fails X and passes Y. |
| D | QCD control region | Probe fails X and Y. |

For expected QCD yields `q_i`, define `kappa = (q_A q_D)/(q_B q_C)` and therefore `q_A = kappa q_B q_C/q_D`. The nominal factorization hypothesis is `kappa = 1`. Non-QCD contributions and signal contamination are modeled in all regions rather than silently included in the QCD transfer relation.

## Histograms

1. Probe-jet ABCD plane
    * Purpose: Region definition, population diagnostics, and correlation assessment.
    * x axis: Probe `log10(E_H/E_EM)`, with the boundary at 1.2.
    * y axis: Probe good-track multiplicity in DeltaR < 0.2, with the boundary between zero and at least one track.
    * Entries: One per selected event, before applying the X/Y region requirement.
2. Event yields in A-D
    * Purpose: Inputs to the simultaneous ABCD likelihood.
    * Output: Observed counts and predicted QCD, cosmic, beam-halo, and signal contributions for each region. Do not inspect the A count until the method and uncertainties are frozen.
3. ABCD closure and kappa
    * Purpose: Validate factorization.
    * Output: Predicted-to-observed closure and fitted kappa in validation subdivisions, versus probe ET, eta, pile-up, run period, and tag/probe Delta phi.
4. Source signal-discrimination distributions
    * Purpose: Source-comparison and signal-model validation.
    * Output: Probe and tag track multiplicity, `log10(E_H/E_EM)`, ET, eta, timing, and missing transverse momentum for data control regions and signal MC.
5. Trigger probability versus truth decay position
    * Purpose: Reproduce the source trigger acceptance diagnostic.
    * x axis: pi_v radial decay position in the barrel or |z| in the endcaps.
    * y axis: Single-pi_v probability to fire the CalRatio trigger.
6. Expected selected signal yield and observed limits versus proper lifetime
    * Purpose: Final interpretation.
    * x axis: pi_v proper decay length in metres.
    * y axis: Expected signal events; observed 95% CL `sigma/sigma_SM` for the 126 GeV parent, or `sigma x BR` in pb for other parent masses.

## Analysis Steps

1. Apply event cleaning and common event selection
    * Apply data quality, CalRatio trigger, primary-vertex, beam-halo veto, and missing-transverse-momentum requirements in that order.
2. Reconstruct jets and assign roles
    * Build and calibrate source-realization anti-kt R=0.4 jets, apply modified jet quality and timing, then assign tag and probe deterministically without using the probe ABCD variables.
3. Construct A-D regions
    * Apply the full nominal LLP selection to the tag, classify the probe using X and Y, and apply the additional-candidate veto identically in A-D.
4. Estimate QCD with ABCD
    * Obtain the QCD expectations in B-D from collision data after accounting for cosmic-ray, beam-halo, and signal contributions.
    * Relate A to B-D through `q_A = kappa q_B q_C/q_D`. Use a simultaneous Poisson likelihood for A-D so low counts and denominator uncertainty are treated correctly.
    * Set nominal kappa to one and constrain its nuisance parameter using the closure program below. Do not derive kappa by extrapolating the source's failed per-jet probability correction.
5. Estimate non-collision backgrounds
    * Preserve the source empty-crossing cosmic estimate: remove the timing and good-vertex requirements in the control sample, extrapolate the uniform cosmic arrival time into the two-jet timing window, scale by relative live time, and weight for collision-induced track overlaps versus eta.
    * Preserve the unpaired-crossing beam-halo cross-check using artificial jet pairs and the missing-transverse-momentum efficiency.
6. Model the signal and extrapolate lifetime
    * Evaluate acceptance for every generated `(m_Phi, m_pi_v)` tuple.
    * Preserve the source lifetime method: generate pi_v decays over 0-50 m and use an efficiency map as a function of pi_v boost to obtain efficiency and expected yield at other proper lifetimes. Do not imply interpolation to ungenerated mass combinations.
7. Validate and freeze
    * Complete trigger, object, ABCD closure, non-collision, and source-reproduction checks. Freeze region definitions and nuisance treatment before unblinding region A.

## Workflow

1. Data Extraction and NTuple Skimming
    * Filtering: Retain every event passing the common event requirements with a valid tag and a non-tag baseline probe. Do not require the probe to pass either ABCD discriminant during skimming, and retain extra-jet information needed for the nominal-candidate veto.
    * Variables: Persist the event, trigger, jet, track, timing, missing-momentum, beam-condition, exposure, truth, and weight information listed in Data Required.
2. Data Analysis and Histogramming
    * Apply calibrated object definitions, deterministic tag/probe assignment, common vetoes, and A-D flags.
    * Produce region counts, two-dimensional ABCD diagnostics, validation subdivisions, and signal acceptance inputs.
3. Background Estimation
    * Build the simultaneous A-D QCD model and the independent cosmic/beam-halo estimates. Evaluate closure and derive the kappa uncertainty without using signal-region data to tune the method.
4. Signal Modeling
    * Calculate benchmark acceptance, lifetime-reweighted yields, and all source-analysis signal variations.
5. Statistical Model Construction
    * Combine A-D Poisson counts, the ABCD transfer relation, non-QCD components, signal contamination, and signal systematic constraints. Produce the source-style counting-experiment limits as a function of lifetime.

## Validation and Cross-checks

* Validate that region A is exactly the nominal published event selection under the deterministic tag/probe interpretation; compare yields cut-by-cut against a direct implementation of the source wording.
* Before unblinding A, test ABCD closure in non-overlapping validation subdivisions formed by splitting the X-fail range into near/far sidebands and the Y-fail range into `n_track = 1` and `n_track >= 2`. Do not alter the nominal A-D boundaries after inspecting A.
* Measure closure versus probe ET, eta, timing, pile-up, run period, and tag/probe Delta phi. Where statistics permit, repeat the ABCD prediction in corresponding bins and combine them.
* Quantify X-Y dependence using the two-dimensional control-region distribution and a correlation measure appropriate for one continuous and one discrete observable. Translate significant non-closure into the kappa constraint.
* Perform signal-injection tests across all benchmark masses and lifetimes to verify unbiased signal recovery when B-D contain signal.
* Verify robustness to alternative deterministic probe definitions and to the extra nominal-candidate veto. Treat differences as closure/modeling uncertainty if they expose QCD composition dependence.
* Reproduce the source's trigger-performance checks and the stated qualitative decay-position dependence; pay particular attention to reduced endcap efficiency from pile-up track isolation.
* Validate cosmic timing uniformity, live-time scaling, and eta-dependent track-overlap weights. Validate beam-halo suppression in unpaired crossings.
* Compare source cut-flow quantities where available, including 24 events in the published signal region. This is a source-fidelity check only and must not be used to tune the ABCD estimate.

## Systematic Uncertainties

### Source-analysis uncertainties

* Integrated luminosity normalization: 2.8%.
* Parent scalar/Higgs production cross section: approximately 10%, with the benchmark-dependent source values retained in the statistical model.
* Signal PDF acceptance: 2.1%, obtained in the source from MSTW2008nlo68cl, CT10, and NNPDF2.3 sets and their errors.
* Signal pile-up acceptance: 10%, dominated by added tracks degrading jet isolation.
* ISR acceptance: source common variation of `+2.9%/-1.2%`, combining ISR multiplicity and parent-boost effects as correlated contributions.
* Low-EMF jet energy scale, trigger efficiency, missing-transverse-momentum scale/resolution, and jet timing: retain the source's benchmark-dependent variations. Repeat the full signal selection and lifetime acceptance evaluation under each variation.
* Finite signal-MC sample statistics. The source found FSR effects negligible.
* Cosmic-ray normalization: empty-crossing statistics, timing-window fraction, trigger live-time ratio, and track-overlap weights.
* Beam-halo normalization: limited unpaired-crossing statistics; negligible nominal contribution after vetoes.

### New-method uncertainties

* ABCD control-region Poisson statistics, represented directly by the B-D likelihood terms.
* Residual X-Y correlation/non-closure, represented by kappa with a constraint derived from blinded validation regions and closure tests. A numerical width is not specified by the source and must be frozen before unblinding A.
* Dependence of closure on probe ET, eta, pile-up, run period, timing, and tag/probe topology; use binning or nuisance variations where a significant dependence is observed.
* Region migration under track reconstruction and calorimeter-energy variations, propagated consistently to A-D for simulated signal and separately tested in data for QCD closure.
* Signal contamination in B-D and non-QCD contamination in all regions, including their normalization and migration uncertainties.
* Probe-assignment and additional-candidate-veto dependence, evaluated with alternative definitions that do not use X or Y.

### Modernization/adaptation uncertainties

* None beyond the ABCD-specific additions above. Any future translation to a different run, trigger, detector configuration, or reconstruction must derive new calibrations and uncertainties rather than reuse Run 1 numerical values.

Correlate nuisances only when they share a physical source. Do not reuse the source multijet uncertainty, its 6% ET-eta term, or its `1.8 +/- 0.5` correlation scale factor as an ABCD uncertainty.

## Statistical Analysis

* Observables/regions entering the model: One event count in each of A-D for every tested signal mass/lifetime hypothesis. Region A is the signal region; B-D constrain QCD. Cosmic and beam-halo estimates enter all applicable regions.
* Parameter of interest: `sigma(Phi) x BR(Phi -> pi_v pi_v)`; for the 126 GeV benchmark also report `sigma/sigma_SM`, using the source `sigma_SM = 19.0 pb`. Limits are functions of pi_v proper lifetime.
* Background constraints: Parameterize QCD with three free control-region expectations and the ABCD relation `q_A = kappa q_B q_C/q_D`, or an algebraically equivalent positive-definite parameterization. Constrain kappa from closure studies. Include non-QCD backgrounds separately.
* Nuisance parameters: Source signal uncertainties, finite sample/control-region statistics, kappa/non-closure, signal and non-QCD contamination, and non-collision normalizations. Use positive-definite constraints where appropriate; the source's Gaussian convolution may be retained only where it cannot imply unphysical yields.
* Test statistic/interval method: Preserve the source profile-likelihood-ratio test statistic and frequentist CLs construction using pseudoexperiments rather than silently replacing it with asymptotic limits.
* Expected and observed outputs: Produce observed 95% CL upper limits versus proper lifetime and excluded lifetime intervals for stated branching-ratio hypotheses, matching the source's reported output. Expected signal yields versus lifetime are required for the test, but expected limit bands are not a source-analysis deliverable; if produced as a diagnostic, label them explicitly as a new addition.
* Source-vs-modernized treatment: Signal modeling, selection, parameter of interest, and toy-based CLs follow the source. The simultaneous A-D likelihood and its kappa nuisance replace the source's single signal-region Poisson term with an externally predicted QCD yield.

## For Review

* The source does not give an ABCD construction. This specification chooses the probe jet's `log10(E_H/E_EM)` and good-track multiplicity because they are the two source LLP discriminants, while fixing the trigger-matched tag in its pass state avoids trigger-induced loss of ABCD sidebands.
* The source wording does not fully specify a unique tag/probe choice when more than two baseline jets are present. The specification assigns the leading-ET matched jet as tag and the leading-ET remaining baseline jet as probe, then vetoes additional nominal LLP candidates. This choice must be verified to make region A cut-by-cut equivalent to the original selection; if it is not, adopt a deterministic source-equivalent pairing rule without changing the A-D axis definitions.
* The broad fail definitions (`X <= 1.2`, `n_track >= 1`) maximize control statistics but may mix different QCD compositions or produce substantial correlation. Near/far and track-multiplicity validation subdivisions must determine whether binning, restricted sidebands, or an enlarged kappa uncertainty is required before unblinding.
* The numerical kappa constraint and the new ABCD QCD yield cannot be obtained from the paper. They require A-D control data and closure results and are intentionally left as measured analysis outputs rather than invented values.
* The source does not state the exact generated lifetime of every signal sample, concrete dataset identifiers, software release, calibration tags, or trigger-chain names. Those implementation metadata must be recovered from the original analysis configuration; no modern identifiers are assumed.
* The published count of 24 events remains the expected cut-flow target because the signal selection is intended to be unchanged. It is not an independent blind observation for this reconstruction and must not be used to optimize the new ABCD boundaries or uncertainty.
