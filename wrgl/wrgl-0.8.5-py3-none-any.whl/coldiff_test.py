from unittest import TestCase

from wrgl.commit import Table
from wrgl.coldiff import longest_increasing_list, moveOps, MoveOp, ColDiff, Column, Move


class LongestIncreasingListTestCase(TestCase):
    def test_run(self):
        for l, res in [
            ([], []),
            ([0], [0]),
            ([0, 1], [0, 1]),
            ([1, 0], [0]),
            ([2, 0, 1], [1, 2]),
            ([1, 2, 0], [0, 1]),
            ([1, 0, 2], [0, 2]),
            ([0, 1, 2], [0, 1, 2]),
            ([2, 1, 0], [1]),
            ([0, 4, 5, 1, 2, 3], [0, 3, 4, 5]),
            ([0, 4, 5, 1, 2], [0, 1, 2]),
            ([4, 5, 0, 2, 1, 3], [2, 3, 5]),
        ]:
            self.assertEqual(longest_increasing_list(l), res)


class MoveOpsTestCase(TestCase):
    def test_run(self):
        for sl, ops in [
            ([], []),
            ([0], []),
            ([0, 1], []),
            ([0, 1, 2], []),
            ([1, 0], [MoveOp(old_ind=0, new_ind=1)]),
            ([1, 0, 2], [MoveOp(old_ind=0, new_ind=1)]),
            ([1, 2, 0], [MoveOp(old_ind=0, new_ind=2)]),
            ([2, 1, 0], [
                MoveOp(old_ind=2, new_ind=0),
                MoveOp(old_ind=0, new_ind=2),
            ]),
            ([0, 1, 2, 5, 3, 4], [MoveOp(old_ind=5, new_ind=3)]),
            ([2, 1, 4, 5, 3, 0], [
                MoveOp(old_ind=1, new_ind=1),
                MoveOp(old_ind=3, new_ind=4),
                MoveOp(old_ind=0, new_ind=5),
            ]),
        ]:
            self.assertEqual(moveOps(sl), ops)


class ColDiffTestCase(TestCase):
    def test_init(self):
        self.maxDiff = None
        for tbl_a, tbl_b, columns in [
            (
                Table(columns=["a"], pk=[]),
                Table(columns=["a"], pk=[]),
                [Column(name="a", base_idx=0, layer_idx={0: 0})]
            ),
            (
                Table(columns=["a"], pk=[]),
                Table(columns=["b"], pk=[]),
                [
                    Column(
                        name="a", base_idx=0, layer_idx={}, removed=set([0])
                    ),
                    Column(name="b", layer_idx={0: 0}, added=set([0]))
                ]
            ),
            (
                Table(columns=["a", "b"], pk=[]),
                Table(columns=["a", "b"], pk=[]),
                [
                    Column(name="a", base_idx=0, layer_idx={0: 0}),
                    Column(name="b", base_idx=1, layer_idx={0: 1})
                ]
            ),
            (
                Table(columns=["a", "b"], pk=[]),
                Table(columns=["b", "a"], pk=[]),
                [
                    Column(name="b", base_idx=1, layer_idx={0: 0}),
                    Column(
                        name="a", base_idx=0, layer_idx={0: 1}, moved={0: Move(before=0)}
                    )
                ]
            ),
            (
                Table(columns=["a", "b", "c"], pk=[]),
                Table(columns=["c", "a"], pk=[]),
                [
                    Column(name="c", base_idx=2, layer_idx={0: 0}),
                    Column(
                        name="a", base_idx=0, layer_idx={0: 1}, moved={0: Move(before=0)}
                    ),
                    Column(name="b", base_idx=1, removed=set([0]))
                ]
            ),
            (
                Table(columns=["c", "b", "a"], pk=[]),
                Table(columns=["a", "b", "c"], pk=[]),
                [
                    Column(
                        name="a", base_idx=2, layer_idx={0: 0}, moved={0: Move(after=1)}
                    ),
                    Column(name="b", base_idx=1, layer_idx={0: 1}),
                    Column(
                        name="c", base_idx=0, layer_idx={0: 2}, moved={0: Move(before=1)}
                    )
                ]
            ),
            (
                Table(columns=["a", "b"], pk=[]),
                Table(columns=["b", "c", "a"], pk=[]),
                [
                    Column(name="b", base_idx=1, layer_idx={0: 0}),
                    Column(name="c", layer_idx={0: 1}, added=set([0])),
                    Column(
                        name="a", base_idx=0, layer_idx={0: 2}, moved={0: Move(before=0)}
                    )
                ]
            ),
            (
                Table(columns=["a", "d", "e", "b", "c"], pk=[]),
                Table(columns=["a", "b", "c", "d", "e"], pk=[]),
                [
                    Column(name="a", base_idx=0, layer_idx={0: 0}),
                    Column(name="b", base_idx=3, layer_idx={0: 1}),
                    Column(name="c", base_idx=4, layer_idx={0: 2}),
                    Column(
                        name="d", base_idx=1, layer_idx={0: 3}, moved={0: Move(after=0)}
                    ),
                    Column(
                        name="e", base_idx=2, layer_idx={0: 4}, moved={0: Move(after=0)}
                    )
                ]
            ),
            (
                Table(columns=["e", "b", "c", "d", "f"], pk=[]),
                Table(columns=["a", "b", "c", "d", "e"], pk=[]),
                [
                    Column(name="a", layer_idx={0: 0}, added=set([0])),
                    Column(name="b", base_idx=1, layer_idx={0: 1}),
                    Column(name="c", base_idx=2, layer_idx={0: 2}),
                    Column(name="d", base_idx=3, layer_idx={0: 3}),
                    Column(name="f", base_idx=4, removed=set([0])),
                    Column(
                        name="e", base_idx=0, layer_idx={0: 4}, moved={0: Move(before=1)}
                    )
                ]
            ),
            (
                Table(columns=["a", "b", "c"], pk=[0]),
                Table(columns=["a", "b", "c"], pk=[0]),
                [
                    Column(
                        base_idx=0, base_pk=True, layer_idx={0: 0}, layer_pk=set([0]), name="a"
                    ),
                    Column(
                        base_idx=1, layer_idx={0: 1}, name="b"
                    ),
                    Column(
                        base_idx=2, layer_idx={0: 2}, name="c"
                    )
                ]
            ),
            (
                Table(columns=["a", "b", "c"], pk=[0]),
                Table(columns=["b", "a", "d"], pk=[2, 1]),
                [
                    Column(
                        added=set([0]), layer_idx={0: 2}, layer_pk=set([0]), name="d"
                    ),
                    Column(
                        base_idx=0, base_pk=True, layer_idx={0: 1}, layer_pk=set([0]), moved={0: Move(before=0)}, name="a"
                    ),
                    Column(
                        base_idx=1, layer_idx={0: 0}, name="b"
                    ),
                    Column(
                        base_idx=2, name="c", removed=set([0])
                    )
                ]
            ),
            (
                Table(
                    columns=[
                        "a", "ab", "ac", "ad", "b", "c", "ca", "cb", "cd", "e", "ea", "eb", "ec",
                    ],
                    pk=[]
                ),
                Table(columns=["a", "b", "c", "d", "e", "f"], pk=[]),
                [
                    Column(name="a", base_idx=0, layer_idx={0: 0}),
                    Column(name="ab", base_idx=1, removed=set([0])),
                    Column(name="ac", base_idx=2, removed=set([0])),
                    Column(name="ad", base_idx=3, removed=set([0])),
                    Column(name="b", base_idx=4, layer_idx={0: 1}),
                    Column(name="c", base_idx=5, layer_idx={0: 2}),
                    Column(name="ca", base_idx=6, removed=set([0])),
                    Column(name="cb", base_idx=7, removed=set([0])),
                    Column(name="cd", base_idx=8, removed=set([0])),
                    Column(name="d", added=set([0]), layer_idx={0: 3}),
                    Column(name="e", base_idx=9, layer_idx={0: 4}),
                    Column(name="ea", base_idx=10, removed=set([0])),
                    Column(name="eb", base_idx=11, removed=set([0])),
                    Column(name="ec", base_idx=12, removed=set([0])),
                    Column(name="f", added=set([0]), layer_idx={0: 5})
                ]
            )
        ]:
            cd = ColDiff(tbl_a, tbl_b)
            self.assertEqual(cd.columns, columns)

    def test_rearrange_base_row(self):
        for tbl_a, tbl_b, row, rearranged in [
            (
                Table(columns=["a", "b", "c"], pk=[0]),
                Table(columns=["a", "b", "c"], pk=[0]),
                ["1", "2", "3"],
                ["1", "2", "3"]
            ),
            (
                Table(columns=["a", "b", "c"], pk=[0]),
                Table(columns=["b", "a", "d"], pk=[2, 1]),
                ["1", "2", "3"],
                [None, "1", "2", "3"]
            )
        ]:
            cd = ColDiff(tbl_a, tbl_b)
            self.assertEqual(cd.rearrange_base_row(row), rearranged)

    def test_rearrange_row(self):
        for tbl_a, tbl_b, row, rearranged in [
            [
                Table(columns=["a", "b", "c"], pk=[0]),
                Table(columns=["a", "b", "c"], pk=[0]),
                ["1", "2", "3"],
                ["1", "2", "3"]
            ],
            [
                Table(columns=["a", "b", "c"], pk=[0]),
                Table(columns=["b", "a", "d"], pk=[2, 1]),
                ["1", "2", "3"],
                ["3", "2", "1", None]
            ]
        ]:
            cd = ColDiff(tbl_a, tbl_b)
            self.assertEqual(cd.rearrange_row(0, row), rearranged)

    def test_combine_rows(self):
        cd = ColDiff(
            Table(columns=["e", "b", "c", "d", "f"]),
            Table(columns=["a", "b", "c", "d", "e"])
        )
        self.assertEqual(
            cd.columns,
            [
                Column(name="a", added=set([0]), layer_idx={0: 0}),
                Column(name="b", layer_idx={0: 1}, base_idx=1),
                Column(name="c", layer_idx={0: 2}, base_idx=2),
                Column(name="d", layer_idx={0: 3}, base_idx=3),
                Column(name="f", removed=set([0]), base_idx=4),
                Column(
                    name="e", layer_idx={0: 4}, base_idx=0, moved={0: Move(before=1)}
                )
            ]
        )
        self.assertEqual(
            cd.combine_rows(
                0,
                ["1", "2", "3", "4", "5"],
                ["6", "2", "7", "4", "5"]
            ),
            [
                ("1", None), ("2", "2"), ("3", "7"),
                ("4", "4"), (None, "5"), ("5", "6")
            ]
        )

    def test_no_column_changes(self):
        for tbl_a, tbl_b, result in [
            (
                Table(columns=["a", "b", "c"]),
                Table(columns=["a", "b", "c"]),
                True
            ),
            (
                Table(columns=["a", "b", "c"]),
                Table(columns=["a", "b", "c", "d"]),
                False
            ),
            (
                Table(columns=["a", "b", "c", "d"]),
                Table(columns=["a", "b", "c"]),
                False
            ),
            (
                Table(columns=["a", "b", "c"]),
                Table(columns=["a", "c", "b"]),
                False
            )
        ]:
            cd = ColDiff(tbl_a, tbl_b)
            self.assertEqual(cd.no_column_changes(), result)

    def test_col_status(self):
        cd = ColDiff(
            Table(columns=["a", "b", "c", "e"]),
            Table(columns=["a", "e", "b", "d"]),
        )
        self.assertEqual(cd.columns[0].name, "a")
        self.assertEqual(cd.columns[0].is_added, False)
        self.assertEqual(cd.columns[0].is_removed, False)
        self.assertEqual(cd.columns[0].is_moved, False)

        self.assertEqual(cd.columns[2].name, "b")
        self.assertEqual(cd.columns[2].is_added, False)
        self.assertEqual(cd.columns[2].is_removed, False)
        self.assertEqual(cd.columns[2].is_moved, True)

        self.assertEqual(cd.columns[3].name, "c")
        self.assertEqual(cd.columns[3].is_added, False)
        self.assertEqual(cd.columns[3].is_removed, True)
        self.assertEqual(cd.columns[3].is_moved, False)

        self.assertEqual(cd.columns[4].name, "d")
        self.assertEqual(cd.columns[4].is_added, True)
        self.assertEqual(cd.columns[4].is_removed, False)
        self.assertEqual(cd.columns[4].is_moved, False)
