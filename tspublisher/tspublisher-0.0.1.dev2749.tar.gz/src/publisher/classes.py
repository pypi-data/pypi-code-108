from __future__ import absolute_import, division, print_function, unicode_literals


class Commit(object):

    NOTYPE = 0
    PUBLIC = 1
    PRIVATE = 2
    TESTING = 3

    def __init__(self, commit_id, comment, author, note):
        self.id = commit_id
        self.comment = comment
        self.author = author
        self.note = note

    def __str__(self):
        return '\n'.join([self.comment,
                          'Author: {0}'.format(self.author),
                          'Current distribution group: {0}'.format(self.note if self.note else 'Not published'),
                          '----------------------------'])

    @property
    def commit_type(self):

        if self.note is None:
            return self.NOTYPE

        note = self.note.lower()

        if "public" in note:
            return self.PUBLIC

        if "ts-testing" in note:
            return self.TESTING

        return self.PRIVATE

    def copy_with_new_note(self, new_note):
        return Commit(self.id, self.comment, self.author, new_note)

    def filter_similar_commits(self, commits):
        def is_note_similar(c):
            return c.commit_type == self.commit_type and c.note is not None

        return [c for c in commits if is_note_similar(c)]
