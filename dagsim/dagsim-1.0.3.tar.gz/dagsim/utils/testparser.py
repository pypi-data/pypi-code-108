from dagsim.utils.parser import DagSimSpec

testValue = 2
parser = DagSimSpec(file_name="testyml.yml")
data = parser.parse(draw=False)
print(data)
