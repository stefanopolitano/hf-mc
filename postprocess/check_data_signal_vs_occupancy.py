import os
import ROOT
import argparse
import numpy as np

# Define color palettes for prompt (red) and non-prompt (blue)
marker_styles = [
    ROOT.kFullCircle,  # Full circle
    ROOT.kFullSquare,  # Full square
    ROOT.kFullTriangleUp,  # Full triangle-up
    ROOT.kFullTriangleDown,  # Full triangle-down
    ROOT.kFullDiamond,  # Full diamond
    ROOT.kFullStar,  # Full star
    ROOT.kFullCross,  # Full plus
    ROOT.kFullFourTrianglesPlus,  # Full pentagon
    ROOT.kFullCrossX,  # Filled triangle-down (alternative style)
    ROOT.kFullDoubleDiamond,  # Filled hourglass
]

color_palette_prompt = [
    # ROOT.TColor.GetColor("#8A3307"),  # Dark Rust
    ROOT.TColor.GetColor("#A73D08"),  # Rust
    # ROOT.TColor.GetColor("#BF360C"),  # Deep Orange
    ROOT.TColor.GetColor("#D84315"),  # Burnt Orange
    # ROOT.TColor.GetColor("#E64A19"),  # Dark Orange
    ROOT.TColor.GetColor("#FF5722"),  # Orange
    # ROOT.TColor.GetColor("#FF6F20"),  # Coral
    ROOT.TColor.GetColor("#FF8C42"),  # Light Coral
    # ROOT.TColor.GetColor("#FFB74D"),  # Peach
    ROOT.TColor.GetColor("#FFCC99"),  # Light Orange
]


def get_empty_clone(hist):
    """
    Function to get empty clone of an histogram.

    Inputs:
        - hist is the hisotgram to copy
    Returns:
        - hclone is the cloned hisotgram
    """
    hclone = hist.Clone(hist.GetName() + "_clone")
    # obtain empty version of the markerstyle
    mstyle = hist.GetMarkerStyle()
    if mstyle == 33:
        mstyle = 27
    if mstyle == 34:
        mstyle = 28
    if mstyle == 20:
        mstyle = 24
    if mstyle == 21:
        mstyle = 25
    if mstyle == 29:
        mstyle = 30
    if mstyle == 47:
        mstyle = 46
    if mstyle == 43:
        mstyle = 42
    if mstyle == 45:
        mstyle = 44
    if mstyle == 22:
        mstyle = 26
    if mstyle == 23:
        mstyle = 32

    hclone.SetMarkerStyle(mstyle)
    hclone.SetMarkerColor(ROOT.kBlack)
    hclone.SetLineWidth(0)

    return hclone


def load_thnsparse(infile_name, directory, thn_name):
    root_file = ROOT.TFile.Open(infile_name, "READ")
    thn = root_file.Get(f"{directory}/{thn_name}")
    return thn


def fit_invariant_mass(hist, mass_range=(1.72, 2.04), label=""):
    """
    Fit the invariant mass of D+ mesons, extract key parameters, and calculate uncertainties.

    Parameters:
    - hist (TH1): The invariant mass histogram to fit.
    - mass_range (tuple): The mass range for fitting, e.g., (1.8, 2.0).
    - label: label

    Returns:
    - dict: A dictionary containing mean, sigma, signal, background, significance, S/B, and their uncertainties.
    """
    # Define the mass observable
    mass = ROOT.RooRealVar(
        "mass", "#it{M} (KK#pi)", mass_range[0], mass_range[1], "GeV/c^{2}"
    )

    # Import the histogram into a RooDataHist
    data_hist = ROOT.RooDataHist(
        "data_hist", "Data Histogram", ROOT.RooArgList(mass), hist
    )

    # Signal: Gaussian
    mean = ROOT.RooRealVar("mean", "Mean", 1.87, 1.85, 1.89)
    sigma = ROOT.RooRealVar("sigma", "Sigma", 0.01, 0.005, 0.05)
    signal = ROOT.RooGaussian("signal", "Signal Gaussian", mass, mean, sigma)

    # Background: Exponential
    slope = ROOT.RooRealVar("slope", "Slope", -1.0, -10.0, 0.0)
    background = ROOT.RooExponential(
        "background", "Background Exponential", mass, slope
    )

    # Combined model: Signal + Background
    sig_frac = ROOT.RooRealVar("sig_frac", "Signal Fraction", 0.5, 0.0, 1.0)
    model = ROOT.RooAddPdf(
        "model",
        "Signal + Background",
        ROOT.RooArgList(signal, background),
        ROOT.RooArgList(sig_frac),
    )

    # Perform the fit
    fit_result = model.fitTo(data_hist, ROOT.RooFit.Save())

    # Extract uncertainties from the fit result
    fit_params = {
        "mean": (mean.getVal(), mean.getError()),
        "sigma": (sigma.getVal(), sigma.getError()),
        "sig_frac": (sig_frac.getVal(), sig_frac.getError()),
        "slope": (slope.getVal(), slope.getError()),
    }

    # Define the 3σ range around the mean
    mean_val, mean_err = fit_params["mean"]
    sigma_val, sigma_err = fit_params["sigma"]
    range_min = mean_val - 3 * sigma_val
    range_max = mean_val + 3 * sigma_val
    mass.setRange("signal_region", range_min, range_max)

    # Integrals for signal and background in the 3σ region
    signal_integral = signal.createIntegral(
        ROOT.RooArgSet(mass),
        ROOT.RooFit.NormSet(ROOT.RooArgSet(mass)),
        ROOT.RooFit.Range("signal_region"),
    ).getVal()
    background_integral = background.createIntegral(
        ROOT.RooArgSet(mass),
        ROOT.RooFit.NormSet(ROOT.RooArgSet(mass)),
        ROOT.RooFit.Range("signal_region"),
    ).getVal()

    # Total number of events in the histogram
    total_events = data_hist.sumEntries()

    # Signal and background yields
    sig_frac_val, sig_frac_err = fit_params["sig_frac"]
    signal_yield = sig_frac_val * total_events * signal_integral
    background_yield = (1 - sig_frac_val) * total_events * background_integral

    # Uncertainty propagation for signal and background yields
    signal_yield_err = (
        signal_yield * sig_frac_err / sig_frac_val if sig_frac_val != 0 else 0
    )
    background_yield_err = (
        background_yield * sig_frac_err / (1 - sig_frac_val) if sig_frac_val != 1 else 0
    )

    # Calculate significance and S/B
    if background_yield > 0:
        sb_ratio = signal_yield / background_yield
        significance = signal_yield / (signal_yield + background_yield) ** 0.5
        sb_ratio_err = (
            sb_ratio
            * (
                (signal_yield_err / signal_yield) ** 2
                + (background_yield_err / background_yield) ** 2
            )
            ** 0.5
        )
        significance_err = (
            significance
            * (
                (signal_yield_err / signal_yield) ** 2
                + (
                    (signal_yield_err + background_yield_err)
                    / (signal_yield + background_yield)
                )
                ** 2
            )
            ** 0.5
        )
    else:
        sb_ratio, sb_ratio_err = float("inf"), 0
        significance, significance_err = float("inf"), 0

    # Print results
    print(f"Mean: {mean_val:.4f} ± {mean_err:.4f} GeV/c^2")
    print(f"Sigma: {sigma_val:.4f} ± {sigma_err:.4f} GeV/c^2")
    print(f"Signal Events: {signal_yield:.2f} ± {signal_yield_err:.2f}")
    print(f"Background Events: {background_yield:.2f} ± {background_yield_err:.2f}")
    print(f"S/B Ratio: {sb_ratio:.2f} ± {sb_ratio_err:.2f}")
    print(f"Significance: {significance:.2f} ± {significance_err:.2f}")

    # Plot the fit
    frame = mass.frame(ROOT.RooFit.Title(label))
    data_hist.plotOn(
        frame,
        ROOT.RooFit.MarkerStyle(ROOT.kFullCircle),
        ROOT.RooFit.MarkerColor(ROOT.kBlack),
        ROOT.RooFit.MarkerSize(1.0),
        ROOT.RooFit.DrawOption("PEZ1"),
    )
    model.plotOn(
        frame,
        ROOT.RooFit.Components("background"),
        ROOT.RooFit.LineStyle(ROOT.kDashed),
        ROOT.RooFit.LineColor(ROOT.kOrange + 1),
    )
    model.plotOn(frame, ROOT.RooFit.LineColor(ROOT.kAzure + 2))
    model.plotOn(
        frame,
        ROOT.RooFit.Components("signal"),
        ROOT.RooFit.LineColor(ROOT.kAzure + 2),
        ROOT.RooFit.FillColor(ROOT.kAzure + 2),
        ROOT.RooFit.FillStyle(3004),
        ROOT.RooFit.LineWidth(1),
        ROOT.RooFit.DrawOption("FL"),
    )

    # Draw the frame
    canvas = ROOT.TCanvas("canvas", "Fit Results", 800, 600)
    frame.Draw()

    # Add LaTeX labels
    latex = ROOT.TLatex()
    latex.SetTextSize(0.04)  # Set text size
    latex.SetTextFont(42)  # Set font (42 = Helvetica)
    latex.SetNDC(True)  # Use normalized device coordinates (NDC)

    # Add labels to the plot
    latex.DrawLatex(
        0.15, 0.84, f"#mu=({mean_val:.3f}#pm{mean_err:.3f}) GeV/#it{{c}}^{{2}}"
    )
    latex.DrawLatex(
        0.15, 0.80, f"#sigma=({sigma_val:.3f}#pm{sigma_err:.3f}) GeV/#it{{c}}^{{2}}"
    )
    latex.DrawLatex(0.60, 0.84, f"#it{{S}}={signal_yield:.2f}#pm{signal_yield_err:.2f}")
    latex.DrawLatex(
        0.60, 0.80, f"#it{{B}}={background_yield:.2f}#pm{background_yield_err:.2f}"
    )
    latex.DrawLatex(0.60, 0.76, f"#it{{S/B}}={sb_ratio:.2f}#pm{sb_ratio_err:.2f}")
    latex.DrawLatex(0.60, 0.72, f"Signif.={significance:.2f}#pm{significance_err:.2f}")

    canvas.SaveAs(f"{outdir}/fit_result_{hist.GetName()}.png")

    # Return results as a dictionary
    results = {
        "mean": (mean_val, mean_err),
        "sigma": (sigma_val, sigma_err),
        "signal": (signal_yield, signal_yield_err),
        "background": (background_yield, background_yield_err),
        "s/b": (sb_ratio, sb_ratio_err),
        "significance": (significance, significance_err),
    }
    return results


def set_style(histo, ytitle):
    histo.GetXaxis().SetTitle("#it{p}_{T} (GeV/#it{c})")
    histo.GetXaxis().SetTitleOffset(1.2)
    histo.GetXaxis().SetLabelSize(0.045)
    histo.GetYaxis().SetTitle(ytitle)
    histo.GetYaxis().SetRangeUser(1.0e-3, 2.02)
    histo.GetYaxis().SetMaxDigits(1)
    histo.SetStats(0)

    color = color_palette_prompt[iocc]
    histo.SetLineColor(color)
    histo.SetMarkerColor(color)
    histo.SetMarkerStyle(marker_styles[iocc])
    histo.SetMarkerSize(1.5)
    histo.SetLineWidth(2)


# Main script
centralities = [20, 50]
useFT0c = False
infile = f"/home/spolitan/alice/analyses/hf-mc/postprocess/inputs/AnalysisResults_data_medium_occupancy_{centralities[0]}{centralities[1]}.root"
if useFT0c:
    indir = "hf-task-flow-charm-hadrons_occ_ft0c"
else:
    indir = "hf-task-flow-charm-hadrons"
thn_name = "hSparseFlowCharm"
if useFT0c:
    outdir = f"data_occupancy_ft0c_{centralities[0]}{centralities[1]}"
else:
    outdir = f"data_medium_occupancy_{centralities[0]}{centralities[1]}"

occupancies = [0, 2000, 4000, 999999]
pt_bins = [2, 3, 4, 5, 6, 8, 10, 12, 24]

thn = load_thnsparse(infile, indir, thn_name)

os.makedirs(outdir, exist_ok=True)
if useFT0c:
    outfile = ROOT.TFile(
        f"{outdir}/projected_thn_dataocc_ft0c_{centralities[0]}{centralities[1]}.root",
        "RECREATE",
    )
else:
    outfile = ROOT.TFile(
    f"{outdir}/projected_thn_dataocc_ft0c_{centralities[0]}{centralities[1]}.root",
    "RECREATE",
    )

hcorr_cent_occ = thn.Projection(2, 4)
if useFT0c: # get scaling factor from ITS to FT0c
    for i, _ in enumerate(occupancies):
        occupancies[i] *= 10
    
    
    '''
    calculate scaling factor with fit to be done
    
    root_file = ROOT.TFile.Open(infile, "READ")
    hcorr_occits_occft0c = root_file.Get(f"{indir}/trackOccVsFT0COcc")
    its_occ = ROOT.RooRealVar("its_occ", "X", 0, 14000)
    ft0c_occ = ROOT.RooRealVar("ft0c_occ", "Y", 0, 140.e+03)

    data = ROOT.RooDataHist(
        "data_hist", "Data Histogram", ROOT.RooArgList(its_occ, ft0c_occ), hcorr_occits_occft0c
    )
    
    p0 = ROOT.RooRealVar("p0", "Intercept", 0, -10, 10)
    p1 = ROOT.RooRealVar("p1", "Slope", 1, -5, 5)

    # RooPolyVar models y as a function of x (y = p0 + p1*x)
    linear_model = ROOT.RooPolynomial("linear_model", "Linear Model", its_occ, ROOT.RooArgList(p1, p0))

    # Step 5: Fit the data
    fit_result = linear_model.fitTo(data, ROOT.RooFit.Save())

    # Step 6: Visualize the fit
    canvas = ROOT.TCanvas("canvas", "Fit Results", 800, 600)

    # Step 6: Plot the TH2 histogram with the fitted linear model
    canvas = ROOT.TCanvas("canvas", "Fit Results", 800, 600)
    hcorr_occits_occft0c.Draw("COLZ")  # Draw the TH2 histogram as a color plot

    # Overlay the linear fit as a line
    fit_line = ROOT.TF1("fit_line", "[0] + [1]*x", 0, 14000)
    fit_line.SetParameter(0, p0.getVal())
    fit_line.SetParameter(1, p1.getVal())
    fit_line.SetLineColor(ROOT.kRed)
    fit_line.SetLineWidth(2)
    fit_line.Draw("SAME")  # Overlay the fit on the histogram
    canvas.SaveAs('cicio.png')
    input()
    '''

hist_mean, hist_sigma, hist_s, hist_b, hist_soverb, hist_signif = ([] for _ in range(6))
for icent, (cent_min, cent_max) in enumerate(
    zip(centralities[:-1], centralities[1:])
):  # loop over centrality
    hist_mean.append({})
    hist_sigma.append({})
    hist_s.append({})
    hist_b.append({})
    hist_soverb.append({})
    hist_signif.append({})

    hist_mean[icent] = {}
    hist_sigma[icent] = {}
    hist_s[icent] = {}
    hist_b[icent] = {}
    hist_soverb[icent] = {}
    hist_signif[icent] = {}

    for iocc, (occ_min, occ_max) in enumerate(
        zip(occupancies[:-1], occupancies[1:])
    ):  # loop over occupancy
        nbins = len(pt_bins) - 1
        hist_mean[icent][iocc] = ROOT.TH1F(
            f"hist_mean_cent{cent_min}_{cent_max}_occ{occ_min}_{occ_max}",
            "; #it{p}_{T} (GeV/#it{c})",
            nbins,
            np.asarray(pt_bins, "d"),
        )
        hist_sigma[icent][iocc] = ROOT.TH1F(
            f"hist_sigma_cent{cent_min}_{cent_max}_occ{occ_min}_{occ_max}",
            "; #it{p}_{T} (GeV/#it{c})",
            nbins,
            np.asarray(pt_bins, "d"),
        )
        hist_s[icent][iocc] = ROOT.TH1F(
            f"hist_s_cent{cent_min}_{cent_max}_occ{occ_min}_{occ_max}",
            "; #it{p}_{T} (GeV/#it{c})",
            nbins,
            np.asarray(pt_bins, "d"),
        )
        hist_b[icent][iocc] = ROOT.TH1F(
            f"hist_b_cent{cent_min}_{cent_max}_occ{occ_min}_{occ_max}",
            "; #it{p}_{T} (GeV/#it{c})",
            nbins,
            np.asarray(pt_bins, "d"),
        )
        hist_soverb[icent][iocc] = ROOT.TH1F(
            f"hist_soverb_cent{cent_min}_{cent_max}_occ{occ_min}_{occ_max}",
            "; #it{p}_{T} (GeV/#it{c})",
            nbins,
            np.asarray(pt_bins, "d"),
        )
        hist_signif[icent][iocc] = ROOT.TH1F(
            f"hist_signif_cent{cent_min}_{cent_max}_occ{occ_min}_{occ_max}",
            "; #it{p}_{T} (GeV/#it{c})",
            nbins,
            np.asarray(pt_bins, "d"),
        )
        for ipt, (pt_min, pt_max) in enumerate(
            zip(pt_bins[:-1], pt_bins[1:])
        ):  # loop over pt bins
            thn.GetAxis(2).SetRangeUser(cent_min, cent_max)
            thn.GetAxis(4).SetRangeUser(occ_min, occ_max)
            thn.GetAxis(1).SetRangeUser(pt_min, pt_max)

            hmass = thn.Projection(0)
            hsp = thn.Projection(3)
            hmass.SetName(
                f"hmass_cent{cent_min}_{cent_max}_occ{occ_min}_{occ_max}_pt{pt_min}_{pt_max}"
            )
            hsp.SetName(
                f"hsp_cent{cent_min}_{cent_max}_occ{occ_min}_{occ_max}_pt{pt_min}_{pt_max}"
            )

            # Perform invariant mass fit
            dict = fit_invariant_mass(
                hmass,
                mass_range=(1.72, 2.04),
                label=f"Cent. {cent_min}-{cent_max}, Occ. {occ_min}-{occ_max}, #it{{p}}_{{T}} {pt_min}-{pt_max}",
            )

            hist_mean[icent][iocc].SetBinContent(ipt + 1, dict["mean"][0])
            hist_mean[icent][iocc].SetBinError(ipt + 1, dict["mean"][1])
            hist_sigma[icent][iocc].SetBinContent(ipt + 1, dict["sigma"][0])
            hist_sigma[icent][iocc].SetBinError(ipt + 1, dict["sigma"][1])
            hist_s[icent][iocc].SetBinContent(ipt + 1, dict["signal"][0])
            hist_s[icent][iocc].SetBinError(ipt + 1, dict["signal"][1])
            hist_b[icent][iocc].SetBinContent(ipt + 1, dict["background"][0])
            hist_b[icent][iocc].SetBinError(ipt + 1, dict["background"][1])
            hist_soverb[icent][iocc].SetBinContent(ipt + 1, dict["s/b"][0])
            hist_soverb[icent][iocc].SetBinError(ipt + 1, dict["s/b"][1])
            hist_signif[icent][iocc].SetBinContent(ipt + 1, dict["significance"][0])
            hist_signif[icent][iocc].SetBinError(ipt + 1, dict["significance"][1])

            hmass.Write()
            hsp.Write()

        hist_mean[icent][iocc].Write()
        hist_sigma[icent][iocc].Write()
        hist_s[icent][iocc].Write()
        hist_b[icent][iocc].Write()
        hist_soverb[icent][iocc].Write()
        hist_signif[icent][iocc].Write()

    hist_ratio_mean, hist_ratio_mean_empty = [], []
    hist_ratio_sigma, hist_ratio_sigma_empty = [], []
    hist_ratio_s, hist_ratio_s_empty = [], []
    hist_ratio_b, hist_ratio_b_empty = [], []
    hist_ratio_signif, hist_ratio_signif_empty = [], []
    hist_ratio_soverb, hist_ratio_soverb_empty = [], []

    canvas_cent_ratio_s = ROOT.TCanvas(
        f"cratio_s_cent{cent_min}_{cent_max}",
        ";#it{p}_{T} (GeV/#it{c}); #it{S}(Occ) / #it{S}(0-2000)",
        600,
        600,
    )
    canvas_cent_ratio_s.cd().SetGridy()
    canvas_cent_ratio_s.cd().SetGridx()
    canvas_cent_ratio_s.cd().SetLogy()
    canvas_cent_ratio_s.cd().SetLeftMargin(0.2)

    legend = ROOT.TLegend(0.35, 0.2, 0.8, 0.5)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetTextSize(0.035)
    leg_empty = legend.Clone()
    legend.SetHeader(f"D^{{#plus}} {cent_min}-{cent_max}% centrality")
    leg_empty.SetHeader(" ")
    for iocc, (occ_min, occ_max) in enumerate(
        zip(occupancies[:-1], occupancies[1:])
    ):  # loop over occupancy
        hist_ratio_s.append(hist_s[icent][iocc].Clone())
        hist_ratio_s[-1].SetName(
            f"hist_ratio_s_cent{cent_min}_{cent_max}_occ{occ_min}_{occ_max}"
        )
        hist_ratio_s[-1].Divide(hist_s[icent][iocc], hist_s[icent][0], 1.0, 1.0, "B")

        set_style(hist_ratio_s[-1], "#it{S}(Occ)/#it{S}(0-2000)")
        hist_ratio_s_empty.append(get_empty_clone(hist_ratio_s[-1]))
        hist_ratio_s_empty[-1].SetDirectory(0)

        canvas_cent_ratio_s.cd()
        hist_ratio_s[-1].Draw("P SAME")
        hist_ratio_s_empty[-1].Draw("P SAME")
        legend.AddEntry(hist_ratio_s[-1], f"Occupancy {occ_min}-{occ_max}", "p")
    legend.Draw()
    canvas_cent_ratio_s.Write()

    canvas_cent_ratio_b = ROOT.TCanvas(
        f"cratio_b_cent{cent_min}_{cent_max}",
        ";#it{p}_{T} (GeV/#it{c}); #it{B}(Occ)/#it{B}(0-2000)",
        600,
        600,
    )
    canvas_cent_ratio_b.cd().SetGridy()
    canvas_cent_ratio_b.cd().SetGridx()
    canvas_cent_ratio_b.cd().SetLogy()
    canvas_cent_ratio_b.cd().SetLeftMargin(0.2)

    legend = ROOT.TLegend(0.35, 0.2, 0.8, 0.5)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetTextSize(0.035)
    leg_empty = legend.Clone()
    legend.SetHeader(f"D^{{#plus}} {cent_min}-{cent_max}% centrality")
    leg_empty.SetHeader(" ")
    for iocc, (occ_min, occ_max) in enumerate(
        zip(occupancies[:-1], occupancies[1:])
    ):  # loop over occupancy
        hist_ratio_b.append(hist_b[icent][iocc].Clone())
        hist_ratio_b[-1].SetName(
            f"hist_ratio_b_cent{cent_min}_{cent_max}_occ{occ_min}_{occ_max}"
        )
        hist_ratio_b[-1].Divide(hist_b[icent][iocc], hist_b[icent][0], 1.0, 1.0, "B")

        set_style(hist_ratio_b[-1], "#it{B}(Occ)/#it{B}(0-2000)")
        hist_ratio_b_empty.append(get_empty_clone(hist_ratio_b[-1]))
        hist_ratio_b_empty[-1].SetDirectory(0)

        canvas_cent_ratio_b.cd()
        hist_ratio_b[-1].Draw("P SAME")
        hist_ratio_b_empty[-1].Draw("P SAME")
        legend.AddEntry(hist_ratio_b[-1], f"Occupancy {occ_min}-{occ_max}", "p")
    legend.Draw()
    canvas_cent_ratio_b.Write()

    canvas_cent_ratio_soverb = ROOT.TCanvas(
        f"cratio_soverb_cent{cent_min}_{cent_max}",
        ";#it{p}_{T} (GeV/#it{c}); #it{S/B}(Occ)/#it{S/B}(0-2000)",
        600,
        600,
    )
    canvas_cent_ratio_soverb.cd().SetGridy()
    canvas_cent_ratio_soverb.cd().SetGridx()
    canvas_cent_ratio_soverb.cd().SetLogy()
    canvas_cent_ratio_soverb.cd().SetLeftMargin(0.2)

    legend = ROOT.TLegend(0.35, 0.2, 0.8, 0.5)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetTextSize(0.035)
    leg_empty = legend.Clone()
    legend.SetHeader(f"D^{{#plus}} {cent_min}-{cent_max}% centrality")
    leg_empty.SetHeader(" ")
    for iocc, (occ_min, occ_max) in enumerate(
        zip(occupancies[:-1], occupancies[1:])
    ):  # loop over occupancy
        hist_ratio_soverb.append(hist_soverb[icent][iocc].Clone())
        hist_ratio_soverb[-1].SetName(
            f"hist_ratio_soverb_cent{cent_min}_{cent_max}_occ{occ_min}_{occ_max}"
        )
        hist_ratio_soverb[-1].Divide(
            hist_soverb[icent][iocc], hist_soverb[icent][0], 1.0, 1.0, "B"
        )

        set_style(hist_ratio_soverb[-1], "#it{S/B}(Occ)/#it{S/B}(0-2000)")
        hist_ratio_soverb_empty.append(get_empty_clone(hist_ratio_soverb[-1]))
        hist_ratio_soverb_empty[-1].SetDirectory(0)

        canvas_cent_ratio_soverb.cd()
        hist_ratio_soverb[-1].Draw("P SAME")
        hist_ratio_soverb_empty[-1].Draw("P SAME")
        legend.AddEntry(hist_ratio_soverb[-1], f"Occupancy {occ_min}-{occ_max}", "p")
    legend.Draw()
    canvas_cent_ratio_soverb.Write()

    canvas_cent_ratio_signif = ROOT.TCanvas(
        f"cratio_signif_cent{cent_min}_{cent_max}",
        ";#it{p}_{T} (GeV/#it{c}); Signif.(Occ)/Signif.(0-2000)",
        600,
        600,
    )
    canvas_cent_ratio_signif.cd().SetGridy()
    canvas_cent_ratio_signif.cd().SetGridx()
    canvas_cent_ratio_signif.cd().SetLogy()
    canvas_cent_ratio_signif.cd().SetLeftMargin(0.2)

    legend = ROOT.TLegend(0.35, 0.2, 0.8, 0.5)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetTextSize(0.035)
    leg_empty = legend.Clone()
    legend.SetHeader(f"D^{{#plus}} {cent_min}-{cent_max}% centrality")
    leg_empty.SetHeader(" ")
    for iocc, (occ_min, occ_max) in enumerate(
        zip(occupancies[:-1], occupancies[1:])
    ):  # loop over occupancy
        hist_ratio_signif.append(hist_signif[icent][iocc].Clone())
        hist_ratio_signif[-1].SetName(
            f"hist_ratio_signif_cent{cent_min}_{cent_max}_occ{occ_min}_{occ_max}"
        )
        hist_ratio_signif[-1].Divide(
            hist_signif[icent][iocc], hist_signif[icent][0], 1.0, 1.0, "B"
        )

        set_style(hist_ratio_signif[-1], "Signif.(Occ)/Signif.(0-2000)")
        hist_ratio_signif_empty.append(get_empty_clone(hist_ratio_signif[-1]))
        hist_ratio_signif_empty[-1].SetDirectory(0)

        canvas_cent_ratio_signif.cd()
        hist_ratio_signif[-1].Draw("P SAME")
        hist_ratio_signif_empty[-1].Draw("P SAME")
        legend.AddEntry(hist_ratio_signif[-1], f"Occupancy {occ_min}-{occ_max}", "p")
    legend.Draw()
    canvas_cent_ratio_signif.Write()

    canvas_cent_ratio_mean = ROOT.TCanvas(
        f"cratio_mean_cent{cent_min}_{cent_max}",
        ";#it{p}_{T} (GeV/#it{c}); #mu(Occ)/#mu(0-2000)",
        600,
        600,
    )
    canvas_cent_ratio_mean.cd().SetGridy()
    canvas_cent_ratio_mean.cd().SetGridx()
    canvas_cent_ratio_mean.cd().SetLeftMargin(0.2)

    legend = ROOT.TLegend(0.35, 0.2, 0.8, 0.5)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetTextSize(0.035)
    leg_empty = legend.Clone()
    legend.SetHeader(f"D^{{#plus}} {cent_min}-{cent_max}% centrality")
    leg_empty.SetHeader(" ")
    for iocc, (occ_min, occ_max) in enumerate(
        zip(occupancies[:-1], occupancies[1:])
    ):  # loop over occupancy
        hist_ratio_mean.append(hist_mean[icent][iocc].Clone())
        hist_ratio_mean[-1].SetName(
            f"hist_ratio_mean_cent{cent_min}_{cent_max}_occ{occ_min}_{occ_max}"
        )
        hist_ratio_mean[-1].Divide(
            hist_mean[icent][iocc], hist_mean[icent][0], 1.0, 1.0, "B"
        )

        set_style(hist_ratio_mean[-1], "#mu(Occ)/#mu(0-2000)")
        hist_ratio_mean_empty.append(get_empty_clone(hist_ratio_mean[-1]))
        hist_ratio_mean_empty[-1].SetDirectory(0)

        canvas_cent_ratio_mean.cd()
        hist_ratio_mean[-1].Draw("P SAME")
        hist_ratio_mean_empty[-1].Draw("P SAME")
        legend.AddEntry(hist_ratio_mean[-1], f"Occupancy {occ_min}-{occ_max}", "p")
    legend.Draw()
    canvas_cent_ratio_mean.Write()

    canvas_cent_ratio_sigma = ROOT.TCanvas(
        f"cratio_sigma_cent{cent_min}_{cent_max}",
        ";#it{p}_{T} (GeV/#it{c}); #sigma(Occ)/#sigma(0-2000)",
        600,
        600,
    )
    canvas_cent_ratio_sigma.cd().SetGridy()
    canvas_cent_ratio_sigma.cd().SetGridx()
    canvas_cent_ratio_sigma.cd().SetLeftMargin(0.2)

    legend = ROOT.TLegend(0.35, 0.2, 0.8, 0.5)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetTextSize(0.035)
    leg_empty = legend.Clone()
    legend.SetHeader(f"D^{{#plus}} {cent_min}-{cent_max}% centrality")
    leg_empty.SetHeader(" ")
    for iocc, (occ_min, occ_max) in enumerate(
        zip(occupancies[:-1], occupancies[1:])
    ):  # loop over occupancy
        hist_ratio_sigma.append(hist_sigma[icent][iocc].Clone())
        hist_ratio_sigma[-1].SetName(
            f"hist_ratio_sigma_cent{cent_min}_{cent_max}_occ{occ_min}_{occ_max}"
        )
        hist_ratio_sigma[-1].Divide(
            hist_sigma[icent][iocc], hist_sigma[icent][0], 1.0, 1.0, "B"
        )

        set_style(hist_ratio_sigma[-1], "#sigma(Occ)/#sigma(0-2000)")
        hist_ratio_sigma_empty.append(get_empty_clone(hist_ratio_sigma[-1]))
        hist_ratio_sigma_empty[-1].SetDirectory(0)

        canvas_cent_ratio_sigma.cd()
        hist_ratio_sigma[-1].Draw("P SAME")
        hist_ratio_sigma_empty[-1].Draw("P SAME")
        legend.AddEntry(hist_ratio_sigma[-1], f"Occupancy {occ_min}-{occ_max}", "p")
    legend.Draw()
    canvas_cent_ratio_sigma.Write()

    canvas_cent_ratio_s.SaveAs(f"{outdir}/cratio_s_cent{cent_min}_{cent_max}.png")
    canvas_cent_ratio_b.SaveAs(f"{outdir}/cratio_b_cent{cent_min}_{cent_max}.png")
    canvas_cent_ratio_soverb.SaveAs(
        f"{outdir}/cratio_soverb_cent{cent_min}_{cent_max}.png"
    )
    canvas_cent_ratio_signif.SaveAs(
        f"{outdir}/cratio_signif_cent{cent_min}_{cent_max}.png"
    )
    canvas_cent_ratio_mean.SaveAs(f"{outdir}/cratio_mean_cent{cent_min}_{cent_max}.png")
    canvas_cent_ratio_sigma.SaveAs(
        f"{outdir}/cratio_sigma_cent{cent_min}_{cent_max}.png"
    )

    for hist in hist_ratio_s:
        hist.Write()
    for hist in hist_ratio_b:
        hist.Write()
    for hist in hist_ratio_soverb:
        hist.Write()
    for hist in hist_ratio_signif:
        hist.Write()
    for hist in hist_ratio_mean:
        hist.Write()
    for hist in hist_ratio_sigma:
        hist.Write()

hcorr_cent_occ.Write()
