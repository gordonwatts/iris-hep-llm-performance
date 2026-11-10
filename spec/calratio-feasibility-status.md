# CalRatio ABCD feasibility: initial real-data checkpoint

Updated November 9, 2026, local time. Related: [issue #8](https://github.com/gordonwatts/iris-hep-llm-performance/issues/8).

**Result:** ServiceX can retrieve several necessary raw inputs from the exact
Run 3 collision PHYSLITE positive control. Nominal ABCD feasibility remains
unestablished: the calorimeter-jet/energy definition, all-track completeness,
Run 3 track selection, and tag-supported trigger acceptance are unresolved.
No unvalidated proxy has been used to produce an ABCD result.

This is an initial frozen review checkpoint. Two working days have **not**
elapsed; the issue's final two-day handoff criterion remains open. No unattended
continuation is scheduled. The draft PR preserves current evidence and the
unfinished work so subsequent effort can remain bounded and reviewable.

## Demonstrated extraction

All seven requests used the exact dataset in `spec/calratio-probe-samples.yaml`,
`NFiles=1`, and no event or object cuts:

```text
data23_13p6TeV:data23_13p6TeV.00451094.physics_Main.deriv.DAOD_PHYSLITE.r15774_p6304_p6700_tid43636932_00
```

The service selected `DAOD_PHYSLITE.43636932._000167.pool.root.1` in every
request. Rucio reports 115,338 input events, GUID
`6f81c62e1783844489294f7e03c181b7`, Adler-32 `305238ab`, and 637,036,359 bytes.
Each successful delivery contains all 115,338 events with unique run/lb/event
keys. The compact ledger records exact submitted QASTLE, request IDs, original
code hashes, file provenance, types, units, ranges and output checksums.

| One-file probe | Inspected result | Interpretation |
| --- | --- | --- |
| Event identity and AnalysisJets kinematics | 712,591 jets in 84,679 nonempty events; aligned pT/eta/phi/E/m arrays; all values finite | Positive extraction control. MeV converted to GeV explicitly; phi in radians. Not a displaced calorimeter-jet calibration test. |
| EMFrac/Timing presence | Both decorations present on all 712,591 inspected jets; returned indicators are float32 1.0 | Storage presence, not valid-energy or calibrated-timing evidence. The generic client stub returns float indicators for this API. |
| EnergyPerSampling | 19,952,548 finite energies; all 712,591 jets have 28 sampling entries; 460,997 entries are negative | Nested sampling vectors are accessible. Layer grouping, energy scale and valid E_H/E_EM treatment remain unresolved. |
| Stored EMFrac | 712,591 finite float32 values; range -0.4684 to 1.5133; 24,040 values outside [0,1] | Exploratory only. An unqualified log10((1-f)/f) conversion is invalid for part of the observed range. No clipping or conversion was performed. |
| InDetTrackParticles kinematics | 1,224,316 tracks in 75,606 nonempty events; aligned pT/eta/phi arrays; finite values | Demonstrates retained tracks, not completeness of all qualifying tracks. Very large finite pT outliers also require quality review. |
| Pixel and SCT hit summaries | 1,224,316 uint8 entries each; pixel 0–10, SCT 0–18 | Reference hit inputs are readable; this does not approve their Run 3 physics interpretation. |
| AntiKt4LCTopoJets | Hosted transform: one failed file, no completed file or ROOT delivery | Unclassified remote failure. The available per-file response omits the worker error; absence is not demonstrated. |

All requests report transformer image
`sslhep/servicex_func_adl_xaod_transformer:25.2.80`; the service app version is
`develop`. Client versions include ServiceX 3.3.1 and
func-adl-servicex-xaodr25 2.5.0.25.2.80, with the full environment in `uv.lock`.
The production p6700 metadata identifies Athena 25.0.26; this is distinct from
the transformation runtime. Kinematic mass values include a small negative
minimum around -0.000106 GeV; finite output is not a physical-quality guarantee.

## What prevents an ABCD diagnostic

The required jets are calorimeter anti-kt R=0.4 candidates with validated low-EMF
response. The client selects `AnalysisJets`. Current-main
[PHYSLITE configuration](https://atlas-sw-doxygen.web.cern.ch/atlas-sw-doxygen/atlas_main--Doxygen/docs/html/de/d42/PHYSLITE_8py_source.html)
builds that collection from particle-flow jets, which is a reason to investigate
its suitability, not release-matched proof about this production. Direct access
to the [Athena 25.0.26 configuration](https://gitlab.cern.ch/atlas/athena/-/blob/release/25.0.26/PhysicsAnalysis/DerivationFramework/DerivationFrameworkPhys/python/PHYSLITE.py)
timed out or failed through the attempted routes. The failed LC-topo request must
be diagnosed before declaring a missing collection and escalating tiers.

The sampling-energy vector is useful evidence, but its layer enumeration,
calibration, hadronic/EM partition and treatment of non-positive measurements
must be agreed before deriving h. Decoration presence does not supply that
validity policy. Stored EMFrac remains a separately labelled exploratory option.

The reference n counts all qualifying tracks with pT>1 GeV inside DeltaR<0.2,
including pile-up tracks, with >=2 pixel and >=9 pixel+SCT hits. Retrieved
kinematics and summaries do not prove those tracks survived derivation thinning.
Current-main [common thinning configuration](https://atlas-sw-doxygen.web.cern.ch/atlas-sw-doxygen/atlas_main--Doxygen/docs/html/d0/d69/PhysCommonThinningConfig_8py_source.html)
confirms that track thinning needs investigation; its exact production behavior
must be checked at the target release. No PV-only restriction, ghost-associated
NumTrkPt1000 replacement, cone-count proxy or approved Run 3 working point is
assumed.

No year/period selection, single-candidate CalRatio chain, tag-only matching,
turn-on/plateau, T_tag, GRL or exposure has been approved. Cleaning, cell timing,
the PV track requirement, full-event BIB veto and MET response also remain
unverified. Consequently, the inputs do not yet permit reproducible nominal
common selection or tag/probe roles. No h/n combination, ABCD yield, A count,
closure measurement, background prediction, sensitivity or limit was computed.
The specification's blinding is preserved.

## Sample suitability and next decisions

Rucio and AMI confirm the positive-control dataset's identity: 267 files,
28,086,634 events, Main stream, `VALID`/`ALL EVENTS AVAILABLE`, and AOD lineage
through `r15774_p6304`. These catalog facts do not establish CalRatio trigger
acceptance, track completeness, upstream sideband retention or analysis readiness.
The uncut query preserves delivered populations but cannot restore upstream losses.

| Role | Current evidence | Decision / next action |
| --- | --- | --- |
| Nominal ABCD data | Exact Main positive-control DID is accessible; nominal suitability unverified | Choose certified periods and tag-supported chain; inspect actual skim/thinning/trigger configuration and validate all four probe populations. |
| Independent inclusive-jet controls | No additional analysis source selected | Resolve trigger sampling/prescales, parent overlap, disjoint validation and h/n retention before using a shared Main source. |
| Empty/unpaired/zero-bias controls | No role-specific source confirmed | Find catalog-confirmed sources with bunch metadata, relaxed vertex/timing retention and appropriate exposures. Main is not assumed to supply them. |
| PHYS or specialist augmentation | No extraction performed; no proven PHYSLITE absence | Obtain worker diagnostics and exact-release content evidence first. Then use a catalog-confirmed candidate and verify fields, parents, event coverage and object matching. |
| Signal and auxiliary MC | Outside this bounded positive control | Resolve approved generation/lifetime/decay coverage and official recommendations later; preserve the specification's exact 13 mass pairs. |

Gordon/physics review is needed for the nominal jet/energy/validity definition,
track-quality translation, and period/trigger scope. Separately, obtain the
worker error for request `5cc8fe4b-b956-4c5b-b389-b0eaea4764b3` and production
job configuration. These are the next bounded investigations, not permission to
replace inputs or launch a full retrieval. Any later tag/probe implementation
must retain tight-first assignment, a stable tie break, the global third-tight
veto, additional ordinary jets, strict boundaries, and the absence of an imported
DeltaPhi cut.

## Reproduction and handoff

Start with [the runnable instructions](../prototypes/calratio/README.md).
Sources and the 22-row bounded requirements table are under `prototypes/calratio/`;
the historical 69-row fixture remains unchanged and has a different specification
hash. The current spec hash is
`83627120fb383317028518c87ad57c7bdaf60b5b39471d667d0301c8ee160d7c`.
Skill commits, client lock, exact queries, artifacts and unfinished work are
recorded in `handoff.json` and `data-source-evidence.json`. No reusable skill was
created or changed, and no delegated worker/model comparison was used.

Bulk artifacts are under `<data-root>/calratio/issue8-20261109/`; the run metadata
records the resolved machine-local root. Local replay requires no credentials
or service connection and checks each delivery against its frozen observations.
The source-mapping structural validator, offline safeguard tests and real-file
replays are the relevant checks; they do not validate the physics definitions.

An initial diagnostic collector briefly retained and displayed credential-bearing
ServiceX status fields. Those fields were removed from the retained diagnostics;
the collector now uses an explicit allowlist, covered by a regression test.
Retained/shared artifacts are scanned for credentials and signed URLs before
commit. The PR remains draft, issue #8 remains open, and no merge is authorized.
