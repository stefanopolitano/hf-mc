"""
Script to analyse output of taskMcEfficiency.cxx task
"""

import os
import argparse
import numpy as np
import ROOT

PDGCODES = {
    "dplus": 411,
    "dzero": 421,
    "ds": 431,
    "lc": 4122
}

PARTLABELS = {
    "dplus": "D^{#plus}",
    "dzero": "D^{0}",
    "ds": "D_{s}^{#plus}",
    "lc": "#Lambda_{c}^{#plus}"
}

COLORS = [ROOT.kBlue + 3, ROOT.kBlue + 1, ROOT.kAzure + 4, ROOT.kAzure + 2,
          ROOT.kGreen + 2, ROOT.kSpring - 6,  ROOT.kOrange + 7, ROOT.kOrange + 9,
          ROOT.kBlack, ROOT.kRed + 1]

LEGNAMES = [
    "kHFStepMC",
    "kHFStepMcInRapidity",
    "kHFStepAcceptance",
    "kHFStepTrackable",
    "kHFStepAcceptanceTrackable",
    "kHFStepTrackableCuts",
    "kHFStepTracked",
    "kHFStepTrackedCuts",
    "kHFStepTrackedSelected",
    "kHFStepTrackedDuplicates"
]


def set_style(histo, color, open_markers=False):
    """

    """
    #histo.SetLineColorAlpha(color, 0.55)
    #histo.SetMarkerColorAlpha(color, 0.55)
    histo.SetLineColor(color)
    histo.SetMarkerColor(color)
    histo.SetLineWidth(2)
    if open_markers:
        histo.SetMarkerStyle(ROOT.kOpenCircle)
    else:
        histo.SetMarkerStyle(ROOT.kFullCircle)


def check_mc_eff(infile_names, outpath, had, pt_max, iddir=None):
    """

    enum HFStep { kHFStepMC = 0,              // MC mothers in the correct decay channel
                  kHFStepMcInRapidity,        // MC mothers in rapidity |y| < 0.5
                  kHFStepAcceptance,          // MC mothers where all prongs are in the acceptance
                  kHFStepTrackable,           // MC mothers where all prongs have a reconstructed track
                  kHFStepAcceptanceTrackable, // MC mothers where all prongs are in the acceptance and have a reconstructed track
                  kHFStepTrackableCuts,       // MC mothers where all prongs have a reconstructed track which passes the track selection
                  kHFStepTracked,             // signal candidates which have been found
                  kHFStepTrackedCuts,         // signal candidates which have been found and all prongs pass the track selection (cross-check)
                  kHFStepTrackedSelected,     // signal candidates which pass the selector
                  kHFStepTrackedDuplicates,   // signal candidates which pass the selector and are duplicated (only the second, third etc. ones are filled)
                  kHFNSteps };

    enum TrackableStep { kTrackableAll = 0, // all tracks
                         kTrackableITS,     // track contains ITS information
                         kTrackableTPC,     // track contains TPC information
                         kTrackableITSTPC,  // track contains ITS and TPC information
                         kNTrackableSteps };
    """

    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)
    ROOT.gStyle.SetPadLeftMargin(0.15)
    ROOT.gStyle.SetPadBottomMargin(0.1)
    ROOT.gStyle.SetPadRightMargin(0.035)
    ROOT.gStyle.SetPadTopMargin(0.075)
    ROOT.gStyle.SetTitleSize(0.045, "xyt")
    ROOT.gStyle.SetLabelSize(0.045, "xyt")
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPalette(ROOT.kRainBow)
    ROOT.gROOT.SetBatch(True)

    try:
        os.makedirs(outpath)
    except FileExistsError:
        pass

    leg_steps_pt = ROOT.TLegend(0.45, 0.55, 0.93, 0.9)
    leg_steps_pt.SetTextSize(0.03)
    leg_steps_pt.SetFillStyle(0)
    leg_steps_pt.SetBorderSize(0)

    leg_steps_cosp = ROOT.TLegend(0.2, 0.5, 0.6, 0.9)
    leg_steps_cosp.SetTextSize(0.03)
    leg_steps_cosp.SetFillStyle(0)
    leg_steps_cosp.SetBorderSize(0)

    leg_steps_eff = ROOT.TLegend(0.4, 0.15, 0.9, 0.35)
    leg_steps_eff.SetTextSize(0.03)
    leg_steps_eff.SetFillStyle(0)
    leg_steps_eff.SetBorderSize(0)

    lat = ROOT.TLatex()
    lat.SetNDC()
    lat.SetTextSize(0.03)
    lat.SetTextFont(42)
    lat.SetTextColor(ROOT.kBlack)

    hist_pt_prompt, hist_pt_nonprompt = {}, {}
    hist_pt_prompt_badcoll, hist_pt_nonprompt_badcoll = {}, {}
    hist_cosp_prompt, hist_cosp_nonprompt = {}, {}
    hist_cosp_prompt_badcoll, hist_cosp_nonprompt_badcoll = {}, {}

    hist_list = []

    for ifile, infile_name in enumerate(infile_names):
        infile = ROOT.TFile.Open(infile_name)
        if iddir is not None:
            candidates = infile.Get(
                f"hf-task-mc-efficiency_id{iddir}/hCandidates")
        else:
            candidates = infile.Get("hf-task-mc-efficiency/hCandidates")

        for step in range(10):  # see steps defined above
            hist = candidates.getTHn(step)
            if not hist:
                continue

            hist_list.append(hist.Clone(f"histSparse_{step}"))
            
            # particle
            hist.GetAxis(2).SetRangeUser(
                PDGCODES[had] - 0.5, PDGCODES[had] + 0.5)
            # prompt
            hist.GetAxis(5).SetRangeUser(1, 1)
            if step in hist_pt_prompt:
                hist_pt_prompt[step].Add(hist.Projection(0))
                hist_cosp_prompt[step].Add(hist.Projection(3))
            else:
                hist_pt_prompt[step] = hist.Projection(0)
                hist_cosp_prompt[step] = hist.Projection(3)
            # non-prompt
            hist.GetAxis(5).SetRangeUser(2, 2)
            if step in hist_pt_nonprompt:
                hist_pt_nonprompt[step].Add(hist.Projection(0))
                hist_cosp_nonprompt[step].Add(hist.Projection(3))
            else:
                hist_pt_nonprompt[step] = hist.Projection(0)
                hist_cosp_nonprompt[step] = hist.Projection(3)

            # badly associated
            if step > 5:  # only for reco it is meaningful
                hist.GetAxis(4).SetRangeUser(0, 0)
                hist.GetAxis(5).SetRangeUser(2, 2)
                if step in hist_pt_prompt_badcoll:
                    hist_pt_prompt_badcoll[step].Add(hist.Projection(0))
                    hist_cosp_prompt_badcoll[step].Add(hist.Projection(3))
                else:
                    hist_pt_prompt_badcoll[step] = hist.Projection(0)
                    hist_cosp_prompt_badcoll[step] = hist.Projection(3)
                hist.GetAxis(5).SetRangeUser(2, 2)
                if step in hist_pt_nonprompt_badcoll:
                    hist_pt_nonprompt_badcoll[step].Add(hist.Projection(0))
                    hist_cosp_nonprompt_badcoll[step].Add(hist.Projection(3))
                else:
                    hist_pt_nonprompt_badcoll[step] = hist.Projection(0)
                    hist_cosp_nonprompt_badcoll[step] = hist.Projection(3)
                hist.GetAxis(4).SetRange(-1, -1)  # release

            # anti-particle
            hist.GetAxis(2).SetRangeUser(
                -PDGCODES[had] - 0.5, -PDGCODES[had] + 0.5)
            # prompt
            hist.GetAxis(5).SetRangeUser(1, 1)
            hist_pt_prompt[step].Add(hist.Projection(0))
            hist_cosp_prompt[step].Add(hist.Projection(3))
            # non-prompt
            hist.GetAxis(5).SetRangeUser(2, 2)
            hist_pt_nonprompt[step].Add(hist.Projection(0))
            hist_cosp_nonprompt[step].Add(hist.Projection(3))

            # badly associated
            if step > 5:  # only for reco it is meaningful
                hist.GetAxis(4).SetRangeUser(0, 0)
                hist.GetAxis(5).SetRangeUser(2, 2)
                hist_pt_prompt_badcoll[step].Add(hist.Projection(0))
                hist_cosp_prompt_badcoll[step].Add(hist.Projection(3))
                hist.GetAxis(5).SetRangeUser(2, 2)
                hist_pt_nonprompt_badcoll[step].Add(hist.Projection(0))
                hist_cosp_nonprompt_badcoll[step].Add(hist.Projection(3))
                hist.GetAxis(4).SetRange(-1, -1)  # release

            set_style(hist_pt_prompt[step], COLORS[step])
            set_style(hist_cosp_prompt[step], COLORS[step])
            set_style(hist_pt_nonprompt[step], COLORS[step])
            set_style(hist_cosp_nonprompt[step], COLORS[step])
            if step > 5:  # only for reco it is meaningful
                set_style(hist_pt_prompt_badcoll[step], COLORS[step], True)
                set_style(hist_cosp_prompt_badcoll[step], COLORS[step], True)
                set_style(hist_pt_nonprompt_badcoll[step], COLORS[step], True)
                set_style(
                    hist_cosp_nonprompt_badcoll[step], COLORS[step], True)

            if ifile == 0:
                leg_steps_pt.AddEntry(hist_pt_prompt[step], LEGNAMES[step], "pl")
                leg_steps_cosp.AddEntry(
                    hist_cosp_prompt[step], LEGNAMES[step], "pl")

    used_steps = list(hist_pt_prompt.keys())
    used_steps_badcoll = list(hist_pt_prompt_badcoll.keys())
    steps_eff = [2, 4, 5, 6, 8, 9]

    # let's rebin
    pt_rebin = np.array((0., 1., 3., 5., 8., 12., 16., 50.))
    npt_reb = len(pt_rebin) - 1
    for step in used_steps:
        hist_pt_prompt[step] = hist_pt_prompt[step].Rebin(
            npt_reb, f"hist_pt_prompt_{step}", pt_rebin)
        hist_pt_nonprompt[step] = hist_pt_nonprompt[step].Rebin(
            npt_reb, f"hist_pt_nonprompt_{step}", pt_rebin)
    for step in used_steps_badcoll:
        hist_pt_prompt_badcoll[step] = hist_pt_prompt_badcoll[step].Rebin(
            npt_reb, f"hist_pt_prompt_badcoll_{step}", pt_rebin)
        hist_pt_nonprompt_badcoll[step] = hist_pt_nonprompt_badcoll[step].Rebin(
            npt_reb, f"hist_pt_nonprompt_badcoll_{step}", pt_rebin)

    h_pt_eff_prompt, h_pt_eff_nonprompt = {}, {}
    for step in steps_eff:
        if step in hist_pt_prompt:
            h_pt_eff_prompt[step] = hist_pt_prompt[step].Clone(
                f"h_pt_eff_prompt_step{step}")
            h_pt_eff_prompt[step].Divide(
                hist_pt_prompt[step], hist_pt_prompt[1], 1., 1., "B")
            leg_steps_eff.AddEntry(hist_pt_prompt[step], LEGNAMES[step], "pl")
        if step in hist_pt_nonprompt:
            h_pt_eff_nonprompt[step] = hist_pt_nonprompt[step].Clone(
                f"h_pt_eff_nonprompt_step{step}")
            h_pt_eff_nonprompt[step].Divide(
                hist_pt_nonprompt[step], hist_pt_nonprompt[1], 1., 1., "B")

    hist_pt_ratio_prompt_badcoll, hist_pt_ratio_nonprompt_badcoll = {}, {}
    for step in used_steps_badcoll:
        hist_pt_ratio_prompt_badcoll[step] = hist_pt_prompt_badcoll[step].Clone(
            f"hist_pt_ratio_prompt_badcoll_step{step}")
        hist_pt_ratio_prompt_badcoll[step].Divide(
            hist_pt_prompt_badcoll[step], hist_pt_prompt[step], 1., 1., "B")
        hist_pt_ratio_nonprompt_badcoll[step] = hist_pt_nonprompt_badcoll[step].Clone(
            f"hist_pt_ratio_nonprompt_badcoll_step{step}")
        hist_pt_ratio_nonprompt_badcoll[step].Divide(
            hist_pt_nonprompt_badcoll[step], hist_pt_nonprompt[step], 1., 1., "B")

    hist_pt_trackedovertrackable_prompt, hist_pt_trackedovertrackable_nonprompt = None, None
    if 5 in hist_pt_prompt and 6 in hist_pt_prompt:
        hist_pt_trackedovertrackable_prompt = hist_pt_prompt[6].Clone(
            "hist_pt_trackedovertrackable_prompt")
        hist_pt_trackedovertrackable_prompt.Divide(
            hist_pt_prompt[6], hist_pt_prompt[5], 1., 1., "B")
    if 5 in hist_pt_nonprompt and 6 in hist_pt_nonprompt:
        hist_pt_trackedovertrackable_nonprompt = hist_pt_nonprompt[6].Clone(
            "hist_pt_trackedovertrackable_nonprompt")
        hist_pt_trackedovertrackable_nonprompt.Divide(
            hist_pt_nonprompt[6], hist_pt_nonprompt[5], 1., 1., "B")

    hist_pt_duplicatesoversel_prompt, hist_pt_duplicatesoversel_nonprompt = None, None
    if 8 in hist_pt_prompt and 9 in hist_pt_prompt:
        hist_pt_duplicatesoversel_prompt = hist_pt_prompt[9].Clone(
            "hist_pt_duplicatesoversel_prompt")
        hist_pt_duplicatesoversel_prompt.Divide(
            hist_pt_prompt[9], hist_pt_prompt[8], 1., 1., "B")
    if 8 in hist_pt_nonprompt and 9 in hist_pt_nonprompt:
        hist_pt_duplicatesoversel_nonprompt = hist_pt_nonprompt[9].Clone(
            "hist_pt_duplicatesoversel_nonprompt")
        hist_pt_duplicatesoversel_nonprompt.Divide(
            hist_pt_nonprompt[9], hist_pt_nonprompt[8], 1., 1., "B")

    for step in used_steps_badcoll:
        hist_pt_ratio_prompt_badcoll[step] = hist_pt_prompt_badcoll[step].Clone(
            f"hist_pt_ratio_prompt_badcoll_step{step}")
        hist_pt_ratio_prompt_badcoll[step].Divide(
            hist_pt_prompt_badcoll[step], hist_pt_prompt[step], 1., 1., "B")
        hist_pt_ratio_nonprompt_badcoll[step] = hist_pt_nonprompt_badcoll[step].Clone(
            f"hist_pt_ratio_nonprompt_badcoll_step{step}")
        hist_pt_ratio_nonprompt_badcoll[step].Divide(
            hist_pt_nonprompt_badcoll[step], hist_pt_nonprompt[step], 1., 1., "B")
        
    output = ROOT.TFile(os.path.join(outpath, "Eff_output.root"), "recreate")
    dir_distr = output.mkdir("distr")
    dir_distr.cd()
    for hist in hist_pt_prompt.values():
        hist.Write()
    for hist in hist_pt_nonprompt.values():
        hist.Write()
    output.cd()
    dir_eff = output.mkdir("efficiencies")
    dir_eff.cd()
    for hist in h_pt_eff_prompt.values():
        hist.Write()
    for hist in h_pt_eff_nonprompt.values():
        hist.Write()
    output.cd()
    for hist in hist_list:
        hist.Write()
    output.Close()

    pt_min = hist_pt_prompt[0].GetXaxis().GetBinLowEdge(1)
    pt_max = min(hist_pt_prompt[0].GetXaxis().GetBinUpEdge(hist_pt_prompt[0].GetNbinsX()), pt_max)
    last_step = used_steps[-1]

    canv_ptratio_badcoll_prompt = ROOT.TCanvas(
        "canv_ptratio_badcoll_prompt", "", 1000, 1000)
    canv_ptratio_badcoll_prompt.Divide(2, 2)
    ipad = 1
    for step in used_steps_badcoll:
        canv_ptratio_badcoll_prompt.cd(ipad).SetLogy()
        hist_pt_ratio_prompt_badcoll[step].GetYaxis().SetRangeUser(1.e-3, 1.)
        hist_pt_ratio_prompt_badcoll[step].SetTitle(LEGNAMES[step])
        hist_pt_ratio_prompt_badcoll[step].GetYaxis().SetTitle(
            "associated to wrong collision / all")
        hist_pt_ratio_prompt_badcoll[step].DrawCopy()
        ipad += 1

    canv_ptratio_badcoll_nonprompt = ROOT.TCanvas(
        "canv_ptratio_badcoll_nonprompt", "", 1000, 1000)
    canv_ptratio_badcoll_nonprompt.Divide(2, 2)
    ipad = 1
    for step in used_steps_badcoll:
        canv_ptratio_badcoll_nonprompt.cd(ipad).SetLogy()
        hist_pt_ratio_nonprompt_badcoll[step].GetYaxis(
        ).SetRangeUser(1.e-3, 1.)
        hist_pt_ratio_nonprompt_badcoll[step].SetTitle(LEGNAMES[step])
        hist_pt_ratio_nonprompt_badcoll[step].GetYaxis().SetTitle(
            "associated to wrong collision / all")
        hist_pt_ratio_nonprompt_badcoll[step].DrawCopy()
        ipad += 1

    canv_cospdistr = ROOT.TCanvas("canv_cospdistr", "", 1000, 500)
    canv_cospdistr.Divide(2, 1)
    cosp_min = hist_cosp_prompt[0].GetXaxis().GetBinLowEdge(1)
    cosp_max = hist_cosp_prompt[0].GetXaxis().GetBinUpEdge(
        hist_cosp_prompt[0].GetNbinsX())
    canv_cospdistr.cd(1).DrawFrame(
        cosp_min,
        max(1.e-1, hist_cosp_prompt[last_step].GetMinimum() / 2),
        cosp_max,
        hist_cosp_prompt[0].GetMaximum() * 5,
        f"prompt {PARTLABELS[had]};cos(#it{{#theta}}_{{P}});counts"
    )
    canv_cospdistr.cd(1).SetLogy()
    for hist in hist_cosp_prompt.values():
        hist.DrawCopy("same")
    leg_steps_cosp.Draw()
    canv_cospdistr.cd(2).DrawFrame(
        cosp_min,
        max(1.e-1, hist_cosp_nonprompt[last_step].GetMinimum() / 2),
        cosp_max,
        hist_cosp_nonprompt[0].GetMaximum() * 5,
        f"non-prompt {PARTLABELS[had]};cos(#it{{#theta}}_{{P}});counts"
    )
    canv_cospdistr.cd(2).SetLogy()
    for hist in hist_cosp_nonprompt.values():
        hist.DrawCopy("same")

    canv_cospdistr_badcoll_prompt = ROOT.TCanvas(
        "canv_cospdistr_badcoll_prompt", "", 1000, 1000)
    canv_cospdistr_badcoll_prompt.Divide(2, 2)
    ipad = 1
    for step in used_steps_badcoll:
        canv_cospdistr_badcoll_prompt.cd(ipad).SetLogy()
        hist_cosp_prompt[step].SetTitle(LEGNAMES[step])
        hist_cosp_prompt[step].GetXaxis().SetTitle("cos(#it{#theta}_{P})")
        hist_cosp_prompt[step].DrawCopy()
        hist_cosp_prompt_badcoll[step].DrawCopy("same")
        ipad += 1
    lat.DrawLatex(0.2, 0.85, "full markers: all")
    lat.DrawLatex(0.2, 0.8, "open markers: associated to wrong collision")

    canv_cospdistr_badcoll_nonprompt = ROOT.TCanvas(
        "canv_cospdistr_badcoll_nonprompt", "", 1000, 1000)
    canv_cospdistr_badcoll_nonprompt.Divide(2, 2)
    ipad = 1
    for step in used_steps_badcoll:
        canv_cospdistr_badcoll_nonprompt.cd(ipad).SetLogy()
        hist_cosp_nonprompt[step].SetTitle(LEGNAMES[step])
        hist_cosp_nonprompt[step].GetXaxis().SetTitle("cos(#it{#theta}_{P})")
        hist_cosp_nonprompt[step].DrawCopy()
        hist_cosp_nonprompt_badcoll[step].DrawCopy("same")
        ipad += 1
    lat.DrawLatex(0.2, 0.85, "full markers: all")
    lat.DrawLatex(0.2, 0.8, "open markers: associated to wrong collision")

    canv_effpt = ROOT.TCanvas("canv_effpt", "", 1000, 500)
    canv_effpt.Divide(2, 1)
    canv_effpt.cd(1).DrawFrame(
        pt_min,
        1.e-3,
        pt_max,
        2.5,
        f"prompt {PARTLABELS[had]};#it{{p}}_{{T}} (GeV/#it{{c}});ratio to kHFStepMcInRapidity"
    )
    canv_effpt.cd(1).SetLogy()
    for hist in h_pt_eff_prompt.values():
        hist.DrawCopy("same")
    leg_steps_eff.Draw()
    canv_effpt.cd(2).DrawFrame(
        pt_min,
        1.e-3,
        pt_max,
        2.5,
        f"non-prompt {PARTLABELS[had]};#it{{p}}_{{T}} (GeV/#it{{c}});ratio to kHFStepMcInRapidity"
    )
    canv_effpt.cd(2).SetLogy()
    for hist in h_pt_eff_nonprompt.values():
        hist.DrawCopy("same")

    canv_trackedovertrackable = ROOT.TCanvas(
        "canv_trackedovertrackable", "", 1000, 500)
    canv_trackedovertrackable.Divide(2, 1)
    canv_trackedovertrackable.cd(1).DrawFrame(
        pt_min,
        0.5,
        pt_max,
        2.,
        f"prompt {PARTLABELS[had]};#it{{p}}_{{T}} (GeV/#it{{c}});kHFStepTracked / kHFStepTrackableCuts"
    )
    hist_pt_trackedovertrackable_prompt.DrawCopy("same")
    canv_trackedovertrackable.cd(2).DrawFrame(
        pt_min,
        0.5,
        pt_max,
        2.,
        f"non-prompt {PARTLABELS[had]};#it{{p}}_{{T}} (GeV/#it{{c}});kHFStepTracked / kHFStepTrackableCuts"
    )
    hist_pt_trackedovertrackable_nonprompt.DrawCopy("same")

    canv_duplicateoversel = ROOT.TCanvas(
        "canv_duplicateoversel", "", 1000, 500)
    canv_duplicateoversel.Divide(2, 1)
    canv_duplicateoversel.cd(1).DrawFrame(
        pt_min,
        1.e-3,
        pt_max,
        1.,
        f"prompt {PARTLABELS[had]};#it{{p}}_{{T}} (GeV/#it{{c}});ratio to kHFStepTrackedDuplicates / kHFStepTrackedSelected"
    )
    canv_duplicateoversel.cd(1).SetLogy()
    if hist_pt_duplicatesoversel_prompt is not None:
        hist_pt_duplicatesoversel_prompt.DrawCopy("same")
    canv_duplicateoversel.cd(2).DrawFrame(
        pt_min,
        1.e-3,
        pt_max,
        1.,
        f"non-prompt {PARTLABELS[had]};#it{{p}}_{{T}} (GeV/#it{{c}});ratio to kHFStepTrackedDuplicates / kHFStepTrackedSelected"
    )
    canv_duplicateoversel.cd(2).SetLogy()
    if hist_pt_duplicatesoversel_nonprompt is not None:
        hist_pt_duplicatesoversel_nonprompt.DrawCopy("same")

    canv_ptratio_badcoll_prompt.SaveAs(
        os.path.join(outpath, f"pt_ratio_badcoll_prompt_{had}.pdf"))
    canv_ptratio_badcoll_nonprompt.SaveAs(
        os.path.join(outpath, f"pt_ratio_badcoll_nonprompt_{had}.pdf"))
    canv_cospdistr.SaveAs(os.path.join(outpath, f"cosp_distr_{had}.pdf"))
    canv_cospdistr_badcoll_prompt.SaveAs(
        os.path.join(outpath, f"cosp_distr_badcoll_prompt_{had}.pdf"))
    canv_cospdistr_badcoll_nonprompt.SaveAs(
        os.path.join(outpath, f"cosp_distr_badcoll_nonprompt_{had}.pdf"))
    canv_effpt.SaveAs(os.path.join(outpath, f"eff_vs_pt_{had}.pdf"))
    canv_trackedovertrackable.SaveAs(
        os.path.join(outpath, f"trackedovertrackable_{had}.pdf"))
    canv_duplicateoversel.SaveAs(os.path.join(
        outpath, f"duplicateoversel_{had}.pdf"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("--infiles", "-i", nargs="+", required=True,
                        help="ROOT input files")
    parser.add_argument("--outpath", "-o", metavar="text", default=".",
                        help="output path")
    parser.add_argument("--particle", "-p", metavar="text", default="dzero",
                        help="hadron to analyse, options: [dzero, lc]")
    parser.add_argument("--iddir", "-id", metavar="text", default=None,
                        help="specific id of input directory")
    parser.add_argument("--pt_max", "-pt", type=float, default=999.,
                        help="max pt for histograms")
    args = parser.parse_args()

    check_mc_eff(args.infiles, args.outpath, args.particle, args.pt_max, args.iddir)