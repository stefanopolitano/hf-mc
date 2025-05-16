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
    #obj.SetDirectory(0)
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
    colors = [ROOT.kRed+2, #ROOT.kRed-6, ROOT.kOrange-1,
              #ROOT.kSpring, ROOT.kTeal-1, ROOT.kViolet+3,
              #ROOT.kAzure+6,
              ROOT.kBlue+2 , ROOT.kCyan+4]
       
    markers = [ROOT.kFullCircle, ROOT.kFullSquare, ROOT.kFullDiamond,
               ROOT.kFullTriangleUp, ROOT.kFullCross, ROOT.kOpenCircle,
               ROOT.kOpenSquare, ROOT.kOpenDiamond, ROOT.kOpenTriangleUp]

    prefix = 'comparison_qa_mc_'
    for label in labels:
        prefix += label

    ismesons = True
    if ismesons:
        hadrons = ["DzeroToKPi", "DplusToPiKPi", "DsToPhiPiToKKPi"]
        had_labels = ["D^{0}", "D^{#plus}", "D_{s}^{#plus}"]
        suffix = 'mesons'
    else:
        hadrons = ["LcToPKPi", "XiCplusToPKPi", "OmegaCToOmegaPi"]
        had_labels = ["#Lambda_{c}^{#plus}", "#Xi_{c}^{#plus}", "#Omega_{c}"]
        suffix = 'baryons'

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

    h_abundancy_prompt, h_abundancy_nonprompt, h_ntracks, h_prompt_eff, h_nonprompt_eff, h_ratio_eff = (
        [] for _ in range(6))
    h_frac_amb, h_eff_amb = [], []
    (
    h_pt_gen_prompt,
    h_pt_gen_fd,
    h_y_gen_prompt,
    h_y_gen_fd,
    h_declenen_gen_prompt,
    h_declenen_gen_fd,
    ) = ([] for i in range(6))
    for i_file, (infile_name, color, marker) in enumerate(
            zip(infiles, colors[:n_files], markers[:n_files])):
        print(f'Comparing {infile_name}')
        infile = ROOT.TFile.Open(infile_name)

        h_collisions = infile.Get("pv/h_collisions")
        eff = h_collisions.GetBinContent(2) / h_collisions.GetBinContent(1)
        err_eff = ROOT.TMath.Sqrt(h_collisions.GetBinContent(2) * (1 - eff)) / h_collisions.GetBinContent(1)
        hist_reco_coll_eff.SetBinContent(i_file+1, eff)
        hist_reco_coll_eff.SetBinError(i_file+1, err_eff)

        h_abundancy_prompt.append({})
        h_abundancy_nonprompt.append({})
        h_pt_gen_prompt.append({})
        h_pt_gen_fd.append({})
        h_y_gen_prompt.append({})
        h_y_gen_fd.append({})
        h_declenen_gen_prompt.append({})
        h_declenen_gen_fd.append({})

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
            h_pt_gen_prompt[i_file][had] = infile.Get(
                f"gen-distr/h_pt_gen_prompt{had}")
            h_pt_gen_fd[i_file][had] = infile.Get(
                f"gen-distr/h_pt_gen_nonprompt{had}")
            h_y_gen_prompt[i_file][had] = infile.Get(
                f"gen-distr/h_y_gen_prompt{had}")
            h_y_gen_fd[i_file][had] = infile.Get(
                f"gen-distr/h_y_gen_nonprompt{had}")
            h_declenen_gen_prompt[i_file][had] = infile.Get(
                f"gen-distr/h_declenen_gen_prompt{had}")
            h_declenen_gen_fd[i_file][had] = infile.Get(
                f"gen-distr/h_declenen_gen_nonprompt{had}")
            h_prompt_eff[i_file][had].SaveAs('cicio.root')
            input()

            set_obj_style(h_prompt_eff[i_file][had], color, marker)
            set_obj_style(h_nonprompt_eff[i_file][had], color, marker)
            set_obj_style(h_ratio_eff[i_file][had], color, marker)
            set_obj_style(h_y_gen_prompt[i_file][had], color, marker)
            set_obj_style(h_y_gen_fd[i_file][had], color, marker)
            set_obj_style(h_pt_gen_prompt[i_file][had], color, marker)
            set_obj_style(h_pt_gen_fd[i_file][had], color, marker)
            set_obj_style(h_declenen_gen_prompt[i_file][had], color, marker)
            set_obj_style(h_declenen_gen_fd[i_file][had], color, marker)

        h_abundancy_prompt[i_file]['meson'] = infile.Get(
            f"gen-distr/h_abundances_promptmeson")
        h_abundancy_nonprompt[i_file]['meson'] = infile.Get(
            f"gen-distr/h_abundances_nonpromptmeson")
        h_abundancy_prompt[i_file]['baryon'] = infile.Get(
            f"gen-distr/h_abundances_promptbaryon")
        h_abundancy_nonprompt[i_file]['baryon'] = infile.Get(
            f"gen-distr/h_abundances_nonpromptbaryon")
        set_obj_style(h_abundancy_prompt[i_file]['meson'], color, marker)
        set_obj_style(h_abundancy_nonprompt[i_file]['meson'], color, marker)
        set_obj_style(h_abundancy_prompt[i_file]['baryon'], color, marker)
        set_obj_style(h_abundancy_nonprompt[i_file]['baryon'], color, marker)

    line_at_unity = ROOT.TLine(0., 1., 50., 1.)
    line_at_unity.SetLineColor(ROOT.kGray+1)
    line_at_unity.SetLineWidth(2)
    line_at_unity.SetLineStyle(9)

    leg = ROOT.TLegend(0.2, 0.18, 0.5, 0.45)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.03)
    for i_file, label in enumerate(labels):
        leg.AddEntry(h_prompt_eff[i_file][had], label, "pl")

    c_abundancy = ROOT.TCanvas("c_abundancy", "", 1600, 1600)
    c_abundancy.Divide(2, 2)
    c_abundancy.cd(1).SetLogy()
    h_abundancy_prompt[0]['meson'].Draw("HIST E")
    for i_file in range(1, n_files):
        h_abundancy_prompt[i_file]['meson'].Draw("HIST E same")
    leg.Draw()
    c_abundancy.cd(2).SetLogy()
    h_abundancy_nonprompt[0]['meson'].Draw("HIST E")
    for i_file in range(1, n_files):
        h_abundancy_nonprompt[i_file]['meson'].Draw("HIST E same")
    c_abundancy.cd(3).SetLogy()
    h_abundancy_prompt[0]['baryon'].Draw("HIST E")
    for i_file in range(1, n_files):
        h_abundancy_prompt[i_file]['baryon'].Draw("HIST E same")
    c_abundancy.cd(4).SetLogy()
    h_abundancy_nonprompt[0]['baryon'].Draw("HIST E")
    for i_file in range(1, n_files):
        h_abundancy_nonprompt[i_file]['baryon'].Draw("HIST E same")
    c_abundancy.Modified()
    c_abundancy.Update()

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

    c_declenen_gen_prompt = ROOT.TCanvas("c_declenen_gen_prompt", "", 1800, 1200)
    c_declenen_gen_prompt.Divide(3, 2)
    for i_had, had in enumerate(hadrons):
        frame = c_declenen_gen_prompt.cd(i_had+1).DrawFrame(0., 5.e-5,
                                           h_declenen_gen_prompt[-1][had].GetXaxis().GetBinUpEdge(
                                               h_declenen_gen_prompt[-1][had].GetNbinsX()), 1.016,
                                           f";#it{{L}}_{{gen}} (#mum); prompt {had_labels[i_had]}")
        frame.GetXaxis().SetNdivisions(505)
        c_declenen_gen_prompt.cd(i_had+1).SetLogy()
        c_declenen_gen_prompt.cd(i_had+1).SetGrid()
        for i_file in range(n_files):
            h_declenen_gen_prompt[i_file][had].GetXaxis().SetNdivisions(505)
            if (h_declenen_gen_prompt[i_file][had].Integral() != 0):
                h_declenen_gen_prompt[i_file][had].Scale(1./h_declenen_gen_prompt[i_file][had].Integral())
            h_declenen_gen_prompt[i_file][had].Draw("same")
        if i_had == 0:
            leg.Draw()
        frame = c_declenen_gen_prompt.cd(i_had+4).DrawFrame(0., 0.86,
                                           h_declenen_gen_prompt[-1][had].GetXaxis().GetBinUpEdge(
                                               h_declenen_gen_prompt[-1][had].GetNbinsX()), 1.16,
                                           f";#it{{L}}_{{gen}} (#mum); ratio to {labels[0]}")
        frame.GetXaxis().SetNdivisions(505)
        c_declenen_gen_prompt.cd(i_had+4).SetGrid()
        for i_file in range(1, n_files):
            hist_ratio = h_declenen_gen_prompt[i_file][had].Clone(
                f"h_prompt_eff_{had}_{i_file}")
            hist_ratio.Divide(h_declenen_gen_prompt[0][had])
            hist_ratio.GetYaxis().SetDecimals()
            hist_ratio.GetXaxis().SetNdivisions(505)
            hist_ratio.DrawCopy("same")
        line_at_unity.Draw()
    c_declenen_gen_prompt.Modified()
    c_declenen_gen_prompt.Update()

    c_declenen_gen_fd = ROOT.TCanvas("c_declenen_gen_fd", "", 1800, 1200)
    c_declenen_gen_fd.Divide(3, 2)
    for i_had, had in enumerate(hadrons):
        frame = c_declenen_gen_fd.cd(i_had+1).DrawFrame(0., 5.e-6,
                                           h_declenen_gen_fd[-1][had].GetXaxis().GetBinUpEdge(
                                               h_declenen_gen_fd[-1][had].GetNbinsX()), 1.16,
                                           f";#it{{L}}_{{gen}} (#mum); nonprompt {had_labels[i_had]}")
        frame.GetXaxis().SetNdivisions(505)
        c_declenen_gen_fd.cd(i_had+1).SetLogy()
        c_declenen_gen_fd.cd(i_had+1).SetGrid()
        for i_file in range(n_files):
            if (h_declenen_gen_fd[i_file][had].Integral() != 0):
                h_declenen_gen_fd[i_file][had].Scale(1./h_declenen_gen_fd[i_file][had].Integral())
            h_declenen_gen_fd[i_file][had].Draw("same")
        if i_had == 0:
            leg.Draw()
        frame = c_declenen_gen_fd.cd(i_had+4).DrawFrame(0., 0.86,
                                           h_declenen_gen_fd[-1][had].GetXaxis().GetBinUpEdge(
                                               h_declenen_gen_fd[-1][had].GetNbinsX()), 1.16,
                                           f";#it{{L}}_{{gen}} (#mum); ratio to {labels[0]}")
        frame.GetXaxis().SetNdivisions(505)
        c_declenen_gen_fd.cd(i_had+4).SetGrid()
        for i_file in range(1, n_files):
            hist_ratio = h_declenen_gen_fd[i_file][had].Clone(
                f"h_fd_eff_{had}_{i_file}")
            hist_ratio.Divide(h_declenen_gen_fd[0][had])
            hist_ratio.GetYaxis().SetDecimals()
            hist_ratio.DrawCopy("same")
        line_at_unity.Draw()
    c_declenen_gen_fd.Modified()
    c_declenen_gen_fd.Update()

    c_pt_gen_prompt = ROOT.TCanvas("c_pt_gen_prompt", "", 1800, 1200)
    c_pt_gen_prompt.Divide(3, 2)
    for i_had, had in enumerate(hadrons):
        frame = c_pt_gen_prompt.cd(i_had+1).DrawFrame(0., 5.e-6,
                                           h_pt_gen_prompt[-1][had].GetXaxis().GetBinUpEdge(
                                               h_pt_gen_prompt[-1][had].GetNbinsX()), 1.16,
                                           f";#it{{p}}_{{T}} (GeV/#it{{c}}); prompt {had_labels[i_had]}")
        frame.GetXaxis().SetNdivisions(505)
        c_pt_gen_prompt.cd(i_had+1).SetLogy()
        c_pt_gen_prompt.cd(i_had+1).SetGrid()
        for i_file in range(n_files):
            if (h_pt_gen_prompt[i_file][had].Integral() != 0):
                h_pt_gen_prompt[i_file][had].Scale(1./h_pt_gen_prompt[i_file][had].Integral())
            h_pt_gen_prompt[i_file][had].Draw("same")
        if i_had == 0:
            leg.Draw()
        frame = c_pt_gen_prompt.cd(i_had+4).DrawFrame(0., 0.86,
                                           h_pt_gen_prompt[-1][had].GetXaxis().GetBinUpEdge(
                                               h_pt_gen_prompt[-1][had].GetNbinsX()), 1.16,
                                           f";#it{{p}}_{{T}} (GeV/#it{{c}}); ratio to {labels[0]}")
        frame.GetXaxis().SetNdivisions(505)
        c_pt_gen_prompt.cd(i_had+4).SetGrid()
        for i_file in range(1, n_files):
            hist_ratio = h_pt_gen_prompt[i_file][had].Clone(
                f"h_prompt_eff_{had}_{i_file}")
            hist_ratio.Divide(h_pt_gen_prompt[0][had])
            hist_ratio.GetYaxis().SetDecimals()
            hist_ratio.DrawCopy("same")
        line_at_unity.Draw()
    c_pt_gen_prompt.Modified()
    c_pt_gen_prompt.Update()

    c_pt_gen_fd = ROOT.TCanvas("c_pt_gen_fd", "", 1800, 1200)
    c_pt_gen_fd.Divide(3, 2)
    for i_had, had in enumerate(hadrons):
        frame = c_pt_gen_fd.cd(i_had+1).DrawFrame(0., 5.e-6,
                                           h_pt_gen_fd[-1][had].GetXaxis().GetBinUpEdge(
                                               h_pt_gen_fd[-1][had].GetNbinsX()), 1.16,
                                           f";#it{{p}}_{{T}} (GeV/#it{{c}}); nonprompt {had_labels[i_had]}")
        frame.GetXaxis().SetNdivisions(505)
        c_pt_gen_fd.cd(i_had+1).SetLogy()
        c_pt_gen_fd.cd(i_had+1).SetGrid()
        for i_file in range(n_files):
            if (h_pt_gen_fd[i_file][had].Integral() != 0):
                h_pt_gen_fd[i_file][had].Scale(1./h_pt_gen_fd[i_file][had].Integral())
            h_pt_gen_fd[i_file][had].Draw("same")
        if i_had == 0:
            leg.Draw()
        frame = c_pt_gen_fd.cd(i_had+4).DrawFrame(0., 0.86,
                                           h_pt_gen_fd[-1][had].GetXaxis().GetBinUpEdge(
                                               h_pt_gen_fd[-1][had].GetNbinsX()), 1.16,
                                           f";#it{{p}}_{{T}} (GeV/#it{{c}}); ratio to {labels[0]}")
        frame.GetXaxis().SetNdivisions(505)
        c_pt_gen_fd.cd(i_had+4).SetGrid()
        for i_file in range(1, n_files):
            hist_ratio = h_pt_gen_fd[i_file][had].Clone(
                f"h_fd_eff_{had}_{i_file}")
            hist_ratio.Divide(h_pt_gen_fd[0][had])
            hist_ratio.GetYaxis().SetDecimals()
            hist_ratio.DrawCopy("same")
        line_at_unity.Draw()
    c_pt_gen_fd.Modified()
    c_pt_gen_fd.Update()

    c_y_gen_prompt = ROOT.TCanvas("c_y_gen_prompt", "", 1800, 1200)
    c_y_gen_prompt.Divide(3, 2)
    for i_had, had in enumerate(hadrons):
        frame = c_y_gen_prompt.cd(i_had+1).DrawFrame(-h_y_gen_prompt[-1][had].GetXaxis().GetBinUpEdge(
                                               h_y_gen_prompt[-1][had].GetNbinsX()), 5.e-6,
                                           h_y_gen_prompt[-1][had].GetXaxis().GetBinUpEdge(
                                               h_y_gen_prompt[-1][had].GetNbinsX()), 1.16,
                                           f";#it{{y}}_{{gen}}; prompt {had_labels[i_had]}")
        frame.GetXaxis().SetNdivisions(505)
        c_y_gen_prompt.cd(i_had+1).SetLogy()
        c_y_gen_prompt.cd(i_had+1).SetGrid()
        for i_file in range(n_files):
            if (h_y_gen_prompt[i_file][had].Integral() != 0):
                h_y_gen_prompt[i_file][had].Scale(1./h_y_gen_prompt[i_file][had].Integral())
            h_y_gen_prompt[i_file][had].Draw("same")
        if i_had == 0:
            leg.Draw()
        frame = c_y_gen_prompt.cd(i_had+4).DrawFrame(-h_y_gen_prompt[-1][had].GetXaxis().GetBinUpEdge(
                                               h_y_gen_prompt[-1][had].GetNbinsX()), 0.86,
                                           h_y_gen_prompt[-1][had].GetXaxis().GetBinUpEdge(
                                               h_y_gen_prompt[-1][had].GetNbinsX()), 1.16,
                                           f";#it{{y}}_{{gen}}; ratio to {labels[0]}")
        frame.GetXaxis().SetNdivisions(505)
        c_y_gen_prompt.cd(i_had+4).SetGrid()
        for i_file in range(1, n_files):
            hist_ratio = h_y_gen_prompt[i_file][had].Clone(
                f"h_prompt_eff_{had}_{i_file}")
            hist_ratio.Divide(h_y_gen_prompt[0][had])
            hist_ratio.GetYaxis().SetDecimals()
            hist_ratio.DrawCopy("same")
    c_y_gen_prompt.Modified()
    c_y_gen_prompt.Update()

    c_y_gen_fd = ROOT.TCanvas("c_y_gen_fd", "", 1800, 1200)
    c_y_gen_fd.Divide(3, 2)
    for i_had, had in enumerate(hadrons):
        frame = c_y_gen_fd.cd(i_had+1).DrawFrame(-h_y_gen_fd[-1][had].GetXaxis().GetBinUpEdge(
                                               h_y_gen_fd[-1][had].GetNbinsX()), 5.e-6,
                                           h_y_gen_fd[-1][had].GetXaxis().GetBinUpEdge(
                                               h_y_gen_fd[-1][had].GetNbinsX()), 1.16,
                                           f";#it{{y}}_{{gen}}; nonprompt {had_labels[i_had]}")
        frame.GetXaxis().SetNdivisions(505)
        c_y_gen_fd.cd(i_had+1).SetLogy()
        c_y_gen_fd.cd(i_had+1).SetGrid()
        for i_file in range(n_files):
            if (h_y_gen_fd[i_file][had].Integral() != 0):
                h_y_gen_fd[i_file][had].Scale(1./h_y_gen_fd[i_file][had].Integral())
            h_y_gen_fd[i_file][had].Draw("same")
        if i_had == 0:
            leg.Draw()
        frame = c_y_gen_fd.cd(i_had+4).DrawFrame(-h_y_gen_fd[-1][had].GetXaxis().GetBinUpEdge(
                                               h_y_gen_fd[-1][had].GetNbinsX()), 0.86,
                                           h_y_gen_fd[-1][had].GetXaxis().GetBinUpEdge(
                                               h_y_gen_fd[-1][had].GetNbinsX()), 1.16,
                                           f";#it{{y}}_{{gen}}; ratio to {labels[0]}")
        frame.GetXaxis().SetNdivisions(505)
        c_y_gen_fd.cd(i_had+4).SetGrid()
        for i_file in range(1, n_files):
            hist_ratio = h_y_gen_fd[i_file][had].Clone(
                f"h_fd_eff_{had}_{i_file}")
            hist_ratio.Divide(h_y_gen_fd[0][had])
            hist_ratio.GetYaxis().SetDecimals()
            hist_ratio.DrawCopy("same")
    c_y_gen_fd.Modified()
    c_y_gen_fd.Update()

    c_abundancy.SaveAs(os.path.join(outdir, f"{prefix}_abundancy_{suffix}.pdf"))
    c_reco_coll_eff.SaveAs(os.path.join(outdir, f"{prefix}_reco_collision_eff_{suffix}.pdf"))
    c_mult.SaveAs(os.path.join(outdir, f"{prefix}_mult_distr_{suffix}.pdf"))
    c_eff_prompt.SaveAs(os.path.join(outdir, f"{prefix}_prompt_efficiencies_{suffix}.pdf"))
    c_eff_nonprompt.SaveAs(os.path.join(outdir, f"{prefix}_nonprompt_efficiencies_{suffix}.pdf"))
    c_eff_ratio.SaveAs(os.path.join(outdir, f"{prefix}_ratio_efficiencies_{suffix}.pdf"))
    c_declenen_gen_prompt.SaveAs(os.path.join(outdir, f"{prefix}_prompt_gen_declen_distr_{suffix}.pdf"))
    c_declenen_gen_fd.SaveAs(os.path.join(outdir, f"{prefix}_nonprompt_gen_declen_distr_{suffix}.pdf"))
    c_pt_gen_prompt.SaveAs(os.path.join(outdir, f"{prefix}_prompt_gen_pt_distr_{suffix}.pdf"))
    c_pt_gen_fd.SaveAs(os.path.join(outdir, f"{prefix}_nonprompt_gen_pt_distr_{suffix}.pdf"))
    c_y_gen_prompt.SaveAs(os.path.join(outdir, f"{prefix}_prompt_gen_y_distr_{suffix}.pdf"))
    c_y_gen_fd.SaveAs(os.path.join(outdir, f"{prefix}_nonprompt_gen_y_distr_{suffix}.pdf"))

    outfile = ROOT.TFile(os.path.join(
        outdir, f"QA_{prefix}_{suffix}.root"), "recreate")
    hist_reco_coll_eff.Write()
    for hist in h_ntracks:
        hist.Write()
    for dictionary in h_prompt_eff:
        for hist in dictionary.values():
            hist.Write()
    for dictionary in h_y_gen_prompt:
        for hist in dictionary.values():
            hist.Write()
    for dictionary in h_y_gen_fd:
        for hist in dictionary.values():
            hist.Write()
    for dictionary in h_pt_gen_prompt:
        for hist in dictionary.values():
            hist.Write()
    for dictionary in h_pt_gen_fd:
        for hist in dictionary.values():
            hist.Write()
    for dictionary in h_declenen_gen_prompt:
        for hist in dictionary.values():
            hist.Write()
    for dictionary in h_declenen_gen_fd:
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
    c_reco_coll_eff.Write()
    c_mult.Write()
    c_eff_prompt.Write()
    c_eff_nonprompt.Write()
    c_eff_ratio.Write()
    c_declenen_gen_prompt.Write()
    c_declenen_gen_fd.Write()
    c_pt_gen_prompt.Write()
    c_pt_gen_fd.Write()
    c_y_gen_prompt.Write()
    c_y_gen_fd.Write()
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