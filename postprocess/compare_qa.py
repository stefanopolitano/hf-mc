import ROOT
import argparse
import os


def compare(f1_path, f2_path, output_folder):
    f1 = ROOT.TFile(f1_path, "read")
    f2 = ROOT.TFile(f2_path, "read")

    dirgen1 = f1.Get("gen-distr")
    dirgen2 = f2.Get("gen-distr")

    dirEff1 = f1.Get("efficiencies")
    dirEff2 = f2.Get("efficiencies")

    histos = [
        "h_pt_gen_promptXiCplusToPKPi",
        "h_pt_gen_nonpromptXiCplusToPKPi",
        "h_y_gen_promptXiCplusToPKPi",
        "h_y_gen_nonpromptXiCplusToPKPi",
        "h_declenen_gen_promptXiCplusToPKPi",
        "h_declenen_gen_nonpromptXiCplusToPKPi",
    ]

    h1 = []
    h2 = []
    c1 = ROOT.TCanvas("c1", "c1", 1200, 800)
    c1.Divide(3, 2)

    for i, histo in enumerate(histos):
        h1.append(dirgen1.Get(histo))
        h2.append(dirgen2.Get(histo))
        if h1[i].GetEntries() == 0 or h2[i].GetEntries() == 0:
            continue

        h1[i].Scale(1.0 / h1[i].GetEntries())
        h2[i].Scale(1.0 / h2[i].GetEntries())

        h1[i].SetMarkerColor(ROOT.kRed)
        h1[i].SetLineColor(ROOT.kRed)
        h2[i].SetMarkerColor(ROOT.kBlue)
        h2[i].SetLineColor(ROOT.kBlue)

        c1.cd(i + 1)
        h1[i].Draw()
        h2[i].Draw("same")

    c1.SaveAs(os.path.join(output_folder, "comparison_gen.pdf"))

    # Efficiencies
    histosEff = [
        "h_eff_promptXiCplusToPKPivcent0_110",
        "h_eff_nonpromptXiCplusToPKPivcent0_110",
        "h_eff_ratioXiCplusToPKPivcent0_110",
    ]

    hEff1 = []
    hEff2 = []
    c2 = ROOT.TCanvas("c2", "c2", 1200, 400)
    c2.Divide(3, 1)

    for i, histo in enumerate(histosEff):
        hEff1.append(dirEff1.Get(histo))
        hEff2.append(dirEff2.Get(histo))
        if hEff1[i].GetEntries() == 0 or hEff2[i].GetEntries() == 0:
            continue

        hEff1[i].SetMarkerColor(ROOT.kRed)
        hEff1[i].SetLineColor(ROOT.kRed)
        hEff2[i].SetMarkerColor(ROOT.kBlue)
        hEff2[i].SetLineColor(ROOT.kBlue)

        c2.cd(i + 1)
        hEff1[i].Draw()
        hEff2[i].Draw("same")

    c2.SaveAs(os.path.join(output_folder, "comparison_efficiencies.pdf"))


def compareRec(f1_path, f2_path, output_folder):
    f1 = ROOT.TFile(f1_path, "read")
    f2 = ROOT.TFile(f2_path, "read")

    dirrec1 = f1.Get("hf-task-mc-validation-rec")
    dirrec2 = f2.Get("hf-task-mc-validation-rec")

    dir1 = dirrec1.Get("XiCplusToPKPi")
    dir2 = dirrec2.Get("XiCplusToPKPi")

    histos = [
        "histDeltaPt",
        "histDeltaSecondaryVertexX",
        "histDeltaSecondaryVertexY",
        "histDeltaSecondaryVertexZ",
        "histDeltaDecayLength",
        "histPtDau0Prompt",
        "histEtaDau0Prompt",
        "histImpactParameterDau0Prompt",
        "histPtDau1Prompt",
        "histEtaDau1Prompt",
        "histImpactParameterDau1Prompt",
        "histPtDau2Prompt",
        "histEtaDau2Prompt",
        "histImpactParameterDau2Prompt",
        "histPtDau0NonPrompt",
        "histEtaDau0NonPrompt",
        "histImpactParameterDau0NonPrompt",
        "histPtDau1NonPrompt",
        "histEtaDau1NonPrompt",
        "histImpactParameterDau1NonPrompt",
        "histPtDau2NonPrompt",
        "histEtaDau2NonPrompt",
        "histImpactParameterDau2NonPrompt",
    ]

    h1 = []
    h2 = []
    c1 = ROOT.TCanvas("c1_rec", "c1_rec", 1200, 800)
    c2 = ROOT.TCanvas("c2_rec", "c2_rec", 1200, 800)
    c1.Divide(4, 3)
    c2.Divide(4, 3)

    for i, histo in enumerate(histos):
        h1.append(dir1.Get(histo))
        h2.append(dir2.Get(histo))

        h1[i].Scale(1.0 / h1[i].GetEntries())
        h2[i].Scale(1.0 / h2[i].GetEntries())

        h1[i].SetMarkerColor(ROOT.kRed)
        h1[i].SetLineColor(ROOT.kRed)
        h2[i].SetMarkerColor(ROOT.kBlue)
        h2[i].SetLineColor(ROOT.kBlue)

        if i < 12:
            c1.cd(i + 1)
            h1[i].Draw()
            h2[i].Draw("same")
        else:
            c2.cd(i - 12 + 1)
            h1[i].Draw()
            h2[i].Draw("same")

    c1.SaveAs(os.path.join(output_folder, "comparison_rec_1.pdf"))
    c2.SaveAs(os.path.join(output_folder, "comparison_rec_2.pdf"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare histograms between two ROOT files."
    )
    parser.add_argument("file1", type=str, help="Path to the first ROOT file")
    parser.add_argument("file2", type=str, help="Path to the second ROOT file")

    args = parser.parse_args()
    output_folder = os.path.dirname(args.file1)

    # Run both comparison functions
    compare(args.file1, args.file2, output_folder)
    compareRec(args.file1, args.file2, output_folder)
