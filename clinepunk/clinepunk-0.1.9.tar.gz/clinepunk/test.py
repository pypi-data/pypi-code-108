import io
import pickle

from clinepunk import model

lst = [
    model.Word(word="test", length=4),
    model.Word(word="better", length=6),
]

col = model.WordCollection(lst)
pickleBuffer = io.BytesIO()
pickle.dump(col, pickleBuffer)
unpickled = pickle.loads(pickleBuffer.getbuffer())
print(unpickled)
