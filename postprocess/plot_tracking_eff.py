import ROOT
import yaml
import argparse

# six home-made color to mimic transparency
_COLOR_BASES = [
    ROOT.kBlack,
    ROOT.kRed + 1,
    ROOT.kAzure + 4,
    ROOT.kOrange + 2,
    ROOT.kGreen + 2,
    ROOT.kViolet + 4,
    ROOT.kCyan + 2,
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
    hist.GetXaxis().SetRangeUser(0, 10)
    hist.GetXaxis().SetTitleOffset(1.2)
    hist.GetYaxis().SetTitleOffset(1.4)

def get_run_number_from_path(path):
    """
    Extracts the run number from a given file path.
    Parameters:
        path (str): The file path to extract the run number from.
    Returns:
        str: The extracted run number, or "unknown" if not found.
    """
    import re
    match = re.search(r'/(\d{6})/', path)
    if match:
        return match.group(1)
    else:
        return "unknown"

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


if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Plot tracking efficiency from ROOT files based on a YAML configuration.")
    parser.add_argument("--config", type=str, default="tracking_efficiency_config.yaml", help="Path to the YAML configuration file.", required=True)
    args = parser.parse_args()

    #load configuration from YAML file
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    input_files = config['input_files']

    mclabels = config['mc_labels']
    pdgs = [211, 321, 2212]  # pi, K, p
    wagonid = config['wagon_id']
    useTfBorderCut = config['useTFBorderCut']
    download_files = config['download_files']
    setlogx = config['plot_style']['set_logx']

    outfile_name = "tracking_efficiency"
    for mc_label in mclabels:
        outfile_name += f"_{mc_label}"
    outfile_name += ".root"
    print(f"Output file will be: {outfile_name}")

    outfile = ROOT.TFile(outfile_name, "RECREATE")

    heff_compare = {}
    canvases = []
    input_origin_label = []
    for ifile, (input_file, mclabel, download_file, id, tfborder) in enumerate(zip(input_files, mclabels, download_files, wagonid, useTfBorderCut)):
        print(f"Processing input file: {input_file} with MC label: {mclabel}")
        outfile.mkdir(mclabel)
        outfile.cd(mclabel)
        heff_compare[mclabel] = {}

        if download_file:
            download_anres(input_file, mclabel)

        folder_name = "qa-efficiency"
        if tfborder:
            folder_name += "_withTFBorderCut"
        if id:
            folder_name += f"_{id}"
        folder_name += "/MC"
        print(f"Using folder: {folder_name}")

        if download_file:
            infile = ROOT.TFile(f"AnalysisResults_trackeff_{mclabel}.root", "READ")
            input_origin_label.append(f"wagon {get_run_number_from_path(input_file)}")
        else:
            infile = ROOT.TFile(input_file, "READ")
            input_origin_label.append('local test')
        heff_its_tpc_pos = []
        heff_its_tpc_neg = []
        for pdg in pdgs:
            heff_compare[mclabel][pdg] = {}
            hits_pos = infile.Get(f"{folder_name}/pdg{pdg}/pt/prm/trk/its_tpc")
            hits_tpc_pos = infile.Get(f"{folder_name}/pdg{pdg}/pt/prm/generated")
        
            outfile.mkdir(f"{mclabel}/pdg{pdg}")
            outfile.cd(f"{mclabel}/pdg{pdg}")

            i = pdgs.index(pdg)
            color = colors[ifile]
            set_style(hits_pos, color, marker_styles[0], labels[i])
            set_style(hits_tpc_pos, color, marker_styles[0], labels[i])

            heff = hits_pos.Clone(f"pdg{pdg}_its_tpc_pos")
            set_style(heff, color, marker_styles[0], labels[i])
            heff.Divide(heff, hits_tpc_pos, 1.0, 1.0, "B")
            heff.Write()

            heff_its_tpc_pos.append(heff)
            heff_compare[mclabel][pdg]['pos'] = heff
            hits_neg = infile.Get(f"{folder_name}/pdg{-pdg}/pt/prm/trk/its_tpc")
            hits_tpc_neg = infile.Get(f"{folder_name}/pdg{-pdg}/pt/prm/generated")
            set_style(hits_neg, color, marker_styles[0], labels[i])
            set_style(hits_tpc_neg, color, marker_styles[0], labels[i])

            outfile.mkdir(f"{mclabel}/pdg{-pdg}")
            outfile.cd(f"{mclabel}/pdg{-pdg}")

            heffneg = hits_neg.Clone(f"pdg{pdg}_its_tpc_neg")
            set_style(heffneg, color, marker_styles[0], labels[i])
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
            hpos.GetYaxis().SetRangeUser(3.e-1, 1.22)
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
    
    legend_compare = ROOT.TLegend(0.18, 0.16,
                                  0.88,
                                  0.30)
    legend_compare.SetBorderSize(1)
    legend_compare.SetTextSize(0.03)
    legend_compare.SetNColumns(len(mclabels) if len(mclabels) <= 4 else 3)  # Adjust number of columns based on number of MC labels
    
    for ifile, mclabel in enumerate(mclabels):
        for i, pdg in enumerate(pdgs):
            canvas_compare.cd(i + 1).SetGridy()
            canvas_compare.cd(i + 1).SetGridx()
            #canvas_compare.cd(i + 1).SetLogx()
            canvas_compare.cd(i + 1).SetLogy()
            canvas_compare.cd(i + 1).SetLeftMargin(0.15)
            if setlogx: canvas_compare.cd(i + 1).SetLogx()

            heff = heff_compare[mclabel][pdg]['pos']
            heffneg = heff_compare[mclabel][pdg]['neg']

            heff.SetStats(0)
            heff.GetYaxis().SetRangeUser(3.e-2, 1.2)
            heff.GetYaxis().SetNdivisions(525)
            heff.GetYaxis().SetMaxDigits(1)
            heff.GetYaxis().SetTitleOffset(1.8)
            heff.GetYaxis().SetMoreLogLabels()
            heff.GetXaxis().SetRangeUser(0.1, 5)
            if setlogx: heff.GetXaxis().SetMoreLogLabels()
            if ifile == 0:
                heff.SetTitle(f"Primary {labels[i]};track #it{{p}}_{{T}} (GeV/c);ITS-TPC tracking #varepsilon ({labels[i]}, primary)")
                heff.DrawCopy("1Z")
            else:
                heff.DrawCopy("1Z SAME")
            if i == 0:
                legend_compare.AddEntry(heff, f"{mclabel}", "pe")

            if i == 1:  # add latex label for input origin in the middle panel
                latex = ROOT.TLatex()
                latex.SetNDC()
                latex.SetTextSize(0.03)
                latex.SetTextAlign(22)  # center alignment
                ypos = 0.18
                latex.DrawLatex(0.7, ypos + 0.05 * ifile, f"{mclabel} from {input_origin_label[ifile]}")

    canvas_compare.cd(1)
    legend_compare.Draw()

    # Ratio panels in bottom row: others / first input (positive charge only)
    ref_label = mclabels[0]
    legend_ratio = ROOT.TLegend(0.18, 0.16,
                                  0.88,
                                  0.30)
    legend_ratio.SetBorderSize(1)
    legend_ratio.SetTextSize(0.03)
    legend_ratio.SetNColumns(len(mclabels) - 1 if len(mclabels) <= 4 else 3)  # Adjust number of columns based on number of MC labels

    for i, pdg in enumerate(pdgs):
        canvas_compare.cd(i + 4).SetGridy()
        canvas_compare.cd(i + 4).SetGridx()
        canvas_compare.cd(i + 4).SetLeftMargin(0.15)
        if setlogx: canvas_compare.cd(i + 4).SetLogx()

        ref = heff_compare[ref_label][pdg]['pos']
        for j, mclabel in enumerate(mclabels[1:], start=1):
            heff_other = heff_compare[mclabel][pdg]['pos']
            ratio = heff_other.Clone(f"pdg{pdg}_pos_ratio_{mclabel}_over_{ref_label}")
            ratio.Divide(ratio, ref, 1.0, 1.0, "B")
            ratio.SetStats(0)
            ratio.GetYaxis().SetRangeUser(0.8, 1.2)
            ratio.GetYaxis().SetNdivisions(515)
            ratio.GetYaxis().SetTitleOffset(1.8)
            ratio.GetYaxis().SetTitle(f"others / {ref_label}")
            ratio.GetXaxis().SetRangeUser(0.1, 5)
            if setlogx: ratio.GetXaxis().SetMoreLogLabels()

            if j == 1:
                ratio.DrawCopy("1Z>")
            else:
                ratio.DrawCopy("1Z> SAME")

            if i == 0:
                legend_ratio.AddEntry(ratio, f"{mclabel}/{ref_label}", "peC")

    canvas_compare.cd(4)
    legend_ratio.Draw()
    canvas_compare.Update()
    if True in useTfBorderCut:
        canvas_compare.SaveAs(f"tracking_efficiency_comparison_{'_'.join(mclabels)}_withTFBorderCut.pdf")
    else:
        canvas_compare.SaveAs(f"tracking_efficiency_comparison_{'_'.join(mclabels)}.pdf")
    canvas_compare.Write()

    outfile.Close()
    infile.Close()

    print("Tracking efficiency histograms saved to tracking_efficiency.root")
