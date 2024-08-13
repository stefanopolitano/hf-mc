runningtime = 3648.21 # s
ntargetevents = 1.e+9
nproducedevents = 400
sizetest = 15.98 #  
nparallelworkers = 8  # always 8 on grid
sectodayconversion = 0.00001157407

# do the math
expectedrunningtime = ntargetevents * runningtime * nparallelworkers * sectodayconversion / (nproducedevents*10000)
print(f"Expected running time: {expectedrunningtime} days @ 10kCPU")

expectedresources = ntargetevents * sizetest / (nproducedevents)
print(f"Expected size: {expectedresources/1.e+6} TB")