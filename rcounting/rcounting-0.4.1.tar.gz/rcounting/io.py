import functools
import logging
import os
import sqlite3
from pathlib import Path

import pandas as pd

from rcounting import models, parsing

printer = logging.getLogger(__name__)


class ThreadLogger:
    """Simple class for logging either to a database or to a csv file"""

    def __init__(self, sql, output_directory, filename=None):
        self.sql = sql
        self.output_directory = output_directory
        self.last_checkpoint = ""
        if self.sql:
            self.setup_sql(filename)
        self.log = self.log_sql if self.sql else self.log_csv

    def setup_sql(self, filename):
        """Connect to the database and get list of existing submissions, if any"""
        last_checkpoint = ""
        known_submissions = []
        if filename is None:
            filename = "counting.sqlite"
        path = self.output_directory / filename
        printer.warning("Writing submissions to sql database at %s", path)
        db = sqlite3.connect(path)
        try:
            known_submissions = pd.read_sql("select * from submissions", db)[
                "submission_id"
            ].tolist()
            checkpoints = pd.read_sql("select submission_id from last_submission", db)
            last_checkpoint = checkpoints.iat[-1, 0]
        except pd.io.sql.DatabaseError:
            pass
        self.db = db
        self.last_checkpoint = last_checkpoint
        self.known_submissions = known_submissions

    def is_already_logged(self, comment):
        """Determine whether a submission has already been logged"""
        if self.sql:
            return comment.submission.id in self.known_submissions
        body = parsing.strip_markdown_links(comment.body)
        basecount = parsing.find_count_in_text(body) - 1000
        hoc_path = self.output_directory / Path(f"{basecount}.csv")
        return os.path.isfile(hoc_path)

    def log_sql(self, comment, df):
        """Save one submission to a database"""
        submission = pd.Series(models.Submission(comment.submission).to_dict())
        submission = submission[["submission_id", "username", "timestamp", "title", "body"]]
        submission["integer_id"] = int(submission["submission_id"], 36)
        df.to_sql("comments", self.db, index_label="position", if_exists="append")
        submission.to_frame().T.to_sql("submissions", self.db, index=False, if_exists="append")

    def log_csv(self, comment, df):
        """Save one submission to a csv file"""
        extract_count = functools.partial(parsing.find_count_in_text, raise_exceptions=False)
        n = int(1000 * ((df["body"].apply(extract_count) - df.index).median() // 1000))
        path = self.output_directory / Path(f"{n}.csv")

        columns = ["username", "timestamp", "comment_id", "submission_id"]
        output_df = df.set_index(df.index + n)[columns].iloc[1:]
        printer.debug("Writing submission log to %s", path)
        header = ["username", "timestamp", "comment_id", "submission_id"]
        with open(path, "w", encoding="utf8") as f:
            print(f"# {comment.submission.title}", file=f)
            print(output_df.to_csv(index_label="count", header=header), file=f, end="")

    def update_checkpoint(self):
        if not self.sql:
            return
        newest_submission = pd.read_sql(
            "select submission_id from submissions order by integer_id", self.db
        ).iloc[-1]
        newest_submission.name = "submission_id"
        newest_submission.to_sql("last_submission", self.db, index=False, if_exists="append")
