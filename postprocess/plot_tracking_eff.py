import ROOT

# six home-made color to mimic transparency
colors = [ROOT.TColor.GetColorTransparent(c, 0.6) for c in [ROOT.kRed+1, ROOT.kAzure+4, ROOT.kGreen+2,
                                                            ROOT.kRed+1, ROOT.kAzure+4, ROOT.kGreen+2,
                                                            ROOT.kOrange+1, ROOT.kViolet+4, ROOT.kCyan+2,
                                                            ROOT.kOrange+1, ROOT.kViolet+4, ROOT.kCyan+2]]
labels = ["#pi", "K", "p"]
marker_styles = [ROOT.kFullCircle, ROOT.kFullSquare, ROOT.kFullTriangleUp, ROOT.kOpenCircle, ROOT.kOpenSquare, ROOT.kOpenTriangleUp,
                    ROOT.kFullStar, ROOT.kFullDiamond, ROOT.kFullCross, ROOT.kOpenStar, ROOT.kOpenDiamond, ROOT.kOpenCross]


ROOT.gStyle.SetGridColor(ROOT.kGray+2)  # set grid color


def set_style(hist, color, marker, label):
    hist.SetLineColor(color)
    hist.SetMarkerColor(color)
    hist.SetMarkerStyle(marker)
    hist.SetMarkerSize(1)
    hist.SetTitle(f";track #it{{p}}_{{T}} (GeV/c);ITS-TPC tracking #varepsilon ({label}, primary)")
    hist.GetYaxis().SetRangeUser(0, 1.2)
    hist.GetXaxis().SetRangeUser(0, 20)
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
    input_files = ["/alice/cern.ch/user/a/alihyperloop/outputs/0048/488721/142852", "/alice/cern.ch/user/a/alihyperloop/outputs/0047/475309/134887"]
    mclabels = ["HF_LHC25g1_All", "HF_LHC24k3_All"]
    pdgs = [211, 321, 2212]  # pi, K, p
    useTfBorderCut = True

    outfile_name = "tracking_efficiency"
    for mc_label in mclabels:
        outfile_name += f"_{mc_label}"
    outfile_name += ".root"
    print(f"Output file will be: {outfile_name}")

    outfile = ROOT.TFile(outfile_name, "RECREATE")

    heff_compare = {}
    canvases = []
    for ifile, (input_file, mclabel) in enumerate(zip(input_files, mclabels)):
        print(f"Processing input file: {input_file} with MC label: {mclabel}")
        outfile.mkdir(mclabel)
        outfile.cd(mclabel)
        heff_compare[mclabel] = {}

        download_anres(input_file, mclabel)

        folder_name = "qa-efficiency"
        if useTfBorderCut:
            folder_name += "_withTFBorderCut"
        folder_name += "/MC"
        print(f"Using folder: {folder_name}")

        infile = ROOT.TFile(f"AnalysisResults_trackeff_{mclabel}.root", "READ")
        heff_its_tpc_pos = []
        heff_its_tpc_neg = []
        hits_all = []
        for pdg in pdgs:

            heff_compare[mclabel][pdg] = {}
            hits_pos = infile.Get(f"{folder_name}/pdg{pdg}/pt/prm/its_tpc")
            hits_tpc_pos = infile.Get(f"{folder_name}/pdg{pdg}/pt/prm/generated")
        
            outfile.mkdir(f"{mclabel}/pdg{pdg}")
            outfile.cd(f"{mclabel}/pdg{pdg}")

            set_style(hits_pos, colors[pdgs.index(pdg)+ifile*6], marker_styles[pdgs.index(pdg)+ifile*6], labels[pdgs.index(pdg)])
            set_style(hits_tpc_pos, colors[pdgs.index(pdg)+ifile*6], marker_styles[pdgs.index(pdg)+ifile*6], labels[pdgs.index(pdg)])

            heff = hits_pos.Clone(f"pdg{pdg}_its_tpc_pos")
            set_style(heff, colors[pdgs.index(pdg)+ifile*6], marker_styles[pdgs.index(pdg)+ifile*6], labels[pdgs.index(pdg)])
            heff.Divide(heff, hits_tpc_pos, 1.0, 1.0, "B")
            heff.Write()

            heff_its_tpc_pos.append(heff)
            heff_compare[mclabel][pdg]['pos'] = heff
            hits_all.append(hits_pos)
            hits_all.append(hits_tpc_pos)

            hits_neg = infile.Get(f"{folder_name}/pdg{-pdg}/pt/prm/its_tpc")
            hits_tpc_neg = infile.Get(f"{folder_name}/pdg{-pdg}/pt/prm/generated")    

            outfile.mkdir(f"{mclabel}/pdg{-pdg}")
            outfile.cd(f"{mclabel}/pdg{-pdg}")

            set_style(hits_neg, colors[pdgs.index(pdg)+ifile*6], marker_styles[pdgs.index(pdg)+ifile*6+3], labels[pdgs.index(pdg)])
            set_style(hits_tpc_neg, colors[pdgs.index(pdg)+ifile*6], marker_styles[pdgs.index(pdg)+ifile*6+3], labels[pdgs.index(pdg)])

            heffneg = hits_neg.Clone(f"pdg{pdg}_its_tpc_neg")
            set_style(heffneg, colors[pdgs.index(pdg)+ifile*6], marker_styles[pdgs.index(pdg)+ifile*6+3], labels[pdgs.index(pdg)])
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
        #legend.SetFillStyle(0)
        legend.SetTextSize(0.04)
        legend.SetNColumns(2)
        legend.SetHeader(mclabel)
        for i, (hpos, hneg) in enumerate(zip(heff_its_tpc_pos, heff_its_tpc_neg)):
            canvases[-1].cd(i+1).SetGridy()
            canvases[-1].cd(i+1).SetGridx()
            canvases[-1].cd(i+1).SetLogx()
            canvases[-1].cd(i+1).SetLogy()

            hpos.SetStats(0)
            hpos.GetYaxis().SetRangeUser(3.e-1, 1.)
            hpos.GetYaxis().SetDecimals()
            hpos.GetYaxis().SetNdivisions(505)
            hpos.GetXaxis().SetRangeUser(0.1, 10)
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
    canvas_compare = ROOT.TCanvas("c2", "Tracking Efficiency Comparison", 1800, 500)
    #canvas_compare.SetLogx()
    canvas_compare.SetLogy()
    canvas_compare.SetGridx()
    canvas_compare.SetGridy()
    canvas_compare.SetLeftMargin(0.25)
    canvas_compare.SetBottomMargin(0.15)
    canvas_compare.SetRightMargin(0.05)
    canvas_compare.Divide(3, 1)
    legend_compare = ROOT.TLegend(0.25, 0.15, 0.85, 0.45)
    legend_compare.SetBorderSize(1)
    #legend_compare.SetFillStyle(0)
    legend_compare.SetTextSize(0.03)
    legend_compare.SetNColumns(2)
    legend_compare.SetHeader(f"{' vs '.join(mclabels)}")
    for ifile, mclabel in enumerate(mclabels):
        for i, pdg in enumerate(pdgs):
            canvas_compare.cd(i+1).SetGridy()
            canvas_compare.cd(i+1).SetGridx()
            #canvas_compare.cd(i+1).SetLogx()
            canvas_compare.cd(i+1).SetLogy()
            canvas_compare.cd(i+1).SetLeftMargin(0.15)

            heff = heff_compare[mclabel][pdg]['pos']
            heffneg = heff_compare[mclabel][pdg]['neg']

            heff.SetStats(0)
            heff.GetYaxis().SetRangeUser(3.e-1, 1.)
            heff.GetYaxis().SetNdivisions(505)
            heff.GetYaxis().SetMaxDigits(1)
            heff.GetYaxis().SetTitleOffset(1.8)
            heff.GetYaxis().SetMoreLogLabels()
            heff.GetXaxis().SetRangeUser(0.1, 20)
            if ifile == 0:
                heff.DrawCopy("E1")
            else:
                heff.DrawCopy("E1 SAME")
            heffneg.DrawCopy("E1 SAME")

            legend_compare.AddEntry(heff, f"{labels[i]}+ {mclabel}", "p")
            legend_compare.AddEntry(heffneg, f"{labels[i]}- {mclabel}", "p")
            

    canvas_compare.cd(1)
    legend_compare.Draw()
    canvas_compare.Update()
    canvas_compare.SaveAs(f"tracking_efficiency_comparison_{'_'.join(mclabels)}.pdf")
    canvas_compare.Write()
    outfile.Close()
    infile.Close()

    print("Tracking efficiency histograms saved to tracking_efficiency.root")
