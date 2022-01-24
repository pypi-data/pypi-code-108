from __future__ import annotations
from typing import Any, Union
import traceback, os

from klee.internal import Structure, log
from klee import files

class InsightText:
    def __init__(self, type = '', text = '', defense = ''):
        self.type = type or ''
        self.text = text or ''
        self.defense = defense or ''

    def __add__(self, other):
        return InsightText(self.type or other.type, self.text or other.text, self.defense or other.defense)

class InsightDict(dict):
    def __init__(self, nodes = None):
        if nodes is None:
            nodes = dict()
        super().__init__(nodes)

    def __add__(self, other: Union[InsightDict, dict]):
        if isinstance(other, dict):
            other = InsightDict(other)
        return InsightDict({key: self.get(key) + other.get(key)
            for key in {*self.keys(), *other.keys()}})

    def get(self, key: Any) -> InsightText:
        return super().get(key, InsightText())

def load_insights() -> InsightDict:
    insights: InsightDict = InsightDict()
    for function in (read_local_files, read_engine_result):
        try:
            insights += function()
        except:
            log.error(traceback.format_exc())

    with open(Structure.reference.insights, 'w') as file:
        file.write(f"# Insights for *{os.path.basename(os.getcwd())}* \n")
        for key in sorted(insights, reverse=True):
            x: InsightText = insights[key]
            md_text = x.text.replace("\n", "\n\n")
            html_defense = x.defense.replace("\n", "<br>")
            file.write(f"\n# Label {key} :: {x.type} \n")
            file.write(f"\n{md_text}\n")
            file.write(f'\n<b style="color:#f57070">\n{html_defense}\n</b>\n')

    return insights


def read_engine_result() -> InsightDict:
    with files.Inspection():
        # noinspection PyUnresolvedReferences
        from engine.result import EngineResult

    insights = InsightDict()
    for field in ('type', 'text', 'defense'):
        insights += {k: InsightText(**{field: v}) for k, v in
            getattr(EngineResult, 'insight_' + field, {}).items()}

    return insights

def read_local_files(folder: str = '') -> InsightDict:
    insights, search_dirs = InsightDict(), [*Structure.iter_search()]
    # custom directory
    if folder:
        search_dirs.append(folder)

    for directory in search_dirs:
        # insights_and_defense.csv / insights.csv / defense.csv
        for option in ('insights_and_defenses', 'insights_and_defense', 'insights', 'defense', 'defenses'):
            ins_csv = os.path.join(directory, option + '.csv')
            if os.path.exists(ins_csv):
                for row in files.read_csv(ins_csv, normalize = True):
                    multilabel = m_get(row, 'insightnode', 'node', 'nodelabel', 'label')
                    for label in map(lambda x: x.strip(), multilabel.split(',')):
                        insights.setdefault(label, InsightText())
                        insights[label] += InsightText(
                            type = m_get(row, 'insighttype'),
                            text = m_get(row, 'insighttext'),
                            defense = m_get(row, 'defensetext', 'defense')
                        )
        # defense.json
        defense_json = os.path.join(directory, 'defense.json')
        if os.path.exists(defense_json):
            for label, defense in files.read_json(defense_json).items():
                insights.setdefault(label, InsightText())
                insights[label] += InsightText(defense=defense)
        # insights.json
        insight_json = os.path.join(directory, 'insights.json')
        if os.path.exists(insight_json):
            for label, combined in files.read_json(insight_json).items():
                i_type, text = map(lambda x: x.strip(), combined.split(":"))
                insights.setdefault(label, InsightText())
                insights[label] += InsightText(type=i_type, text=text)
        # test_dataset.csv
        dataset_csv = os.path.join(directory, 'test_dataset.csv')
        if os.path.exists(dataset_csv):
            for idx, row in enumerate(files.read_csv(dataset_csv, normalize=True), 1):
                insights[f"row-{idx}"] = InsightText(defense = m_get(row, 'policyexcerpt'))
    return insights

def m_get(_dict, *cols):
    for key in cols:
        value = _dict.get(key)
        if value:
            return value
    return ''
