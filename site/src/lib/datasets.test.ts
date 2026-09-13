import { describe, expect, it } from "vitest";
import { extractDatasets } from "./datasets";

describe("extractDatasets", () => {
  it("extracts a user.* rucio dataset", () => {
    expect(
      extractDatasets(
        "Plot the ETmiss of all events in the rucio dataset user.zmarshal:user.zmarshal.364702_OpenData_v1_p6026_2024-04-23.",
      ),
    ).toEqual([
      "user.zmarshal:user.zmarshal.364702_OpenData_v1_p6026_2024-04-23",
    ]);
  });

  it("extracts an opendata: dataset and strips trailing punctuation", () => {
    expect(
      extractDatasets(
        "Plot the ETmiss of events in opendata:mc20_13TeV.700325.Sh_2211_Zmumu_maxHTpTV2_CVetoBVeto.deriv.DAOD_PHYSLITE.e8351_s3681_r13167_p6026.",
      ),
    ).toEqual([
      "opendata:mc20_13TeV.700325.Sh_2211_Zmumu_maxHTpTV2_CVetoBVeto.deriv.DAOD_PHYSLITE.e8351_s3681_r13167_p6026",
    ]);
  });

  it("extracts multiple datasets mentioned in one question", () => {
    const text =
      "Make a stacked histogram in user.zmarshal:user.zmarshal.364702_OpenData_v1_p6026_2024-04-23 " +
      "and user.zmarshal:user.zmarshal.364703_OpenData_v1_p6026_2024-04-23 between 100 and 200 GeV.";
    expect(extractDatasets(text)).toEqual([
      "user.zmarshal:user.zmarshal.364702_OpenData_v1_p6026_2024-04-23",
      "user.zmarshal:user.zmarshal.364703_OpenData_v1_p6026_2024-04-23",
    ]);
  });

  it("returns an empty array for a question with no dataset-like token", () => {
    expect(
      extractDatasets("Print out the list of /skills in the status."),
    ).toEqual([]);
  });

  it("does not match a bare URL as a dataset", () => {
    expect(
      extractDatasets("See https://example.com/docs for details."),
    ).toEqual([]);
  });
});
