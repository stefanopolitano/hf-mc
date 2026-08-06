import ROOT
import yaml
import argparse
import os

pdgs = [211, 321, 2212]  # pi, K, p
pdg_label = {211: "pi", 321: "ka", 2212: "pr"}
pdg_title = {211: "pi", 321: "kaon", 2212: "proton"}

ROOT.gStyle.GetColorPalette(ROOT.kRainbow)

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
        os.system(f"alien_cp alien:{file_name}/AnalysisResults.root file:./AnalysisResults_tpcpid_{mclabel}.root")
    else:
        print(f"File {file_name} already exists locally.")

def make_mean_graph_x_slices(hist2, name):
    graph = ROOT.TGraphErrors(hist2.GetNbinsX())
    graph.SetName(name)

    for ix in range(1, hist2.GetNbinsX() + 1):
        projection = hist2.ProjectionY(f"{name}_proj_x{ix}", ix, ix)
        projection.SetDirectory(0)

        point = ix - 1
        x_center = hist2.GetXaxis().GetBinCenter(ix)
        x_err = 0.5 * hist2.GetXaxis().GetBinWidth(ix)

        if projection.GetEntries() > 0:
            y_mean = projection.GetMean()
            y_err = projection.GetMeanError()
        #else:
        #    y_mean = 0.0
        #    y_err = 0.0

        graph.SetPoint(point, x_center, y_mean)
        graph.SetPointError(point, x_err, y_err)

    graph.SetMarkerStyle(ROOT.kFullCircle)
    graph.SetMarkerSize(0.8)
    graph.SetMarkerColor(ROOT.kBlack)
    graph.SetLineColor(ROOT.kBlack)
    graph.SetLineWidth(2)

    return graph

def style_mean_graph(graph, color, marker_style):
    graph.SetMarkerStyle(marker_style)
    graph.SetMarkerSize(0.9)
    graph.SetMarkerColor(color)
    graph.SetLineColor(color)
    graph.SetLineWidth(2)

if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Plot dE/dx vs pT for different particle species from MC")
    parser.add_argument("--config", type=str, default="tracking_efficiency_config.yaml", help="Path to the YAML configuration file.", required=True)
    args = parser.parse_args()

    #load configuration from YAML file
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    input_files = config['input_files']
    mclabels = config['mc_labels']
    wagonid = config['wagon_id']
    download_files = config['download_files']
    setlogx = config['plot_style'].get('set_logx', False)
    setlogy = config['plot_style'].get('set_logy', False)
    setlogz = config['plot_style'].get('set_logz', False)
    xmin = config['plot_style'].get('xmin', 0.1)
    xmax = config['plot_style'].get('xmax', 10.0)
    ymin = config['plot_style'].get('ymin', 0.001)
    ymax = config['plot_style'].get('ymax', 1.0)
    rebinx = config['plot_style'].get('rebinx', 1)
    rebiny = config['plot_style'].get('rebiny', 1)
    outdir = config['output_directory']
    path_to_hist = config['path_to_th2']

    # check if output directory exists, if not create it
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        print(f"Created output directory: {outdir}")
    else:
        print(f"Output directory already exists: {outdir}")

    outfile_name = "tpc_dedx"
    for mc_label in mclabels:
        outfile_name += f"_{mc_label}"
    outfile_name += ".pdf"
    print(f"Output file will be: {outfile_name}")

    outfile = ROOT.TFile(f"{outdir}{outfile_name}", "RECREATE")

    h2_tpcdedx = {}
    canvases = []
    # Loop over input files and MC labels
    for ifile, (input_file, mclabel, download_file, id) in enumerate(zip(input_files, mclabels, download_files, wagonid)):
        print(f"Processing input file: {input_file} with MC label: {mclabel}")
        outfile.mkdir(mclabel)
        outfile.cd(mclabel)
        h2_tpcdedx[mclabel] = {}

        if download_file:
            download_anres(input_file, mclabel)

        folder_name = "pid-tpc-qa-mc"
        if id:
            folder_name += f"_{id}"
        print(f"Using folder: {folder_name}")

        if download_file:
            infile = ROOT.TFile(f"AnalysisResults_tpcpid_{mclabel}.root", "READ")
            if not infile or infile.IsZombie():
                raise RuntimeError(f"Cannot open ROOT file: AnalysisResults_tpcpid_{mclabel}.root")
        else:
            infile = ROOT.TFile.Open(input_file, "READ")
            if not infile or infile.IsZombie():
                raise RuntimeError(f"Cannot open ROOT file: {input_file}")

        # get tpc maps
        for pdg in pdgs:
            th2_path = path_to_hist[mclabel][pdg_label[pdg]]
            h2_tpcdedx[mclabel][pdg] = infile.Get(th2_path)
            if not h2_tpcdedx[mclabel][pdg]:
                raise RuntimeError(f"Histogram {th2_path} not found in file {input_file} under folder {folder_name}")
            h2_tpcdedx[mclabel][pdg].SetDirectory(0)  # Detach from file
            h2_tpcdedx[mclabel][pdg].SetName(f"h2_tpcdedx_{mclabel}_{pdg_label[pdg]}")
            h2_tpcdedx[mclabel][pdg].Write()
    outfile.Close()


    canvas = ROOT.TCanvas("canvas", "TPC dE/dx", 1000, 1200)
    canvas.Divide(len(mclabels), 3)
    
    ipad = 1
    mean_graphs = {}
    colors = [
        ROOT.kBlack,
        ROOT.kRed + 1,
        ROOT.kBlue + 1,
        ROOT.kGreen + 2,
        ROOT.kMagenta + 1,
        ROOT.kOrange + 7,
        ROOT.kCyan + 2,
    ]
    colors = [ROOT.TColor.GetColorTransparent(c, 0.6) for c in colors]
    marker_styles = [
        ROOT.kFullCircle,
        ROOT.kFullSquare,
        ROOT.kFullTriangleUp,
        ROOT.kFullTriangleDown,
        ROOT.kOpenCircle,
        ROOT.kOpenSquare,
        ROOT.kOpenTriangleUp,
    ]
    for pdg in pdgs:
        for mclabel in mclabels:
            canvas.cd(ipad)
            if setlogz:
                ROOT.gPad.SetLogz()
    
            hist = h2_tpcdedx[mclabel][pdg]
            print(f"Drawing TPC dE/dx for MC label: {mclabel}, PDG: {pdg} ({pdg_title[pdg]})")
            hist.SetTitle(f"{mclabel} {pdg_title[pdg]}")
            hist.RebinX(rebinx)
            hist.RebinY(rebiny)
            hist.GetXaxis().SetRangeUser(xmin, xmax)
            hist.GetYaxis().SetRangeUser(ymin, ymax)
            hist.SetStats(0)
            hist.SetContour(255)
            ROOT.gStyle.SetPalette(ROOT.kRainBow)
            hist.Draw("COLZ same")

            hist.Draw("COLZ")

            mean_graph = make_mean_graph_x_slices(
                hist,
                f"mean_{mclabel}_{pdg}"
            )

            mean_graphs[(mclabel, pdg)] = mean_graph
            mean_graph.Draw("PZ same")
            ipad += 1
    
    canvas.Update()
    canvas.SaveAs(f"{outdir}/{outfile_name}")

    mean_canvas = ROOT.TCanvas("mean_canvas", "Mean TPC dE/dx by MC", 400, 400 * len(pdgs))
    mean_canvas.Divide(1, len(pdgs))
    mean_canvas_objects = []
    for ipad, pdg in enumerate(pdgs, start=1):
        mean_canvas.cd(ipad)
        if setlogx: ROOT.gPad.SetLogx()
        if setlogy: ROOT.gPad.SetLogy()

        multigraph = ROOT.TMultiGraph(
            f"mg_mean_{pdg}",
            f"Mean TPC dE/dx - {pdg_title[pdg]};#it{{p}} (GeV/#it{{c}}) ;#LT dE/dx #GT"
        )
        legend = ROOT.TLegend(0.65, 0.65, 0.88, 0.88)
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.SetTextSize(0.04)

        for imc, mclabel in enumerate(mclabels):
            mean_graph = mean_graphs[(mclabel, pdg)]
            color = colors[imc % len(colors)]
            marker_style = marker_styles[imc % len(marker_styles)]
            style_mean_graph(mean_graph, color, marker_style)
            multigraph.Add(mean_graph, "PZ")
            legend.AddEntry(mean_graph, mclabel, "pl")

        multigraph.Draw("A PZ")
        multigraph.GetXaxis().SetLimits(xmin, xmax)
        multigraph.GetYaxis().SetRangeUser(ymin, ymax)
        
        if ipad == 1: legend.Draw()
        mean_canvas_objects.extend([multigraph, legend])

    mean_canvas.Update()
    mean_canvas.SaveAs(f"{outdir}/{outfile_name.replace('.pdf', '_mean_mcs.pdf')}")
