from ssmdevices.instruments import MiniCircuitsRCDAT

myatten = MiniCircuitsRCDAT(resource='11604210008',frequency=6000e6, calibration_path='12104060073.csv.xz')
with myatten:
    myatten.attenuation = 20
    print(myatten.attenuation)
    print(myatten.frequency)