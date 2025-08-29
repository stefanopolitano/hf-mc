#!/usr/bin/env python3
import ROOT

# Input file and tree
root_file = "/Users/spolitan/alice/hf-mc/test_tags/AO2D_corrbkg.root"
tree_name = "DF_2402381385269600/O2hfcanddplite"

file = ROOT.TFile.Open(root_file)
tree = file.Get(tree_name)
if not tree:
    raise RuntimeError(f"Tree {tree_name} not found in {root_file}")

# --- Decay channel mapping (from your enum) ---
channels = {
    0:  "All",
    1:  "DplusToPiKPi",
    2:  "DplusToPiKPiPi0",
    3:  "DplusToPiPiPi",
    4:  "DplusToPiKK",
    5:  "DsToPiKK",
    6:  "DsToPiKKPi0",
    7:  "DsToPiPiK",
    8:  "DsToPiPiPi",
    9:  "DsToPiPiPiPi0",
    10: "DstarToPiKPi",
    11: "DstarToPiKPiPi0",
    12: "DstarToPiKPiPi0Pi0",
    13: "DstarToPiKK",
    14: "DstarToPiKKPi0",
    15: "DstarToPiPiPi",
    16: "DstarToPiPiPiPi0",
    17: "LcToPKPi",
    18: "LcToPKPiPi0",
    19: "LcToPPiPi",
    20: "LcToPKK",
    21: "XicToPKPi",
    22: "XicToPKK",
    23: "XicToSPiPi",
}

# --- Resonant channels ---
channelsRes = {
    0:  "NonResonant",
    1:  "DplusToPhiPi",
    2:  "DplusToKstar0K",
    3:  "DplusToKstar1430_0K",
    4:  "DplusToRho0Pi",
    5:  "DplusToF2_1270Pi",
    6:  "DsToPhiPi",
    7:  "DsToPhiRhoplus",
    8:  "DsToKstar0K",
    9:  "DsToKstar0Pi",
    10: "DsToRho0Pi",
    11: "DsToRho0K",
    12: "DsToF2_1270Pi",
    13: "DsToF0_1370K",
    14: "DsToEtaPi",
    15: "DstarToD0ToRhoplusPi",
    16: "DstarToD0ToRhoplusK",
    17: "DstarToD0ToKstar0Pi0",
    18: "DstarToD0ToKstarPi",
    19: "DstarToDplusToPhiPi",
    20: "DstarToDplusToKstar0K",
    21: "DstarToDplusToKstar1430_0K",
    22: "DstarToDplusToRho0Pi",
    23: "DstarToDplusToF2_1270Pi",
    24: "LcToPKstar0",
    25: "LcToDeltaplusplusK",
    26: "LcToL1520Pi",
    27: "XicToPKstar0",
    28: "XicToPPhi",
}

# Output file
outfile = ROOT.TFile("invMassOverlay.root", "RECREATE")

# Create canvas
canvas = ROOT.TCanvas("c", "Invariant Mass Overlay", 1000, 800)
canvas.SetLogy()

# Legend
legend = ROOT.TLegend(0.25, 0.5, 0.88, 0.88)
legend.SetBorderSize(0)
legend.SetFillStyle(0)
legend.SetTextSize(0.01)
legend.SetNColumns(4)

# --- Integrated histogram (all channels) ---
hIntegrated = ROOT.TH1F("hIntegrated", ";M (GeV/c^{2});Entries", 200, 1.6, 2.2)
tree.Draw("fM>>hIntegrated", "fFlagMcMatchRec>0", "goff")
hIntegrated.SetLineColor(ROOT.kBlack)
hIntegrated.SetLineWidth(2)
hIntegrated.SetStats(0)
hIntegrated.GetYaxis().SetRangeUser(1, 1.e+08)
hIntegrated.Draw("HIST")
legend.AddEntry(hIntegrated, "All channels", "l")

# Colors from kRainBow
ROOT.gStyle.SetPalette(ROOT.kRainBow)
ncolors = 50
colors = [ROOT.TColor.GetColorTransparent(ROOT.TColor.GetColorPalette(int(i*300/(ncolors-1))), 0.3) for i in range(ncolors)]


# --- Per-channel histograms ---
histos = []
hratios = []
counter = 0
for i, (chan, label) in enumerate(channels.items()):
    for j, (reso, resolabel) in enumerate(channelsRes.items()):
        if chan == 0 and reso == 0:
            continue

        full_label = f"{label}_{resolabel}"
        hist_name = f"hM_{full_label}"

        hist = ROOT.TH1F(hist_name, ";M (GeV/c^{2});Entries", 200, 1.6, 2.2)

        cut = f"fFlagMcDecayChanRec=={reso} && fFlagMcMatchRec=={chan}"
        tree.Draw(f"fM>>{hist_name}", cut, "goff")

        # Only keep non-empty histograms
        if hist.GetEntries() > 0 and hist.Integral() > 0:

            hist.SetLineColor(colors[counter])
            hist.SetFillColorAlpha(colors[counter], 0.3)

            counter += 1
            hist.SetLineWidth(2)
            histos.append(hist)
            hist.Draw("HIST SAME")
            #print(f"Channel: {full_label}, Entries: {hist.GetEntries()}, Integral: {hist.Integral():.2f}")
            legend.AddEntry(hist, full_label, "l")
            #input()

            # Ratio to integrated
            ratio_name = f"hRatio_{full_label}"
            ratio = hist.Clone(ratio_name)
            ratio.SetTitle(f";M (GeV/c^{{2}});{full_label}/All channels")
            ratio.Divide(ratio, hIntegrated, 1.0, 1.0, "B")
            hratios.append(ratio)

# Draw legend and save
legend.Draw()
canvas.Update()

canvas.SaveAs("invMassOverlay.png")
canvas.SaveAs("invMassOverlay.pdf")
canvas.Write()

# ratio canvas


outfile.Close()
file.Close()

print("Saved overlay plot to invMassOverlay.png/pdf and histograms in invMassOverlay.root")
