import ROOT
import os
import argparse

run_mapping = {
    '825836':    '539908',
    '825835':    '539906',
    '825834':    '539884',
    '825833':    '539883',
    '825832':    '539882',
    '825831':    '539877',
    '825830':    '539876',
    '825829':    '539875',
    '825828':    '539874',
    '825827':    '539873',
    '825826':    '539700',
    '825825':    '539647',
    '825824':    '539646',
    '825823':    '539644',
    '825822':    '539638',
    '825821':    '539637',
    '825820':    '539636',
    '825819':    '539623',
    '825818':    '539622',
    '825817':    '539580',
    '825816':    '539557',
    '825815':    '539556',
    '825814':    '539531',
    '825813':    '539517',
    '825812':    '539501',
    '825811':    '539483',
    '825810':    '539482',
    '825809':    '539481',
    '825808':    '539480',
    '825807':    '539466',
    '825806':    '539445',
    '825805':    '539444',
    '825804':    '539443',
    '825803':    '539339',
    '825802':    '539333',
    '825801':    '539332',
    '825800':    '539331',
    '825799':    '539317',
    '825798':    '539316',
    '825797':    '539315',
    '825796':    '539314',
    '825795':    '539273',
    '825794':    '539272',
    '825793':    '539271',
    '825792':    '539270',
    '825791':    '539269',
    '825790':    '539268',
    '825789':    '539267',
    '825788':    '539227',
    '825787':    '539226',
    '825786':    '539222',
    '825785':    '539221',
    '825784':    '539220',
    '825783':    '539219',
    '825782':    '539218',
    '825781':    '539133',
    '825780':    '539132',
    '825779':    '539130',
    '825778':    '539129',
    '825777':    '539108',
    '825776':    '539107',
    '825775':    '539089',
    '825774':    '539088',
    '825773':    '539087',
    '825772':    '539086',
    '825771':    '539071',
    '825770':    '539058',
    '825769':    '539008',
    '825768':    '538970',
    '825767':    '538968',
    '825766':    '538967',
    '825765':    '538966',
    '825764':    '538964',
    '825763':    '538961',
    '825762':    '538960',
    '825761':    '538958',
    '825760':    '538956',
    '825759':    '538933',
    '825758':    '538932',
    '825757':    '538931',
    '825756':    '538923',
    '825755':    '538018',
    '825754':    '537965',
    '825753':    '537963',
    '825752':    '537960',
    '825751':    '537959',
    '825750':    '537912',
    '825749':    '537903',
    '825748':    '537901',
    '825747':    '537900',
    '825746':    '537899',
    '825745':    '537897',
    '825744':    '537893',
    '825743':    '537870',
    '825742':    '537867',
    '825741':    '537865',
    '825740':    '537864',
    '825739':    '537861',
    '825738':    '537855',
    '825737':    '537853',
    '825736':    '537836',
    '825735':    '537829',
    '825734':    '537827',
    '825733':    '537826',
    '825732':    '537825',
    '825731':    '537822',
    '825730':    '537770',
    '825729':    '537769',
    '825728':    '537740',
    '825727':    '537739',
    '825726':    '537736',
    '825725':    '537734',
    '825724':    '537661',
    '825723':    '537660',
    '825722':    '537659',
    '825721':    '537658',
    '825720':    '537645',
    '825719':    '537636',
    '825718':    '537632',
    '825717':    '537623',
    '825716':    '537622',
    '825715':    '537605',
    '825714':    '537602',
    '825713':    '537594',
    '825712':    '537553',
    '825711':    '537551',
    '825710':    '537549',
    '825709':    '537547',
    '825708':    '537546',
    '825707':    '537531',
    '825706':    '537511',
    '825705':    '537509',
    '825704':    '537505',
    '825703':    '537504',
    '825702':    '537480',
    '825701':    '537466',
    '825700':    '537465',
    '825699':    '537464',
    '825698':    '537449',
    '825697':    '537448',
    '825696':    '537447',
    '825695':    '537426',
    '825694':    '537425',
    '825693':    '537411',
    '825692':    '537401',
    '825691':    '537397',
    '825690':    '537276',
    '825689':    '537274',
    '825688':    '536971',
    '825687':    '536969',
    '825686':    '536968',
    '825685':    '536957',
    '825684':    '536908',
    '825683':    '536906',
    '825682':    '536899',
    '825681':    '536898',
    '825680':    '536848',
    '825679':    '536843',
    '825678':    '536842',
    '825677':    '536839',
    '825676':    '536822',
    '825675':    '536790',
    '825674':    '536774',
    '825673':    '536762',
    '825672':    '536757',
    '825671':    '536685',
    '825670':    '536683',
    '825669':    '536663',
    '825668':    '536613',
    '825667':    '536612',
    '825666':    '536611',
    '825665':    '536610',
    '825664':    '536609',
    '825663':    '536608',
    '825662':    '536607',
    '825661':    '536606',
    '825660':    '536548',
    '825659':    '536547',
    '825658':    '536545',
    '825657':    '536490',
    '825656':    '536489',
    '825655':    '536488',
    '825654':    '536487',
    '825653':    '536416',
    '825652':    '536403',
    '825651':    '536402',
    '825650':    '536401',
    '825649':    '536370',
    '825648':    '536346',
    '825647':    '536344',
    '825646':    '536343',
    '825645':    '536340',
    '825644':    '536339',
    '825643':    '536338',
    '825642':    '536262',
    '825641':    '536261',
    '825640':    '536257',
    '825639':    '536255',
    '825638':    '536239',
    '825637':    '536238',
    '825636':    '536237',
    '825635':    '536236',
    '825634':    '536235',
    '825633':    '536199',
    '825632':    '536176',
    '825631':    '536108',
    '825630':    '536106',
    '825629':    '536055',
    '825628':    '536025',
    '825627':    '536020',
    '825626':    '535999',
    '825625':    '535983',
    '825624':    '535966',
    '825623':    '535964',
    '825622':    '535941',
    '825621':    '535725',
    '825620':    '535722',
    '825619':    '535721',
    '825618':    '535716',
    '825617':    '535711',
    '825616':    '535645',
    '825615':    '535644',
    '825614':    '535627',
    '825613':    '535624',
    '825612':    '535623',
    '825611':    '535621',
    '825610':    '535613',
    '825609':    '535566',
    '825608':    '535563',
    '825607':    '535545',
    '825606':    '535526',
    '825605':    '535525',
    '825604':    '535517',
    '825603':    '535514',
    '825600':    '535480',
    '825599':    '535479',
    '825598':    '535478',
    '825597':    '535476',
    '825596':    '535475',
    '825595':    '535365',
    '825594':    '535345',
    '825593':    '535087',
    '825592':    '535085',
    '825591':    '535084',
    '825590':    '535069'
}


def main(input_dir, output_file, hist_name):
    # Create an output histogram to store the entries
    output_hist = ROOT.TH1F("output_hist", "N_{ev}^{gen} vs  run; ; N_{ev}^{gen}", 220, 0, 220)  # Adjust bin settings as needed
    output_hist.SetLineWidth(2)
    output_hist.SetLineColor(ROOT.kAzure+2)

    # Loop over all files in the input directory
    for ifile, (file_name) in enumerate(os.listdir(input_dir)):
        if file_name.endswith('.root'):
            file_path = os.path.join(input_dir, file_name)
            print(f"Processing file: {file_path}")
            suffix = file_name[-11:-5]
            suffix = run_mapping[suffix]

            # Open the ROOT file
            with ROOT.TFile.Open(file_path) as root_file:
                if not root_file or root_file.IsZombie():
                    print(f"Error opening file: {file_path}")
                    continue

                # Get the histogram by name
                hist = root_file.Get(hist_name)
                if not hist:
                    print(f"Histogram '{hist_name}' not found in file: {file_path}")
                    continue

                # Get the number of entries in the histogram
                num_entries = hist.GetEntries()
                print(f"Number of entries in histogram '{hist_name}' from file '{file_name}': {num_entries}")

                # Fill the output histogram with the number of entries
                output_hist.SetBinContent(ifile, num_entries)
                output_hist.SetBinError(ifile, 0.)
                
                output_hist.GetXaxis().SetLabelSize(0.03)  # Set label size
                #output_hist.GetXaxis().SetLabelOffset(0.02)  # Increase the offset between labels
                output_hist.GetXaxis().SetBinLabel(ifile, suffix)
                output_hist.GetXaxis().LabelsOption("v")  # Rotate labels vertically
    print(f'[info] Total number of events: {output_hist.Integral()}')

    # Create a canvas wide enough to see all the x labels
    canvas = ROOT.TCanvas("canvas", "Histogram Canvas", 3200, 400)  # Width = 1600, Height = 600
    #canvas.SetPad(0.01, 0.000000000001, 1.0, 0.9)
    canvas.SetGridy()
    canvas.SetGridx()
    canvas.SetLogy()
    output_hist.Draw('hist same')  # Draw the histogram on the canvas

    # Add a LaTeX label with the total number of entries
    latex = ROOT.TLatex()
    latex.SetNDC()  # Set coordinates in normalized device coordinates (0 to 1)
    latex.SetTextSize(0.03)
    latex.SetTextAlign(13)  # Align at the top left
    latex.DrawLatex(0.15, 0.85, f"#splitline{{Total generated events:}}{{{int(output_hist.Integral()):,}}}")

    canvas.Update()

    # Save the canvas as an image (optional)
    canvas.SaveAs("output_histogram.png")

    # Save the output histogram to a new ROOT file
    with ROOT.TFile(output_file, "RECREATE") as output_root_file:
        output_hist.Write()

    print(f"Output histogram saved to '{output_file}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process ROOT files and store histogram entries.')
    parser.add_argument('input_dir', type=str, default='./outputs/', help='Directory containing input ROOT files')
    parser.add_argument('output_file', type=str, default='./', help='Output ROOT file for storing the histogram')
    parser.add_argument('--hist_name', type=str, default='hNevGen', help='Name of the histogram to process')
    args = parser.parse_args()

    # Call the main function
    main(args.input_dir, args.output_file, args.hist_name)
