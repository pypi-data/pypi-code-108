import pandas as pd

from beep.protocol.maccor import Procedure

parameters = pd.read_csv("./parameters.csv")
for index, protocol_params in parameters.iterrows():
    proc = Procedure.from_file("./testV1.000")
    proc["MaccorTestProcedure"]["ProcSteps"]["TestStep"][8]["StepValue"] = protocol_params["power"]
    proc.to_file("./project{}.000".format(str(index)))
