import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
from uuid import uuid4


def generate_id():
    return str(uuid4())[:8]


class BasePredictor(object):

    def get_keys(self):
        pass

    def process(self, task):
        pass


class SpacyPredictor(BasePredictor):

    def __init__(self, name=''):
        self.name = name
        self.nlp = spacy.load('en_core_web_sm')
        self.nlp.add_pipe('spacytextblob')

    def get_keys(self):
        return [
            'token',
            'ner',
            'sentiment'
        ]

    def process_many(self, tasks):
        return list(map(self.process, tasks))

    def process(self, task):
        text = task['data']['text']
        doc = self.nlp(text)
        predictions = []
        for ent in doc.ents:
            # add named entity
            ent_id = generate_id()
            head_id = generate_id()
            predictions.append({
                'id': ent_id,
                'from_name': 'ner',
                'to_name': 'text',
                'type': 'labels',
                'value': {
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'labels': [ent.label_],
                    'text': ent.text
                }
            })
            # add syntactic head
            head = ent.root.head
            predictions.append({
                'id': head_id,
                'from_name': 'head',
                'to_name': 'text',
                'type': 'labels',
                'value': {
                    'start': head.idx,
                    'end': head.idx + len(head.text),
                    'labels': [head.pos_],
                    'text': head.text
                }
            })
            # add dependency
            predictions.append({
                'type': 'relation',
                'from_id': head_id,
                'to_id': ent_id,
                'direction': 'right',
                'labels': [ent.root.dep_]
            })

        # add sentiment
        predictions.append({
            'id': generate_id(),
            'from_name': 'sentiment',
            'to_name': 'text',
            'type': 'choices',
            'value': {
                'choices': ['positive' if doc._.polarity > 0 else 'negative']
            }
        })
        return predictions
