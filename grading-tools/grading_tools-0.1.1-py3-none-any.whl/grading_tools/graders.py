"""
The `graders` module contains all the grader classes.
"""
import pprint
import random
from math import isclose

import markdown
import pandas as pd


class BaseGrader(object):
    """
    Base class for all graders.

    Attributes
    ----------
    submission :
        Student's submission object.
    answer :
        Correct answer object.
    points : int or float, default=1
        Total point value awarded if submission is correct.
    score : int or float, default=0
        Student's current ``score``. Default is ``0`` because submission has yet to
        be graded.
    passed : bool
        Whether student's ``score`` is equal to or greater than possible ``points``.
        Default is ``False`` because submission has yet to be graded.
    comment : str
        Feedback one student's submission. Default is empty string because
        submission has yet to be graded. Note that you can use
        [Markdown syntax](https://daringfireball.net/projects/markdown/).

    """

    def __init__(self, submission, answer, points=1, score=0, passed=False, comment=""):
        self.answer = answer
        self.comment = comment
        self.passed = passed
        self.points = points
        self.score = score
        self.submission = submission

        if not isinstance(self.submission, type(self.answer)):
            raise TypeError(
                f"Your submission needs to be type {type(self.answer).__name__}, "
                f"not type {type(self.submission).__name__}."
            )

    def __repr__(self) -> str:
        rep_dict = {
            "points": self.points,
            "submission dtype": type(self.submission),
            "answer dtype": type(self.answer),
            "current score": self.score,
            "passed": self.passed,
            "comment": self.comment,
        }

        return pprint.pformat(rep_dict, indent=2, sort_dicts=False)

    def positive_comment(self) -> None:
        """Generate positive comment.

        Assigns a randomly-chosen comment to the ``comment`` attribute of grader object.

        Returns
        -------
        None

        """
        comments = [
            "🥳",
            "Awesome work.",
            "Boom! You got it.",
            "Correct.",
            "Excellent work.",
            "Excellent! Keep going.",
            "Good work!",
            "Party time! 🎉🎉🎉",
            "Python master 😁",
            "Yes! Keep on rockin'. 🎸" "That's right.",
            "That's the right answer. Keep it up!",
            "Very impressive.",
            "Way to go!",
            "Wow, you're making great progress.",
            "Yes! Great problem solving.",
            "Yes! Your hard work is paying off.",
            "You = coding 🥷",
            "You got it. Dance party time! 🕺💃🕺💃",
            "You're making this look easy. 😉",
            "Yup. You got it.",
        ]

        self.comment = random.choice(comments)

    def add_to_score(self, points=1) -> None:
        """Increment score.

        This method adds points to grader's `score` attribute, then checks if `score`
        meets `points` theshold. If threshold met, a positive comment is added to
        `comment` attribute.

        Parameters
        ----------
        points : int or float, default=1
            Number of points to add to `score` attribute.

        Returns
        -------
        None

        """
        self.score += points
        self.passed = self.score >= self.points
        # If there's already a comment, it's been added in another method
        if self.passed and self.comment == "":
            self.positive_comment()

    def update_comment(self, new_comment):
        """Change grader ``comment``.

        Parameters
        ----------
        new_comment : str
            Text of new comment. Note that you can use
            [Markdown syntax](https://daringfireball.net/projects/markdown/).

        """
        self.comment = new_comment

    def return_feedback(self, html=True) -> dict:
        """Return feedback to student.

        Parameters
        ----------
        html : bool, default=True
            If ``True`` converts comment text to HTML. This is only important is you
            the comment has been written using
            [Markdown syntax](https://daringfireball.net/projects/markdown/).

        Returns
        -------
        feedback_dict : dict
            Dictionary has three keys:
            ``{"score": self.score, "passed": self.passed, "comment": comment}``

        """
        if html:
            comment = markdown.markdown(self.comment)
        else:
            comment = self.comment
        feedback_dict = {"score": self.score, "passed": self.passed, "comment": comment}
        return feedback_dict


class PythonGrader(BaseGrader):
    """
    Grader for evaluating `data types <https://docs.python.org/3/library/stdtypes.html>`_ from the Python standard library.

    """

    def __init__(self, submission, answer, points=1):
        super().__init__(submission, answer, points)

    def check_list(self, match_order=True, tolerance=0.0, return_bool=False):
        """Evaluate student's submitted list.

        Evaluate whether ``submission`` list matches ``answer``. Depending on parameter
        settings, submission can be in different order, and there is tolerance if
        numerical items don't exactly match answer. Note that, in most cases, you
        will have to allow for some tolerance when a submission has floating-point
        numbers.

        Parameters
        ----------
        match_order : bool, default=True
            Do the items in the submitted list need to be in the same order as those in
            the answer list?

        tolerance : float, default=0.0
            For numerical values, what is the maximum allowed difference between ``submission`` and
            ``answer``? If 0.0, values must be identical. If 0.1, values must be within 10%
            must be within 10% of each other (relative to the larger absolute value of the two).
            Uses `math.isclose() <https://docs.python.org/3/library/math.html#math.isclose>`_.

        return_bool : bool, default=False
            Whether to return ``self.passed`` once grading is complete. You'll need this if
            you want to design your own grading workflow beyond the default.

        Examples
        --------
        If values must match, but order isn't important.

        >>> g = PythonGrader(submission=[1, 0], answer=[0, 1])
        >>> g.check_list(match_order=False, tolerance=0.0, return_bool=True)
        True

        If order must match, and numerical values must be exact match.

        >>> g = PythonGrader(submission=[1.1, 2.2], answer=[1, 2])
        >>> g.check_list(match_order=True, tolerance=0.0, return_bool=True)
        False

        If order must match, but numerical values don't need to be exact match.

        >>> g = PythonGrader(submission=[1.1, 2.2], answer=[1, 2])
        >>> g.check_list(match_order=True, tolerance=0.1, return_bool=True)
        True

        """
        if not isinstance(self.submission, list):
            raise TypeError(
                f"check_list method can only be used with list submissions, not {type(self.submission).__name__}."
            )

        if len(self.submission) != len(self.answer):
            self.update_comment(
                f"Your submission should have `{len(self.answer)}` items, not `{len(self.submission)}`."
            )
            return

        if match_order is False:
            self.submission.sort()
            self.answer.sort()

        if not tolerance and self.submission == self.answer:
            self.add_to_score()
        elif tolerance and all(
            isclose(a, b, rel_tol=tolerance)
            for a, b in zip(self.submission, self.answer)
        ):
            self.add_to_score()
        else:
            self.update_comment("Your submission doesn't match the expected result.")

        if return_bool:
            return self.passed
        else:
            return

    def check_dict(self, tolerance=0.0, return_bool=False):
        """Evaluate student's submitted dict.

        Evaluate whether ``submission`` dict matches ``answer``. Depending on parameter
        settings, there is tolerance if numerical items don't exactly match answer.
        Note that, in most cases, you will have to allow for some tolerance when a
        submission has floating-point numbers.

        Parameters
        ----------
        tolerance : float, default=0.0
            For numerical values (not keys, just values), what is the maximum allowed
            difference between ``submission`` and ``answer``? If 0.0, values must be
            identical. If 0.1, values must be within 10% must be within 10% of each
            other (relative to the larger absolute value of the two). Uses
            `math.isclose() <https://docs.python.org/3/library/math.html#math.isclose>`_.

        return_bool : bool, default=False
            Whether to return ``self.passed`` once grading is complete. You'll need this if
            you want to design your own grading workflow beyond the default.

        Examples
        --------
        Check if dictionaries match. (Note that key order doesn't matter for
        dictionaries in Python 3.9.)

        >>> g = PythonGrader(submission={"a": 1, "b": 2}, answer={"a": 1, "b": 2})
        >>> g.check_dict(tolerance=0.0, return_bool=True)
        True

        Check if dictionaries match, allowing for approximate value matches.

        >>> g = PythonGrader(submission={"a": 1, "b": 2.2}, answer={"a": 1, "b": 2})
        >>> g.check_dict(tolerance=0.1, return_bool=True)
        True

        When submission keys don't match answer, grader alerts student.

        >>> g = PythonGrader(submission={"a": 1, "z": 2}, answer={"a": 1, "b": 2})
        >>> g.check_dict(tolerance=0.0, return_bool=False)
        >>> print(g.comment)
        One or more of the keys in your dictionary doesn't match the expected result.

        When submission keys match answer but values don't, grader tells student which
        key-value pair is wrong.

        >>> g = PythonGrader(submission={"a": 1, "b": 2.2}, answer={"a": 1, "b": 2})
        >>> g.check_dict(tolerance=0.0, return_bool=False)
        >>> print(g.comment)
        The value for key `b` doesn't match the expected result.

        """

        if not isinstance(self.submission, dict):
            raise TypeError(
                f"check_dict method can only be used with dict submissions, not {type(self.submission).__name__}."
            )

        # Exact match, give point and done
        if self.submission == self.answer:
            self.add_to_score()
            if return_bool:
                return self.passed
            else:
                return

        # Is it the keys that don't match?
        if self.submission.keys() != self.answer.keys():
            self.update_comment(
                "One or more of the keys in your dictionary doesn't match the expected result."
            )
            if return_bool:
                return self.passed
            else:
                return

        # If keys match, iteratate through keys and check values
        for k in self.submission.keys():
            # Flag set to True when vals don't match or not w/in tolerance
            break_flag = False
            sub = self.submission[k]
            ans = self.answer[k]
            sub_is_num = isinstance(sub, (int, float))
            key_val_comment = (
                f"The value for key `{k}` doesn't match the expected result."
            )

            # For numerical values
            if sub_is_num and sub != ans:
                if (tolerance > 0) and isclose(sub, ans, rel_tol=tolerance):
                    # This will continue to be True as long as all vals are w/in tolerance
                    self.passed = True
                else:
                    self.update_comment(key_val_comment)
                    break_flag = True

            # For non-numerical values
            if not sub_is_num and sub != ans:
                self.update_comment(key_val_comment)
                break_flag = True

            if break_flag:
                break

        # If submission got through loop with self.passed==True, all vals are w/in tolerance
        if self.passed:
            self.add_to_score()

        if return_bool:
            return self.passed
        else:
            return


class PandasGrader(BaseGrader):
    """
    Grader for evaluating objects from `pandas <https://pandas.pydata.org/docs/index.html>`_.

    """

    def __init__(self, submission, answer, points=1):
        super().__init__(submission, answer, points)

    def check_df(
        self,
        match_index=True,
        match_index_col_order=True,
        tolerance=0.0,
        return_bool=False,
    ):
        """Evaluate submitted DataFrame.

        Parameters
        ----------
        match_index : bool, default=True
            Whether or not to consider the index of the submitted DataFrame. If ``False``, index is
            reset before it's evaluated.

        match_index_col_order : bool, default=True
            Whether or not to consider the order of the index and columns in the submitted
            DataFrame.

        tolerance: int or float, default=0.0
            For numerical values, what is the maximum allowed
            difference between ``submission`` and ``answer``? If 0.0, values must be
            identical. If 0.1, values must be within 10% must be within 10% of each
            other (relative to the larger absolute value of the two).

        return_bool : bool, default=False
            Whether to return ``self.passed`` once grading is complete. You'll need this if
            you want to design your own grading workflow beyond the default.

        Examples
        --------
        Here are two DataFrames. The first ``ans_df`` is the expected answer, and the second
        ``sub_df``is the student submission. Note that both have the same values, but order of the
        indices and columns is different.

        >>> import pandas as pd
        >>> ans_df = pd.DataFrame(
        ...     {"city": ["Puhi", "Napa", "Derby"], "pop": [3, 79, 13]}, index=[16, 14, 4]
        ... )
        >>> sub_df = pd.DataFrame(
        ...     {"pop": [79, 3, 13], "city": ["Napa", "Puhi", "Derby"]}, index=[14, 16, 4]
        ... )
        >>> print(ans_df)
             city  pop
        16   Puhi    3
        14   Napa   79
        4   Derby   13
        >>> print(sub_df)
            pop   city
        14   79   Napa
        16    3   Puhi
        4    13  Derby
        >>> g = PandasGrader(submission=sub_df, answer=ans_df)
        >>> g.check_df(match_index_col_order=False, return_bool=True)
        True
        >>> g.check_df(match_index_col_order=True, return_bool=True)
        False
        >>> print(g.comment)
        DataFrame.index are different

        DataFrame.index values are different (66.66667 %)
        [submission]:  Int64Index([14, 16, 4], dtype='int64')
        [answer]: Int64Index([16, 14, 4], dtype='int64')
        """

        if not isinstance(self.submission, pd.DataFrame):
            raise TypeError(
                f"check_df method can only be used with DataFrames submissions, not {type(self.submission).__name__}."
            )

        if not match_index:
            self.submission = self.submission.reset_index(drop=True)
            self.answer = self.answer.reset_index(drop=True)

        try:
            pd.testing.assert_frame_equal(
                self.submission,
                self.answer,
                check_like=not match_index_col_order,
                check_exact=not bool(tolerance),
                rtol=tolerance,
            )
            self.add_to_score()
            if return_bool:
                return self.passed
            else:
                return None

        except AssertionError as e:
            # Need to shorten error message string for big DataFrames
            if len(self.submission) > 10:
                comment = (
                    "Your DataFrame doesn't match the expected result:\n\n"
                    + str(e)[: str(e).find("\n")]
                )
            else:
                comment = (
                    str(e)
                    .replace(
                        "DataFrame are different",
                        "Your DataFrame doesn't match the expected result:",
                    )
                    .replace("left", "submission")
                    .replace("right", "answer")
                )
            self.update_comment(comment)
            if return_bool:
                return self.passed
            else:
                return None
