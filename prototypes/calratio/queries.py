"""Uncut extraction probes. These measure storage, not CalRatio equivalence."""

from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
from func_adl_servicex_xaodr25.type_support import cpp_float, cpp_vfloat, cpp_type

cpp_u8 = cpp_type[int]("uint8_t", int)


def smoke():
    return (FuncADLQueryPHYSLITE()
        .Select(lambda e: {"info": e.EventInfo("EventInfo"), "jets": e.Jets()})
        .Select(lambda c: {
            "run": c.info.runNumber(), "lb": c.info.lumiBlock(),
            "event": c.info.eventNumber(),
            "jet_pt": c.jets.Select(lambda j: j.pt() / 1000.0),
            "jet_eta": c.jets.Select(lambda j: j.eta()),
            "jet_phi": c.jets.Select(lambda j: j.phi()),
            "jet_e": c.jets.Select(lambda j: j.e() / 1000.0),
            "jet_m": c.jets.Select(lambda j: j.m() / 1000.0),
        }))


def calo_validity():
    return (FuncADLQueryPHYSLITE()
        .Select(lambda e: {"info": e.EventInfo("EventInfo"), "jets": e.Jets()})
        .Select(lambda c: {
            "run": c.info.runNumber(), "lb": c.info.lumiBlock(),
            "event": c.info.eventNumber(),
            "jet_has_emfrac": c.jets.Select(lambda j: j.isAvailable[cpp_float]("EMFrac")),
            "jet_has_timing": c.jets.Select(lambda j: j.isAvailable[cpp_float]("Timing")),
        }))


def calo_emfrac():
    return (FuncADLQueryPHYSLITE()
        .Select(lambda e: {"info": e.EventInfo("EventInfo"), "jets": e.Jets()})
        .Select(lambda c: {
            "run": c.info.runNumber(), "lb": c.info.lumiBlock(),
            "event": c.info.eventNumber(),
            "jet_emfrac": c.jets.Select(lambda j: j.getAttribute[cpp_float]("EMFrac")),
        }))


def tracks():
    return (FuncADLQueryPHYSLITE()
        .Select(lambda e: {"info": e.EventInfo("EventInfo"),
                           "tracks": e.TrackParticles("InDetTrackParticles")})
        .Select(lambda c: {
            "run": c.info.runNumber(), "lb": c.info.lumiBlock(),
            "event": c.info.eventNumber(),
            "track_pt": c.tracks.Select(lambda t: t.pt() / 1000.0),
            "track_eta": c.tracks.Select(lambda t: t.eta()),
            "track_phi": c.tracks.Select(lambda t: t.phi()),
        }))


def calo_sampling():
    return (FuncADLQueryPHYSLITE()
        .Select(lambda e: {"info": e.EventInfo("EventInfo"), "jets": e.Jets()})
        .Select(lambda c: {
            "run": c.info.runNumber(), "lb": c.info.lumiBlock(),
            "event": c.info.eventNumber(),
            "jet_sampling": c.jets.Select(lambda j:
                j.getAttribute[cpp_vfloat]("EnergyPerSampling").Select(lambda x: x / 1000.0)),
        }))


def track_hits():
    return (FuncADLQueryPHYSLITE()
        .Select(lambda e: {"info": e.EventInfo("EventInfo"),
                           "tracks": e.TrackParticles("InDetTrackParticles")})
        .Select(lambda c: {
            "run": c.info.runNumber(), "lb": c.info.lumiBlock(),
            "event": c.info.eventNumber(),
            "track_npixel": c.tracks.Select(lambda t: t.auxdataConst[cpp_u8]("numberOfPixelHits")),
            "track_nsct": c.tracks.Select(lambda t: t.auxdataConst[cpp_u8]("numberOfSCTHits")),
        }))


def calo_collection():
    """Test a source-like LC-topo collection, without asserting calibration."""
    return (FuncADLQueryPHYSLITE()
        .Select(lambda e: {"info": e.EventInfo("EventInfo"),
                           "jets": e.Jets("AntiKt4LCTopoJets")})
        .Select(lambda c: {
            "run": c.info.runNumber(), "lb": c.info.lumiBlock(),
            "event": c.info.eventNumber(),
            "jet_pt": c.jets.Select(lambda j: j.pt() / 1000.0),
        }))


PROBES = {"smoke": smoke, "calo-validity": calo_validity,
          "calo-emfrac": calo_emfrac, "tracks": tracks, "calo-sampling": calo_sampling,
          "track-hits": track_hits, "calo-collection": calo_collection}
