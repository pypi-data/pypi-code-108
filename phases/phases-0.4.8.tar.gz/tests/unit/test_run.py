from phases.util.pdict import pdict
from pyPhases.Project import Project
from pyPhases.Phase import Phase
from phases.commands.run import Run
from shutil import copyfile
import unittest


class MockPhase(Phase):
    index = 0

    def main(self):

        self.project.gridOutput = {"runIndex": MockPhase.index}
        MockPhase.index += 1


class TestGrid(unittest.TestCase):
    fullGrid = [
        (["p0"], [0, 1]),
        (["p1"], [2, 3]),
        (["p2"], [4, 5, 6]),
        (["p3"], [7, 8]),
        (["p4"], [9]),
        (["p5", "deep"], [10, 11, 12]),
    ]

    def runFullGrid(self, random=False, resume=False):
        run = Run({})
        run.csvLogFile = "tests/data-gen/tmp.csv"
        config = "grid.random.yaml" if random else "grid.yaml"
        run.projectGridFile = "tests/res/configs/" + config

        run.resume = resume

        grid = run.prepareGridFile()
        self.assertEqual(grid, self.fullGrid)
        grid = run.prepareGridFile()
        self.assertEqual(grid, self.fullGrid)
        flattenGrid = run.flattenGrid(grid)
        self.checkFullFlattenDiff(flattenGrid)

        project = Project()
        MockPhase.index = 0
        project.addPhase(MockPhase())
        project.config = pdict()
        run.runProject(project)
        allEntries = run.getLogEntries()

        self.assertEqual(allEntries[0], ["run", "p0", "p1", "p2", "p3", "p4", "p5/deep", "runIndex"])

        return allEntries, flattenGrid

    def testGridRun(self):

        allEntries, flattenGrid = self.runFullGrid()

        for index, resultGrid in enumerate(flattenGrid):
            resultConfig = [str(val) for i, val in resultGrid]
            row = allEntries[index + 1]
            self.assertEqual(row[0], str(index + 1))
            self.assertEqual(row[1:7], resultConfig)
            self.assertEqual(row[7], str(index))

    def testGridRunRandom(self):

        allEntries, flattenGrid = self.runFullGrid(random=True)

        fixedRandomSeeds = self.getRandomOrder()

        for index in range(len(flattenGrid)):
            runId = fixedRandomSeeds[index]
            resultGrid = flattenGrid[runId - 1]
            resultConfig = [str(val) for _, val in resultGrid]
            row = allEntries[index + 1]
            self.assertEqual(row[0], str(runId))
            self.assertEqual(row[1:7], resultConfig)
            self.assertEqual(row[7], str(index))

    def testGridRunResume(self):
        copyfile("tests/res/runs/seq.csv", "tests/data-gen/tmp.csv")
        allEntries, flattenGrid = self.runFullGrid(random=False, resume=True)

        startWith = 44
        for index in range(startWith, len(flattenGrid)):
            runId = index + 1
            resultGrid = flattenGrid[runId - 1]
            resultConfig = [str(val) for _, val in resultGrid]
            row = allEntries[index + 1]
            self.assertEqual(row[0], str(runId))
            self.assertEqual(row[1:7], resultConfig)
            self.assertEqual(row[7], str(index - startWith))

    def testGridRunRandomResume(self):
        copyfile("tests/res/runs/rand.csv", "tests/data-gen/tmp.csv")
        allEntries, flattenGrid = self.runFullGrid(random=True, resume=True)
        fixedRandomSeeds = self.getRandomOrder()

        startWith = 23
        for index in range(startWith, len(flattenGrid)):
            runId = fixedRandomSeeds[index]
            resultGrid = flattenGrid[runId - 1]
            resultConfig = [str(val) for _, val in resultGrid]
            row = allEntries[index + 1]
            self.assertEqual(row[0], str(runId))
            self.assertEqual(row[1:7], resultConfig)
            self.assertEqual(row[7], str(index - startWith))

    def testFlattenGrid(self):
        grids = [
            [("p0", [0])],
            [["p0", [0]], ["p1", [1]]],
            [["p0", [0]], ["p1", [1, 2]]],
        ]

        run = Run({})
        self.assertEqual(run.flattenGrid(grids[0]), [[("p0", 0)]])
        self.assertEqual(run.flattenGrid(grids[1]), [[("p0", 0), ("p1", 1)]])
        self.assertEqual(run.flattenGrid(grids[2]), [[("p0", 0), ("p1", 1)], [("p0", 0), ("p1", 2)]])
        self.checkFullFlattenDiff(run.flattenGrid(self.fullGrid))

    def checkFullFlattenDiff(self, flattenGrid):
        self.assertEqual(
            flattenGrid,
            [
                [(["p0"], 0), (["p1"], 2), (["p2"], 4), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 1), (["p1"], 2), (["p2"], 4), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 0), (["p1"], 3), (["p2"], 4), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 1), (["p1"], 3), (["p2"], 4), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 0), (["p1"], 2), (["p2"], 5), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 1), (["p1"], 2), (["p2"], 5), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 0), (["p1"], 3), (["p2"], 5), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 1), (["p1"], 3), (["p2"], 5), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 0), (["p1"], 2), (["p2"], 6), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 1), (["p1"], 2), (["p2"], 6), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 0), (["p1"], 3), (["p2"], 6), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 1), (["p1"], 3), (["p2"], 6), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 0), (["p1"], 2), (["p2"], 4), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 1), (["p1"], 2), (["p2"], 4), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 0), (["p1"], 3), (["p2"], 4), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 1), (["p1"], 3), (["p2"], 4), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 0), (["p1"], 2), (["p2"], 5), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 1), (["p1"], 2), (["p2"], 5), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 0), (["p1"], 3), (["p2"], 5), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 1), (["p1"], 3), (["p2"], 5), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 0), (["p1"], 2), (["p2"], 6), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 1), (["p1"], 2), (["p2"], 6), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 0), (["p1"], 3), (["p2"], 6), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 1), (["p1"], 3), (["p2"], 6), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 10)],
                [(["p0"], 0), (["p1"], 2), (["p2"], 4), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 1), (["p1"], 2), (["p2"], 4), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 0), (["p1"], 3), (["p2"], 4), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 1), (["p1"], 3), (["p2"], 4), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 0), (["p1"], 2), (["p2"], 5), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 1), (["p1"], 2), (["p2"], 5), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 0), (["p1"], 3), (["p2"], 5), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 1), (["p1"], 3), (["p2"], 5), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 0), (["p1"], 2), (["p2"], 6), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 1), (["p1"], 2), (["p2"], 6), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 0), (["p1"], 3), (["p2"], 6), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 1), (["p1"], 3), (["p2"], 6), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 0), (["p1"], 2), (["p2"], 4), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 1), (["p1"], 2), (["p2"], 4), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 0), (["p1"], 3), (["p2"], 4), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 1), (["p1"], 3), (["p2"], 4), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 0), (["p1"], 2), (["p2"], 5), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 1), (["p1"], 2), (["p2"], 5), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 0), (["p1"], 3), (["p2"], 5), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 1), (["p1"], 3), (["p2"], 5), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 0), (["p1"], 2), (["p2"], 6), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 1), (["p1"], 2), (["p2"], 6), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 0), (["p1"], 3), (["p2"], 6), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 1), (["p1"], 3), (["p2"], 6), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 11)],
                [(["p0"], 0), (["p1"], 2), (["p2"], 4), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 1), (["p1"], 2), (["p2"], 4), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 0), (["p1"], 3), (["p2"], 4), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 1), (["p1"], 3), (["p2"], 4), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 0), (["p1"], 2), (["p2"], 5), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 1), (["p1"], 2), (["p2"], 5), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 0), (["p1"], 3), (["p2"], 5), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 1), (["p1"], 3), (["p2"], 5), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 0), (["p1"], 2), (["p2"], 6), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 1), (["p1"], 2), (["p2"], 6), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 0), (["p1"], 3), (["p2"], 6), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 1), (["p1"], 3), (["p2"], 6), (["p3"], 7), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 0), (["p1"], 2), (["p2"], 4), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 1), (["p1"], 2), (["p2"], 4), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 0), (["p1"], 3), (["p2"], 4), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 1), (["p1"], 3), (["p2"], 4), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 0), (["p1"], 2), (["p2"], 5), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 1), (["p1"], 2), (["p2"], 5), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 0), (["p1"], 3), (["p2"], 5), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 1), (["p1"], 3), (["p2"], 5), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 0), (["p1"], 2), (["p2"], 6), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 1), (["p1"], 2), (["p2"], 6), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 0), (["p1"], 3), (["p2"], 6), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 12)],
                [(["p0"], 1), (["p1"], 3), (["p2"], 6), (["p3"], 8), (["p4"], 9), (["p5", "deep"], 12)],
            ],
        )

    def getRandomOrder(self):
        return [
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            70,
            71,
            64,
            65,
            66,
            67,
            68,
            69,
            63,
            3,
            4,
            5,
            6,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            62,
            59,
            60,
            61,
            1,
            2,
            35,
            36,
            37,
            38,
            39,
            40,
            41,
            42,
            43,
            44,
            57,
            58,
            0,
            45,
            46,
            47,
            48,
            49,
            56,
            50,
            51,
            52,
            53,
            54,
            55,
        ]
