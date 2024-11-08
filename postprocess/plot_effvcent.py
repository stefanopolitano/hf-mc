import ROOT
import os

def get_empty_clone(hist):
    '''
    Function to get empty clone of an histogram.

    Inputs:
        - hist is the hisotgram to copy
    Returns:
        - hclone is the cloned hisotgram
    '''
    hclone = hist.Clone(hist.GetName() + '_clone')
    # obtain empty version of the markerstyle
    mstyle = hist.GetMarkerStyle()
    if mstyle == 33:
        mstyle = 27
    if mstyle == 34:
        mstyle = 28
    if mstyle == 20:
        mstyle = 24
    if mstyle == 21:
        mstyle = 25
    if mstyle == 29:
        mstyle = 30
    if mstyle == 47:
        mstyle = 46
    if mstyle == 43:
        mstyle = 42
    if mstyle == 45:
        mstyle = 44
    if mstyle == 22:
        mstyle = 26
    if mstyle == 23:
        mstyle = 32

    hclone.SetMarkerStyle(mstyle)
    hclone.SetMarkerColor(ROOT.kBlack)
    hclone.SetLineWidth(0)

    return hclone

# Define file paths and particle information
file_paths = [
    "/home/spolitan/alice/analyses/hf-mc/postprocess/outputs/HF_LHC24g2_Small_2P3PDstar_020_train289014/QA_output_HF_LHC24g2_Small_2P3PDstar_020_train289014.root",
    "/home/spolitan/alice/analyses/hf-mc/postprocess/outputs/HF_LHC24g2_Small_2P3PDstar_2050_train288969/QA_output_HF_LHC24g2_Small_2P3PDstar_2050_train288969.root",
    "/home/spolitan/alice/analyses/hf-mc/postprocess/outputs/HF_LHC24g2_Small_2P3PDstar_50100_train288635/QA_output_HF_LHC24g2_Small_2P3PDstar_50100_train288635.root",
]

# Define particle speceis to be analysed
particle_data = [
    ("DzeroToKPi", "D^{0}#rightarrow K#pi", 1.e-2, 3, 3), # channel, label, ymin comparison, ymax cent ratio, ymax np / p ratio
    ("DplusToPiKPi", "D^{+}#rightarrow K#pi#pi", 1.e-4, 8, 8),
    ("DsToPhiPiToKKPi", "D_{s}^{+}#rightarrow#phi#pi#rightarrow KK#pi", 1.e-4, 6, 8),
    ("LcToPKPi", "#Lambda_{c}^{+}#rightarrow pK#pi", 1.e-4, 8, 8)
    # Additional particles can be added here as needed
]

# Centrality bins
centralities = [
    "0_10",
    "10_20",
    "20_30",
    "30_40",
    "40_50",
    "50_60",
    "60_70",
    "70_80",
    "80_90",
    "90_100",
]

# Define color palettes for prompt (red) and non-prompt (blue)
marker_styles = [
    ROOT.kFullCircle,  # Full circle
    ROOT.kFullSquare,  # Full square
    ROOT.kFullTriangleUp,  # Full triangle-up
    ROOT.kFullTriangleDown,  # Full triangle-down
    ROOT.kFullDiamond,  # Full diamond
    ROOT.kFullStar,  # Full star
    ROOT.kFullCross,  # Full plus
    ROOT.kFullFourTrianglesPlus,  # Full pentagon
    ROOT.kFullCrossX,  # Filled triangle-down (alternative style)
    ROOT.kFullDoubleDiamond,  # Filled hourglass
]

color_palette_prompt = [
    ROOT.TColor.GetColor("#8A3307"),  # Dark Rust
    ROOT.TColor.GetColor("#A73D08"),  # Rust
    ROOT.TColor.GetColor("#BF360C"),  # Deep Orange
    ROOT.TColor.GetColor("#D84315"),  # Burnt Orange
    ROOT.TColor.GetColor("#E64A19"),  # Dark Orange
    ROOT.TColor.GetColor("#FF5722"),  # Orange
    ROOT.TColor.GetColor("#FF6F20"),  # Coral
    ROOT.TColor.GetColor("#FF8C42"),  # Light Coral
    ROOT.TColor.GetColor("#FFB74D"),  # Peach
    ROOT.TColor.GetColor("#FFCC99"),  # Light Orange
]

color_palette_nonprompt = [
    ROOT.TColor.GetColor("#092147"),  # Midnight Blue
    ROOT.TColor.GetColor("#0E3B7C"),  # Dark Navy
    ROOT.TColor.GetColor("#316C97"),  # Teal Blue
    ROOT.TColor.GetColor("#1A53B0"),  # Deep Ocean Blue
    ROOT.TColor.GetColor("#1C75BC"),  # Medium Blue
    ROOT.TColor.GetColor("#4A90E2"),  # Sky Blue
    ROOT.TColor.GetColor("#5398DD"),  # Fresh Blue
    ROOT.TColor.GetColor("#74B3CE"),  # Soft Blue
    ROOT.TColor.GetColor("#7AA9E9"),  # Soft Azure
    ROOT.TColor.GetColor("#A7C7E7"),  # Light Sky Blue
]

outfile = ROOT.TFile("eff_vcent.root", "recreate")

# Loop over mesons
for meson in particle_data:
    print(f"[info] {meson[0]}")
    mes = meson[0]
    outfile.mkdir(mes)
    outfile.cd(mes)

    canvas_npvp_ratio = ROOT.TCanvas(
        f"ceffratio_{mes}", ";#it{p}_{T} (GeV/#it{c}); non-prompt/prompt", 600, 600
    )
    canvas_npvp_ratio.cd().SetGridy()
    canvas_npvp_ratio.cd().SetGridx()
    canvas_npvp_ratio.cd().SetLeftMargin(0.2)

    # Loop over category (prompt, nonprompt)
    for category in ["prompt", "nonprompt"]:
        print(f"[info]      {category}")
        hratio = []

        canvas = ROOT.TCanvas(
            f"ceff_{category}{mes}",
            ";#it{p}_{T} (GeV/#it{c}); Acc.#times#varepsilon",
            600,
            600,
        )
        canvas.cd().SetLogy()
        canvas.cd().SetGridy()
        canvas.cd().SetGridx()
        canvas.cd().SetLeftMargin(0.2)

        canvas_cent_ratio = ROOT.TCanvas(
            f"ceff_{category}{mes}_ratio",
            ";#it{p}_{T} (GeV/#it{c}); Acc.#times#varepsilon",
            600,
            600,
        )
        canvas_cent_ratio.cd().SetGridy()
        canvas_cent_ratio.cd().SetGridx()
        canvas_cent_ratio.cd().SetLeftMargin(0.2)

        legend = ROOT.TLegend(0.45, 0.3, 0.9, 0.6)
        legend.SetNColumns(2)
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.SetTextSize(0.035)
        leg_empty = legend.Clone()
        legend.SetHeader(f"{category} {meson[1]}")
        leg_empty.SetHeader(" ")

        heff_empty = []
        heff_npvp_ratio_empty = []
        # Loop over centrality
        for icent, (centrality) in enumerate(centralities):
            if centrality in ['0_10', '10_20']:
                cent_class = 0
            elif centrality in ["20_30", "30_40", "40_50"]:
                cent_class = 1
            else:
                cent_class = 2

            file = ROOT.TFile.Open(file_paths[cent_class])
            heff = file.Get(f"efficiencies/h_eff_{category}{mes}vcent{centrality}")

            heff.SetTitle("")
            heff.SetDirectory(0)
            heff.GetXaxis().SetRangeUser(0, 50)
            heff.GetXaxis().SetTitle("#it{p}_{T} (GeV/#it{c})")
            heff.GetXaxis().SetTitleOffset(1.2)
            heff.GetXaxis().SetLabelSize(0.045)
            heff.GetYaxis().SetRangeUser(meson[2], 2)
            heff.GetYaxis().SetMaxDigits(1)
            heff.GetYaxis().SetTitle(f"{category} {meson[1]} Acc.#times#varepsilon")

            color = (
                color_palette_prompt[icent]
                if category == "prompt"
                else color_palette_nonprompt[icent]
            )
            heff.SetLineColor(color)
            heff.SetMarkerColor(color)
            heff.SetMarkerStyle(marker_styles[icent])
            heff.SetMarkerSize(1.5)
            heff.SetLineWidth(2)
            heff_empty.append(get_empty_clone(heff))
            heff_empty[-1].SetDirectory(0)

            canvas.cd()
            heff.Draw("P SAME")
            heff_empty[-1].Draw("P SAME")
            hratio.append(heff)
            legend.AddEntry(heff, f"{centrality.replace('_', '-')}%", "p")
            leg_empty.AddEntry(heff_empty[-1], f"{centrality.replace('_', '-')}%", "p")
            outfile.cd(mes)
            heff.Write()

            # plot np / p eff. ratio
            if category == "nonprompt":  # redoundant otherwise
                heff_npvp_ratio = file.Get(
                    f"efficiencies/h_eff_ratio{mes}vcent{centrality}"
                )

                heff_npvp_ratio.SetTitle("")
                heff_npvp_ratio.SetDirectory(0)

                heff_npvp_ratio.GetXaxis().SetRangeUser(0, 50)
                heff_npvp_ratio.GetXaxis().SetTitle("#it{p}_{T} (GeV/#it{c})")
                heff_npvp_ratio.GetXaxis().SetLabelSize(0.045)
                heff_npvp_ratio.GetXaxis().SetTitleOffset(1.2)
                heff_npvp_ratio.GetYaxis().SetRangeUser(5.0e-06, meson[4])
                heff_npvp_ratio.GetYaxis().SetTitle(
                    f"non-prompt/prompt {meson[1]} ratio"
                )
                heff.GetYaxis().SetMaxDigits(1)
                heff_npvp_ratio.SetLineColor(color)
                heff_npvp_ratio.SetMarkerColor(color)
                heff_npvp_ratio.SetMarkerStyle(marker_styles[icent])
                heff_npvp_ratio.SetMarkerSize(1.5)
                heff_npvp_ratio.SetLineWidth(2)
                heff_npvp_ratio_empty.append(get_empty_clone(heff_npvp_ratio))

                canvas_npvp_ratio.cd()
                heff_npvp_ratio.Draw("P SAME")
                heff_npvp_ratio_empty[-1].Draw("P SAME")
                outfile.cd(mes)
                heff_npvp_ratio.Write()

        if category == "nonprompt":
            canvas_npvp_ratio.cd()
            #legend.Draw()
            #leg_empty.Draw()
            canvas_npvp_ratio.SaveAs(f"{mes}meson_efficiencyratio_comparison.jpg")
            canvas_npvp_ratio.Write()

        canvas.cd()
        legend.Draw()
        leg_empty.Draw()
        canvas.Draw()
        canvas.SaveAs(f"{category}{mes}meson_efficiency_comparison.jpg")
        canvas.Write()

        canvas_cent_ratio.cd()
        canvas_cent_ratio.cd().SetGridy()
        canvas_cent_ratio.cd().SetGridx()

        h_ratio = []
        h_ratio_empty = []
        for ih, (h) in enumerate(hratio):
            h_ratio.append(
                h.Clone(f"h_ratio_{category}{mes}_{centralities[ih]}_over_0_10")
            )
            h_ratio[-1].SetDirectory(0)
            h_ratio[-1].GetYaxis().SetTitle(
                f"Acc.#times#varepsilon(cent) / Acc.#times#varepsilon(0-10%)"
            )
            h_ratio[-1].Divide(h, hratio[0], 1.0, 1.0, "B")
            h_ratio_empty.append(get_empty_clone(h_ratio[-1]))

        for ih, (hratio, hratioempty) in enumerate(zip(h_ratio, h_ratio_empty)):
            hratio.GetYaxis().SetRangeUser(0.0, meson[3])
            hratio.Draw("P SAME")
            hratioempty.Draw("P SAME")
            hratio.Write()

        canvas_cent_ratio.Draw()
        canvas_cent_ratio.SaveAs(f"{category}{mes}meson_efficiencyratio_comparison.jpg")
        canvas_cent_ratio.Write()

        del hratio
        heff_empty.clear()


outfile.Close()
print("[info] Done!")
