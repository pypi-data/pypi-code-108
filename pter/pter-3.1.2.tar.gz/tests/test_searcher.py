import unittest
import pathlib
import datetime

from pytodotxt import Task

from pter.searcher import Searcher
from pter.source import Source


class FakeSource:
    def __init__(self, tasks):
        self.tasks = tasks
        self.filename = pathlib.Path('/tmp/test.txt')


class SearcherTest(unittest.TestCase):
    def setUp(self):
        self.searcher = Searcher('', False)

    def search(self, text, tasks):
        self.searcher.text = text
        self.searcher.parse()
        result = []
        source = Source(FakeSource(tasks))
        source.update_contexts_and_projects()
        self.searcher.update_sources([source])
        for task in source.tasks:
            task.todotxt = source
            if self.searcher.match(task):
                result.append(task)
        return result


class TestDue(SearcherTest):
    TASKS = [Task("Soon due:9999-12-31 id:1"),
             Task("Passed due:1900-01-01 id:2"),
             Task("No due date id:3")]

    def test_due(self):
        results = self.search("due:yes", self.TASKS)

        self.assertEqual(len(results), 2)
        self.assertEqual(set(sum([r.attributes['id'] for r in results], start=[])),
                         {'1', '2'})

    def test_no_due(self):
        results = self.search("due:no", self.TASKS)

        self.assertEqual(len(results), 1)
        self.assertEqual(set(sum([r.attributes['id'] for r in results], start=[])),
                         {'3',})

    def test_due_before0(self):
        results = self.search("duebefore:1890-01-01", self.TASKS)
        self.assertEqual(len(results), 0)

    def test_due_before1(self):
        results = self.search("duebefore:2000-01-01", self.TASKS)

        self.assertEqual(len(results), 1)
        self.assertEqual(set(sum([r.attributes['id'] for r in results], start=[])),
                         {'2',})

    def test_due_after0(self):
        results = self.search("dueafter:9999-12-31", self.TASKS)
        self.assertEqual(len(results), 0)

    def test_due_after2(self):
        results = self.search("dueafter:1899-12-31", self.TASKS)

        self.assertEqual(len(results), 2)
        self.assertEqual(set(sum([r.attributes['id'] for r in results], start=[])),
                         {'1', '2',})

    def test_due_between(self):
        results = self.search("dueafter:1899-12-31 duebefore:9999-12-31", self.TASKS)

        self.assertEqual(len(results), 1)
        self.assertEqual(set(sum([r.attributes['id'] for r in results], start=[])),
                         {'2',})

    def test_relative_due_after_date(self):
        today = datetime.datetime.now().strftime(Task.DATE_FMT)
        results = self.search("dueafter:yesterday",
                              [Task(f"id:1 Some task due:{today}"),
                               Task("id:2 Some task without due date"),
                               Task("id:3 Another task due:1900-01-01")])

        self.assertEqual(len(results), 1)
        self.assertEqual(set(sum([r.attributes['id'] for r in results], start=[])),
                         {'1',})

    def test_relative_due_date(self):
        today = datetime.datetime.now().strftime(Task.DATE_FMT)
        results = self.search("due:today",
                              [Task(f"id:1 Some task due:{today}"),
                               Task("id:2 Some task without due date"),
                               Task("id:3 Another task due:1900-01-01")])

        self.assertEqual(len(results), 1)
        self.assertEqual(set(sum([r.attributes['id'] for r in results], start=[])),
                         {'1',})


class TestCreated(SearcherTest):
    TASKS = [Task("1900-01-01 A bit older id:1"),
             Task(f"{datetime.datetime.now().strftime(Task.DATE_FMT)} Created today id:2"),
             Task("9876-12-31 I hope there are better tools than pter available by then! id:3"),
             Task("What person wouldn't add a creation date to a task? Right. Me. id:4")]

    def test_relative_created1(self):
        results = self.search("createdbefore:tomorrow", self.TASKS)

        self.assertEqual(len(results), 2)
        self.assertEqual(set(sum([r.attributes['id'] for r in results], start=[])),
                         {'1', '2'})

    def test_relative_created2(self):
        results = self.search("createdafter:-2", self.TASKS)

        self.assertEqual(len(results), 2)
        self.assertEqual(set(sum([r.attributes['id'] for r in results], start=[])),
                         {'2', '3'})


class TestCompleted(SearcherTest):
    TASKS = [Task("x 2004-12-31 1830-01-01 That took a while id:1"),
             Task("1831-01-01 Another old one id:2"),
             Task("x Task without creation or completion date id:3"),
             Task("x 9999-12-31 2004-12-31 Sure, that's when I finished it id:4")]

    def test_relative1(self):
        results = self.search("completedbefore:today", self.TASKS)

        self.assertEqual(len(results), 1)
        self.assertEqual(set(sum([r.attributes['id'] for r in results], start=[])),
                         {'1',})


class TestImportance(SearcherTest):
    TASKS = [Task("(A) important and urgent id:1"),
             Task("(B) important id:2"),
             Task("(C) urgent id:3"),
             Task("(D) neither id:4"),
             Task("meh! id:5")]

    def test_pri_match(self):
        results = self.search('pri:A', self.TASKS)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attributes.get('id'), ['1'])

    def test_no_pri_match(self):
        results = self.search('not:pri:A', self.TASKS)

        self.assertEqual(len(results), 4)
        self.assertEqual(set(sum([r.attributes['id'] for r in results], start=[])),
                         {'2', '3', '4', '5'})

    def test_less_important(self):
        results = self.search('lessimportant:b', self.TASKS)

        self.assertEqual(len(results), 3)
        self.assertEqual(set(sum([r.attributes['id'] for r in results], start=[])),
                         {'3', '4', '5'})

    def test_more_important(self):
        results = self.search('moreimportant:C', self.TASKS)

        self.assertEqual(len(results), 2)
        self.assertEqual(set(sum([r.attributes['id'] for r in results], start=[])),
                         {'1', '2'})

    def test_importance_range(self):
        results = self.search('mi:d li:a', self.TASKS)

        self.assertEqual(len(results), 2)
        self.assertEqual(set(sum([r.attributes['id'] for r in results], start=[])),
                         {'2', '3'})


class TestAfter(SearcherTest):
    def test_show_all(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 after:1')]
        results = self.search('after:', tasks)
        self.assertEqual(len(results), 2)

    def test_hide_after(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 after:1')]
        results = self.search('', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['1'])

    def test_recursion(self):
        tasks = [Task('a id:1 after:3'),
                 Task('b id:2 after:1'),
                 Task('c id:3 after:2')]
        results = self.search('', tasks)
        self.assertEqual(len(results), 0)

    def test_more_parents(self):
        tasks = [Task('a id:1'),
                 Task('b id:2'),
                 Task('c after:1,2')]
        results = self.search('', tasks)
        self.assertEqual(len(results), 2)

        results = self.search('after:1', tasks)
        self.assertEqual(len(results), 1)
        self.assertIn('c', str(results[0]))

    def test_parent_completed(self):
        tasks = [Task('x a id:1'),
                 Task('b after:1 id:test')]
        results = self.search('done:n', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['test'])

    def test_some_parents_completed(self):
        tasks = [Task('x a id:1'),
                 Task('b id:2'),
                 Task('c id:3 after:1,2')]
        results = self.search('done:n', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['2'])

    def test_some_parents_completed2(self):
        tasks = [Task('x a id:1'),
                 Task('b id:2'),
                 Task('c id:3 after:1 after:2')]
        results = self.search('done:n', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['2'])

    def test_all_parents_completed(self):
        tasks = [Task('x a id:1'),
                 Task('x b id:2'),
                 Task('c id:3 after:1,2')]
        results = self.search('done:n', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['3'])

    def test_all_parents_completed2(self):
        tasks = [Task('x a id:1'),
                 Task('x b id:2'),
                 Task('c id:3 after:1 after:2')]
        results = self.search('done:n', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['3'])


class TestIDs(SearcherTest):
    def test_id(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1')]
        results = self.search('id:1', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['1'])

    def test_id_not_there(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1')]
        results = self.search('id:3', tasks)
        self.assertEqual(len(results), 0)

    def test_ids(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1')]
        results = self.search('id:1,2', tasks)
        self.assertEqual(len(results), 2)

    def test_ids2(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1')]
        results = self.search('id:1 id:2', tasks)
        self.assertEqual(len(results), 2)

    def test_not_id(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1')]
        results = self.search('-id:1', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['2'])

    def test_not_ids(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1')]
        results = self.search('-id:1,2', tasks)
        self.assertEqual(len(results), 0)

    def test_not_ids2(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1')]
        results = self.search('-id:1 -id:2', tasks)
        self.assertEqual(len(results), 0)

    def test_has_id(self):
        tasks = [Task('a id:1'),
                 Task('b')]
        results = self.search('id:', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['1'])

    def test_has_no_id(self):
        tasks = [Task('a id:1'),
                 Task('b')]
        results = self.search('-id:', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(str(results[0]), 'b')


class TestRef(SearcherTest):
    def test_ref_not_there(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1')]
        results = self.search('ref:2', tasks)
        self.assertEqual(len(results), 0)

    def test_ref_search(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1')]
        results = self.search('ref:1', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['2'])

    def test_after_search(self):
        tasks = [Task('x a id:1'),
                 Task('t id:2 after:1')]
        results = self.search('ref:1', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['2'])

    def test_ref_multiple(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1,4')]
        results = self.search('ref:4', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['2'])

    def test_ref_multiple2(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1 ref:4')]
        results = self.search('ref:4', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['2'])


class SearchFilename(SearcherTest):
    def test_match(self):
        tasks = [Task('a id:1')]
        results = self.search('file:test', tasks)
        self.assertEqual(len(results), 1)

    def test_no_match(self):
        tasks = [Task('a id:1')]
        results = self.search('file:nope', tasks)
        self.assertEqual(len(results), 0)

    def test_match_not(self):
        tasks = [Task('a id:1')]
        results = self.search('not:file:test', tasks)
        self.assertEqual(len(results), 0)

    def test_no_match_not(self):
        tasks = [Task('a id:1')]
        results = self.search('not:file:nope', tasks)
        self.assertEqual(len(results), 1)
