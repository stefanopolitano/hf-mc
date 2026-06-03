#!/usr/bin/env python3
import ROOT

# Input file and tree
root_file = "/alice/cern.ch/user/a/alihyperloop/outputs/0069/691495/251360"
tree_name = "DF_2298103924494048/O2hfcanddplite"
outlabel = "24h1d"
do_download = True

if do_download:
    import os
    if not os.path.isfile(root_file):
        print(f"File {root_file} not found locally. Downloading from MonALISA...")
        os.system(f"alien_cp alien:{root_file}/AO2D.root file:./AO2D_corrbkg_{outlabel}.root")
        root_file = f"AO2D_corrbkg_{outlabel}.root"
    else:
        print(f"File {root_file} already exists locally.")

# Open file and tree
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

# --- Legend labels ---
labels_channels = {
    0:  "All",
    1:  "D^{+}#rightarrow #pi K #pi",
    2:  "D^{+}#rightarrow #pi K #pi #pi^{0}",
    3:  "D^{+}#rightarrow #pi #pi #pi",
    4:  "D^{+}#rightarrow #pi KK",
    5:  "D_{s}^{+}#rightarrow #pi KK",
    6:  "D_{s}^{+}#rightarrow #pi KK #pi^{0}",
    7:  "D_{s}^{+}#rightarrow #pi #pi K",
    8:  "D_{s}^{+}#rightarrow #pi #pi #pi",
    9:  "D_{s}^{+}#rightarrow #pi #pi #pi #pi^{0}",
    10: "D*#rightarrow D^{0}#rightarrow #pi K #pi",
    11: "D*#rightarrow D^{0}#rightarrow #pi K #pi #pi^{0}",
    12: "D*#rightarrow D^{0}#rightarrow #pi K #pi #pi^{0} #pi^{0}",
    13: "D*#rightarrow D^{0}#rightarrow KK",
    14: "D*#rightarrow D^{0}#rightarrow KK #pi^{0}",
    15: "D*#rightarrow D^{0}#rightarrow #pi #pi #pi",
    16: "D*#rightarrow D^{0}#rightarrow #pi #pi #pi #pi^{0}",
    17: "Lc #\rightarrow p K^{-} #pi",
    18: "Lc #\rightarrow p K^{-} #pi #\pi^0",
    19: "Lc #\rightarrow p p \\, \\bar{\\mathrm{p}}",
    20: "Lc #\rightarrow p KK",
    21: "Xic #\rightarrow p K^{-} \\pi",
    22: "Xic #\rightarrow p KK",
    23: "Xic #\rightarrow \\Sigma \\pi \\pi",
}


labels_reso = {
    0:  "",
    1:  "D^{+}#rightarrow #phi #pi",
    2:  "D^{+}#rightarrow K^{*0}K",
    3:  "D^{+}#rightarrow K^{*1430}_{0}K",
    4:  "D^{+}#rightarrow #rho_{0} #pi",
    5:  "D^{+}#rightarrow F_{2}^{1270} #pi",
    6:  "D_{s}^{+}#rightarrow #phi #pi",
    7:  "D_{s}^{+}#rightarrow #phi #rho^{+}",
    8:  "D_{s}^{+}#rightarrow K^{*0}K",
    9:  "D_{s}^{+}#rightarrow K^{*0} #pi",
    10: "D_{s}^{+}#rightarrow #rho_{0} #pi",
    11: "D_{s}^{+}#rightarrow #rho_{0} K",
    12: "D_{s}^{+}#rightarrow F_{2}^{1270} #pi",
    13: "D_{s}^{+}#rightarrow F_{0}^{1370} K",
    14: "D_{s}^{+}#rightarrow #eta #pi",
    15: "D*#rightarrow D_{0} #rightarrow #rho^{+} #pi",
    16: "D*#rightarrow D_{0} #rightarrow #rho^{+} K",
    17: "D*#rightarrow D_{0} #rightarrow K^{*0} #pi^{0}",
    18: "D*#rightarrow D_{0} #rightarrow K^{*} #pi",
    19: "D*#rightarrow D^{+} #rightarrow #phi #pi",
    20: "D*#rightarrow D^{+} #rightarrow K^{*0}K",
    21: "D*#rightarrow D^{+} #rightarrow K^{*1430}_{0}K",
    22: "D*#rightarrow D^{+} #rightarrow #rho_{0} #pi",
    23: "D*#rightarrow D^{+} #rightarrow F_{2}^{1270} #pi",
    24: "Lc #rightarrow p K^{*0}",
    25: "Lc #rightarrow #Delta^{+}^{+} K",
    26: "Lc #rightarrow L_{1520} #pi",
    27: "X_{ic} #rightarrow p K^{*0}",
    28: "X_{ic} #rightarrow p #phi",
}


# Output file
outfile = ROOT.TFile("invMassOverlay.root", "RECREATE")

# Create canvas
canvas = ROOT.TCanvas("c", "Invariant Mass Overlay", 800, 800)
canvas.SetLogy()

# Legend
legend = ROOT.TLegend(0.45, 0.7, 0.88, 0.88)
legend.SetBorderSize(0)
legend.SetFillStyle(0)
legend.SetTextSize(0.02)
legend.SetNColumns(2)

# --- Integrated histogram (all channels) ---
hIntegrated = ROOT.TH1F("hIntegrated", ";#it{M} (GeV/c^{2});Entries", 200, 1.6, 2.2)
tree.Draw("fM>>hIntegrated", "fFlagMcMatchRec>0", "goff")
hIntegrated.SetLineColor(ROOT.kBlack)
hIntegrated.SetLineWidth(2)
hIntegrated.SetStats(0)
hIntegrated.GetYaxis().SetRangeUser(1, hIntegrated.GetMaximum() * 20.4)
hIntegrated.GetXaxis().SetRangeUser(1.65, 2.08)
hIntegrated.Draw("HIST")

# Colors from kRainBow
ROOT.gStyle.SetPalette(ROOT.kRainBow)
_COLOR_BASES = [
    ROOT.kRed + 1,
    ROOT.kAzure + 4,
    ROOT.kOrange + 2,
    ROOT.kGreen + 2,
    ROOT.kViolet + 4,
    ROOT.kCyan + 2,
    ROOT.kTeal + 2,
    ROOT.kPink + 1,
    ROOT.kYellow + 1,
    ROOT.kOrange + 1,
    ROOT.kCyan + 1,
    ROOT.kMagenta + 1,
    ROOT.kGreen + 1,
    ROOT.kBlue + 1,
    ROOT.kRed + 1,
    ROOT.kViolet + 1,
    ROOT.kAzure + 1,
    ROOT.kPink + 2,
    ROOT.kYellow + 2,
    ROOT.kOrange + 3,
    ROOT.kCyan + 3,
    ROOT.kMagenta + 3,
    ROOT.kGreen + 3,
    ROOT.kBlue + 3,
    ROOT.kRed + 3,
    ROOT.kViolet + 3,
]
colors = [ROOT.TColor.GetColorTransparent(c, 0.6) for c in _COLOR_BASES]


# --- Per-channel histograms ---
histos = []
hratios = []
counter = 0
for i, (chan, label) in enumerate(channels.items()):
    for j, (reso, resolabel) in enumerate(channelsRes.items()):
        if chan == 0 and reso == 0:
            continue  # Skip resonant sub-channels for "All"

        full_label = f"{label}_{resolabel}"
        hist_name = f"hM_{full_label}"

        hist = ROOT.TH1F(hist_name, ";M (GeV/c^{2});Entries", 200, 1.6, 2.2)

        cut = f"fFlagMcDecayChanRec=={reso} && fFlagMcMatchRec=={chan}"
        tree.Draw(f"fM>>{hist_name}", cut, "goff")

        # Only keep non-empty histograms
        if hist.GetEntries() > 0 and hist.Integral() > 1000:

            hist.SetLineColor(colors[counter])
            hist.SetMarkerColor(colors[counter])
            hist.SetFillColorAlpha(colors[counter], 0.3)

            counter += 1
            hist.SetLineWidth(2)
            histos.append(hist)
            hist.Draw("a5 HIST SAME")
            legend.AddEntry(hist, f"{labels_channels[chan]} - {labels_reso[reso]}", "f") if labels_reso[reso] != "" else legend.AddEntry(hist, f"{labels_channels[chan]}", "f")

            # Ratio to integrated
            ratio_name = f"hRatio_{full_label}"
            ratio = hist.Clone(ratio_name)
            ratio.SetTitle(f";M (GeV/c^{{2}});{full_label}/All channels")
            ratio.Divide(ratio, hIntegrated, 1.0, 1.0, "B")
            hratios.append(ratio)

# Draw legend and save
legend.Draw()
canvas.Update()

canvas.SaveAs(f"invMassOverlay_{outlabel}.png")
canvas.SaveAs(f"invMassOverlay_{outlabel}.pdf")
canvas.Write()


outfile.Close()
file.Close()

print("Saved overlay plot to invMassOverlay.png/pdf and histograms in invMassOverlay.root")
