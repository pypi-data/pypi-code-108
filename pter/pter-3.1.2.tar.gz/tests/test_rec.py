import unittest
import datetime

from pytodotxt import Task, TodoTxt

from pter import utils


TODAY = datetime.datetime.now().strftime(Task.DATE_FMT)
YESTERDAY = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime(Task.DATE_FMT)
TOMORROW = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(Task.DATE_FMT)


class TestableTodoTxt(TodoTxt):
    def save(self, *args, **kwargs):
        pass


class TestRecurringTask(unittest.TestCase):
    def setUp(self):
        self.todotxt = TestableTodoTxt('./test.txt')

    def test_create_new(self):
        task = Task('2021-06-01 Do something rec:1w',
                    todotxt=self.todotxt)
        self.todotxt.tasks.append(task)

        utils.toggle_done(task, [], False, False)

        self.assertEqual(task.creation_date, datetime.date(2021, 6, 1))
        self.assertTrue(task.is_completed)
        self.assertEqual(len(self.todotxt.tasks), 2)
        self.assertIsNot(self.todotxt.tasks[-1], task)

    def test_reuse(self):
        task = Task('2021-06-01 Do something rec:1w',
                    todotxt=self.todotxt)
        self.todotxt.tasks.append(task)

        utils.toggle_done(task, [], True, False)

        self.assertEqual(task.creation_date, datetime.date.today())
        self.assertFalse(task.is_completed)
        self.assertEqual(len(self.todotxt.tasks), 1)

    def test_push_due_normal(self):
        task = Task(f'2021-06-01 Do something rec:1w due:{TOMORROW}')
        self.todotxt.tasks.append(task)

        utils.toggle_done(task, [], True, False)

        self.assertEqual(len(self.todotxt.tasks), 1)
        self.assertFalse(task.is_completed)
        self.assertEqual(task.creation_date, datetime.date.today())
        expected_due_date = (datetime.datetime.now()
                             + datetime.timedelta(days=7)).strftime(Task.DATE_FMT)
        self.assertEqual(task.attributes['due'][0], expected_due_date)

    def test_push_due_strict(self):
        task = Task(f'2021-06-01 Do something rec:+1w due:{TOMORROW}')
        self.todotxt.tasks.append(task)

        utils.toggle_done(task, [], True, False)

        self.assertEqual(len(self.todotxt.tasks), 1)
        self.assertFalse(task.is_completed)
        self.assertEqual(task.creation_date, datetime.date.today())
        expected_due_date = (datetime.datetime.now()
                             + datetime.timedelta(days=8)).strftime(Task.DATE_FMT)
        self.assertEqual(task.attributes['due'][0], expected_due_date)

    def test_push_t_normal(self):
        task = Task(f'2021-06-01 Do something rec:1w t:{YESTERDAY}')
        self.todotxt.tasks.append(task)

        utils.toggle_done(task, [], True, False)

        self.assertEqual(len(self.todotxt.tasks), 1)
        self.assertFalse(task.is_completed)
        self.assertEqual(task.creation_date, datetime.date.today())
        expected_due_date = (datetime.datetime.now()
                             + datetime.timedelta(days=7)).strftime(Task.DATE_FMT)
        self.assertEqual(task.attributes['t'][0], expected_due_date)

    def test_push_t_strict(self):
        task = Task(f'2021-06-01 Do something rec:+1w t:{YESTERDAY}')
        self.todotxt.tasks.append(task)

        utils.toggle_done(task, [], True, False)

        self.assertEqual(len(self.todotxt.tasks), 1)
        self.assertFalse(task.is_completed)
        self.assertEqual(task.creation_date, datetime.date.today())
        expected_t_date = (datetime.datetime.now()
                           + datetime.timedelta(days=6)).strftime(Task.DATE_FMT)
        self.assertEqual(task.attributes['t'][0], expected_t_date)

    def test_create_due_and_t_strict(self):
        task = Task(f'2021-06-01 Do something rec:+1w t:{YESTERDAY} due:{TOMORROW}',
                    todotxt=self.todotxt)
        self.todotxt.tasks.append(task)

        utils.toggle_done(task, [], False, False)

        self.assertEqual(len(self.todotxt.tasks), 2)
        self.assertTrue(task.is_completed)
        self.assertEqual(task.completion_date, datetime.date.today())

        other = self.todotxt.tasks[-1]
        self.assertIsNot(task, other)
        self.assertFalse(other.is_completed)
        expected_due_date = (datetime.datetime.now()
                             + datetime.timedelta(days=8)).strftime(Task.DATE_FMT)
        expected_t_date = (datetime.datetime.now()
                           + datetime.timedelta(days=6)).strftime(Task.DATE_FMT)
        self.assertEqual(other.attributes['due'][0], expected_due_date)
        self.assertEqual(other.attributes['t'][0], expected_t_date)

    def test_create_due_and_t_normal(self):
        task = Task(f'2021-06-01 Do something rec:1w t:{YESTERDAY} due:{TOMORROW}',
                    todotxt=self.todotxt)
        self.todotxt.tasks.append(task)

        utils.toggle_done(task, [], False, False)

        self.assertEqual(len(self.todotxt.tasks), 2)
        self.assertTrue(task.is_completed)
        self.assertEqual(task.completion_date, datetime.date.today())

        other = self.todotxt.tasks[-1]
        self.assertIsNot(task, other)
        self.assertFalse(other.is_completed)
        expected_due_date = (datetime.datetime.now()
                             + datetime.timedelta(days=7)).strftime(Task.DATE_FMT)
        expected_t_date = (datetime.datetime.now()
                           + datetime.timedelta(days=5)).strftime(Task.DATE_FMT)
        self.assertEqual(other.attributes['due'][0], expected_due_date)
        self.assertEqual(other.attributes['t'][0], expected_t_date)

    def test_create_due_and_t_same(self):
        task = Task(f'2021-06-01 Do something rec:1w t:{TODAY} due:{TODAY}',
                    todotxt=self.todotxt)
        self.todotxt.tasks.append(task)

        utils.toggle_done(task, [], False, False)

        self.assertEqual(len(self.todotxt.tasks), 2)
        self.assertTrue(task.is_completed)
        self.assertEqual(task.completion_date, datetime.date.today())

        other = self.todotxt.tasks[-1]
        self.assertIsNot(task, other)
        self.assertFalse(other.is_completed)
        expected_due_date = (datetime.datetime.now()
                             + datetime.timedelta(days=7)).strftime(Task.DATE_FMT)
        expected_t_date = (datetime.datetime.now()
                           + datetime.timedelta(days=7)).strftime(Task.DATE_FMT)
        self.assertEqual(other.attributes['due'][0], expected_due_date)
        self.assertEqual(other.attributes['t'][0], expected_t_date)
