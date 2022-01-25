import base64
def ToBase64(file):
    with open(file, 'rb') as fileObj:
        image_data = fileObj.read()
        base64_data = base64.b64encode(image_data)
        return base64_data

res = ToBase64('D:/gitttt/dobotedu/test/4.jpg')
print(res)
res2 = face.create_person(group_id="123", person_name="shua", person_id="333", image=res)
print(res2)