"""
Script to compare reco collision efficiency in MC from perform_qa.py outputs
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
    colors = [ROOT.kRed+2, ROOT.kRed-6, ROOT.kOrange-1,
              ROOT.kSpring, ROOT.kTeal-1, ROOT.kViolet+3,
              ROOT.kAzure+6, ROOT.kBlue+2 , ROOT.kCyan+4]
       
    markers = [ROOT.kFullCircle, ROOT.kFullSquare, ROOT.kFullDiamond,
               ROOT.kFullTriangleUp, ROOT.kFullCross, ROOT.kOpenCircle,
               ROOT.kOpenSquare, ROOT.kOpenDiamond, ROOT.kOpenTriangleUp]
    hadrons = ["DzeroToKPi", "DplusToPiKPi", "LcToPKPi"]

    try:
        os.makedirs(outdir)
    except FileExistsError:
        pass

    n_files = len(infiles)
    if len(labels) < n_files:
        labels = ["" for _ in range(n_files)]
    print(f'Number of provided files: {n_files}')
    print(f'Lables: {labels}')

    hist_reco_coll_eff = ROOT.TH1F(
        "hist_reco_coll_eff", ";;reco collisions / gen collisions", n_files, -0.5, n_files-0.5)
    hist_reco_coll_eff.SetLineColor(ROOT.kBlack)
    hist_reco_coll_eff.SetLineWidth(2)
    for i_bin, label in enumerate(labels):
        hist_reco_coll_eff.GetXaxis().SetBinLabel(i_bin+1, label)

    h_ntracks, h_prompt_eff, h_nonprompt_eff, h_ratio_eff = (
        [] for _ in range(4))
    h_frac_amb, h_eff_amb = [], []
    for i_file, (infile_name, color, marker) in enumerate(
            zip(infiles, colors[:n_files], markers[:n_files])):
        print(f'Comparing {infile_name}')
        infile = ROOT.TFile.Open(infile_name)

        h_collisions = infile.Get("pv/h_collisions")
        eff = h_collisions.GetBinContent(2) / h_collisions.GetBinContent(1)
        err_eff = ROOT.TMath.Sqrt(h_collisions.GetBinContent(2) * (1 - eff)) / h_collisions.GetBinContent(1)
        hist_reco_coll_eff.SetBinContent(i_file+1, eff)
        hist_reco_coll_eff.SetBinError(i_file+1, err_eff)

        h_prompt_eff.append({})
        h_nonprompt_eff.append({})
        h_ratio_eff.append({})
        for had in hadrons:
            h_prompt_eff[i_file][had] = infile.Get(
                f"efficiencies/h_eff_prompt{had}vcent0_110")
            h_nonprompt_eff[i_file][had] = infile.Get(
                f"efficiencies/h_eff_nonprompt{had}vcent0_110")
            h_ratio_eff[i_file][had] = infile.Get(
                f"efficiencies/h_eff_ratio{had}vcent0_110")
            set_obj_style(h_prompt_eff[i_file][had], color, marker)
            set_obj_style(h_nonprompt_eff[i_file][had], color, marker)
            set_obj_style(h_ratio_eff[i_file][had], color, marker)

    line_at_unity = ROOT.TLine(0., 1., 10., 1.)
    line_at_unity.SetLineColor(ROOT.kGray+1)
    line_at_unity.SetLineWidth(2)
    line_at_unity.SetLineStyle(9)

    leg = ROOT.TLegend(0.2, 0.18, 0.5, 0.45)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.03)
    for i_file, label in enumerate(labels):
        leg.AddEntry(h_prompt_eff[i_file][had], label, "pl")

    c_reco_coll_eff = ROOT.TCanvas("c_reco_coll_eff", "", 1200, 800)
    c_reco_coll_eff.SetRightMargin(0.1)
    hist_reco_coll_eff.GetYaxis().SetRangeUser(0., 1.1)
    hist_reco_coll_eff.Draw("HIST E")
    c_reco_coll_eff.Modified()
    c_reco_coll_eff.Update()

    c_mult = ROOT.TCanvas("c_mult", "", 800, 800)
    c_mult.DrawFrame(0., 1.e-6, 100., 1.,
                     ";number of global tracks;normalised counts")
    c_mult.SetLogy()
    for hist in h_ntracks:
        hist.Draw("same")
    leg.Draw()
    c_mult.Modified()
    c_mult.Update()

    had_labels = ["D^{0}", "D^{#plus}", "#Lambda_{c}^{#plus}"]
    c_eff_prompt = ROOT.TCanvas("c_eff_prompt", "", 1800, 1200)
    c_eff_prompt.Divide(3, 2)
    for i_had, had in enumerate(hadrons):
        c_eff_prompt.cd(i_had+1).DrawFrame(0., 5.e-2,
                                           h_prompt_eff[-1][had].GetXaxis().GetBinUpEdge(
                                               h_prompt_eff[-1][had].GetNbinsX()), 1.6,
                                           f";#it{{p}}_{{T}} (GeV/#it{{c}}); prompt {had_labels[i_had]} efficiency")
        c_eff_prompt.cd(i_had+1).SetLogy()
        for i_file in range(n_files):
            h_prompt_eff[i_file][had].Draw("same")
        if i_had == 0:
            leg.Draw()
        c_eff_prompt.cd(i_had+4).DrawFrame(0., 0.86,
                                           h_prompt_eff[-1][had].GetXaxis().GetBinUpEdge(
                                               h_prompt_eff[-1][had].GetNbinsX()), 1.14,
                                           f";#it{{p}}_{{T}} (GeV/#it{{c}}); ratio to {labels[0]}")
        for i_file in range(1, n_files):
            hist_ratio = h_prompt_eff[i_file][had].Clone(
                f"h_prompt_eff_{had}_{i_file}")
            hist_ratio.Divide(h_prompt_eff[0][had])
            hist_ratio.GetYaxis().SetDecimals()
            hist_ratio.DrawCopy("same")
        line_at_unity.Draw()
    c_eff_prompt.Modified()
    c_eff_prompt.Update()

    c_eff_nonprompt = ROOT.TCanvas("c_eff_nonprompt", "", 1800, 1200)
    c_eff_nonprompt.Divide(3, 2)
    for i_had, had in enumerate(hadrons):
        c_eff_nonprompt.cd(i_had+1).DrawFrame(0., 5.e-2,
                                              h_nonprompt_eff[-1][had].GetXaxis().GetBinUpEdge(
                                                  h_nonprompt_eff[-1][had].GetNbinsX()), 1.6,
                                              f";#it{{p}}_{{T}} (GeV/#it{{c}}); non-prompt {had_labels[i_had]} efficiency")
        c_eff_nonprompt.cd(i_had+1).SetLogy()
        for i_file in range(n_files):
            h_nonprompt_eff[i_file][had].Draw("same")
        if i_had == 0:
            leg.Draw()
        c_eff_nonprompt.cd(i_had+4).DrawFrame(0., 0.8,
                                              h_nonprompt_eff[-1][had].GetXaxis().GetBinUpEdge(
                                                  h_nonprompt_eff[-1][had].GetNbinsX()), 1.2,
                                              f";#it{{p}}_{{T}} (GeV/#it{{c}}); ratio to {labels[0]}")
        for i_file in range(1, n_files):
            hist_ratio = h_nonprompt_eff[i_file][had].Clone(
                f"h_nonprompt_eff_{had}_{i_file}")
            hist_ratio.Divide(h_nonprompt_eff[0][had])
            hist_ratio.GetYaxis().SetDecimals()
            hist_ratio.DrawCopy("same")
        line_at_unity.Draw()
    c_eff_nonprompt.Modified()
    c_eff_nonprompt.Update()

    c_eff_ratio = ROOT.TCanvas("c_eff_ratio", "", 1800, 1200)
    c_eff_ratio.Divide(3, 2)
    for i_had, had in enumerate(hadrons):
        c_eff_ratio.cd(i_had+1).DrawFrame(0., 0.,
                                          h_ratio_eff[-1][had].GetXaxis().GetBinUpEdge(
                                              h_ratio_eff[-1][had].GetNbinsX()), 2.,
                                          f";#it{{p}}_{{T}} (GeV/#it{{c}}); non-prompt/prompt {had_labels[i_had]} efficiency ratio")
        for i_file in range(n_files):
            h_ratio_eff[i_file][had].Draw("same")
        if i_had == 0:
            leg.Draw()
        line_at_unity.Draw()
        c_eff_ratio.cd(i_had+4).DrawFrame(0., 0.8,
                                          h_ratio_eff[-1][had].GetXaxis().GetBinUpEdge(
                                              h_ratio_eff[-1][had].GetNbinsX()), 1.2,
                                          f";#it{{p}}_{{T}} (GeV/#it{{c}}); ratio to {labels[0]}")
        for i_file in range(1, n_files):
            hist_ratio = h_ratio_eff[i_file][had].Clone(
                f"h_ratio_eff_{had}_{i_file}")
            hist_ratio.Divide(h_ratio_eff[0][had])
            hist_ratio.GetYaxis().SetDecimals()
            hist_ratio.DrawCopy("same")
        line_at_unity.Draw()
    c_eff_ratio.Modified()
    c_eff_ratio.Update()

    c_reco_coll_eff.SaveAs(os.path.join(outdir, "reco_collision_eff.pdf"))
    c_mult.SaveAs(os.path.join(outdir, "mult_distr.pdf"))
    c_eff_prompt.SaveAs(os.path.join(outdir, "prompt_efficiencies.pdf"))
    c_eff_nonprompt.SaveAs(os.path.join(outdir, "nonprompt_efficiencies.pdf"))
    c_eff_ratio.SaveAs(os.path.join(outdir, "ratio_efficiencies.pdf"))

    outfile = ROOT.TFile(os.path.join(
        outdir, "QA_comparison.root"), "recreate")
    hist_reco_coll_eff.Write()
    for hist in h_ntracks:
        hist.Write()
    for dictionary in h_prompt_eff:
        for hist in dictionary.values():
            hist.Write()
    for dictionary in h_nonprompt_eff:
        for hist in dictionary.values():
            hist.Write()
    for dictionary in h_ratio_eff:
        for hist in dictionary.values():
            hist.Write()
    for dictionary in h_frac_amb:
        for hist in dictionary.values():
            hist.Write()
    for dictionary in h_eff_amb:
        for hist in dictionary.values():
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