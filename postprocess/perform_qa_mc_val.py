"""
Script to analyse output of HFMCValidation.cxx task
"""

import os
import argparse
import numpy as np
import ROOT

# gloabal variables
particle_data = [
    ("DzeroToKPi", "D^{0} #rightarrow K#pi"),
    ("DstarToDzeroPi", "D*^{+} #rightarrow D^{0}#pi"),
    ("DplusToPiKPi", "D^{+} #rightarrow K#pi#pi"),
    ("DplusToPhiPiToKKPi", "D^{+} #rightarrow KK#pi"),
    ("DsToPhiPiToKKPi", "D_{s}^{+} #rightarrow #phi#pi #rightarrow KK#pi"),
    ("DsToK0starKToKKPi", "D_{s}^{+} #rightarrow K^{*}K #rightarrow KK#pi"),
    ("Ds1ToDStarK0s", "D_{s}1 #rightarrow D*^{+}K^{0}_{s}"),
    ("Ds2StarToDPlusK0s", "D_{s}2* #rightarrow D^{+}K^{0}_{s}"),
    ("D10ToDStarPi", "D1^{0} #rightarrow D*^{+}#pi"),
    ("D2Star0ToDPlusPi", "D2^{*} #rightarrow D^{+}#pi"),
    ("LcToPKPi", "#Lambda_{c}^{+} #rightarrow pK#pi"),
    ("LcToPiK0s", "#Lambda_{c}^{+} #rightarrow pK^{0}_{s}"),
    ("XiCplusToPKPi", "#Xi_{c}^{+} #rightarrow pK#pi"),
    ("XiCplusToXiPiPi", "#Xi_{c}^{+} #rightarrow #Xi#pi#pi"),
    ("XiCzeroToXiPi", "#Xi_{c}^{0} #rightarrow #Xi#pi"),
    ("OmegaCToOmegaPi", "#Omega_{c}^{0} #rightarrow #Omega#pi"),
    ("OmegaCToXiPi", "#Omega_{c}^{0} #rightarrow #Xi#pi"),
]
plot_full=False # plot additional info, not needed for std QA
nmesons=10 # number of meson needed to properly handle baryon histos

# Extract part names and labels from particle_data
part_names, part_labels = zip(*particle_data)

# Decay labels and baryon labels are dynamically split based on the particle type
decay_labels = part_labels[:nmesons]  # Meson decays
decay_labels_baryons = part_labels[nmesons:]  # Baryon decays
plot = [True] * len(part_names)

pt_bins = np.array([0., 1., 2., 3., 4., 5., 6., 8., 10., 12., 16., 24., 36, 50.])
cent_bins = [0., 110]

#origin_labels = ["fake", "light", "charm", "beauty"]
origin_labels = []

def compute_eff_vcent(th2gen, th2reco, centmin, centmax):
    proj_gen_p = th2gen.GetYaxis().SetRangeUser(centmin, centmax)
    proj_gen_p = th2gen.ProjectionX('gen')
    proj_reco_p = th2reco.GetYaxis().SetRangeUser(centmin, centmax)
    proj_reco_p = th2reco.ProjectionX('reco')
    proj_reco_p = proj_reco_p.Rebin(len(pt_bins)-1,
                      proj_reco_p.GetName(),
                      pt_bins)
    proj_gen_p = proj_gen_p.Rebin(len(pt_bins)-1,
                     proj_gen_p.GetName(),
                     pt_bins)

    h_eff = proj_reco_p.Clone(f"h_eff_vpt_vcent{centmin}_{centmax}")
    if proj_gen_p.GetEntries() != 0:
        h_eff.Divide(proj_reco_p, proj_gen_p, 1., 1., "B")
    else:
        h_eff.Reset()

    return h_eff

def set_style(th1, decay='prompt'):
    if decay == 'prompt':
        color = ROOT.kRed+1
        marker = ROOT.kFullSquare
    elif decay == 'fd':
        color = ROOT.kAzure+4
        marker = ROOT.kFullCircle
    else:
        color = ROOT.kBlack
        marker = ROOT.kFullCircle

    th1.SetLineColor(color)
    th1.SetMarkerColor(color)
    th1.SetLineWidth(2)
    th1.SetMarkerStyle(marker)

# pylint: disable=too-many-locals,too-many-statements, too-many-branches, no-member
def perform_qa_mc_val(infile, outpath, suffix, coll_system, coll_ass_tof, event_type, batch):
    """
    Method used to perform QA
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

    ROOT.gROOT.SetBatch(batch)

    ev_tag = ""
    if event_type == "mb":
        ev_tag = "_minimum_bias"
    if event_type == "b":
        ev_tag = "_beauty"
    if event_type == "c":
        ev_tag = "_charm"

    if coll_system == 'pp':
        cent_bins = [0, 110] # default value in pp is 105
    ncent_bins = len(cent_bins) -1

    ev_tag = ""
    outpath += ev_tag
    task_rec_name = f"hf-task-mc-validation-rec{ev_tag}"
    task_gen_name = f"hf-task-mc-validation-gen{ev_tag}"

    try:
        os.makedirs(outpath)
    except FileExistsError:
        pass

    infile = ROOT.TFile.Open(infile)
    # gen collisions
    n_events_gen = infile.Get(f"{task_gen_name}/hNevGen").GetEntries()
    # reco collisions
    n_events = infile.Get(f"{task_rec_name}/histXvtxReco").GetEntries()
    # protection against no selected events
    if n_events == 0:
        n_events = 1

    # generated distributions
    h_pt_gen_prompt_meson_vshad = infile.Get(
        f"{task_gen_name}/PromptCharmMesons/hPromptMesonsPtDistr")
    h_pt_gen_nonprompt_meson_vshad = infile.Get(
        f"{task_gen_name}/NonPromptCharmMesons/hNonPromptMesonsPtDistr")
    h_pt_vcent_gen_prompt_meson_vshad = infile.Get(
        f"{task_gen_name}/PromptCharmMesons/hPromptMesonsPtCentDistr")
    h_pt_vcent_gen_nonprompt_meson_vshad = infile.Get(
        f"{task_gen_name}/NonPromptCharmMesons/hNonPromptMesonsPtCentDistr")
    h_y_gen_prompt_meson_vshad = infile.Get(
        f"{task_gen_name}/PromptCharmMesons/hPromptMesonsYDistr")
    h_y_gen_nonprompt_meson_vshad = infile.Get(
        f"{task_gen_name}/NonPromptCharmMesons/hNonPromptMesonsYDistr")
    h_declen_gen_prompt_meson_vshad = infile.Get(
        f"{task_gen_name}/PromptCharmMesons/hPromptMesonsDecLenDistr")
    h_declen_gen_nonprompt_meson_vshad = infile.Get(
        f"{task_gen_name}/NonPromptCharmMesons/hNonPromptMesonsDecLenDistr")
    h_pt_gen_prompt_baryon_vshad = infile.Get(
        f"{task_gen_name}/PromptCharmBaryons/hPromptBaryonsPtDistr")
    h_pt_gen_nonprompt_baryon_vshad = infile.Get(
        f"{task_gen_name}/NonPromptCharmBaryons/hNonPromptBaryonsPtDistr")
    h_pt_vcent_gen_prompt_baryon_vshad = infile.Get(
        f"{task_gen_name}/PromptCharmBaryons/hPromptBaryonsPtCentDistr")
    h_pt_vcent_gen_nonprompt_baryon_vshad = infile.Get(
        f"{task_gen_name}/NonPromptCharmBaryons/hNonPromptBaryonsPtCentDistr")
    h_y_gen_prompt_baryon_vshad = infile.Get(
        f"{task_gen_name}/PromptCharmBaryons/hPromptBaryonsYDistr")
    h_y_gen_nonprompt_baryon_vshad = infile.Get(
        f"{task_gen_name}/NonPromptCharmBaryons/hNonPromptBaryonsYDistr")
    h_declen_gen_prompt_baryon_vshad = infile.Get(
        f"{task_gen_name}/PromptCharmBaryons/hPromptBaryonsDecLenDistr")
    h_declen_gen_nonprompt_baryon_vshad = infile.Get(
        f"{task_gen_name}/NonPromptCharmBaryons/hNonPromptBaryonsDecLenDistr")
    h_pt_gen_prompt_meson_vshad.SetDirectory(0)
    h_pt_gen_nonprompt_meson_vshad.SetDirectory(0)
    h_pt_vcent_gen_prompt_meson_vshad.SetDirectory(0)
    h_pt_vcent_gen_nonprompt_meson_vshad.SetDirectory(0)
    h_y_gen_prompt_meson_vshad.SetDirectory(0)
    h_y_gen_nonprompt_meson_vshad.SetDirectory(0)
    h_declen_gen_prompt_meson_vshad.SetDirectory(0)
    h_declen_gen_nonprompt_meson_vshad.SetDirectory(0)
    h_pt_gen_prompt_baryon_vshad.SetDirectory(0)
    h_pt_gen_nonprompt_baryon_vshad.SetDirectory(0)
    h_pt_vcent_gen_prompt_baryon_vshad.SetDirectory(0)
    h_pt_vcent_gen_nonprompt_baryon_vshad.SetDirectory(0)
    h_y_gen_prompt_baryon_vshad.SetDirectory(0)
    h_y_gen_nonprompt_baryon_vshad.SetDirectory(0)
    h_declen_gen_prompt_baryon_vshad.SetDirectory(0)
    h_declen_gen_nonprompt_baryon_vshad.SetDirectory(0)

    h_abundances_promptmeson = h_pt_gen_prompt_meson_vshad.ProjectionX("h_abundances_promptmeson")
    h_abundances_nonpromptmeson = h_pt_gen_nonprompt_meson_vshad.ProjectionX("h_abundances_nonpromptmeson")
    h_abundances_promptmeson = h_pt_gen_prompt_meson_vshad.ProjectionX("h_abundances_promptmeson")
    h_abundances_nonpromptmeson = h_pt_gen_nonprompt_meson_vshad.ProjectionX("h_abundances_nonpromptmeson")
    # TODO remove hPromptMesonsPtDistr
    h_abundances_promptbaryon = h_pt_gen_prompt_baryon_vshad.ProjectionX("h_abundances_promptbaryon")
    h_abundances_nonpromptbaryon = h_pt_gen_nonprompt_baryon_vshad.ProjectionX("h_abundances_nonpromptbaryon")
    h_abundances_promptmeson.Scale(1./n_events)
    h_abundances_nonpromptmeson.Scale(1./n_events)
    h_abundances_promptbaryon.Scale(1./n_events)
    h_abundances_nonpromptbaryon.Scale(1./n_events)

    # mesons
    canv_abundances = ROOT.TCanvas("canv_abundances", "", 600, 600)
    leg_abundances = ROOT.TLegend(0.5, 0.7, 0.8, 0.9)
    leg_abundances.SetTextSize(0.045)
    leg_abundances.SetFillStyle(0)
    leg_abundances.SetBorderSize(0)
    leg_abundances.AddEntry(h_abundances_promptmeson, "prompt", "l")
    leg_abundances.AddEntry(h_abundances_nonpromptmeson, "non-prompt", "l")
    canv_abundances.SetLogy()
    canv_abundances.SetRightMargin(0.1)
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.04)
    h_abundances_promptmeson.GetYaxis().SetRangeUser(1.e-8, 1.e2)
    for ipart, part_label in enumerate(decay_labels):
        h_abundances_promptmeson.GetXaxis().SetBinLabel(ipart+1, part_label)
    h_abundances_promptmeson.GetYaxis().SetDecimals()
    h_abundances_promptmeson.GetXaxis().SetLabelSize(0.04)
    h_abundances_promptmeson.GetYaxis().SetTitle("Generated particles per collision")
    h_abundances_promptmeson.SetLineColor(ROOT.kRed+1)
    h_abundances_promptmeson.SetLineWidth(2)
    h_abundances_nonpromptmeson.GetYaxis().SetTitle("Generated particles per collision")
    h_abundances_nonpromptmeson.SetLineColor(ROOT.kAzure+4)
    h_abundances_nonpromptmeson.SetLineWidth(2)
    h_abundances_promptmeson.Draw("hist")
    h_abundances_nonpromptmeson.Draw("histsame")
    leg_abundances.Draw()
    canv_abundances.Modified()
    canv_abundances.Update()
    canv_abundances.SaveAs(os.path.join(
        outpath, f"particle_abundances_mesons{suffix}.pdf"))

    # baryons
    canv_abundances_baryons = ROOT.TCanvas("canv_abundances_baryons", "", 600, 600)
    leg_abundances_baryons = ROOT.TLegend(0.5, 0.7, 0.8, 0.9)
    leg_abundances_baryons.SetTextSize(0.045)
    leg_abundances_baryons.SetFillStyle(0)
    leg_abundances_baryons.SetBorderSize(0)
    leg_abundances_baryons.AddEntry(h_abundances_promptbaryon, "prompt", "l")
    leg_abundances_baryons.AddEntry(h_abundances_nonpromptbaryon, "non-prompt", "l")
    canv_abundances_baryons.SetLogy()
    canv_abundances_baryons.SetRightMargin(0.1)
    h_abundances_promptbaryon.GetYaxis().SetRangeUser(1.e-5, 1.e2)
    for ipart, part_label in enumerate(decay_labels_baryons):
        h_abundances_promptbaryon.GetXaxis().SetBinLabel(ipart+1, part_label)
    h_abundances_promptbaryon.GetYaxis().SetDecimals()
    h_abundances_promptbaryon.GetXaxis().SetLabelSize(0.05)
    h_abundances_promptbaryon.GetYaxis().SetTitle("Generated particles per collision")
    h_abundances_promptbaryon.SetLineColor(ROOT.kRed+1)
    h_abundances_promptbaryon.SetLineWidth(2)
    h_abundances_promptbaryon.Draw("hist")
    h_abundances_nonpromptbaryon.SetLineColor(ROOT.kAzure+4)
    h_abundances_nonpromptbaryon.SetLineWidth(2)
    h_abundances_nonpromptbaryon.Draw("histsame")
    leg_abundances_baryons.Draw()
    canv_abundances_baryons.Modified()
    canv_abundances_baryons.Update()
    canv_abundances_baryons.SaveAs(os.path.join(
        outpath, f"particle_abundances_baryons{suffix}.pdf"))


    # efficiencies mesons
    h_pt_reco_prompt, h_pt_reco_nonprompt = {}, {}
    h_pt_vcent_reco_prompt, h_pt_vcent_reco_nonprompt = {}, {}
    h_pt_gen_prompt, h_pt_gen_nonprompt = [], []
    h_pt_vcent_gen_prompt, h_pt_vcent_gen_nonprompt = {}, {}
    h_y_gen_prompt, h_y_gen_nonprompt = [], []
    h_declen_gen_prompt, h_declen_gen_nonprompt = [], []
    h_eff_prompt, h_eff_nonprompt, h_eff_ratio = [], [], []

    leg = ROOT.TLegend(0.6, 0.3, 0.9, 0.4)
    leg.SetTextSize(0.045)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)

    # loop over particle species
    for ipart, (part_name, part_label) in enumerate(zip(part_names, part_labels)):
        if ipart < nmesons:
            h_pt_gen_p_hadron = h_pt_gen_prompt_meson_vshad
            h_pt_gen_np_hadron = h_pt_gen_nonprompt_meson_vshad
            h_pt_vcent_gen_p_hadron = h_pt_vcent_gen_prompt_meson_vshad
            h_pt_vcent_gen_np_hadron = h_pt_vcent_gen_nonprompt_meson_vshad
            h_y_gen_p_hadron = h_y_gen_prompt_meson_vshad
            h_y_gen_np_hadron = h_y_gen_nonprompt_meson_vshad
            h_dl_gen_p_hadron = h_declen_gen_prompt_meson_vshad
            h_dl_gen_np_hadron = h_declen_gen_nonprompt_meson_vshad
            iproj = ipart + 1
        else:
            h_pt_gen_p_hadron = h_pt_gen_prompt_baryon_vshad
            h_pt_gen_np_hadron = h_pt_gen_nonprompt_baryon_vshad
            h_pt_vcent_gen_p_hadron = h_pt_vcent_gen_prompt_baryon_vshad
            h_pt_vcent_gen_np_hadron = h_pt_vcent_gen_nonprompt_baryon_vshad
            h_y_gen_p_hadron = h_y_gen_prompt_baryon_vshad
            h_y_gen_np_hadron = h_y_gen_nonprompt_baryon_vshad
            h_dl_gen_p_hadron = h_declen_gen_prompt_baryon_vshad
            h_dl_gen_np_hadron = h_declen_gen_nonprompt_baryon_vshad
            iproj = ipart + 1 - nmesons

        h_pt_gen_prompt.append(h_pt_gen_p_hadron.ProjectionY(
            f"h_pt_gen_prompt{part_name}", iproj, iproj))
        h_pt_gen_nonprompt.append(h_pt_gen_np_hadron.ProjectionY(
            f"h_pt_gen_nonprompt{part_name}", iproj, iproj))
        h_pt_gen_prompt[ipart].Sumw2()
        h_pt_gen_nonprompt[ipart].Sumw2()

        h_pt_vcent_gen_prompt[part_name] = []
        h_pt_vcent_gen_nonprompt[part_name] = []

        h_pt_vcent_gen_p_hadron.GetXaxis().SetRangeUser(iproj-1, iproj-1)
        h_pt_vcent_gen_np_hadron.GetXaxis().SetRangeUser(iproj-1, iproj-1)

        h_pt_vcent_gen_prompt[part_name] = h_pt_vcent_gen_p_hadron.Project3D('zy')
        h_pt_vcent_gen_nonprompt[part_name] = h_pt_vcent_gen_np_hadron.Project3D('zy')

        h_pt_vcent_gen_prompt[part_name].SetName(f"h_pt_vcent_gen_prompt{part_name}")
        h_pt_vcent_gen_nonprompt[part_name].SetName(f"h_pt_vcent_gen_nonprompt{part_name}")

        h_pt_vcent_gen_prompt[part_name].Sumw2()
        h_pt_vcent_gen_nonprompt[part_name].Sumw2()

        h_y_gen_prompt.append(h_y_gen_p_hadron.ProjectionY(
            f"h_y_gen_prompt{part_name}", iproj, iproj))
        h_y_gen_nonprompt.append(h_y_gen_np_hadron.ProjectionY(
            f"h_y_gen_nonprompt{part_name}", iproj, iproj))
        h_y_gen_prompt[ipart].Sumw2()
        h_y_gen_nonprompt[ipart].Sumw2()

        h_declen_gen_prompt.append(h_dl_gen_p_hadron.ProjectionY(
            f"h_declenen_gen_prompt{part_name}", iproj, iproj))
        h_declen_gen_nonprompt.append(h_dl_gen_np_hadron.ProjectionY(
            f"h_declenen_gen_nonprompt{part_name}", iproj, iproj))
        h_declen_gen_prompt[ipart].Sumw2()
        h_declen_gen_nonprompt[ipart].Sumw2()

        set_style(h_pt_gen_prompt[ipart])
        set_style(h_pt_gen_nonprompt[ipart], 'fd')

        set_style(h_y_gen_prompt[ipart])
        set_style(h_y_gen_nonprompt[ipart], 'fd')

        set_style(h_declen_gen_prompt[ipart])
        set_style(h_declen_gen_nonprompt[ipart], 'fd')

        if ipart == 0:
            leg.AddEntry(h_pt_gen_prompt[ipart], "prompt", "p")
            leg.AddEntry(h_pt_gen_nonprompt[ipart], "non-prompt", "p")

        canv_pt = ROOT.TCanvas(f"canv_pt{part_name}", "", 500, 500)
        canv_pt.Divide(3, 2)
        canv_pt.cd().DrawFrame(0.,
                               1.,
                               pt_bins[-1],
                               max(h_pt_gen_prompt[ipart].GetMaximum(
                               ), h_pt_gen_nonprompt[ipart].GetMaximum()) * 5,
                               f";{part_label} #it{{p}}_{{T}} (GeV/#it{{c}});"
                               "entries")
        canv_pt.cd().SetLogy()
        h_pt_gen_prompt[ipart].Draw("same")
        h_pt_gen_nonprompt[ipart].Draw("same")
        leg.Draw()
        canv_pt.Modified()
        canv_pt.Update()
        if plot_full: canv_pt.SaveAs(os.path.join(outpath, f"{part_name}_ptgen_distr{suffix}.pdf"))

        canv_y = ROOT.TCanvas(f"canv_y{part_name}", "", 500, 500)
        canv_y.Divide(3, 2)
        canv_y.cd().DrawFrame(-1.5,
                              1.,
                              1.5,
                              max(h_y_gen_prompt[ipart].GetMaximum(
                              ), h_y_gen_nonprompt[ipart].GetMaximum()) * 5,
                              f";{part_label} #it{{y}};"
                              "entries")
        canv_y.cd().SetLogy()
        h_y_gen_prompt[ipart].Draw("same")
        h_y_gen_nonprompt[ipart].Draw("same")
        leg.Draw()
        canv_y.Modified()
        canv_y.Update()
        if plot_full: canv_y.SaveAs(os.path.join(outpath, f"{part_name}_ygen_distr{suffix}.pdf"))

        canv_declen = ROOT.TCanvas(f"canv_declen{part_name}", "", 500, 500)
        canv_declen.Divide(3, 2)
        if h_declen_gen_prompt[ipart].GetMaximum() > h_declen_gen_nonprompt[ipart].GetMaximum():
            max_height = h_declen_gen_prompt[ipart].GetMaximum() * 5
        else:
            max_height = h_declen_gen_nonprompt[ipart].GetMaximum() * 5
        frame = canv_declen.cd().DrawFrame(0., 1., 1.e4, max_height,
                                           f";{part_label} decay length (#mum);"
                                           "entries")
        frame.GetXaxis().SetNdivisions(505)
        canv_declen.cd().SetLogy()
        h_declen_gen_prompt[ipart].Draw("same")
        h_declen_gen_nonprompt[ipart].Draw("same")
        leg.Draw()
        canv_declen.Modified()
        canv_declen.Update()
        if plot_full:  canv_declen.SaveAs(os.path.join(outpath, f"{part_name}_declengen_distr{suffix}.pdf"))

        h_pt_gen_prompt[ipart] = h_pt_gen_prompt[ipart].Rebin(
            len(pt_bins)-1,
            h_pt_gen_prompt[ipart].GetName(),
            pt_bins
        )
        h_pt_gen_nonprompt[ipart] = h_pt_gen_nonprompt[ipart].Rebin(
            len(pt_bins)-1,
            h_pt_gen_nonprompt[ipart].GetName(),
            pt_bins
        )

        print(" ")
        print(f"Processing {part_name}")
        h_pt_vcent_reco_prompt[part_name] = infile.Get(f"{task_rec_name}/{part_name}/histPtCentRecoPrompt")
        h_pt_vcent_reco_nonprompt[part_name] = infile.Get(f"{task_rec_name}/{part_name}/histPtCentRecoNonPrompt")
        h_eff_prompt.append([])
        h_eff_nonprompt.append([])
        h_eff_ratio.append([])

        # in PbPb, efficiency vs centrality
        if coll_system == 'PbPb':
            # First entry 0-100% centrality
            h_eff_prompt[ipart].append(compute_eff_vcent(h_pt_vcent_gen_prompt[part_name],
                                                  h_pt_vcent_reco_prompt[part_name],
                                                  0, 100))
            h_eff_nonprompt[ipart].append(compute_eff_vcent(h_pt_vcent_gen_nonprompt[part_name],
                                                     h_pt_vcent_reco_nonprompt[part_name],
                                                     0, 100))
            h_eff_prompt[ipart][-1].SetName(f"h_eff_prompt{part_name}vcent0_100")
            h_eff_nonprompt[ipart][-1].SetName(f"h_eff_nonprompt{part_name}vcent0_100")
            h_eff_ratio[ipart].append(h_eff_nonprompt[ipart][-1].Clone(f"h_eff_ratio{part_name}vcent0_100"))
            if h_eff_prompt[ipart][-1].GetEntries() != 0:
                h_eff_ratio[ipart][-1].Divide(h_eff_prompt[ipart][-1])
            h_eff_ratio[ipart][-1].SetTitle(";#it{p}_{T} (GeV/#it{c});non-prompt / prompt")

            set_style(h_eff_prompt[ipart][-1])
            set_style(h_eff_nonprompt[ipart][-1], 'fd')
            set_style(h_eff_ratio[ipart][-1], '')

            for _, (cent_min, cent_max) in enumerate(zip(cent_bins[:-1], cent_bins[1:])):
                h_eff_prompt[ipart].append(compute_eff_vcent(h_pt_vcent_gen_prompt[part_name],
                                                      h_pt_vcent_reco_prompt[part_name],
                                                      cent_min, cent_max))
                h_eff_nonprompt[ipart].append(compute_eff_vcent(h_pt_vcent_gen_nonprompt[part_name],
                                                      h_pt_vcent_reco_nonprompt[part_name],
                                                      cent_min, cent_max))
                h_eff_prompt[ipart][-1].SetName(f"h_eff_prompt{part_name}vcent{cent_min}_{cent_max}")
                h_eff_nonprompt[ipart][-1].SetName(f"h_eff_nonprompt{part_name}vcent{cent_min}_{cent_max}")
                h_eff_ratio[ipart].append(h_eff_nonprompt[ipart][-1].Clone(f"h_eff_ratio{part_name}vcent{cent_min}_{cent_max}"))
                if h_eff_prompt[ipart][-1].GetEntries() != 0:
                    h_eff_ratio[ipart][-1].Divide(h_eff_prompt[ipart][-1])
                h_eff_ratio[ipart][-1].SetTitle(";#it{p}_{T} (GeV/#it{c});non-prompt / prompt")

                set_style(h_eff_prompt[ipart][-1])
                set_style(h_eff_nonprompt[ipart][-1], 'fd')
                set_style(h_eff_ratio[ipart][-1], '')
        # pp
        else:
            h_eff_prompt[ipart].append(compute_eff_vcent(h_pt_vcent_gen_prompt[part_name],
                                                  h_pt_vcent_reco_prompt[part_name],
                                                  0, 110))
            h_eff_nonprompt[ipart].append(compute_eff_vcent(h_pt_vcent_gen_nonprompt[part_name],
                                                     h_pt_vcent_reco_nonprompt[part_name],
                                                     0, 110))
            h_eff_prompt[ipart][-1].SetName(f"h_eff_prompt{part_name}vcent0_110")
            h_eff_nonprompt[ipart][-1].SetName(f"h_eff_nonprompt{part_name}vcent0_110")
            h_eff_ratio[ipart].append(h_eff_nonprompt[ipart][-1].Clone(f"h_eff_ratio{part_name}vcent0_110"))
            if h_eff_prompt[ipart][-1].GetEntries() != 0:
                h_eff_ratio[ipart][-1].Divide(h_eff_prompt[ipart][-1])
            h_eff_ratio[ipart][-1].SetTitle(";#it{p}_{T} (GeV/#it{c});non-prompt / prompt")

            set_style(h_eff_prompt[ipart][-1])
            set_style(h_eff_nonprompt[ipart][-1], 'fd')
            set_style(h_eff_ratio[ipart][-1], '')

        if plot[ipart]:
            for ihisto, (heff_p, heff_np, heff_ratio) in enumerate(zip(h_eff_prompt[ipart],
                                                                       h_eff_nonprompt[ipart],
                                                                       h_eff_ratio[ipart])):

                if (heff_p.GetEntries() == 0 or heff_np.GetEntries() == 0):
                    continue

                if ihisto == 0:
                    cent_min = 0
                    cent_max = 100
                else:
                    cent_min = cent_bins[ihisto-1]
                    cent_max = cent_bins[ihisto]
                cent_label = f'_vcent{cent_min}_{cent_max}'

                canv = ROOT.TCanvas(f"c{part_name}{cent_label}", "", 500, 500)
                canv.cd().SetGridy()
                canv.cd().SetGridx()
                canv.cd().DrawFrame(1.e-10,
                                    max(min(heff_p.GetMinimum(), heff_np.GetMinimum()), 1.e-5) * 0.5,
                                    pt_bins[-1],
                                    1.5,
                                    "Centrality interval ;#it{p}_{T} (GeV/#it{c});"
                                    f"{part_label} efficiency #times acceptance")
                canv.cd().SetLogy()
                heff_p.Draw("same")
                heff_np.Draw("same")
                leg.Draw()
                if coll_system == 'PbPb': latex.DrawLatex(0.2, 0.2, f'Centrality {cent_min} - {cent_max}')
                canv.Modified()
                canv.Update()
                
                canv.SaveAs(os.path.join(outpath, f"{part_name}_efficiency{cent_label}{suffix}.pdf"))
                canv_ratio = ROOT.TCanvas(f"cratio{part_name}", "", 500, 500)
                canv_ratio.Divide(3, 2)
                canv_ratio.cd().DrawFrame(0., 0.5, pt_bins[-1], 1.5,
                                          ";#it{p}_{T} (GeV/#it{c});"
                                          f"{part_label} non-prompt / prompt")
                heff_ratio.Draw("same")
                if coll_system == 'PbPb': latex.DrawLatex(0.2, 0.2, f'Centrality {cent_min} - {cent_max}')
                canv_ratio.Modified()
                canv_ratio.Update()
                if plot_full: canv_ratio.SaveAs(os.path.join(outpath, f"{part_name}_efficiency_ratio{cent_label}{suffix}.pdf"))

    h_ass, h_nonass, h_assgood, h_assgood_amb, \
        h_eff_ass, h_eff_assgood, h_eff_assgood_wamb = (
            [] for _ in range(7))
    h_ass_eta, h_nonass_eta, h_assgood_eta, h_assgood_amb_eta, \
        h_eff_ass_eta, h_eff_assgood_eta, h_eff_assgood_wamb_eta = (
            [] for _ in range(7))
    h_zvtx_goodass = []

    track_to_coll_path = 'TrackToCollChecks'
    h_coll_asso = infile.Get(f"{task_rec_name}/{track_to_coll_path}/histOriginAssociatedTracks")
    h_coll_not_asso = infile.Get(f"{task_rec_name}/{track_to_coll_path}/histOriginNonAssociatedTracks")
    h_coll_assogood = infile.Get(f"{task_rec_name}/{track_to_coll_path}/histOriginGoodAssociatedTracks")
    h_coll_assogood_ambiguous = infile.Get(f"{task_rec_name}/{track_to_coll_path}/histOriginGoodAssociatedTracksAmbiguous")

    canv_coll_association = ROOT.TCanvas(
        "canv_coll_association", "", 500, 500)
    canv_coll_association.DrawFrame(
        0., 1.e-5, 10., 1.,
        ";#it{p}_{T} (GeV/#it{c}); tracks w/o collision / tracks w/ collision")

    canv_coll_association_good = ROOT.TCanvas(
        "canv_coll_association_good", "", 500, 500)
    canv_coll_association_good.DrawFrame(
        0., 0., 10., 1.2,
        ";#it{p}_{T} (GeV/#it{c}); tracks w/ correct collision / tracks w/ collision")

    canv_coll_association_eta = ROOT.TCanvas(
        "canv_coll_association_eta", "", 500, 500)
    canv_coll_association_eta.DrawFrame(
        -1., 1.e-5, 1., 1.,
        ";#it{#eta}; tracks w/o collision / tracks w/ collision")

    canv_coll_association_good_eta = ROOT.TCanvas(
        "canv_coll_association_good_eta", "", 500, 500)
    canv_coll_association_good_eta.DrawFrame(
        -1., 0., 1., 1.2,
        ";#it{#eta}; tracks w/ correct collision / tracks w/ collision")

    canv_zvtx = ROOT.TCanvas("canv_zvtx", "canv_zvtx", 600, 600)
    canv_zvtx.SetLogy()

    leg_orig = ROOT.TLegend(0.2, 0.7, 0.4, 0.95)
    leg_orig.SetTextSize(0.045)
    leg_orig.SetFillStyle(0)
    leg_orig.SetBorderSize(0)

    leg_orig_wofake = ROOT.TLegend(0.2, 0.3, 0.4, 0.5)
    leg_orig_wofake.SetTextSize(0.045)
    leg_orig_wofake.SetFillStyle(0)
    leg_orig_wofake.SetBorderSize(0)

    lat = ROOT.TLatex()
    lat.SetTextSize(0.04)
    lat.SetTextFont(42)
    lat.SetTextColor(ROOT.kBlack)
    lat.SetNDC()

    delta_zvtx_max = 10.

    colors = [ROOT.kGray+1, ROOT.kGreen+2, ROOT.kRed+1, ROOT.kAzure+4]
    for iorigin, origin_label in enumerate(origin_labels):
        bin_zvtx_min = h_coll_assogood.GetAxis(
            3).FindBin(-delta_zvtx_max*0.999)
        bin_zvtx_max = h_coll_assogood.GetAxis(
            3).FindBin(delta_zvtx_max*0.999)
        h_coll_asso.GetAxis(0).SetRange(iorigin+1, iorigin+1)
        h_coll_not_asso.GetAxis(0).SetRange(iorigin+1, iorigin+1)
        h_coll_assogood.GetAxis(0).SetRange(iorigin+1, iorigin+1)
        h_coll_assogood_ambiguous.GetAxis(0).SetRange(iorigin+1, iorigin+1)
        if coll_ass_tof:
            h_coll_asso.GetAxis(5).SetRange(2, 2)
            h_coll_not_asso.GetAxis(5).SetRange(2, 2)
            h_coll_assogood.GetAxis(5).SetRange(2, 2)
            h_coll_assogood_ambiguous.GetAxis(5).SetRange(2, 2)
        h_coll_assogood.GetAxis(3).SetRange(bin_zvtx_min, bin_zvtx_max)
        h_ass.append(h_coll_asso.Projection(1))
        h_nonass.append(h_coll_not_asso.Projection(1))
        h_assgood.append(h_coll_assogood.Projection(1))
        h_assgood_amb.append(h_coll_assogood_ambiguous.Projection(1))
        h_nonass[iorigin].Sumw2()
        h_ass[iorigin].Sumw2()
        h_assgood[iorigin].Sumw2()
        h_assgood_amb[iorigin].Sumw2()
        h_assgood_amb[iorigin].Add(h_assgood[iorigin])
        h_nonass[iorigin].SetName(f"h_nonass_{origin_label}")
        h_ass[iorigin].SetName(f"h_ass_{origin_label}")
        h_assgood[iorigin].SetName(f"h_assgood_{origin_label}")
        h_assgood_amb[iorigin].SetName(f"h_assgood_amb_{origin_label}")
        h_nonass[iorigin].SetLineColor(colors[iorigin])
        h_ass[iorigin].SetLineColor(colors[iorigin])
        h_assgood[iorigin].SetLineColor(colors[iorigin])
        h_assgood_amb[iorigin].SetLineColor(colors[iorigin])
        h_nonass[iorigin].SetMarkerColor(colors[iorigin])
        h_ass[iorigin].SetMarkerColor(colors[iorigin])
        h_assgood[iorigin].SetMarkerColor(colors[iorigin])
        h_assgood_amb[iorigin].SetMarkerColor(colors[iorigin])
        h_nonass[iorigin].SetMarkerStyle(ROOT.kFullCircle)
        h_ass[iorigin].SetMarkerStyle(ROOT.kFullCircle)
        h_assgood[iorigin].SetMarkerStyle(ROOT.kFullCircle)
        h_assgood_amb[iorigin].SetMarkerStyle(ROOT.kOpenCircle)
        h_nonass[iorigin].SetLineWidth(2)
        h_ass[iorigin].SetLineWidth(2)
        h_assgood[iorigin].SetLineWidth(2)
        h_assgood_amb[iorigin].SetLineWidth(2)
        h_eff_ass.append(h_nonass[iorigin].Clone(
            f"h_eff_ass_{origin_label}"))
        h_eff_ass[iorigin].Divide(
            h_nonass[iorigin], h_ass[iorigin], 1., 1.)
        h_eff_assgood.append(h_assgood[iorigin].Clone(
            f"h_eff_assgood_{origin_label}"))
        h_eff_assgood[iorigin].Divide(
            h_assgood[iorigin], h_ass[iorigin], 1., 1., "B")
        h_eff_assgood_wamb.append(h_assgood_amb[iorigin].Clone(
            f"h_eff_assgood_wamb_{origin_label}"))
        h_eff_assgood_wamb[iorigin].Divide(
            h_assgood_amb[iorigin], h_ass[iorigin], 1., 1., "B")

        canv_coll_association.cd().SetLogy()
        h_eff_ass[iorigin].Draw("esame")
        leg_orig.AddEntry(h_eff_ass[iorigin], origin_label, "pl")

        canv_coll_association_good.cd()
        h_eff_assgood[iorigin].Draw("esame")
        h_eff_assgood_wamb[iorigin].Draw("esame")
        if iorigin != 0:
            leg_orig_wofake.AddEntry(h_eff_ass[iorigin], origin_label, "pl")

        h_ass_eta.append(h_coll_asso.Projection(2))
        h_nonass_eta.append(h_coll_not_asso.Projection(2))
        h_assgood_eta.append(h_coll_assogood.Projection(2))
        h_assgood_amb_eta.append(h_coll_assogood_ambiguous.Projection(2))
        h_nonass_eta[iorigin].Sumw2()
        h_ass_eta[iorigin].Sumw2()
        h_assgood_eta[iorigin].Sumw2()
        h_assgood_amb_eta[iorigin].Sumw2()
        h_assgood_amb_eta[iorigin].Add(h_assgood_eta[iorigin])
        h_nonass_eta[iorigin].SetName(f"h_nonass_eta_{origin_label}")
        h_ass_eta[iorigin].SetName(f"h_ass_eta_{origin_label}")
        h_assgood_eta[iorigin].SetName(f"h_assgood_eta_{origin_label}")
        h_assgood_amb_eta[iorigin].SetName(
            f"h_assgood_amb_eta_{origin_label}")
        h_nonass_eta[iorigin].SetLineColor(colors[iorigin])
        h_ass_eta[iorigin].SetLineColor(colors[iorigin])
        h_assgood_eta[iorigin].SetLineColor(colors[iorigin])
        h_assgood_amb_eta[iorigin].SetLineColor(colors[iorigin])
        h_nonass_eta[iorigin].SetMarkerColor(colors[iorigin])
        h_ass_eta[iorigin].SetMarkerColor(colors[iorigin])
        h_assgood_eta[iorigin].SetMarkerColor(colors[iorigin])
        h_assgood_amb_eta[iorigin].SetMarkerColor(colors[iorigin])
        h_nonass_eta[iorigin].SetMarkerStyle(ROOT.kFullCircle)
        h_ass_eta[iorigin].SetMarkerStyle(ROOT.kFullCircle)
        h_assgood_eta[iorigin].SetMarkerStyle(ROOT.kFullCircle)
        h_assgood_amb_eta[iorigin].SetMarkerStyle(ROOT.kOpenCircle)
        h_nonass_eta[iorigin].SetLineWidth(2)
        h_ass_eta[iorigin].SetLineWidth(2)
        h_assgood_eta[iorigin].SetLineWidth(2)
        h_assgood_amb_eta[iorigin].SetLineWidth(2)
        h_eff_ass_eta.append(h_nonass_eta[iorigin].Clone(
            f"h_eff_ass_eta_{origin_label}"))
        h_eff_ass_eta[iorigin].Divide(
            h_nonass_eta[iorigin], h_ass_eta[iorigin], 1., 1.)
        h_eff_assgood_eta.append(h_assgood_eta[iorigin].Clone(
            f"h_eff_assgood_eta_{origin_label}"))
        h_eff_assgood_eta[iorigin].Divide(
            h_assgood_eta[iorigin], h_ass_eta[iorigin], 1., 1., "B")
        h_eff_assgood_wamb_eta.append(h_assgood_amb_eta[iorigin].Clone(
            f"h_eff_assgood_eta_{origin_label}"))
        h_eff_assgood_wamb_eta[iorigin].Divide(
            h_assgood_amb_eta[iorigin], h_ass_eta[iorigin], 1., 1., "B")

        canv_coll_association_eta.cd().SetLogy()
        h_eff_ass_eta[iorigin].Draw("esame")

        canv_coll_association_good_eta.cd()
        h_eff_assgood_eta[iorigin].Draw("esame")
        h_eff_assgood_wamb_eta[iorigin].Draw("esame")

        h_zvtx_goodass.append(h_coll_assogood.Projection(3))

        canv_zvtx.cd()
        h_zvtx_goodass[iorigin].SetNameTitle(
            f"h_zvtx_goodass_{origin_label}",
            ";#it{Z}_{vtx}^{ reco} - #it{Z}_{vtx}^{ gen} (cm);entries"
        )
        h_zvtx_goodass[iorigin].SetLineWidth(2)
        h_zvtx_goodass[iorigin].SetLineColor(colors[iorigin])
        h_zvtx_goodass[iorigin].SetNdivisions(505)
        if iorigin > 0:
            drawopt = "hist"
            if iorigin > 1:
                drawopt = "histsame"
            h_zvtx_goodass[iorigin].Draw(drawopt)

    canv_coll_association.cd()
    leg_orig.Draw()
    if plot_full: canv_coll_association.SaveAs(os.path.join(outpath, f"collision_association_efficiency{suffix}.pdf"))

    canv_coll_association_good.cd()
    leg_orig_wofake.Draw()
    lat.DrawLatex(0.2, 0.25, "Full markers: only main collision")
    lat.DrawLatex(0.2, 0.2, "Open markers: all compatible collisions")
    if plot_full: canv_coll_association_good.SaveAs(os.path.join(outpath, f"collision_good_association_efficiency{suffix}.pdf"))

    canv_coll_association_eta.cd()
    leg_orig.Draw()
    if plot_full: canv_coll_association_eta.SaveAs(os.path.join(outpath, f"collision_association_efficiency_vseta{suffix}.pdf"))

    canv_coll_association_good_eta.cd()
    leg_orig_wofake.Draw()
    lat.DrawLatex(0.2, 0.25, "Full markers: only main collision")
    lat.DrawLatex(0.2, 0.2, "Open markers: all compatible collisions")
    if plot_full: canv_coll_association_good_eta.SaveAs(os.path.join(outpath, f"collision_good_association_efficiency_vseta{suffix}.pdf"))

    canv_zvtx.cd()
    leg_orig_wofake.SetY1(0.7)
    leg_orig_wofake.SetY2(0.9)
    leg_orig_wofake.Draw()
    if plot_full: canv_zvtx.SaveAs(os.path.join(outpath, f"Zvtx_residual_matchedcoll{suffix}.pdf"))

    # ambiguous tracks
    canv_fracanv_amb = ROOT.TCanvas("canv_fracanv_amb", "", 800, 800)
    canv_fracanv_amb.DrawFrame(
        0., 0., 10., 1., ";#it{p}_{T} (GeV/#it{c});fraction of ambiguous tracks")
    h_tr_per_origin, h_ambtr_per_origin, h_fracanv_amb_per_origin = [], [], []
    h_tr = infile.Get(f"{task_rec_name}/histTracks")
    h_ambtr = infile.Get(f"{task_rec_name}/{track_to_coll_path}/histAmbiguousTracks")
    for iorigin, origin_label in enumerate(origin_labels[1:]):
        h_tr_per_origin.append(h_tr.ProjectionY(
            f"h_tr_per_origin_{origin_label}", iorigin+2, iorigin+2))
        h_ambtr_per_origin.append(h_ambtr.ProjectionY(
            f"h_ambtr_per_origin_{origin_label}", iorigin+2, iorigin+2))
        h_tr_per_origin[iorigin].Sumw2()
        h_ambtr_per_origin[iorigin].Sumw2()
        h_fracanv_amb_per_origin.append(
            h_ambtr_per_origin[iorigin].Clone(f"h_fracanv_amb_per_origin_{origin_label}"))
        h_fracanv_amb_per_origin[iorigin].Divide(
            h_ambtr_per_origin[iorigin], h_tr_per_origin[iorigin], 1., 1., "B")
        h_fracanv_amb_per_origin[iorigin].SetLineColor(colors[iorigin+1])
        h_fracanv_amb_per_origin[iorigin].SetMarkerColor(colors[iorigin+1])
        h_fracanv_amb_per_origin[iorigin].SetMarkerStyle(ROOT.kFullCircle)
        h_fracanv_amb_per_origin[iorigin].SetLineWidth(2)
        canv_fracanv_amb.cd()
        h_fracanv_amb_per_origin[iorigin].Draw("same")
    canv_fracanv_amb.cd()
    leg_orig_wofake.Draw()
    if plot_full:
        canv_fracanv_amb.SaveAs(os.path.join(outpath, f"fraction_ambiguous_tracks{suffix}.pdf"))

    # fake PV
    h_ntracks = infile.Get(f"{task_rec_name}/histNtracks")
    h_ntracks.SetName("h_ntracks")
    h_ntracks.SetLineColor(ROOT.kBlack)
    h_ntracks.SetMarkerColor(ROOT.kBlack)
    h_ntracks.SetMarkerStyle(ROOT.kFullCircle)
    h_ntracks.SetLineWidth(2)

    h_frac_good_contr = infile.Get(f"{task_rec_name}/{track_to_coll_path}/histFracGoodContributors")
    h_frac_good_contr.SetName("h_frac_good_contr")
    h_frac_good_contr.SetLineColor(ROOT.kBlack)
    h_frac_good_contr.SetLineWidth(2)

    h_collisions = ROOT.TH1F("h_collisions", ";;counts", 2, 0.5, 2.5)
    h_collisions.GetXaxis().SetBinLabel(1, "generated collisions")
    h_collisions.GetXaxis().SetBinLabel(2, "reconstructed collisions")
    h_collisions.SetBinContent(1, n_events_gen)
    h_collisions.SetBinContent(2, n_events)
    h_collisions.SetLineColor(ROOT.kBlack)
    h_collisions.SetLineWidth(2)

    canv_collisions = ROOT.TCanvas("canv_collisions", "", 800, 800)
    canv_collisions.SetTopMargin(0.05)
    canv_collisions.SetBottomMargin(0.1)
    h_collisions.Draw()
    canv_collisions.SaveAs(os.path.join(outpath, f"collision_counter{suffix}.pdf"))

    h_collisions_eff = ROOT.TH1F("h_collisions_eff", ";;reco. efficiency", 1, 0.5, 1.5)
    h_collisions_eff.GetXaxis().SetBinLabel(1, "collision reco. efficiency")
    h_collisions_eff.SetBinContent(1, n_events / n_events_gen)
    h_collisions_eff.SetLineColor(ROOT.kBlack)
    h_collisions_eff.SetLineWidth(2)

    canv_collisions_eff = ROOT.TCanvas("canv_collisions_eff", "", 800, 800)
    canv_collisions_eff.SetTopMargin(0.05)
    canv_collisions_eff.SetBottomMargin(0.1)
    h_collisions_eff.Draw()
    canv_collisions_eff.SaveAs(os.path.join(outpath, f"collision_reco_eff{suffix}.pdf"))

    h_coll_samebc = infile.Get(f"{task_rec_name}/{track_to_coll_path}/histCollisionsSameBC")

    h_ncontr = h_coll_samebc.Projection(0)
    h_ncontr.Add(h_coll_samebc.Projection(1))
    h_ncontr.SetName("h_ncontr")

    h_corr_ncontr = h_coll_samebc.Projection(1, 0)
    h_corr_ncontr.SetName("h_corr_ncontr")
    h_coll_samebc.GetAxis(4).SetRange(2, 100)
    h_corr_ncontr_withb1 = h_coll_samebc.Projection(1, 0)
    h_corr_ncontr_withb1.SetName("h_corr_ncontr_withb1")
    h_coll_samebc.GetAxis(4).SetRange(-1, -1)
    h_coll_samebc.GetAxis(5).SetRange(2, 100)
    h_corr_ncontr_withb2 = h_coll_samebc.Projection(1, 0)
    h_corr_ncontr_withb2.SetName("h_corr_ncontr_withb2")
    h_coll_samebc.GetAxis(5).SetRange(-1, -1)

    h_corr_nbeauty = h_coll_samebc.Projection(5, 4)
    h_corr_nbeauty.SetName("h_corr_nbeauty")

    h_corr_ncontr_nbeauty = h_coll_samebc.Projection(4, 0)
    h_corr_ncontr_nbeauty.Add(h_coll_samebc.Projection(5, 1))
    h_corr_ncontr_nbeauty.GetXaxis().SetRangeUser(0., 100.)
    h_corr_ncontr_nbeauty.GetXaxis().SetTitle("number of contributors")
    h_corr_ncontr_nbeauty.GetYaxis().SetTitle(
        "number of contributors from beauty")

    h_corr_radius = h_coll_samebc.Projection(3, 2)
    h_corr_radius.SetName("h_corr_radius")

    h_corr_ncontr_radius = h_coll_samebc.Projection(0, 2)
    h_corr_ncontr_radius.SetName("h_corr_ncontr_radius")
    h_corr_ncontr_radius.Add(h_coll_samebc.Projection(1, 3))
    h_corr_ncontr_radius.GetYaxis().SetTitle("number of contributors")
    h_corr_ncontr_radius.GetXaxis().SetTitle("#it{R}_{xy} (cm)")

    h_coll_samebc.GetAxis(4).SetRange(1, 1)
    h_coll_samebc.GetAxis(5).SetRange(1, 1)

    h_corr_ncontr_radius_nobeauty = h_coll_samebc.Projection(0, 2)
    h_corr_ncontr_radius_nobeauty.SetName(
        "h_corr_ncontr_radius_nobeauty")
    h_corr_ncontr_radius_nobeauty.Add(h_coll_samebc.Projection(1, 3))
    h_corr_ncontr_radius_nobeauty.GetYaxis().SetTitle("number of contributors")
    h_corr_ncontr_radius_nobeauty.GetXaxis().SetTitle("#it{R}_{xy} (cm)")

    h_coll_samebc.GetAxis(4).SetRange(-1, -1)
    h_coll_samebc.GetAxis(5).SetRange(-1, -1)

    h_corr_nbeauty_radius = h_coll_samebc.Projection(4, 2)
    h_corr_nbeauty_radius.SetName("h_corr_nbeauty_radius")
    h_corr_nbeauty_radius.Add(h_coll_samebc.Projection(5, 3))

    #canv_frac_good_contr = ROOT.TCanvas("canv_frac_good_contr", "", 800, 800)
    #canv_frac_good_contr.SetLogy()
    #h_frac_good_contr.Draw("colz")
    #canv_frac_good_contr.SaveAs(os.path.join(
    #    outpath, f"fraction_good_contributors{suffix}.pdf"))

    canv_corr_ncontr = ROOT.TCanvas("canv_corr_ncontr", "", 1200, 400)
    canv_corr_ncontr.Divide(3, 1)
    canv_corr_ncontr.cd(1).SetRightMargin(0.12)
    canv_corr_ncontr.cd(1).SetLogz()
    h_corr_ncontr.Draw("colz")
    canv_corr_ncontr.cd(2).SetRightMargin(0.12)
    canv_corr_ncontr.cd(2).SetLogz()
    h_corr_ncontr_withb1.Draw("colz")
    canv_corr_ncontr.cd(3).SetRightMargin(0.12)
    canv_corr_ncontr.cd(3).SetLogz()
    h_corr_ncontr_withb2.Draw("colz")
    if plot_full:  canv_corr_ncontr.SaveAs(os.path.join(outpath, f"correlation_number_contributors_collisions_samebc{suffix}.pdf"))

    canv_corr_nbeauty = ROOT.TCanvas("canv_corr_nbeauty", "", 800, 800)
    canv_corr_nbeauty.SetRightMargin(0.12)
    h_corr_nbeauty.Draw("colz")
    if plot_full: canv_corr_nbeauty.SaveAs(os.path.join(outpath, f"correlation_number_beauty_collisions_samebc{suffix}.pdf"))

    canv_corr_ncontr_nbeauty = ROOT.TCanvas(
        "canv_corr_ncontr_nbeauty", "", 800, 800)
    canv_corr_ncontr_nbeauty.SetRightMargin(0.12)
    h_corr_ncontr_nbeauty.Draw("colz")
    if plot_full: canv_corr_ncontr_nbeauty.SaveAs(os.path.join(outpath, f"correlation_number_contributors_number_beauty_collisions_samebc{suffix}.pdf"))

    canv_corr_radius = ROOT.TCanvas("canv_corr_radius", "", 800, 800)
    canv_corr_radius.SetRightMargin(0.12)
    h_corr_radius.Draw("colz")
    if plot_full: canv_corr_radius.SaveAs(os.path.join(outpath, f"correlation_radius_collisions_samebc{suffix}.pdf"))

    canv_corr_ncontr_radius = ROOT.TCanvas(
        "canv_corr_ncontr_radius", "", 800, 800)
    canv_corr_ncontr_radius.SetRightMargin(0.12)
    h_corr_ncontr_radius.Draw("colz")
    if plot_full:
        canv_corr_ncontr_radius.SaveAs(os.path.join(
        outpath, f"correlation_number_contributors_radius_collisions_samebc{suffix}.pdf"))

    canv_corr_ncontr_radius_nobeauty = ROOT.TCanvas(
        "canv_corr_ncontr_radius_nobeauty", "", 800, 800)
    canv_corr_ncontr_radius_nobeauty.SetRightMargin(0.12)
    h_corr_ncontr_radius_nobeauty.Draw("colz")
    if plot_full:
        canv_corr_ncontr_radius_nobeauty.SaveAs(os.path.join(
            outpath, f"correlation_number_contributors_radius_collisions_samebcanv_nobeauty{suffix}.pdf"))

    canv_corr_nbeauty_radius = ROOT.TCanvas(
        "canv_corr_nbeauty_radius", "", 800, 800)
    canv_corr_nbeauty_radius.SetRightMargin(0.12)
    h_corr_nbeauty_radius.Draw("colz")
    if plot_full:
        canv_corr_nbeauty_radius.SaveAs(os.path.join(
        outpath, f"correlation_number_beauty_radius_collisions_samebc{suffix}.pdf"))
    
    output = ROOT.TFile(os.path.join(outpath, f"QA_output{suffix}.root"), "recreate")
    dir_distr = output.mkdir("gen-distr")
    dir_distr.cd()
    h_abundances_promptmeson.Write()
    h_abundances_nonpromptmeson.Write()
    for hist in h_pt_gen_prompt:
        hist.Write()
    for hist in h_pt_gen_nonprompt:
        hist.Write()
    for hist in h_pt_reco_prompt:
        hist.Write()
    for hist in h_pt_reco_nonprompt:
        hist.Write()
    for hist in h_y_gen_prompt:
        hist.Write()
    for hist in h_y_gen_nonprompt:
        hist.Write()
    for hist in h_declen_gen_prompt:
        hist.Write()
    for hist in h_declen_gen_nonprompt:
        hist.Write()
    output.cd()
    dir_eff = output.mkdir("efficiencies")
    dir_eff.cd()
    for part in h_eff_prompt:
        for hist in part:
            hist.Write()
    for part in h_eff_nonprompt:
        for hist in part:
            hist.Write()
    for part in h_eff_ratio:
        for hist in part:
            hist.Write()
    output.cd()
    dir_pv = output.mkdir("pv")
    dir_pv.cd()
    h_collisions.Write()
    h_ntracks.Write()
    h_ncontr.Write()
    h_corr_ncontr.Write()
    h_corr_nbeauty.Write()
    h_corr_ncontr_withb1.Write()
    h_corr_ncontr_withb2.Write()
    h_corr_ncontr_nbeauty.Write()
    h_corr_radius.Write()
    h_corr_ncontr_radius.Write()
    h_corr_ncontr_radius_nobeauty.Write()
    h_corr_nbeauty_radius.Write()
    h_frac_good_contr.Write()
    output.cd()
    dir_pvass = output.mkdir("pv-association")
    dir_pvass.cd()
    for hist in h_ass:
        hist.Write()
    for hist in h_nonass:
        hist.Write()
    for hist in h_assgood:
        hist.Write()
    for hist in h_eff_ass:
        hist.Write()
    for hist in h_eff_assgood:
        hist.Write()
    for hist in h_fracanv_amb_per_origin:
        hist.Write()
    for hist in h_ass_eta:
        hist.Write()
    for hist in h_nonass_eta:
        hist.Write()
    for hist in h_assgood_eta:
        hist.Write()
    for hist in h_eff_ass_eta:
        hist.Write()
    for hist in h_eff_assgood_eta:
        hist.Write()
    output.Close()

    print(" ")
    print("Finshed!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("infile", metavar="text", default="AnalysisResults.root",
                        help="ROOT imput file")
    parser.add_argument("outpath", metavar="text", default=".",
                        help="output path")
    parser.add_argument("suffix", metavar="text", default="", help="suffix")
    parser.add_argument("coll_system", metavar="text", choices=["pp", "PbPb"], help="Collision system (pp, PbPb)") 
    parser.add_argument("--collassTOF", action="store_true", default=False,
                        help="flag to require TOF for tracks to track-to-collision association studies")
    parser.add_argument("--eventType", "-e", choices=["all", "mb", "b", "c"], metavar="text", default="all",
                        help="kind of events to keep, using generator information")
    parser.add_argument("--batch", help="suppress video output", action="store_true")
    args = parser.parse_args()

    perform_qa_mc_val(args.infile, args.outpath, args.suffix, args.coll_system, args.collassTOF, args.eventType, args.batch)