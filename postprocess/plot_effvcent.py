import ROOT

# Define file paths and particle information
file_paths = [
    "/home/spolitan/alice/analyses/hf-mc/postprocess/outputs/HF_LHC24g2_Small_2P3PDstar_020_train278233/QA_output_HF_LHC24g2_Small_2P3PDstar_020_train278233.root",
    "/home/spolitan/alice/analyses/hf-mc/postprocess/outputs/HF_LHC24g2_Small_2P3PDstar_2050_train284725/QA_output_HF_LHC24g2_Small_2P3PDstar_2050_train284725.root",
    "/home/spolitan/alice/analyses/hf-mc/postprocess/outputs/HF_LHC24g2_Small_2P3PDstar_50100_train284513/QA_output_HF_LHC24g2_Small_2P3PDstar_50100_train284513.root",
]

# Define particle speceis to be analysed
particle_data = [
    ("DzeroToKPi", "D^{0}#rightarrow K#pi"),
    ("DplusToPiKPi", "D^{+}#rightarrow K#pi#pi"),
    ("DsToPhiPiToKKPi", "D_{s}^{+}#rightarrow#phi#pi#rightarrow KK#pi"),
    ("LcToPKPi", "#Lambda_{c}^{+}#rightarrow pK#pi"),
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
    20,  # Full circle
    21,  # Full square
    22,  # Full triangle-up
    23,  # Full triangle-down
    24,  # Open circle
    25,  # Open square
    26,  # Open triangle-up
    27,  # Open diamond
    28,  # Cross
    30,  # Star
]

color_palette_prompt = [
    ROOT.TColor.GetColor("#FFCC99"),  # Light Orange
    ROOT.TColor.GetColor("#FFB74D"),  # Peach
    ROOT.TColor.GetColor("#FF8C42"),  # Light Coral
    ROOT.TColor.GetColor("#FF6F20"),  # Coral
    ROOT.TColor.GetColor("#FF5722"),  # Orange
    ROOT.TColor.GetColor("#E64A19"),  # Dark Orange
    ROOT.TColor.GetColor("#D84315"),  # Burnt Orange
    ROOT.TColor.GetColor("#BF360C"),  # Deep Orange
    ROOT.TColor.GetColor("#A73D08"),  # Rust
    ROOT.TColor.GetColor("#8A3307"),  # Dark Rust
]

color_palette_nonprompt = [
    ROOT.TColor.GetColor("#A7C7E7"),  # Light Sky Blue
    ROOT.TColor.GetColor("#7AA9E9"),  # Soft Azure
    ROOT.TColor.GetColor("#74B3CE"),  # Soft Blue
    ROOT.TColor.GetColor("#5398DD"),  # Fresh Blue
    ROOT.TColor.GetColor("#4A90E2"),  # Sky Blue
    ROOT.TColor.GetColor("#1C75BC"),  # Medium Blue
    ROOT.TColor.GetColor("#1A53B0"),  # Deep Ocean Blue
    ROOT.TColor.GetColor("#316C97"),  # Teal Blue
    ROOT.TColor.GetColor("#0E3B7C"),  # Dark Navy
    ROOT.TColor.GetColor("#092147"),  # Midnight Blue
]

outfile = ROOT.TFile("eff_vcent.root", "recreate")

# Loop over mesons
for meson in particle_data:
    print(f"[info] {meson[0]}")
    mes = meson[0]
    outfile.mkdir(mes)
    outfile.cd(mes)

    canvas_ratio = ROOT.TCanvas(
        f"ceffratio_{mes}", ";#it{p}_{T} (GeV/#it{c}); non-prompt/prompt", 600, 600
    )
    canvas_ratio.cd().SetGridy()
    canvas_ratio.cd().SetGridx()
    canvas_ratio.cd().SetLeftMargin(0.2)

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

        canvas_bottom = ROOT.TCanvas(
            f"ceff_{category}{mes}_ratio",
            ";#it{p}_{T} (GeV/#it{c}); Acc.#times#varepsilon",
            600,
            600,
        )
        canvas_bottom.cd().SetGridy()
        canvas_bottom.cd().SetGridx()
        canvas_bottom.cd().SetLeftMargin(0.2)

        legend = ROOT.TLegend(0.6, 0.3, 0.85, 0.6)
        legend.SetNColumns(2)
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.SetTextSize(0.035)
        legend.SetHeader(f"{category} {meson[1]}")

        # Loop over centrality
        for icent, (centrality) in enumerate(centralities):
            if icent <= 1:
                cent_class = 0
            elif icent > 1 and icent <= 4:
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
            heff.GetYaxis().SetRangeUser(5.0e-06, 2)
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
            heff.SetLineWidth(1)

            canvas.cd()
            heff.Draw("P SAME")
            hratio.append(heff)
            legend.AddEntry(heff, f"{centrality.replace('_', '-')}%", "p")
            outfile.cd(mes)
            heff.Write()

            if category == "nonprompt":  # redoundant otherwise
                heff_npvp_ratio = file.Get(
                    f"efficiencies/h_eff_ratio{mes}vcent{centrality}"
                )

                heff_npvp_ratio.SetTitle("")
                heff_npvp_ratio.SetDirectory(0)

                heff_npvp_ratio.GetXaxis().SetRangeUser(0, 50)
                heff_npvp_ratio.GetXaxis().SetTitle("#it{p}_{T} (GeV/#it{c})")
                heff_npvp_ratio.GetYaxis().SetRangeUser(5.0e-06, 8)
                heff_npvp_ratio.GetYaxis().SetTitle(
                    f"non-prompt/prompt {meson[1]} ratio"
                )

                heff_npvp_ratio.SetLineColor(color)
                heff_npvp_ratio.SetMarkerColor(color)
                heff_npvp_ratio.SetMarkerStyle(marker_styles[icent])
                heff_npvp_ratio.SetMarkerSize(1.5)
                heff_npvp_ratio.SetLineWidth(1)

                canvas_ratio.cd()
                heff_npvp_ratio.Draw("P SAME")
                outfile.cd(mes)
                heff_npvp_ratio.Write()

        if category == "nonprompt":
            canvas_ratio.cd()
            legend.Draw()
            canvas_ratio.SaveAs(f"{mes}meson_efficiencyratio_comparison.pdf")
            canvas_ratio.Write()

        legend.Draw()
        canvas.Draw()
        canvas.SaveAs(f"{category}{mes}meson_efficiency_comparison.pdf")
        canvas.Write()

        canvas_bottom.cd()
        canvas_bottom.cd().SetGridy()
        canvas_bottom.cd().SetGridx()

        h_ratio = []

        for ih, (h) in enumerate(hratio):
            h_ratio.append(
                h.Clone(f"h_ratio_{category}{mes}_{centralities[ih]}_over_0_10")
            )
            h_ratio[-1].SetDirectory(0)
            h_ratio[-1].GetYaxis().SetTitle(
                f"Acc.#times#varepsilon(cent) / Acc.#times#varepsilon(0-10%)"
            )
            h_ratio[-1].Divide(h, hratio[0], 1.0, 1.0, "B")

        for h in h_ratio:
            h.GetYaxis().SetRangeUser(0.0, 6.5)
            h.Draw("P SAME")
            h.Write()

        canvas_bottom.Draw()
        canvas_bottom.SaveAs(f"{category}{mes}meson_efficiencyratio_comparison.pdf")
        canvas_bottom.Write()

        del hratio


outfile.Close()
print("[info] Done!")
