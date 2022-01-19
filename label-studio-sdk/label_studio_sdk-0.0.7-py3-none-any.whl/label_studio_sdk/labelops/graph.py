import neo4j
from neo4j import GraphDatabase

import logging
neo4j_log = logging.getLogger("neo4j.bolt")
neo4j_log.setLevel(logging.DEBUG)


class LabelGraphDB(object):

    def __init__(self, uri, db_name, password):
        self.uri = uri
        self.db_name = db_name
        self.password = password

        self._driver = GraphDatabase.driver(uri, auth=(db_name, password))

    def run(self, command, parameters=None):
        with self._driver.session(default_access_mode=neo4j.WRITE_ACCESS) as session:
            result = session.run(command, parameters)
            return list(result)

    def clear_graph(self):
        self.run('MATCH (n) DETACH DELETE n')

    def close(self):
        self._driver.close()

    def _safe_int(self, i):
        return int(i) if i is not None else -1

    def _convert(self, result, v):
        return {
            'start': self._safe_int(result['value'].get('start')),
            'end': self._safe_int(result['value'].get('end'))
        }, result['value'][result['type']][0], result['from_name'], {'text': result['value'].get('text')}

    def prepare_singletons_pairs(self, task):
        singletons, pairs = [], []
        predictions = task['predictions']
        for prediction in predictions:
            result = prediction['result']
            model_version = prediction['model_version']
            regions = {r['id']: self._convert(r, model_version) for r in result if 'id' in r}
            relations = [(r['from_id'], r['to_id'], r['labels'][0]) for r in result if r['type'] == 'relation']
            ids_with_relations = set(id for pair in relations for id in pair[:2])
            singleton_regions = [id for id in regions if id not in ids_with_relations]

            # build singletons
            for id in singleton_regions:
                singletons.append({
                    'task': task['id'],
                    'region': regions[id][0],
                    'region_label': regions[id][1],
                    'region_type': regions[id][2],
                    'data': regions[id][3]
                })

            print(f'{len(singletons)} singletons found.')

            # build pairs
            for from_id, to_id, label in relations:
                pairs.append({
                    'task': task['id'],
                    'region_from': regions[from_id][0],
                    'region_from_label': regions[from_id][1],
                    'region_from_type': regions[from_id][2],
                    'region_from_data': regions[from_id][3],
                    'region_to': regions[to_id][0],
                    'region_to_label': regions[to_id][1],
                    'region_to_type': regions[to_id][2],
                    'region_to_data': regions[to_id][3],
                    'relation': label,
                })

            print(f'{len(pairs)} pairs found.')
        return singletons, pairs

    def unwind_tasks(self, tasks):

        prep_tasks = []
        for task in tasks:
            singletons, pairs = self.prepare_singletons_pairs(task)
            prep_tasks.append({
                'id': task['id'],
                'data': task['data'],
                'singletons': singletons,
                'pairs': pairs
            })

        query1 = '''
            UNWIND $tasks as task
            CREATE (d:Data {label: 'data', task: task.id})
            SET d += task.data
            WITH task.singletons as singletons, d
                UNWIND singletons as s
                MERGE (d)-[:region]->(r:Region {task: s.task})-[:label]->(l:Label {label: s.region_label, type: s.region_type})
                SET r += s.region
            RETURN count(r)
        '''
        self.run(query1, parameters={'tasks': prep_tasks})

        query2 = '''
            UNWIND $tasks as task
            MATCH (d:Data {task: task.id})
            WITH task.pairs as pairs, d
                UNWIND pairs as p
                MERGE (d)-[:region]->(rf:Region {task: p.task})-[:label]->(:Label {label: p.region_from_label, type: p.region_from_type})
                MERGE (d)-[:region]->(rt:Region {task: p.task})-[:label]->(:Label {label: p.region_to_label, type: p.region_to_type})
                MERGE (rf)-[:relation]->(rt)
                MERGE (rf)-[:data]->(rfd:Data {label: 'data'})
                MERGE (rt)-[:data]->(rtd:Data {label: 'data'})
                SET rf += p.region_from
                SET rfd += p.region_from_data
                SET rt += p.region_to
                SET rtd += p.region_to_data
            RETURN count(*)
        '''
        result_pairs = self.run(query2, parameters={'tasks': prep_tasks})
        return 1

    def match_data_regex(self, regex):
        selector = []
        for k, v in regex.items():
            selector.append(f"d.{k} =~ '{v}'")
        selector = ' AND '.join(selector)
        query = f'''
            MATCH (d:Data)-[:region]->(r:Region {{start: -1, end: -1}})
            WHERE {selector}
            RETURN collect(id(r)) as ids
        '''
        results = self.run(query, parameters={'regex': regex})[0]
        return results.data()

    def match_labels(self, patterns):
        q = []
        nodes = []
        collects = {}
        for i, item in enumerate(patterns):
            item_id = item.get('id') or f'item{i}'
            node_name = f'r{i}'
            q.append(f'MATCH ({node_name}:Region)-->(:Label {{label: \'{item["label"]}\', type: \'{item["type"]}\'}})')
            nodes.append(node_name)
            if item.get('select'):
                collects[item_id] = f'collect(id({node_name})) as {item_id}'
        q = '\n'.join(q)
        query = f'''
            {q}
            MATCH {"-->".join(map(lambda n: f'({n})', nodes))}
            RETURN {",".join(collects.values())}
        '''

        results = self.run(query)[0]
        return results.data()

    def get_regions_by_ids(self, ids):
        query = '''
            MATCH (n)
            WHERE id(n) IN $ids
            RETURN n
        '''
        result = self.run(query, parameters={'ids': ids})
        return [r.data()['n'] for r in result]

    def get_regions_by_ids_with_data(self, ids):
        query = '''
            MATCH (d:Data)-->(r:Region)
            WHERE id(r) IN $ids
            RETURN r as region, d as data
        '''
        result = self.run(query, parameters={'ids': ids})
        return [r.data() for r in result]

    def commit(self, project):
        query = '''
            MATCH (l:Label)-->(r:Region)-->(t:Task)
            return l.label as label, r as region, t.id as task
        '''
        results = self.run(query)
        predictions = []
        for result in results:
            predictions.append({
                'task': result['task'],
                'result': result['label'],
                'score': 1.0
            })
        project.create_predictions(predictions)

