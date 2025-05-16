import ROOT

def compute_ratio_th3(file_name, hist1_name, hist2_name, output_hist_name):
    """
    Computes the ratio of two TH3 histograms and writes the result to a new histogram.

    Parameters:
        file_name (str): The name of the ROOT file containing the histograms.
        hist1_name (str): The name of the numerator TH3 histogram.
        hist2_name (str): The name of the denominator TH3 histogram.
        output_hist_name (str): The name of the output ratio histogram.

    Returns:
        ROOT.TH3: The resulting ratio histogram.
    """
    # Open the ROOT file
    file = ROOT.TFile(file_name, "READ")
    if not file.IsOpen():
        raise IOError(f"Could not open file {file_name}.")

    # Retrieve the histograms
    hist1 = file.Get(hist1_name)
    hist2 = file.Get(hist2_name)

    if not hist1 or not isinstance(hist1, ROOT.TH3):
        raise ValueError(f"Histogram {hist1_name} not found or not a TH3 in file {file_name}.")
    if not hist2 or not isinstance(hist2, ROOT.TH3):
        raise ValueError(f"Histogram {hist2_name} not found or not a TH3 in file {file_name}.")

    # Clone the numerator histogram to create the ratio histogram
    ratio_hist = hist1.Clone(output_hist_name)
    ratio_hist.SetDirectory(0)  # Detach from the file
    ratio_hist.Reset()  # Reset contents to zero

    # Compute the ratio bin by bin
    for x_bin in range(1, hist1.GetNbinsX() + 1):
        for y_bin in range(1, hist1.GetNbinsY() + 1):
            for z_bin in range(1, hist1.GetNbinsZ() + 1):
                numerator = hist1.GetBinContent(x_bin, y_bin, z_bin)
                denominator = hist2.GetBinContent(x_bin, y_bin, z_bin)

                if denominator != 0:
                    ratio = numerator / denominator
                    ratio_hist.SetBinContent(x_bin, y_bin, z_bin, ratio)
                else:
                    ratio_hist.SetBinContent(x_bin, y_bin, z_bin, 0)  # Avoid division by zero

    file.Close()

    return ratio_hist

def project_and_save_z(hist, x_bins, y_bins, output_prefix):
    """
    Projects a TH3 histogram along the z-axis in given bins of x and y axes and saves the projections.

    Parameters:
        hist (ROOT.TH3): The input TH3 histogram.
        x_bins (list of tuple): List of (x_bin_min, x_bin_max) ranges for the x-axis.
        y_bins (list of tuple): List of (y_bin_min, y_bin_max) ranges for the y-axis.
        output_prefix (str): The prefix for the output projection histograms.
    """
    if not isinstance(x_bins, list) or not isinstance(y_bins, list):
        raise ValueError("x_bins and y_bins must be lists of tuples.")

    for x_range in x_bins:
        for y_range in y_bins:
            x_bin_min, x_bin_max = x_range
            y_bin_min, y_bin_max = y_range

            # Project along the z-axis
            projection = hist.ProjectionZ(f"{output_prefix}_x{x_bin_min}_{x_bin_max}_y{y_bin_min}_{y_bin_max}",
                                          x_bin_min, x_bin_max, y_bin_min, y_bin_max)
            projection_ptocc = hist.Project3D("zy")

            # Write the projection to a file
            output_file = ROOT.TFile(f"{output_prefix}_projections.root", "UPDATE")
            output_file.cd()
            projection.Write()
            projection_ptocc.Write()
            output_file.Close()

# Example usage
if __name__ == "__main__":
    input_file = "/home/spolitan/alice/analyses/hf-mc/postprocess/inputs/AnalysisResults_LHC24g2_small_tracking.root"
    hist1_name = "qa-efficiency_hf_occ/MC/occ_cent/reco/pos/its_tpc"
    hist2_name = "qa-efficiency_hf_occ/MC/occ_cent/gen/pos"
    output_hist_name = "RatioHistogram_pos"

    ratio_hist = compute_ratio_th3(input_file, hist1_name, hist2_name, output_hist_name)

    # Save the result to a new ROOT file
    output_file = ROOT.TFile("ratio_output.root", "RECREATE")
    output_file.cd()
    ratio_hist.Write()
    output_file.Close()

    print(f"Ratio histogram saved as {output_hist_name} in ratio_output.root.")

    # Define the bins for x and y axes
    x_bins = [(0, 20), (20, 50), (50, 100)]  # Example ranges for x-axis
    y_bins = [(0, 2000), (2000, 4000), (4000, 99999999)]  # Example ranges for y-axis

    # Create projections along the z-axis and save them
    project_and_save_z(ratio_hist, x_bins, y_bins, "RatioHistogram")
