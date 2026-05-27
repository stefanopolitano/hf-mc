import ROOT

# six home-made color to mimic transparency
_COLOR_BASES = [
    ROOT.kOrange + 2,
    ROOT.kAzure + 4,
    ROOT.kRed + 1,
    ROOT.kGreen + 2,
    ROOT.kRed + 1,
    ROOT.kAzure + 4,
    ROOT.kGreen + 2,
    ROOT.kOrange + 1,
    ROOT.kViolet + 4,
    ROOT.kCyan + 2,
    ROOT.kViolet + 4,
    ROOT.kCyan + 2,
    ROOT.kTeal + 2,
    ROOT.kPink + 1,
    ROOT.kYellow + 1,
    ROOT.kTeal + 2,
    ROOT.kPink + 1,
    ROOT.kYellow + 1,
]
colors = [ROOT.TColor.GetColorTransparent(c, 0.6) for c in _COLOR_BASES]

labels = ["#pi", "K", "p"]
marker_styles = [
    ROOT.kFullCircle,
    ROOT.kFullSquare,
    ROOT.kFullCrossX,
    ROOT.kFullTriangleUp,
    ROOT.kOpenCircle,
    ROOT.kOpenSquare,
    ROOT.kOpenTriangleUp,
    ROOT.kFullStar,
    ROOT.kFullDiamond,
    ROOT.kFullCross,
    ROOT.kOpenStar,
    ROOT.kOpenDiamond,
    ROOT.kOpenCross,
    ROOT.kFullFourTrianglesPlus,
    ROOT.kFullFourTrianglesX,
    ROOT.kOpenCrossX,
    ROOT.kOpenFourTrianglesPlus,
    ROOT.kOpenFourTrianglesX,
]


ROOT.gStyle.SetGridColor(ROOT.kGray + 2)  # set grid color


def set_style(hist, color, marker, label):
    hist.SetLineColor(color)
    hist.SetMarkerColor(color)
    hist.SetMarkerStyle(marker)
    hist.SetMarkerSize(1)
    hist.SetTitle(f";track #it{{p}}_{{T}} (GeV/c);ITS-TPC tracking #varepsilon ({label}, primary)")
    hist.GetYaxis().SetRangeUser(0, 1.2)
    hist.GetXaxis().SetRangeUser(0, 5)
    hist.GetXaxis().SetTitleOffset(1.2)
    hist.GetYaxis().SetTitleOffset(1.4)


def download_anres(file_name, mclabel):
    """
    Downloads the ANRES file from MonALISA if the file does not exist locally.
    Parameters:
        file_name (str): The name of the ROOT file to check/download.
        mclabel (str): The MC label to create the directory if needed.
    """
    import os
    if not os.path.isfile(file_name):
        print(f"File {file_name} not found locally. Downloading from MonALISA...")
        os.system(f"alien_cp alien:{file_name}/AnalysisResults.root file:./AnalysisResults_trackeff_{mclabel}.root")
    else:
        print(f"File {file_name} already exists locally.")


# Example usage
if __name__ == "__main__":
    input_files = [
        "/alice/cern.ch/user/a/alihyperloop/outputs/0062/628342/213754",
        "/alice/cern.ch/user/a/alihyperloop/outputs/0066/668947/237364",
    ]  # corresponding input files for the MC labels
    mclabels = ["25g3b", "26c9"]  # corresponding labels for the input files
    pdgs = [211, 321, 2212]  # pi, K, p
    useTfBorderCut = False
    download_files = [True, True]  # Set to True to enable downloading files from MonALISA if not present locally

    outfile_name = "tracking_efficiency"
    for mc_label in mclabels:
        outfile_name += f"_{mc_label}"
    outfile_name += ".root"
    print(f"Output file will be: {outfile_name}")

    outfile = ROOT.TFile(outfile_name, "RECREATE")

    heff_compare = {}
    canvases = []
    for ifile, (input_file, mclabel, download_file) in enumerate(zip(input_files, mclabels, download_files)):
        print(f"Processing input file: {input_file} with MC label: {mclabel}")
        outfile.mkdir(mclabel)
        outfile.cd(mclabel)
        heff_compare[mclabel] = {}

        if download_file:
            download_anres(input_file, mclabel)

        folder_name = "qa-efficiency"
        if useTfBorderCut:
            folder_name += "_withTFBorderCut"
        folder_name += "/MC"
        print(f"Using folder: {folder_name}")

        if download_file:
            infile = ROOT.TFile(f"AnalysisResults_trackeff_{mclabel}.root", "READ")
        else:
            infile = ROOT.TFile(input_file, "READ")
        heff_its_tpc_pos = []
        heff_its_tpc_neg = []
        for pdg in pdgs:
            heff_compare[mclabel][pdg] = {}
            hits_pos = infile.Get(f"{folder_name}/pdg{pdg}/pt/prm/its_tpc")
            hits_tpc_pos = infile.Get(f"{folder_name}/pdg{pdg}/pt/prm/generated")
        
            outfile.mkdir(f"{mclabel}/pdg{pdg}")
            outfile.cd(f"{mclabel}/pdg{pdg}")

            i = pdgs.index(pdg)
            color = colors[ifile]
            set_style(hits_pos, color, marker_styles[i], labels[i])
            set_style(hits_tpc_pos, color, marker_styles[i], labels[i])

            heff = hits_pos.Clone(f"pdg{pdg}_its_tpc_pos")
            set_style(heff, color, marker_styles[i], labels[i])
            heff.Divide(heff, hits_tpc_pos, 1.0, 1.0, "B")
            heff.Write()

            heff_its_tpc_pos.append(heff)
            heff_compare[mclabel][pdg]['pos'] = heff
            hits_neg = infile.Get(f"{folder_name}/pdg{-pdg}/pt/prm/its_tpc")
            hits_tpc_neg = infile.Get(f"{folder_name}/pdg{-pdg}/pt/prm/generated")    
            set_style(hits_neg, color, marker_styles[i], labels[i])
            set_style(hits_tpc_neg, color, marker_styles[i], labels[i])

            outfile.mkdir(f"{mclabel}/pdg{-pdg}")
            outfile.cd(f"{mclabel}/pdg{-pdg}")

            heffneg = hits_neg.Clone(f"pdg{pdg}_its_tpc_neg")
            set_style(heffneg, color, marker_styles[i], labels[i])
            heffneg.Divide(heffneg, hits_tpc_neg, 1.0, 1.0, "B")
            heffneg.Write()
            heff_its_tpc_neg.append(heffneg)
            heff_compare[mclabel][pdg]['neg'] = heffneg

        outfile.cd(mclabel)
        canvases.append(ROOT.TCanvas(f"c1_{mclabel}", f"Tracking Efficiency {mclabel}", 1800, 500))
        canvases[-1].SetLogx()
        canvases[-1].SetLogy()
        canvases[-1].SetGridx()
        canvases[-1].SetGridy()
        canvases[-1].SetLeftMargin(0.15)
        canvases[-1].SetBottomMargin(0.15)
        canvases[-1].SetRightMargin(0.05)
        canvases[-1].Divide(3, 1)
        
        legend = ROOT.TLegend(0.45, 0.15, 0.85, 0.45)
        legend.SetBorderSize(1)
        legend.SetTextSize(0.02)
        legend.SetNColumns(3)
        legend.SetHeader(mclabel)
        
        for i, (hpos, hneg) in enumerate(zip(heff_its_tpc_pos, heff_its_tpc_neg)):
            canvases[-1].cd(i+1).SetGridy()
            canvases[-1].cd(i+1).SetGridx()
            canvases[-1].cd(i+1).SetLogx()
            canvases[-1].cd(i+1).SetLogy()

            hpos.SetStats(0)
            hpos.GetYaxis().SetRangeUser(3.e-1, 1.2)
            hpos.GetYaxis().SetDecimals()
            hpos.GetYaxis().SetNdivisions(505)
            hpos.GetXaxis().SetRangeUser(0.1, 5)
            hpos.DrawCopy("E1")
            hneg.DrawCopy("E1 SAME")

            legend.AddEntry(hpos, f"{labels[i]}+", "p")
            legend.AddEntry(hneg, f"{labels[i]}-", "p")

        canvases[-1].cd(1)
        legend.Draw()
        canvases[-1].Update()
        canvases[-1].SaveAs(f"tracking_efficiency_{mclabel}.pdf")
        canvases[-1].Write()

    outfile.cd()
    canvas_compare = ROOT.TCanvas("c2", "Tracking Efficiency Comparison", 1800, 1000)
    canvas_compare.SetGridx()
    canvas_compare.SetGridy()
    canvas_compare.SetLeftMargin(0.25)
    canvas_compare.SetBottomMargin(0.15)
    canvas_compare.SetRightMargin(0.05)
    canvas_compare.Divide(3, 2)
    
    legend_compare = ROOT.TLegend(0.25, 0.15, 0.85, 0.45)
    legend_compare.SetBorderSize(1)
    legend_compare.SetTextSize(0.03)
    legend_compare.SetNColumns(3)
    legend_compare.SetHeader(f"{' vs '.join(mclabels)}", "C")
    
    for ifile, mclabel in enumerate(mclabels):
        for i, pdg in enumerate(pdgs):
            canvas_compare.cd(i + 1).SetGridy()
            canvas_compare.cd(i + 1).SetGridx()
            #canvas_compare.cd(i + 1).SetLogx()
            canvas_compare.cd(i + 1).SetLogy()
            canvas_compare.cd(i + 1).SetLeftMargin(0.15)

            heff = heff_compare[mclabel][pdg]['pos']
            heffneg = heff_compare[mclabel][pdg]['neg']

            heff.SetStats(0)
            heff.GetYaxis().SetRangeUser(3.e-2, 1.2)
            heff.GetYaxis().SetNdivisions(505)
            heff.GetYaxis().SetMaxDigits(1)
            heff.GetYaxis().SetTitleOffset(1.8)
            heff.GetYaxis().SetMoreLogLabels()
            heff.GetXaxis().SetRangeUser(0.1, 5)
            if ifile == 0:
                heff.SetTitle(f"Primary {labels[i]};track #it{{p}}_{{T}} (GeV/c);ITS-TPC tracking #varepsilon ({labels[i]}, primary)")
                heff.DrawCopy("E1Z")
            else:
                heff.DrawCopy("E1Z SAME")
            #heffneg.DrawCopy("E1 SAME")

            legend_compare.AddEntry(heff, f"{labels[i]}+ {mclabel}", "p")
            #legend_compare.AddEntry(heffneg, f"{labels[i]}- {mclabel}", "p")

    canvas_compare.cd(1)
    legend_compare.Draw()

    # Ratio panels in bottom row: others / first input (positive charge only)
    ref_label = mclabels[0]
    legend_ratio = ROOT.TLegend(0.25, 0.15, 0.85, 0.45)
    legend_ratio.SetBorderSize(1)
    legend_ratio.SetTextSize(0.03)
    legend_ratio.SetNColumns(max(1, len(mclabels) - 1))
    legend_ratio.SetHeader("")

    for i, pdg in enumerate(pdgs):
        canvas_compare.cd(i + 4).SetGridy()
        canvas_compare.cd(i + 4).SetGridx()
        canvas_compare.cd(i + 4).SetLeftMargin(0.15)

        ref = heff_compare[ref_label][pdg]['pos']
        for j, mclabel in enumerate(mclabels[1:], start=1):
            heff_other = heff_compare[mclabel][pdg]['pos']
            ratio = heff_other.Clone(f"pdg{pdg}_pos_ratio_{mclabel}_over_{ref_label}")
            ratio.Divide(ratio, ref, 1.0, 1.0, "B")
            ratio.SetStats(0)
            ratio.GetYaxis().SetRangeUser(0.8, 1.2)
            ratio.GetYaxis().SetNdivisions(505)
            ratio.GetYaxis().SetTitleOffset(1.8)
            ratio.GetYaxis().SetTitle(f"others / {ref_label}")
            ratio.GetXaxis().SetRangeUser(0.1, 5)

            if j == 1:
                ratio.DrawCopy("E1Z")
            else:
                ratio.DrawCopy("E1Z SAME")

            legend_ratio.AddEntry(ratio, f"{labels[i]}+ {mclabel}/{ref_label}", "p")

    canvas_compare.cd(4)
    legend_ratio.Draw()
    canvas_compare.Update()
    canvas_compare.SaveAs(f"tracking_efficiency_comparison_{'_'.join(mclabels)}.pdf")
    canvas_compare.Write()

    outfile.Close()
    infile.Close()

    print("Tracking efficiency histograms saved to tracking_efficiency.root")
