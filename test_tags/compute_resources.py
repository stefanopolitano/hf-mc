# Defining the variables given by the user
output_path = "./24_apass1_D2H/lhc24ag_resources.txt"
runningtime = 1488.735  # seconds (from alien_log_xxxx.txt)
ntargetevents = 1.0e9
nproducedevents = 500
sizetest = 23.34  # size in arbitrary units (assumed to be MB for context)
nparallelworkers = 8  # workers on grid, always 8
sectodayconversion = 0.00001157407  # seconds to days conversion factor

# Performing calculations
expectedrunningtime = (
    ntargetevents
    * runningtime
    * nparallelworkers
    * sectodayconversion
    / (nproducedevents * 10000)
)
expectedresources = ntargetevents * sizetest / nproducedevents  # in MB

# Formatting the output as a string for storage in txt
output = (
    f"Input size: {sizetest} MB\n"
    f"Global runtime: {runningtime} s\n"
    "------------------------------------\n"
    f"Expected running time: {expectedrunningtime} days @ 10kCPU\n"
    f"Expected size: {expectedresources / 1.e+6} TB"
)

# Writing the output to a text file
with open(output_path, "w") as file:
    file.write(output)
