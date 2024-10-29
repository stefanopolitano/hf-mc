import ROOT
import argparse

def load_anres_and_store_histogram(root_file_path):
    # Open the ROOT file
    file = ROOT.TFile.Open(root_file_path)

    if not file or file.IsZombie():
        print(f"Error: Could not open file {root_file_path}")
        return

    hGenEv = file.Get("hf-task-mc-validation-gen/hNevGen")
    hGenEv.SaveAs('hGenEv.root')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load AnRes object and store TH1 histogram.")
    parser.add_argument("root_file", help="Path to the ROOT file")
    args = parser.parse_args()

    load_anres_and_store_histogram(args.root_file)
