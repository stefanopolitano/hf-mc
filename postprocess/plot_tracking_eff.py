import ROOT
import yaml
import argparse
import os

pdgs = [211, 321, 2212]  # pi, K, p
pdg_label = {211: "#pi^{+}", 321: "K^{+}", 2212: "p", -211: "#pi^{-}", -321: "K^{-}", -2212: "#bar{p}"}


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
pdg_color = {211: colors[0], 321: colors[1], 2212: colors[5], -211: colors[2], -321: colors[4], -2212: colors[3]}

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

def set_legend_style(legend, header):
    """
    Sets the style for a ROOT TLegend object.
    Parameters:
        legend (ROOT.TLegend): The legend object to style.
    """
    legend.SetBorderSize(1)
    legend.SetTextSize(0.02)
    legend.SetNColumns(2)
    legend.SetTextFont(42)
    legend.SetHeader(header, "C")

def convert_teff_to_th1(teff, name):
    """
    Converts a ROOT TEfficiency object to a TH1 histogram.
    Parameters:
        teff (ROOT.TEfficiency): The TEfficiency object to convert.
        name (str): The name for the resulting TH1 histogram.
    Returns:
        ROOT.TH1: The converted TH1 histogram with efficiency values and errors.
    """
    total = teff.GetTotalHistogram()
    passed = teff.GetPassedHistogram()

    hist = total.Clone(name)
    hist.Reset("ICES")
    hist.SetDirectory(0)

    for ibin in range(1, hist.GetNbinsX() + 1):
        n_total = total.GetBinContent(ibin)
        n_passed = passed.GetBinContent(ibin)

        if n_total <= 0 or n_passed < 0 or n_passed > n_total:
            hist.SetBinContent(ibin, 0.0)
            hist.SetBinError(ibin, 0.0)
            continue

        hist.SetBinContent(ibin, teff.GetEfficiency(ibin))

        err_low = teff.GetEfficiencyErrorLow(ibin)
        err_up = teff.GetEfficiencyErrorUp(ibin)
        hist.SetBinError(ibin, 0.5 * (err_low + err_up))

    return hist

def set_style(hist, color, marker, label, xmin=0, xmax=10, ymin=0, ymax=1.2):
    """
    Sets the style for a ROOT histogram or graph.
    Parameters:
        hist (ROOT.TH1 or ROOT.TGraph): The histogram or graph to style.
        color (int): The color to set for the line and marker.
        marker (int): The marker style to set.
        label (str): The label to use in the title.
    """
    if isinstance(hist, ROOT.TEfficiency):
        hist  = convert_teff_to_th1(hist, hist.GetName())
    hist.SetLineColor(color)
    hist.SetMarkerColor(color)
    hist.SetMarkerStyle(marker)
    hist.SetMarkerSize(1)
    hist.SetTitle(f";track #it{{p}}_{{T}} (GeV/c);ITS-TPC tracking #varepsilon ({label}, primary)")
    hist.GetYaxis().SetRangeUser(ymin, ymax)
    hist.GetXaxis().SetRangeUser(xmin, xmax)
    hist.GetXaxis().SetTitleOffset(1.2)
    hist.GetYaxis().SetTitleOffset(1.4)
    hist.SetStats(0)  # Disable the statistics box

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

def get_heff(infile, folder_name, pdg, teff_name="ITS-TPC_vsPt_Prm_Trk"):
    """
    Retrieves the positive tracking efficiency histogram for a given PDG code.
    Parameters:
        infile (ROOT.TFile): The input ROOT file containing the histograms.
        folder_name (str): The folder name in the ROOT file where the histograms are located.
        pdg (int): The PDG code of the particle for which to retrieve the histograms.
    Returns:
        hits_pos (ROOT.TH1): The positive tracking efficiency histogram.
    Raises:
        RuntimeError: If the folder or histograms cannot be found in the ROOT file.
        RuntimeError: If the histograms cannot be found for the given PDG code.
    """

    eff_list = infile.Get(folder_name)
    if not eff_list:
        raise RuntimeError(f"Could not find {folder_name}")

    # positive
    particle_list = eff_list.FindObject(pdg_label[pdg])
    if not particle_list:
        raise RuntimeError(f"Could not find {pdg_label[pdg]} inside {folder_name}")
    hits_pos = particle_list.FindObject(teff_name)
    if not hits_pos:
        raise RuntimeError(
            f"Could not find {teff_name} inside {folder_name}/{pdg_label[pdg]}"
        )
    
    heff = convert_teff_to_th1(hits_pos, f"pdg{pdg}_pos")
    heff.SetDirectory(0)  # Detach from the file to avoid issues when closing the file

    return heff



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
    wagonid = config['wagon_id']
    download_files = config['download_files']
    setlogx = config['plot_style']['set_logx']
    setlogy = config['plot_style']['set_logy']
    ptmin = config['plot_style']['ptmin']
    ptmax = config['plot_style']['ptmax']
    ymin = config['plot_style'].get('ymin', 0.001)
    ymax = config['plot_style'].get('ymax', 1.0)
    outdir = config['output_directory']
    do_plots = config['do_plots']

    # check if output directory exists, if not create it
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        print(f"Created output directory: {outdir}")
    else:
        print(f"Output directory already exists: {outdir}")

    outfile_name = "tracking_efficiency"
    for mc_label in mclabels:
        outfile_name += f"_{mc_label}"
    outfile_name += ".root"
    print(f"Output file will be: {outfile_name}")

    outfile = ROOT.TFile(f"{outdir}{outfile_name}", "RECREATE")

    heff_compare = {}
    canvases = []
    input_origin_label = []
    # Loop over input files and MC labels
    for ifile, (input_file, mclabel, download_file, id) in enumerate(zip(input_files, mclabels, download_files, wagonid)):
        print(f"Processing input file: {input_file} with MC label: {mclabel}")
        outfile.mkdir(mclabel)
        outfile.cd(mclabel)
        heff_compare[mclabel] = {}

        if download_file:
            download_anres(input_file, mclabel)

        folder_name = "qa-efficiency"
        if id:
            folder_name += f"_{id}"
        folder_name += "/EfficiencyMC"
        print(f"Using folder: {folder_name}")

        if download_file:
            infile = ROOT.TFile(f"AnalysisResults_trackeff_{mclabel}.root", "READ")
            if not infile or infile.IsZombie():
                raise RuntimeError(f"Cannot open ROOT file: AnalysisResults_trackeff_{mclabel}.root")
            input_origin_label.append(f"wagon {get_run_number_from_path(input_file)}")
        else:
            infile = ROOT.TFile.Open(input_file, "READ")
            if not infile or infile.IsZombie():
                raise RuntimeError(f"Cannot open ROOT file: {input_file}")
            input_origin_label.append('local test')
        
        heff_its_tpc_pos = []
        heff_its_tpc_neg = []
        heff_gen_pos = []
        hratio_reco_gen = []
        # Loop over PDG codes to retrieve and style histograms
        for ipdg, pdg in enumerate(pdgs):
            heff_compare[mclabel][pdg] = {}

            heff_pos = get_heff(infile, folder_name, pdg)
            set_style(heff_pos, colors[ipdg], marker_styles[0], labels[ipdg])
            outfile.mkdir(f"{mclabel}/pdg{pdg}")
            outfile.cd(f"{mclabel}/pdg{pdg}")
            heff_pos.Write()
            heff_its_tpc_pos.append(heff_pos)
            heff_compare[mclabel][pdg]["pos"] = heff_pos

            heff_neg = get_heff(infile, folder_name, -pdg)
            set_style(heff_neg, colors[ipdg+3], marker_styles[1], labels[ipdg])
            outfile.mkdir(f"{mclabel}/pdg{-pdg}")
            outfile.cd(f"{mclabel}/pdg{-pdg}")
            heff_neg.Write()
            heff_its_tpc_neg.append(heff_neg)
            heff_compare[mclabel][pdg]["neg"] = heff_neg

            if do_plots['do_reco_gen']:
                heff_gen = get_heff(infile, folder_name, pdg, teff_name="ITS-TPC_vsPt_Prm")
                set_style(heff_gen, colors[ipdg+3], marker_styles[2], labels[ipdg])
                outfile.mkdir(f"{mclabel}/pdg{pdg}/gen")
                outfile.cd(f"{mclabel}/pdg{pdg}/gen")
                heff_gen.Write()
                heff_gen_pos.append(heff_gen)

                hratio = heff_gen.Clone(f"hratio_{pdg}")
                hratio.Divide(heff_its_tpc_pos[ipdg])
                hratio_reco_gen.append(hratio)

        #__________________________________________________________________________
        # Single species plots for each MC label
        if do_plots['do_single_species']:
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
            set_legend_style(legend, mclabel)

            # Plotting positive and negative tracking efficiency histograms for each PDG code
            for ihist, (hpos, hneg) in enumerate(zip(heff_its_tpc_pos, heff_its_tpc_neg)):
                canvases[-1].cd(ihist+1).SetGridy()
                canvases[-1].cd(ihist+1).SetGridx()
                canvases[-1].cd(ihist+1).SetLogx()
                canvases[-1].cd(ihist+1).SetLogy()

                hpos.SetStats(0)
                hpos.GetYaxis().SetRangeUser(3.e-1, 1.22)
                hpos.GetYaxis().SetDecimals()
                hpos.GetYaxis().SetNdivisions(505)
                hpos.GetXaxis().SetRangeUser(ptmin, ptmax)
                hpos.GetYaxis().SetRangeUser(ymin, ymax)

                hneg.SetStats(0)
                hneg.GetXaxis().SetRangeUser(ptmin, ptmax)
                hneg.GetYaxis().SetRangeUser(ymin, ymax)
                print("NEG", pdg, hneg.GetEntries(), hneg.Integral(), hneg.GetMaximum())
                hpos.DrawCopy("E1Z>")
                hneg.DrawCopy("E1Z> SAME")

                legend.AddEntry(hpos, f"{pdg_label[pdgs[ihist]]}", "p")
                legend.AddEntry(hneg, f"{pdg_label[-pdgs[ihist]]}", "p")

            canvases[-1].cd(1)
            legend.Draw()
            canvases[-1].Update()
            canvases[-1].SaveAs(f"{outdir}tracking_efficiency_{mclabel}.pdf")
            canvases[-1].Write()
        
        #__________________________________________________________________________
        # Reco vs Gen efficiency plots
        if do_plots['do_reco_gen']:
            outfile.cd(mclabel)
            canvases.append(ROOT.TCanvas(f"c1_{mclabel}", f"Tracking Efficiency {mclabel}", 1800, 1000))
            canvases[-1].SetLogx()
            canvases[-1].SetLogy()
            canvases[-1].SetGridx()
            canvases[-1].SetGridy()
            canvases[-1].SetLeftMargin(0.15)
            canvases[-1].SetBottomMargin(0.15)
            canvases[-1].SetRightMargin(0.05)
            canvases[-1].Divide(3, 2)

            legend = ROOT.TLegend(0.45, 0.15, 0.85, 0.45)
            set_legend_style(legend, mclabel)

            # Plotting reco vs gen efficiency histograms and their ratios for each PDG code
            for ihist, (hreco, hgen, hratio) in enumerate(zip(heff_its_tpc_pos, heff_gen_pos, hratio_reco_gen)):
                canvases[-1].cd(ihist+1).SetGridy()
                canvases[-1].cd(ihist+1).SetGridx()
                canvases[-1].cd(ihist+1).SetLogx()
                canvases[-1].cd(ihist+1).SetLogy()

                hreco.SetStats(0)
                hreco.GetYaxis().SetRangeUser(3.e-1, 1.22)
                hreco.GetYaxis().SetDecimals()
                hreco.GetYaxis().SetNdivisions(505)
                hreco.GetXaxis().SetRangeUser(ptmin, ptmax)

                hgen.SetStats(0)
                hgen.GetXaxis().SetRangeUser(ptmin, ptmax)
                hgen.GetYaxis().SetRangeUser(ymin, ymax)

                hreco.DrawCopy("E1Z>")
                hgen.DrawCopy("E1Z> SAME")

                legend.AddEntry(hreco, f"{pdg_label[pdgs[ihist]]} - reco", "p")
                legend.AddEntry(hgen, f"{pdg_label[pdgs[ihist]]} - gen", "p")

                hratio.GetYaxis().SetRangeUser(0.8, 1.2)
                hratio.GetYaxis().SetNdivisions(515)
                hratio.GetYaxis().SetTitleOffset(1.6)
                hratio.GetXaxis().SetDecimals()
                hratio.GetYaxis().SetTitle(f"reco / gen")
                hratio.GetXaxis().SetRangeUser(ptmin, ptmax)

                canvases[-1].cd(ihist+4).SetGridy()
                canvases[-1].cd(ihist+4).SetGridx()
                canvases[-1].cd(ihist+4).SetLogx()
                hratio.DrawCopy("E1Z>")

            canvases[-1].cd(1)
            legend.Draw()
            canvases[-1].Update()
            canvases[-1].SaveAs(f"{outdir}tracking_efficiency_{mclabel}_reco_gen.pdf")
            canvases[-1].Write()
    
    outfile.cd()

    #__________________________________________________________________________
    # Comparison plots for different MC labels
    if do_plots['do_compare_mc']:
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
            for ipdg, pdg in enumerate(pdgs):
                canvas_compare.cd(ipdg + 1).SetGridy()
                canvas_compare.cd(ipdg + 1).SetGridx()

                if setlogy: canvas_compare.cd(ipdg + 1).SetLogy()
                canvas_compare.cd(ipdg + 1).SetLeftMargin(0.15)
                if setlogx: canvas_compare.cd(ipdg + 1).SetLogx()

                heff = heff_compare[mclabel][pdg]['pos']
                heff.SetStats(0)
                heff.GetYaxis().SetRangeUser(ymin, ymax)
                heff.GetYaxis().SetNdivisions(525)
                heff.GetYaxis().SetMaxDigits(1)
                heff.GetYaxis().SetTitleOffset(1.8)
                heff.GetYaxis().SetMoreLogLabels()
                heff.GetXaxis().SetRangeUser(ptmin, ptmax)
                if ifile != 0:
                    set_style(heff, colors[len(pdgs) + ipdg], marker_styles[ifile], labels[ipdg], xmin=ptmin, xmax=ptmax, ymin=ymin, ymax=ymax)
                
                if setlogx: heff.GetXaxis().SetMoreLogLabels()
                if ifile == 0:
                    heff.SetTitle(f"Primary {labels[ipdg]};track #it{{p}}_{{T}} (GeV/c);ITS-TPC tracking #varepsilon ({labels[ipdg]}, primary)")
                    heff.DrawCopy("1Z>")
                else:
                    heff.DrawCopy("1Z SAME>")
                if ipdg == 0:
                    legend_compare.AddEntry(heff, f"{mclabel}", "pe")

                if ipdg == 1:  # add latex label for input origin in the middle panel
                    latex = ROOT.TLatex()
                    latex.SetNDC()
                    latex.SetTextSize(0.03)
                    latex.SetTextAlign(22)  # center alignment
                    ypos = 0.18
                    latex.DrawLatex(0.7, ypos + 0.05 * ifile, f"{mclabel} from {input_origin_label[ifile]}")

        canvas_compare.cd(1)
        legend_compare.Draw()

        # hratio panels in bottom row: others / first input (positive charge only)
        ref_label = mclabels[0]
        legend_ratio = ROOT.TLegend(0.18, 0.16,
                                      0.88,
                                      0.30)
        legend_ratio.SetBorderSize(1)
        legend_ratio.SetTextSize(0.03)
        legend_ratio.SetNColumns(len(mclabels) - 1 if len(mclabels) <= 4 else 3)  # Adjust number of columns based on number of MC labels

        for ipdg, pdg in enumerate(pdgs):
            canvas_compare.cd(ipdg + 4).SetGridy()
            canvas_compare.cd(ipdg + 4).SetGridx()
            canvas_compare.cd(ipdg + 4).SetLeftMargin(0.15)
            if setlogx: canvas_compare.cd(ipdg + 4).SetLogx()

            ref = heff_compare[ref_label][pdg]['pos']
            for j, mclabel in enumerate(mclabels[1:], start=1):
                heff_other = heff_compare[mclabel][pdg]['pos']
                hratio = heff_other.Clone(f"pdg{pdg}_pos_ratio_{mclabel}_over_{ref_label}")
                hratio.Divide(hratio, ref, 1.0, 1.0, "B")
                hratio.SetStats(0)
                hratio.GetYaxis().SetRangeUser(0.8, 1.2)
                hratio.GetYaxis().SetNdivisions(515)
                hratio.GetYaxis().SetTitleOffset(1.8)
                hratio.GetYaxis().SetDecimals()
                hratio.GetYaxis().SetTitle(f"others / {ref_label}")
                hratio.GetXaxis().SetRangeUser(ptmin, ptmax)
                if setlogx: hratio.GetXaxis().SetMoreLogLabels()

                if j == 1:
                    hratio.DrawCopy("1Z>")
                else:
                    hratio.DrawCopy("1Z> SAME")


        canvas_compare.cd(4)
        canvas_compare.Update()
        canvas_compare.SaveAs(f"{outdir}tracking_efficiency_comparison_{'_'.join(mclabels)}.pdf")
        canvas_compare.Write()

        outfile.Close()
        infile.Close()

    print("Tracking efficiency histograms saved to tracking_efficiency.root")
