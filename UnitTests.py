import unittest
from RankingMethodsClass import ClimbingRanker
import random
import numpy as np
import DegreeOfIndependence as di

class TestRankingProgram(unittest.TestCase):

    def test_fybBNatsSemis2016(self):
        ranker = ClimbingRanker("fybBNatsSemis2016.csv")
        self.assertEqual(ranker.linearProgrammingOptimalSplit(), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 14, 15,
                                                                  21, 17, 18, 19, 20])

    def test_fydBNatsSemis2016(self):
        ranker = ClimbingRanker("fydBNatsSemis2016.csv")
        self.assertEqual(ranker.linearProgrammingOptimalSplit(), [1, 2, 3, 4, 7, 5, 8, 16, 9, 6, 10, 11, 12, 14, 15, 13,
                                                                  18, 17, 19, 20, 21])

    def test_fyaBNatsQualis2016(self):
        ranker = ClimbingRanker("fyaBNatsQualis2016.csv")
        self.assertEqual(ranker.linearProgrammingOptimalSplit(), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 11, 13, 14, 15,
                                                                  16, 17, 18, 20, 21, 19, 23, 25, 24, 22, 27, 26, 29, 28,
                                                                  34, 33, 30, 31, 32, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                                                                  45, 44, 48, 50, 47, 46, 49])

    def test_independenceIndex(self):
        listOfMethodNums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        random.seed(1)
        results = di.doIndependenceAnalysisMultithreaded(listOfMethodNums, 5, 1, 4, 1000, seed=1, haveClimberAbilities=False)
        self.assertEqual(results[0], .578) #l2 norm method no tops
        self.assertEqual(results[1], .764) #l2 norm method
        self.assertEqual(results[2], .749) #geomean method
        self.assertEqual(results[3], .563) #geomean method no tops
        self.assertEqual(results[4], .743) #usac method
        self.assertEqual(results[5], .56) #usac method no tops
        self.assertEqual(results[6], .496) #borda method no tops
        self.assertEqual(results[7], .704) #borda method
        self.assertEqual(results[8], .731) #borda method usac ranking points
        self.assertEqual(results[9], 1) #merged method
        self.assertEqual(results[10], 1) #abs10 method
        self.assertEqual(results[11], 1) #top score method
        self.assertEqual(results[12], .761) #w algorithm integer
        self.assertEqual(results[13], .624) #w algorithm optimal integer
        self.assertEqual(results[14], .438) #w algorithm no tops
        self.assertEqual(results[15], .86) #linear program
        self.assertEqual(results[16], .012) #basline



suite = unittest.TestLoader().loadTestsFromTestCase(TestRankingProgram)
unittest.TextTestRunner(verbosity=2).run(suite)
