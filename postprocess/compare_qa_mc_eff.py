"""
Script to compare reco collision efficiency and duplicates in MC from check_mc_eff.py outputs
"""

import os
import argparse
import ROOT

def set_obj_style(obj, col, mark):
    """
    Helper function to set object style
    """
    obj.SetDirectory(0)
    obj.SetLineColorAlpha(col, 0.6)
    obj.SetLineWidth(2)
    obj.SetMarkerColorAlpha(col, 0.6)
    obj.SetMarkerStyle(mark)


def plot_efficiency(histo_list, labels, name, x_min, y_min, y_max, y_title, y_ratio_min, y_ratio_max, log = True):
    x_max = histo_list[0].GetXaxis().GetBinUpEdge(histo_list[0].GetNbinsX())

    line_at_unity = ROOT.TLine(0., 1., x_max, 1.)
    line_at_unity.SetLineColor(ROOT.kGray+1)
    line_at_unity.SetLineWidth(2)
    line_at_unity.SetLineStyle(9)

    leg = ROOT.TLegend(0.2, 0.18, 0.5, 0.45)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.03)
    for hist, label in zip(histo_list, labels):
        leg.AddEntry(hist, label, "pl")

    canv = ROOT.TCanvas(f"c_{name}", "", 1800, 900)
    canv.Divide(2, 1)
    canv.cd(1).DrawFrame(x_min, y_min, x_max, y_max, f";#it{{p}}_{{T}} (GeV/#it{{c}}); {y_title}")
    if log:
        canv.cd(1).SetLogy()
    for histo in histo_list:
        histo.Draw("same")
    leg.DrawClone()

    canv.cd(2).DrawFrame(x_min, y_ratio_min, x_max, y_ratio_max, f";#it{{p}}_{{T}} (GeV/#it{{c}}); Ratio to {labels[0]}")
    for i, histo in enumerate(histo_list[1:]):
        hist_ratio = histo.Clone(f"h_{name}_{i}")
        hist_ratio.Divide(histo_list[0])
        hist_ratio.GetYaxis().SetDecimals()
        hist_ratio.DrawCopy("same")
    line_at_unity.DrawClone()
    canv.Modified()
    canv.Update()

    return canv


def compare(infiles, labels, outdir):
    """
    Main function for comparison
    """
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)
    ROOT.gStyle.SetPadLeftMargin(0.15)
    ROOT.gStyle.SetPadBottomMargin(0.15)
    ROOT.gStyle.SetPadRightMargin(0.035)
    ROOT.gStyle.SetPadTopMargin(0.035)
    ROOT.gStyle.SetTitleSize(0.045, "xyt")
    ROOT.gStyle.SetLabelSize(0.045, "xyt")
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetPalette(ROOT.kRainBow)
    ROOT.gStyle.SetMarkerSize(1.2)
    colors = [ROOT.kRed+1, ROOT.kRed-7, ROOT.kOrange-2,
              ROOT.kSpring-1, ROOT.kTeal-2, ROOT.kViolet+2,
              ROOT.kAzure+5, ROOT.kBlue+1 , ROOT.kCyan+3]
              
    markers = [ROOT.kFullCircle, ROOT.kFullSquare, ROOT.kFullDiamond,
               ROOT.kFullTriangleUp, ROOT.kFullCross, ROOT.kOpenCircle,
               ROOT.kOpenSquare, ROOT.kOpenDiamond, ROOT.kOpenTriangleUp]
    
    had_label = "D^{0}"
    
    try:
        os.makedirs(outdir)
    except FileExistsError:
        pass

    n_files = len(infiles)
    if len(labels) < n_files:
        labels = ["" for _ in range(n_files)]

    h_prompt_eff_list, h_nonprompt_eff_list, h_ratio_eff_list = [], [], []
    h_prompt_dupl_list, h_nonprompt_dupl_list, h_prompt_no_dupl_list, h_nonprompt_no_dupl_list  = [], [], [], []
    for infile_name, color, marker in zip(infiles, colors[:n_files], markers[:n_files]):
        infile = ROOT.TFile.Open(infile_name)

        h_prompt_eff = infile.Get(f"efficiencies/h_pt_eff_prompt_step8")
        h_nonprompt_eff = infile.Get(f"efficiencies/h_pt_eff_nonprompt_step8")
        h_ratio_eff = h_nonprompt_eff.Clone("h_eff_ratio_step8")
        h_ratio_eff.Divide(h_prompt_eff)
        h_prompt_dupl = infile.Get(f"efficiencies/h_pt_eff_prompt_step9")
        h_nonprompt_dupl = infile.Get(f"efficiencies/h_pt_eff_nonprompt_step9")
        h_prompt_no_dupl = h_prompt_eff.Clone("h_pt_eff_prompt_no_dupl")
        h_prompt_no_dupl.Add(h_prompt_dupl, -1)
        h_nonprompt_no_dupl = h_nonprompt_eff.Clone("h_pt_eff_nonprompt_no_dupl")
        h_nonprompt_no_dupl.Add(h_nonprompt_dupl, -1)

        set_obj_style(h_prompt_eff, color, marker)
        set_obj_style(h_nonprompt_eff, color, marker)
        set_obj_style(h_ratio_eff, color, marker)
        set_obj_style(h_prompt_dupl, color, marker)
        set_obj_style(h_nonprompt_dupl, color, marker)
        set_obj_style(h_prompt_no_dupl, color, marker)
        set_obj_style(h_nonprompt_no_dupl, color, marker)

        h_prompt_eff_list.append(h_prompt_eff)
        h_nonprompt_eff_list.append(h_nonprompt_eff)
        h_ratio_eff_list.append(h_ratio_eff)
        h_prompt_dupl_list.append(h_prompt_dupl)
        h_nonprompt_dupl_list.append(h_nonprompt_dupl)
        h_prompt_no_dupl_list.append(h_prompt_no_dupl)
        h_nonprompt_no_dupl_list.append(h_nonprompt_no_dupl)

    c_eff_prompt = plot_efficiency(h_prompt_eff_list, labels, "eff_prompt", 0., 5.e-2, 1.6, f"Prompt {had_label} eff.", 0.86, 1.14)
    c_eff_nonprompt = plot_efficiency(h_nonprompt_eff_list, labels, "eff_nonprompt", 0., 5.e-2, 1.6, f"Non-prompt {had_label} eff.", 0.8, 1.2)
    c_eff_ratio = plot_efficiency(h_ratio_eff_list, labels, "eff_ratio", 0., 0., 2., f"Non-prompt/prompt {had_label} eff.", 0.8, 1.2, False)
    c_eff_prompt_dupl = plot_efficiency(h_prompt_dupl_list, labels, "eff_prompt_dupl", 0., 5.e-5, 5.e-2, f"Prompt {had_label} eff. (duplicates only)", 0.5, 1.5)
    c_eff_nonprompt_dupl = plot_efficiency(h_nonprompt_dupl_list, labels, "eff_nonprompt_dupl", 0., 5.e-5, 2.e-1, f"Non-prompt {had_label} eff. (duplicates only)", 0.5, 1.5)
    c_eff_prompt_nodupl = plot_efficiency(h_prompt_no_dupl_list, labels, "eff_prompt_no_dupl", 0., 5.e-2, 1.6, f"Prompt {had_label} eff. (no duplicates)", 0.86, 1.14)
    c_eff_nonprompt_nodupl = plot_efficiency(h_nonprompt_no_dupl_list, labels, "eff_nonprompt_no_dupl", 0., 5.e-2, 1.6, f"Non-prompt {had_label} eff. (no duplicates)", 0.8, 1.2)

    c_eff_prompt.SaveAs(os.path.join(outdir, "prompt_efficiencies.pdf"))
    c_eff_nonprompt.SaveAs(os.path.join(outdir, "nonprompt_efficiencies.pdf"))
    c_eff_ratio.SaveAs(os.path.join(outdir, "ratio_efficiencies.pdf"))
    c_eff_prompt_dupl.SaveAs(os.path.join(outdir, "prompt_dupl_efficiencies.pdf"))
    c_eff_nonprompt_dupl.SaveAs(os.path.join(outdir, "nonprompt_dupl_efficiencies.pdf"))
    c_eff_prompt_nodupl.SaveAs(os.path.join(outdir, "prompt_efficiencies_no_dupl.pdf"))
    c_eff_nonprompt_nodupl.SaveAs(os.path.join(outdir, "nonprompt_efficiencies_no_dupl.pdf"))

    outfile = ROOT.TFile(os.path.join(outdir, "QA_comparison.root"), "recreate")
    for hist in h_prompt_eff_list + h_nonprompt_eff_list + h_ratio_eff_list + h_prompt_dupl_list + h_nonprompt_dupl_list + h_prompt_no_dupl_list + h_nonprompt_no_dupl_list:
        hist.Write()
    outfile.Close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("-i", "--infiles", nargs="+", required=True,
                        help="ROOT input files")
    parser.add_argument("-l", "--labels", nargs="+", default=[], required=False,
                        help="ROOT input files")
    parser.add_argument("-o", "--output_dir", metavar="text", default=".",
                        help="output directory")
    args = parser.parse_args()

    compare(args.infiles, args.labels, args.output_dir)