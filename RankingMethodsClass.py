from ReadInData import ClimbingDataFile
import GetTopsInfo as gti
import SomeStatsStuff as sss
import numpy as np
import BubbleDistance as bd
import LinearProgramming as lp
import copy


class ClimbingRanker:
    """
    Creates object that runs ranking methods on data from fileName
    """
    def __init__(self, fileName, *args):
        """
        Initialize ClimbingRanker object
        :param fileName: file where data is (csv format)
        :param args: optional - can specify how many climbers to use (input int numberOfClimbers) or a list of all the
        information you want to run the ranking methods on (must have all of these indices):
        args[0][0] = list of climbers (1D list)
        args[0][1] = number of problems
        args[0][2] = matrix of ranks for each climber on each problem (rows = climbers)
        args[0][3] = list with total number of tops for each climber
        args[0][4] = list of total number of attempts for each climber
        args[0][5] = matrix of attempts for each climber on each problem (rows = climbers)
        args[0][6] = list of total number of hold points for each climber
        args[0][7] = matrix of hold points for each climber on each problem (rows = climbers)
        args[0][8] = matrix with 1 if climber i topped problem j and 0 otherwise
        args[0][9] = category (3 letter string like "fyd" - lowercase)
        args[0][10] = round of competition (qualis, semis, finals - String)
        args[0][11] = true if the set of data is complete (no climbers excluded) and false otherwise (for use in old
        USAC methods)
        (or all of these indices (for the degreeOfIndependence analysis):
        args[0][0] = list of climbers (1D list)
        args[0][1] = number of problems
        args[0][2] = matrix of ranks for each climber on each problem (rows = climbers)
        args[0][3] = list with total number of tops for each climber
        """
        if(args != ()):
            if(isinstance(args[0], list)): #used for cross validation
                if(len(args[0]) == 12):
                    self.climbers = args[0][0]
                    self.numProblems = args[0][1]
                    self.numClimbers = len(self.climbers)
                    self.ranks = args[0][2]
                    self.flippedRanks = self.__flipRankings()
                    self.tops = args[0][3]
                    self.attempts = args[0][4]
                    self.attemptsPerProblem = args[0][5]
                    self.points = args[0][6]
                    self.pointsPerProblem = args[0][7]
                    self.topsPerProblem = args[0][8]
                    self.category = args[0][9] #used to complete incomplete data and determine the average number of holds on a climb
                    self.round = args[0][10] #only used to complete incomplete data
                    self.complete = args[0][11]
                elif(len(args[0]) == 4): #will be used to calculate degreeOfIndependence
                    self.climbers = args[0][0]
                    self.numProblems = args[0][1]
                    self.numClimbers = len(self.climbers)
                    self.ranks = args[0][2]
                    self.flippedRanks = self.__flipRankings()
                    self.tops = args[0][3]
                    self.complete = True
                    if(len(self.tops) != self.numClimbers):
                        raise ValueError("length of the tops vector must equal numClimbers")
                else:
                    raise ValueError("Invalid arguments")
            else:
                if(isinstance(args[0], int)): #also used for cross validation, also if you just want part of data set
                    self.data = ClimbingDataFile(fileName, args[0])
                    self.climbers = self.data.getClimbers()
                    self.numProblems = self.data.numProblems
                    self.numClimbers = len(self.climbers)
                    self.ranks = self.data.getRanks()
                    self.flippedRanks = self.__flipRankings()
                    self.tops = self.data.getTops()
                    self.attempts = self.data.getAttempts()
                    self.attemptsPerProblem = self.data.getAttemptsPerProblem()
                    self.points = self.data.getPoints()
                    self.pointsPerProblem = self.data.getPointsPerProblem()
                    self.topsPerProblem = gti.getTopsInfo(self.pointsPerProblem, self.tops)
                    self.category = fileName[0:3]
                    self.round = fileName[4:len(fileName)-4]
                    self.complete = False
                else:
                    raise ValueError("Invalid arguments")
        else:
            self.data = ClimbingDataFile(fileName, 0)
            self.climbers = self.data.getClimbers()
            self.numProblems = self.data.numProblems
            self.numClimbers = len(self.climbers)
            self.ranks = self.data.getRanks()
            self.flippedRanks = self.__flipRankings()
            self.tops = self.data.getTops()
            self.attempts = self.data.getAttempts()
            self.attemptsPerProblem = self.data.getAttemptsPerProblem()
            self.points = self.data.getPoints()
            self.pointsPerProblem = self.data.getPointsPerProblem()
            self.topsPerProblem = gti.getTopsInfo(self.pointsPerProblem, self.tops)
            self.complete = True
            self.round = fileName[4:len(fileName)-4]
            self.category = fileName[0:3]
        self.methods = [self.l2NormMethodNoTops, self.l2NormMethod, self.geometricMeanMethod,
                        self.geometricMeanMethodNoTops, self.usacMethod, self.usacMethodNoTops,
                        self.bordaMethodNoTops, self.bordaMethod, self.bordaMethodUsacRankingPoints, self.mergedOldMethod, self.abs10Method,
                        self.topScoreMethod, self.wAlgorithmInteger, self.wAlgorithmOptimalInteger, self.wAlgorithmNoTops,
                        self.linearProgrammingOptimalSplit]

    def bordaMethod(self):  # l1 norm method
        """
        uses the borda method of rank aggregation to aggregate the ranks in rankings matrix (but doesn't take average
        rank when tied). add up rankings of each climber on each problem and then rank them based on number of tops and
        then these totalPoint numbers (higher number of tops is better, higher numbers in totalPoints list are worse).
        :return: list of climbers in their final ranked order and aggregated rank as calculated by the borda method
        """
        topsList = self.tops.copy()  # copy it so you don't change the original tops list when tops gets changed in getMinIndexWithTops
        totalPoints = [0] * self.numClimbers  # will store borda points for each climber
        for climber in range(0, self.numClimbers):
            for problem in range(0, self.numProblems):
                totalPoints[climber] += self.ranks[climber][problem]
        return self.__calculateFinalRank(topsList, totalPoints)

    def bordaMethodUsacRankingPoints(self):
        """
        uses the borda method of rank aggregation to aggregate the rank points in the ranking points matrix.
        add up rankings of each climber on each problem and then rank them based on number of tops and
        then these totalPoint numbers (higher number of tops is better, higher numbers in totalPoints list are worse).
        :return: list of climbers in their final ranked order and aggregated rank as calculated by the borda method
        """
        rankings = self.__getUSAClimbingRankingPoints()
        topsList = self.tops.copy()  # copy it so you don't change the original tops list when tops gets changed in getMinIndexWithTops
        totalPoints = [0] * self.numClimbers  # will store borda points for each climber
        for climber in range(0, self.numClimbers):
            for problem in range(0, self.numProblems):
                totalPoints[climber] += rankings[climber][problem]
        return self.__calculateFinalRank(topsList, totalPoints)

    def bordaMethodNoTops(self):
        """
        uses the borda method of rank aggregation to aggregate the ranks in rankings matrix. add up rankings of each climber
        on each problem and then rank them based on these totalPoint numbers (higher numbers in totalPoints list are worse)
        :return: list of climbers in their final ranked order and aggregated rank as calculated by the borda method
        """
        totalPoints = [0] * self.numClimbers  # will store borda points for each climber
        for climber in range(0, self.numClimbers):
            for problem in range(0, self.numProblems):
                totalPoints[climber] += self.ranks[climber][problem]
        return self.__calculateFinalRankNoTops(totalPoints)

    # usac current method (if you use usac ranking points as calculated below)
    def geometricMeanMethod(self):  # sorts candidates by geometric mean of position vectors
        """
        this method is the method used by USAC if rankings = usac ranking points (calculated by method below)
        uses the geometric mean method of rank aggregation to aggregate the ranks in rankings matrix. multiply rankings of each climber
        on each problem and then rank them based number of tops and then on the nth root of these products
        (n = number of problems, lower number is better)
        :return: list of climbers in their final ranked order and aggregated rank as calculated by the geometric mean method
        """
        topsList = self.tops.copy()  # copy it so you don't change the original tops list when tops gets changed in getMinIndexWithTops
        totalPoints = [0] * self.numClimbers  # will store points for each climber
        for climber in range(0, self.numClimbers):
            product = 1
            for problem in range(0, self.numProblems):
                product *= self.ranks[climber][problem]
            totalPoints[climber] = product ** (1 / self.numProblems)
        return self.__calculateFinalRank(topsList, totalPoints)

    def geometricMeanMethodNoTops(self):
        """
        uses the geometric mean method of rank aggregation to aggregate the ranks in rankings matrix. multiply rankings of each climber
        on each problem and then rank them based on the nth root of these products (n = number of problems, lower number is better)
        :return: list of climbers in their final ranked order and aggregated rank as calculated by the geometric mean method
        """
        totalPoints = [0] * self.numClimbers  # will store points for each climber
        for climber in range(0, self.numClimbers):
            product = 1
            for problem in range(0, self.numProblems):
                product *= self.ranks[climber][problem]
            totalPoints[climber] = product ** (1 / self.numProblems)
        return self.__calculateFinalRankNoTops(totalPoints)

    def usacMethod(self):
        """
        this method is the method used by USAC (same as geomean method but uses USAC ranking points)
        uses the geometric mean method of rank aggregation to aggregate the ranks in rankings matrix. multiply rankings of each climber
        on each problem and then rank them based number of tops and then on the nth root of these products
        (n = number of problems, lower number is better)
        :return: list of climbers in their final ranked order and aggregated rank as calculated by the geometric mean method
        """
        rankings = self.__getUSAClimbingRankingPoints()
        topsList = self.tops.copy()  # copy it so you don't change the original tops list when tops gets changed in getMinIndexWithTops
        totalPoints = [0] * self.numClimbers  # will store points for each climber
        for climber in range(0, self.numClimbers):
            product = 1
            for problem in range(0, self.numProblems):
                product *= rankings[climber][problem]
            totalPoints[climber] = product ** (1 / self.numProblems)
        return self.__calculateFinalRank(topsList, totalPoints)

    def usacMethodNoTops(self):
        """
        uses the geometric mean method of rank aggregation to aggregate the ranks in rankings matrix (calculates USAC ranking
        points from rankings matrix). multiply rankings of each climber on each problem and then rank them on the nth root
        of these products (n = number of problems, lower number is better)
        :return: list of climbers in their final ranked order and aggregated rank as calculated by the geometric mean method
        """
        rankings = self.__getUSAClimbingRankingPoints()
        totalPoints = [0] * self.numClimbers  # will store points for each climber
        for climber in range(0, self.numClimbers):
            product = 1
            for problem in range(0, self.numProblems):
                product *= rankings[climber][problem]
            totalPoints[climber] = product ** (1 / self.numProblems)
        return self.__calculateFinalRankNoTops(totalPoints)

    def l2NormMethod(self): #not mentioned in research paper at all
        """
        uses the l2 norm method of rank aggregation to aggregate the ranks in rankings matrix. add the square of the
        rankings of each climber on each problem and then rank them based number of tops and then on the square root of these
        sums (lower number is better)
        :return: list of climbers in their final ranked order and aggregated rank as calculated by the l2 norm method
        """
        topsList = self.tops.copy()  # copy it so you don't change the original tops list when tops gets changed in getMinIndexWithTops
        totalPoints = [0] * self.numClimbers  # will store points for each climber
        for climber in range(0, self.numClimbers):
            sum = 0
            for problem in range(0, self.numProblems):
                sum += (self.ranks[climber][problem]) ** 2  # squared
            totalPoints[climber] = sum ** (1 / 2)
        return self.__calculateFinalRank(topsList, totalPoints)

    def l2NormMethodNoTops(self):
        """
        uses the l2 norm method of rank aggregation to aggregate the ranks in rankings matrix. add the square of the
        rankings of each climber on each problem and rank them based on the square root of these sums (lower number is better)
        :return: list of climbers in their final ranked order and aggregated rank as calculated by the l2 norm method
        """
        totalPoints = [0] * self.numClimbers  # will store points for each climber
        for climber in range(0, self.numClimbers):
            sum = 0
            for problem in range(0, self.numProblems):
                sum += (self.ranks[climber][problem]) ** 2  # squared
            totalPoints[climber] = sum ** (1 / 2)
        return self.__calculateFinalRankNoTops(totalPoints)

    def topScoreMethod(self):
        """
        tops, total points (1 point per handhold), flashes, attempts to top, attempts to high point
        :return: aggregated rank as calculated by Top Score method
        """
        topsList = self.tops.copy()
        points = self.points.copy()
        finalNumRank = [0] * self.numClimbers  # aggregated rank where climbers are in original order and these are their places
        finalRank = [""] * self.numClimbers  # aggregated rank of climbers
        attemptsToTop, attemptsToHighPoint = self.__separateAttempts()
        flashes = self.__getFlashes()
        i = 0  # what place the climbers is in in the final rank
        while (i < self.numClimbers):
            indices = self.__getMinIndexForTopScoreMethod(points, attemptsToTop, attemptsToHighPoint, topsList, flashes)
            j = 0
            while (j < len(indices)):  # climbers whose indices are in indices list all tie
                finalNumRank[indices[j]] = i + 1  # +1 because rank from 1 to numClimbers
                finalRank[i] += self.climbers[indices[j]] + ";"
                j += 1
            i += len(indices)
        # return finalRank, finalNumRank
        return finalNumRank

    def __getFlashes(self):
        """
        calculates the number of flashes for each climber (used in Top Score)
        :return: 1D list where each entry is the number of flashes of the given climber
        """
        flashes = []
        for climber in range(self.numClimbers):
            count = 0
            for problem in range(self.numProblems):
                if(self.attemptsPerProblem[climber][problem] == 1 and self.topsPerProblem[climber][problem] == 1):
                    count += 1
            flashes.append(count)
        return flashes

    def mergedOldMethod(self):
        """
        a combination of the abs10 method and the Top Score method
        ranks based first on number of tops, then total points where holds are worth 1000/{total number of holds on climb},
        then attempts to top, then attempts to high point
        :return: list of climbers in their final ranked order and aggregated rank as calculated by the old USAC method
        """
        topsList = self.tops.copy()  # copy it so you don't change the original tops list when tops gets changed in getMinIndexWithTops
        holdNumbers = []  # maximum number of holds on each climb, -1 if that cannot be determined (no one topped)
        #loop through each problem and calculates maximum number of holds on each climb
        if(self.complete):
            for col in range(0, len(self.topsPerProblem[0])):
                for row in range(0, len(self.topsPerProblem)):
                    if (self.topsPerProblem[row][col] == 1):
                        holdNumbers.append(self.pointsPerProblem[row][col])
                        break
                    if (row == len(self.topsPerProblem) - 1):
                        holdNumbers.append(-1)
        else:
            fullData = ClimbingRanker(self.category + "BNats" + self.round + "2016.csv")
            tpp = fullData.topsPerProblem
            ppp = fullData.pointsPerProblem
            for col in range(0, len(tpp[0])):
                for row in range(0, len(tpp)):
                    if (tpp[row][col] == 1):
                        holdNumbers.append(ppp[row][col])
                        break
                    if (row == len(tpp) - 1):
                        holdNumbers.append(-1)
        #if max number of holds could not be determined then take average points per climb in given category
        averagePoints = sss.getAverageNumberOfHolds(self.category)
        holdPointsPerProblem = []
        #each hold is worth 1000/number of holds on problem
        for problem in range(0, len(holdNumbers)):
            if (holdNumbers[problem] == -1):
                holdPointsPerProblem.append(1000 / averagePoints[1])
            else:
                holdPointsPerProblem.append(1000 / holdNumbers[problem])
        finalNumRank = [0] * self.numClimbers  # aggregated rank where climbers are in original order and these are their places
        finalRank = [""] * self.numClimbers  # aggregated rank of climbers
        attemptsToTop, attemptsToHighPoint = self.__separateAttempts()
        newPoints = [] #points as determined by combined old USAC methods
        for climber in range(0, self.numClimbers):
            pointCount = 0
            for problem in range(0, self.numProblems):
                pointCount += self.pointsPerProblem[climber][problem] * holdPointsPerProblem[problem]
            newPoints.append(pointCount)
        i = 0  # what place the climbers is in in the final rank
        while (i < self.numClimbers):
            indices = self.__getMinIndexForMergedMethod(newPoints, attemptsToTop, attemptsToHighPoint, topsList)
            j = 0
            while (j < len(indices)):  # climbers whose indices are in indices list all tie
                finalNumRank[indices[j]] = i + 1  # +1 because rank from 1 to numClimbers
                finalRank[i] += self.climbers[indices[j]] + ";"
                j += 1
            i += len(indices)
        #return finalRank, finalNumRank
        return finalNumRank

    def abs10Method(self):
        """
        ranks based on total points where holds are worth 1000/{total number of holds on climb}
        and there is a 20 point flash bonus and -5 points for each fall
        :return: list of climbers in their final ranked order and aggregated rank as calculated by the abs10 method
        """
        holdNumbers = []  # maximum number of holds on each climb, -1 if that cannot be determined (no one topped)
        # loop through each problem and calculates maximum number of holds on each climb
        if (self.complete):
            for col in range(0, len(self.topsPerProblem[0])):
                for row in range(0, len(self.topsPerProblem)):
                    if (self.topsPerProblem[row][col] == 1):
                        holdNumbers.append(self.pointsPerProblem[row][col])
                        break
                    if (row == len(self.topsPerProblem) - 1):
                        holdNumbers.append(-1)
        else: #partial dataset - we use the full data set to see if anyone topped the problem so we get hold numbers (makes it independent)
            fullData = ClimbingRanker(self.category + "BNats" + self.round + "2016.csv")
            tpp = fullData.topsPerProblem
            ppp = fullData.pointsPerProblem
            for col in range(0, len(tpp[0])):
                for row in range(0, len(tpp)):
                    if (tpp[row][col] == 1):
                        holdNumbers.append(ppp[row][col])
                        break
                    if (row == len(tpp) - 1):
                        holdNumbers.append(-1)
        # if max number of holds could not be determined then take average points per climb in given category
        averagePoints = sss.getAverageNumberOfHolds(self.category)
        holdPointsPerProblem = []
        # each hold is worth 1000/number of holds on problem
        for problem in range(0, len(holdNumbers)):
            if (holdNumbers[problem] == -1):
                holdPointsPerProblem.append(1000 / averagePoints[1])
            else:
                holdPointsPerProblem.append(1000 / holdNumbers[problem])
        finalNumRank = [0] * self.numClimbers  # aggregated rank where climbers are in original order and these are their places
        finalRank = [""] * self.numClimbers  # aggregated rank of climbers
        newPoints = []  # points as determined by abs10 method
        for climber in range(0, self.numClimbers):
            pointCount = 0
            for problem in range(0, self.numProblems):
                pointCount += self.pointsPerProblem[climber][problem] * holdPointsPerProblem[problem]
                if (self.attemptsPerProblem[climber][problem] == 1 and self.topsPerProblem[climber][problem] == 1):
                    pointCount += 20  # 20 point flash bonus
                else:
                    pointCount -= (self.attemptsPerProblem[climber][problem] - 1) * 5  # -5 for each fall
            newPoints.append(pointCount*-1) #so that we can use getMinIndex method instead of having to find the max indices
        i = 0  # what place the climbers is in in the final rank
        while (i < self.numClimbers):
            indices = self.__getMinIndex(newPoints)
            j = 0
            while (j < len(indices)):  # climbers whose indices are in indices list all tie
                finalNumRank[indices[j]] = i + 1  # +1 because rank from 1 to numClimbers
                finalRank[i] += self.climbers[indices[j]] + ";"
                j += 1
            i += len(indices)
        # return finalRank, finalNumRank
        return finalNumRank

    def __calculateFinalRank(self, tops, totalPoints):
        """
        calculates the aggregated rank of climbers where they are ranked first by tops (more = better) and second by
        totalPoints (lower = better)
        :param tops: 1D list where each entry is the number of tops that climber has
        :param totalPoints: 1D list where each entry is the number of "points" (determined by whatever method) the
        climber has
        :return: a 1D list where each entry is the final rank of that climber
        """
        finalNumRank = [0] * self.numClimbers  # aggregated rank where climbers are listed in original order and these are their places
        finalRank = [""] * self.numClimbers  # aggregated rank
        i = 0  # what place the climber is in in the final rank
        while (i < self.numClimbers):
            indices = self.__getMinIndexWithTops(totalPoints, tops)
            j = 0
            while (j < len(indices)):  # climbers whose indices are in indices list all tie
                finalNumRank[indices[j]] = i + 1  # +1 because rank from 1 to numClimbers
                finalRank[i] += self.climbers[indices[j]] + ";"
                j += 1
            i += len(indices)
        #return finalRank, finalNumRank
        return finalNumRank

    def __calculateFinalRankNoTops(self, totalPoints):  # lower number of points means higher rank
        """
        calculates the aggregated rank of climbers where they are ranked by totalPoints (lower = better)
        :param totalPoints: 1D list where each entry is the number of "points" (determined by whatever method) the
        climber has
        :return: a 1D list where each entry is the final rank of that climber
        """
        finalNumRank = [0] * self.numClimbers  # aggregated rank where climbers are listed in original order and these are their places
        finalRank = [""] * self.numClimbers  # aggregated rank
        i = 0  # what place the climber is in in the final rank
        while (i < self.numClimbers):
            indices = self.__getMinIndex(totalPoints)
            j = 0
            while (j < len(indices)):  # climbers whose indices are in indices list all tie
                finalNumRank[indices[j]] = i + 1  # +1 because rank from 1 to numClimbers
                finalRank[i] += self.climbers[indices[j]] + ";"
                j += 1
            i += len(indices)
        #return finalRank, finalNumRank
        return finalNumRank

    def __getMinIndexForMergedMethod(self, points, attemptsToTop, attemptsToHighPoint, tops):
        """
        Finds the indices of the climbers who have the most tops, most points, fewest attempts to top, and fewest
        attempts to high point and then returns those indices and sets them to -1 if we maximize and 1000 if we minimize
        :param points: 1D list with points (for merged method) for each climber
        :param attemptsToTop: 1D list with number of attempts to top for each climber
        :param attemptsToHighPoint: 1D list with number of attempts to high point (not top although it
        doesn't matter because if its used, climbers have equal numbers of attempts to top) for each climber
        :param tops: 1D list where each entry is the total number of tops for that climber
        :return: indices fo climbers with the most tops, most points, fewest attempts to top, and fewest
        attempts to high point
        """
        # find the maximum number of tops and if there are multiple climbers with that number of tops
        max = [0]  # stores indices of maximum values
        for i in range(1, len(tops)):
            if (tops[i] > tops[max[0]]):
                max = [i]
            elif (tops[i] == tops[max[0]]):
                max.append(i)
        maxPointIndices = [max[0]]  # index of climber(s) with maximum point value
        if (len(max) > 1):  # out of the climbers with maximum number of tops find one with fewest points
            for index in max:
                if (points[index] > points[maxPointIndices[0]]):
                    maxPointIndices = [index]
                elif (points[index] == points[maxPointIndices[0]] and index != maxPointIndices[
                    0]):  # two climbers have same points & same tops
                    maxPointIndices.append(index)
        minAttemptsToTopIndices = [maxPointIndices[0]]
        if (len(maxPointIndices) > 1):  # out of the climbers with the same number of tops and points find the one with the fewest attempts to top
            for index in maxPointIndices:
                if (attemptsToTop[index] < attemptsToTop[minAttemptsToTopIndices[0]]):
                    minAttemptsToTopIndices = [index]
                elif (attemptsToTop[index] == attemptsToTop[minAttemptsToTopIndices[0]] and index !=
                    minAttemptsToTopIndices[0]):  # two climbers have same points & same tops
                    minAttemptsToTopIndices.append(index)
        minAttemptsToHPIndices = [minAttemptsToTopIndices[0]]
        if (len(minAttemptsToTopIndices) > 1):  # out of the climbers with the same number of tops and points and attempts to top find the one with the fewest attempts to high point
            for index in minAttemptsToTopIndices:
                if (attemptsToHighPoint[index] < attemptsToHighPoint[minAttemptsToHPIndices[0]]):
                    minAttemptsToHPIndices = [index]
                elif (attemptsToHighPoint[index] == attemptsToHighPoint[minAttemptsToHPIndices[0]] and index !=
                    minAttemptsToHPIndices[0]):  # two climbers have same points & same tops
                    minAttemptsToHPIndices.append(index)
        # now get rid of maximum point value and that climber's score in tops list
        for index in minAttemptsToHPIndices:
            points[index] = -1  # since looking for biggest value, make it small so we don't hit it again
            tops[index] = -1  # since looking for highest number of tops, make it small so we don't hit it again
            attemptsToTop[index] = 100  # since looking for the smallest number of attempts, make it big so we don't hit it again
            attemptsToHighPoint[index] = 100  # since we are looking for the smallest number of attempts, make it big so we don't hit it again
        return minAttemptsToHPIndices

    def __getMinIndexForTopScoreMethod(self, points, attemptsToTop, attemptsToHighPoint, tops, flashes):
        """
        Finds the indices of the climbers with the most tops, the most points, the most flashes, the fewest attempts to
        top, and the fewest attempts to high point and then returns those indices and sets them to -1 if we maximize
        and 1000 if we minimize
        :param points: 1D list where each entry is the total number of holds that climber reached (copy of self.points)
        :param attemptsToTop: 1D list where each entry is the number of attempts to top the climber had
        :param attemptsToHighPoint: 1D list where each entry is the number of attempts to high point the climber had
        (total attempts - attempts to top)
        :param tops: 1D list where each entry is the total number of tops the climber had
        :param flashes: 1D list where each entry is the total number of flashes the climber had
        :return: the indices of the climbers with the most tops, the most points, the most flashes, the fewest attempts to
        top, and the fewest attempts to high point
        """
        # find the maximum number of tops and if there are multiple climbers with that number of tops
        max = [0]  # stores indices of maximum values
        for i in range(1, len(tops)):
            if (tops[i] > tops[max[0]]):
                max = [i]
            elif (tops[i] == tops[max[0]]):
                max.append(i)
        maxPointIndices = [max[0]]  # index of climber(s) with maximum tops
        if (len(max)>1):  # out of the climbers with maximum number of tops find one with fewest points
            for index in max:
                if (points[index] > points[maxPointIndices[0]]):
                    maxPointIndices = [index]
                elif (points[index] == points[maxPointIndices[0]] and index != maxPointIndices[0]):  # two climbers have same points & same tops
                    maxPointIndices.append(index)
        maxFlashesIndices = [maxPointIndices[0]]
        if(len(maxPointIndices)>1):
            for index in maxPointIndices:
                if (flashes[index] > flashes[maxFlashesIndices[0]]):
                    maxFlashesIndices = [index]
                elif (flashes[index] == flashes[maxFlashesIndices[0]] and index != maxFlashesIndices[0]):  # two climbers have same points & same tops
                    maxFlashesIndices.append(index)
        minAttemptsToTopIndices = [maxFlashesIndices[0]]
        if (len(maxFlashesIndices) > 1):  # out of the climbers with the same number of tops and points find the one with the fewest attempts to top
            for index in maxPointIndices:
                if (attemptsToTop[index] < attemptsToTop[minAttemptsToTopIndices[0]]):
                    minAttemptsToTopIndices = [index]
                elif (attemptsToTop[index] == attemptsToTop[minAttemptsToTopIndices[0]] and index != minAttemptsToTopIndices[0]):  # two climbers have same points & same tops
                    minAttemptsToTopIndices.append(index)
        minAttemptsToHPIndices = [minAttemptsToTopIndices[0]]
        if (len(minAttemptsToTopIndices) > 1):  # out of the climbers with the same number of tops and points and attempts to top find the one with the fewest attempts to high point
            for index in minAttemptsToTopIndices:
                if (attemptsToHighPoint[index] < attemptsToHighPoint[minAttemptsToHPIndices[0]]):
                    minAttemptsToHPIndices = [index]
                elif (attemptsToHighPoint[index] == attemptsToHighPoint[minAttemptsToHPIndices[0]] and index !=
                    minAttemptsToHPIndices[0]):  # two climbers have same points & same tops
                    minAttemptsToHPIndices.append(index)
        # now get rid of maximum point value and that climber's score in tops list
        for index in minAttemptsToHPIndices:
            points[index] = -1  # since looking for biggest value, make it small so we don't hit it again
            flashes[index] = -1 #since we are looking for largest number, make it small so we don't hit it again
            tops[index] = -1  # since looking for highest number of tops, make it small so we don't hit it again
            attemptsToTop[index] = 100  # since looking for the smallest number of attempts, make it big so we don't hit it again
            attemptsToHighPoint[index] = 100  # since we are looking for the smallest number of attempts, make it big so we don't hit it again
        return minAttemptsToHPIndices

    def __separateAttempts(self):
        """
        separates attempts matrix into list of total attempts to top and list of total attempts to high point
        :return: 1D list of attempts to top and 1D list of attempts to high point
        """
        attemptsToTop = [0] * self.numClimbers
        attemptsToHighPoint = [0] * self.numClimbers
        for climber in range(0, self.numClimbers):
            topSum = 0
            hpSum = 0
            for problem in range(0, self.numProblems):
                if (self.topsPerProblem[climber][problem] == 1):  # climber topped the problem
                    topSum += self.attemptsPerProblem[climber][problem]
                else:  # climber did not top the problem
                    hpSum += self.attemptsPerProblem[climber][problem]
            attemptsToTop[climber] = topSum
            attemptsToHighPoint[climber] = hpSum
        return attemptsToTop, attemptsToHighPoint

    def __getMinIndex(self, list):
        """
        returns the indices of the minimum value in a list and changes the min values to 1000
        :param list: list where minimum value will be found
        :return: indices in list with that minimum value
        """
        minIndex = [0]
        for i in range(1, len(list)):
            if (list[i] < list[minIndex[0]]):
                minIndex = [i]
            elif (list[i] == list[minIndex[0]]):
                minIndex.append(i)
        for index in minIndex:
            list[index] = 1000  # 100 wasn't big enough - beware
        return minIndex

    def __getMinIndexWithTops(self, list, tops):
        """
        Finds the indices of climbers with the highest number of tops and lowest number of points (in list) and then
        sets those indices in tops to -1 and in list to 1000
        :param list: 1D list of points for each climber (given by some method)
        :param tops: 1D list with total number of tops for each climber
        :return: indices of climbers with the highest number of tops and lowest number of points (in list)
        """
        # find the maximum number of tops and if there are multiple climbers with that number of tops
        count = 1
        max = [0]  # stores indices of maximum values
        for i in range(1, len(tops)):
            if (tops[i] > tops[max[0]]):
                max = [i]
                count = 1
            elif (tops[i] == tops[max[0]]):
                count += 1
                max.append(i)
        minPointIndices = [max[0]]  # index of climber(s) with minimum point value
        if (count > 1):  # out of the climbers with maximum number of tops find one with fewest points
            for index in max:
                if (list[index] < list[minPointIndices[0]]):
                    minPointIndices = [index]
                elif (list[index] == list[minPointIndices[0]] and index != minPointIndices[
                    0]):  # two climbers have same points & same tops
                    minPointIndices.append(index)
        # now get rid of maximum point value and that climber's score in tops list
        for index in minPointIndices:
            list[index] = 100  # since looking for smallest value, make it big so we don't hit it again
            tops[index] = -1  # since looking for highest number of tops, make it small so we don't hit it again
        return minPointIndices

    def __getUSAClimbingRankingPoints(self):
        """
        Takes self.ranks and assigns tied climbers a rank equal to that of their tied places (how ties are generally
        handled in ranking methods)
        :return: 2D list similar to self.ranks
        """
        ranks = copy.deepcopy(self.ranks)
        for col in range(0, len(self.ranks[0])):  # loops through each problem
            rank = 1
            while (rank < len(self.ranks) + 1):  # loops through each possible rank on problem
                indices = []  # hold the indices in rankings that have that particular rank
                for row in range(0, len(self.ranks)):  # loops through each climber for that problem
                    if (ranks[row][col] == rank):  # if that climber got that rank on the problem
                        indices.append(row)  # add that index to the indices list
                if (len(
                        indices) > 1):  # if the indices list is larger than 1, change all the appropriate values in rank so that they are the average rank
                    i = 0
                    sum = 0
                    while (i < len(indices)):
                        sum += rank + i
                        i += 1
                    newRank = sum / len(indices)
                    for i in indices:
                        ranks[i][col] = newRank
                    rank += len(indices) - 1
                rank += 1
        return ranks

    def __flipRankings(self):  # flips rankings so rows represent each complete rank
        """
        flips rankings so rows represent each complete rank
        :return: 2D list of ranks where each row is the rank of climbers on a problem
        """
        ranks = np.zeros(shape=(self.numProblems, self.numClimbers))
        for row in range(0, len(ranks)):
            for col in range(0, len(ranks[0])):
                ranks[row][col] = self.ranks[col][row]
        return ranks

    def __wAlgorithm(self):
        """
        uses weiszfeld's algorithm to calculate the geometric median of the ranks (in Euclidean space)
        :return: point generated by weiszfeld's algorithm (rating, not a rank)
        """
        numClimbers = len(self.ranks)
        numProblems = len(self.ranks[0])
        # calculate initial rank: centroid
        finalRank = [0] * numClimbers
        for i in range(0, numClimbers):
            sum = 0
            for m in range(0, numProblems):
                sum += self.flippedRanks[m][i]
            finalRank[i] = sum / numProblems
        # calculate next final rank
        newRank = self.__calculateNextFinalRank(finalRank)
        while (bd.euclideanDistance(finalRank, newRank) > .1):
            finalRank = newRank
            newRank = self.__calculateNextFinalRank(finalRank)
        return newRank

    def __calculateNextFinalRank(self, finalRank):
        """
        Calculates the next aggregated rank according to weiszfeld's algorithm (next approximation)
        :param finalRank: current approximation
        :return: next approximation
        """
        sum = [0] * self.numClimbers
        sum2 = 0
        for i in range(0, self.numProblems):
            d = bd.euclideanDistance(finalRank, self.flippedRanks[i])
            if (d == 0):
                raise ZeroDivisionError("landed on one of the points: ", finalRank)
            sum = self.__listAdd(sum, self.__listDivide(self.flippedRanks[i], d))
            sum2 += 1 / d
        newRank = self.__listDivide(sum, sum2)
        return newRank

    def __listDivide(self, list, num):
        """
        divides every element in list by num
        :param list: 1D list of numbers
        :param num: number that list will be divided by
        :return: new list where newList_i = list_i/num
        """
        newList = [0] * len(list)
        for i in range(0, len(list)):
            newList[i] = list[i] / num
        return newList

    def __listAdd(self, listA, listB):
        """
        adds elements in listA and listB to create a new list
        :param listA: first list to be added
        :param listB: second list to be added
        :return: new list where listC_i = listA_i+listB_i
        """
        if (len(listA) == len(listB)):
            listC = [0] * len(listA)
            for i in range(0, len(listA)):
                listC[i] = listA[i] + listB[i]
            return listC
        else:
            raise Exception("lengths don't match, cannot add")

    def __calcSum(self, finalRank, method):
        """
        Calculates the sum of distances from finalRank to each rank in the ranks matrix using the given distance
        :param finalRank: aggregated rank
        :param method: which distance to use
        :return: the sum of the distances from finalRank to each of the ranks in self.ranks
        """
        sum = 0
        for rank in self.flippedRanks:
            sum += method(finalRank, rank)
        return sum

    def wAlgorithmInteger(self):  # turns algorithm output into optimal rank based solely on ordering of values
        """
        performs weiszfeld's algorithm to get a rating of the climbers and then turns that rating into a rank based soley
        on number of tops and then the ordering of the values.
        :return: the rank
        """
        finalRank = self.__wAlgorithm()
        return self.__getIntegerRanks(finalRank, 0)

    def __sort(self, finalRankAndIndices, threshold):
        finalRankSorted = []
        for i in range(0, len(finalRankAndIndices)):
            finalRankAndIndices[i].append(0)
            finalRankSorted.append(finalRankAndIndices[i])
        #do insertion sort on ratings
        for i in range(1, len(finalRankSorted)):
            j = i
            while (j > 0 and finalRankSorted[j][0] < finalRankSorted[j - 1][0]):
                temp = finalRankSorted[j]
                finalRankSorted[j] = finalRankSorted[j - 1]
                finalRankSorted[j - 1] = temp
                j -= 1
        # add places to finalRankSorted
        finalRankSorted[0][2] = 1
        count = 1
        for i in range(1, len(finalRankSorted)):
            if (finalRankSorted[i][0] - finalRankSorted[i - 1][0] <= threshold):  # tie
                finalRankSorted[i][2] = finalRankSorted[i - 1][2]
                count += 1
            else:
                finalRankSorted[i][2] = finalRankSorted[i - 1][2] + count
                count = 1
        return finalRankSorted

    def __sortWithTops(self, finalRankAndIndices, threshold):
        """
        Sorts finalRankAndIndices and adds an extra element to each sublist that has final rank
        :param finalRankAndIndices: 2-d list where each sublist is the rating output by weizsfel'ds algorithm
        followed by the index of the rating (indices are in order for this list, used to keep track during sorting)
        :param threshold: if two ratings are within threshold of eachother, the climbers tie
        :return: finalRankSorted, which is a 2-d list with each sublist having the rating output by weiszfeld's algorithm,
        the index of the rating (which climber it goes with) and the final place of that climber
        """
        finalRankSorted = []
        for i in range(0,len(finalRankAndIndices)):
            finalRankAndIndices[i].append(0)
            finalRankSorted.append(finalRankAndIndices[i])
        for i in range(1, len(finalRankSorted)): #insertion sort
            j = i
            while (j > 0 and
                       ((finalRankSorted[j][0] < finalRankSorted[j - 1][0] and self.tops[finalRankSorted[j][1]] ==
                           self.tops[finalRankSorted[j - 1][1]])
                        or self.tops[finalRankSorted[j][1]] > self.tops[finalRankSorted[j - 1][1]])):
                #swap j and j-1
                temp = finalRankSorted[j]
                finalRankSorted[j] = finalRankSorted[j - 1]
                finalRankSorted[j - 1] = temp
                j -= 1
        # add places to finalRankSorted
        finalRankSorted[0][2] = 1
        count = 1
        for i in range(1, len(finalRankSorted)):
            if(finalRankSorted[i][0]-finalRankSorted[i-1][0]<=threshold and self.tops[finalRankSorted[i][1]] ==
                           self.tops[finalRankSorted[i - 1][1]]): #tie
                finalRankSorted[i][2] = finalRankSorted[i-1][2]
                count+=1
            else:
                finalRankSorted[i][2] = finalRankSorted[i-1][2] + count
                count = 1
        return finalRankSorted

    def __getIntegerRanks(self, finalRank, threshold):
        """
        turns the weiszfeld ratings into a rank, where climbers tie if their ratings are within threshold of eachother
        :param finalRank:rating from Weiszfeld's algorithm
        :param threshold: if two ratings are within this distance, the climbers tie
        :return: the final rank of the climbers
        """
        finalRankAndIndices = []
        for index in range(len(finalRank)):
            finalRankAndIndices.append([finalRank[index], index])
        finalRankAndIndicesSorted = self.__sortWithTops(finalRankAndIndices, threshold)
        integerRank = [0]*len(finalRank)
        for i in range(0, len(finalRankAndIndicesSorted)):
            integerRank[finalRankAndIndicesSorted[i][1]] = finalRankAndIndicesSorted[i][2]
        return integerRank

    def __getIntegerRanksNoTops(self, finalRank, threshold):
        """
        turns the weiszfeld ratings into a rank, where climbers tie if their ratings are within threshold of eachother
        :param finalRank:rating from Weiszfeld's algorithm
        :param threshold: if two ratings are within this distance, the climbers tie
        :return: the final rank of the climbers
        """
        finalRankAndIndices = []
        for index in range(len(finalRank)):
            finalRankAndIndices.append([finalRank[index], index])
        finalRankAndIndicesSorted = self.__sort(finalRankAndIndices, threshold)
        integerRank = [0] * len(finalRank)
        for i in range(0, len(finalRankAndIndicesSorted)):
            integerRank[finalRankAndIndicesSorted[i][1]] = finalRankAndIndicesSorted[i][2]
        return integerRank

    def wAlgorithmNoTops(self):
        finalRank = self.__wAlgorithm()
        optimalRank = self.__getIntegerRanksNoTops(finalRank, 0) #will be updated if a different threshold produces a more optimal rank
        optimalSum = self.__calcSum(optimalRank, bd.euclideanDistance)  # will be updated to reflect the distance sum from optimalRank
        optimalThreshold = 0  # updated when a new threshold produces an optimal ranking
        threshold = .1
        while (threshold <= .5):
            testRank = self.__getIntegerRanksNoTops(finalRank, threshold)
            testSum = self.__calcSum(testRank, bd.euclideanDistance)
            if (testSum < optimalSum):  # testRank is more optimal than optimalRank
                optimalRank = testRank
                optimalSum = testSum
                optimalThreshold = threshold
            threshold += .1
        # return optimalRank, optimalThreshold
        return optimalRank

    def wAlgorithmOptimalInteger(self):
        """
        Performs weiszfeld's algorithm to get a rating of the different climbers and then returns the optimal ranking
        of those climbers (tests different tie thresholds between 0 and .5)
        :return: the optimal rank
        """
        finalRank = self.__wAlgorithm()
        optimalRank = self.__getIntegerRanks(finalRank, 0)  # will be updated if a different threshold produces a more optimal rank
        optimalSum = self.__calcSum(optimalRank, bd.euclideanDistance)  # will be updated to reflect the distance sum from optimalRank
        optimalThreshold = 0  # updated when a new threshold produces an optimal ranking
        threshold = .1
        while (threshold <= .5):
            testRank = self.__getIntegerRanks(finalRank, threshold)
            testSum = self.__calcSum(testRank, bd.euclideanDistance)
            if (testSum < optimalSum):  # testRank is more optimal than optimalRank
                optimalRank = testRank
                optimalSum = testSum
                optimalThreshold = threshold
            threshold += .1
        #return optimalRank, optimalThreshold
        return optimalRank

    def linearProgrammingOptimal(self):
        """
        uses scipy's linear program solver to determine optimal rank
        trying to maximize cij * xij, where cij is the number of lists with
        i ranked ahead of j, and xij is 1 if i is ranked ahead of j, -1 if
        i is ranked below j, and 0 if i and j are tied.
        basically trying to minimize pairwise disagreements between final rank
        and each ranking (but not the same as minimizing the bubble distance between final rank and each ranking)
        """
        return lp.optimize(self.ranks, self.climbers, self.tops)[0]

    def linearProgrammingOptimalSplit(self):
        """
        splits problem up by number of tops, so find optimal rank for each set of climbers
        with the same number of tops
        uses scipy's linear program solver to determine optimal rank
        trying to maximize cij * xij, where cij is the number of lists with
        i ranked ahead of j, and xij is 1 if i is ranked ahead of j, -1 if
        i is ranked below j, and 0 if i and j are tied.
        basically trying to minimize pairwise disagreements between final rank
        and each ranking (but not the same as minimizing the bubble distance between final rank and each ranking)
        """
        return lp.optimizeSplit(self.ranks, self.climbers, self.tops)[0]

    def locallyKemenize(self, method):
        """
        Given a final ranking and a set of rankings that that final ranking aggregated,
        determines if there are any swaps that can be made in ranking (switch places i and i+1 or
        make climbers in i and i+1 places both in ith place)
        to get a better final ranking. Current method saves optimal ranking as it goes down list
        of places in goodTestRank variable. If the new testRank is better than the old one, goodTestRank
        is updated and goodSum becomes testSum and goodRankedClimbers is altered to match the goodTestRank.
        When it encounters a tie in the i+1 place, the climber
        in place i is tested swapping with all climbers tied for i+1 (until a better rank is found).
        when it encounters a tie in the ith place, each climber tied for that place is tested as being
        in the i+1 place (until a better rank is found). Once the end of the list is reached, if changes
        have been made, then goodTestRank becomes finalRank and goodRankedClimbers becomes rankedClimbers
        and we go through again and see if any changes can be made
        :param method: method whose produced aggregated rank will be locally kemenized
        :return: locally kemenized rank
        """
        return self.__locallyKemenize(method(), self.ranks, self.tops, self.climbers, False)

    def __locallyKemenize(self, finalRank, rankings, tops, climbers, recursion):
        """
        Given a final ranking and a set of rankings that that final ranking aggregated,
        determines if there are any swaps that can be made in ranking (switch places i and i+1 or
        make climbers in i and i+1 places both in ith place)
        to get a better final ranking. Current method saves optimal ranking as it goes down list
        of places in goodTestRank variable. If the new testRank is better than the old one, goodTestRank
        is updated and goodSum becomes testSum and goodRankedClimbers is altered to match the goodTestRank.
        When it encounters a tie in the i+1 place, the climber
        in place i is tested swapping with all climbers tied for i+1 (until a better rank is found).
        when it encounters a tie in the ith place, each climber tied for that place is tested as being
        in the i+1 place (until a better rank is found). Once the end of the list is reached, if changes
        have been made, then goodTestRank becomes finalRank and goodRankedClimbers becomes rankedClimbers
        and we go through again and see if any changes can be made
        :param finalRank: 1D list of rank for each climber (given by some rank aggregation method)
        :param rankings: 2D list of rankings where each row is the rank on each problem for a given climber
        :param tops: 1D list of total number of tops for each climber
        :param rankedClimbers: 1D list that has climbers' names in order of their finalRank
        :param climbers: 1D list that has climbers' names in the order they are in the data (how tops and ranks are kept track of)
        :param recursion: true if this time through was a recursive call, always false when you call the method yourself
        :return: locally kemenized ranking from finalRank and also updates rankedClimbers so there is an accurate list of
        climbers in the order of their final rank
        """

        # flip rankings so rows represent each complete rank
        # ranks = [[0]*len(rankings[0])]*len(rankings) doesn't work because multiplication only does shallow copy
        if (recursion == False):
            ranks = np.zeros(shape=(len(rankings[0]), len(rankings)))
            for row in range(0, len(ranks)):
                for col in range(0, len(ranks[0])):
                    ranks[row][col] = rankings[col][row]
        else:
            ranks = rankings
        sum = self.__calcSum(finalRank, bd.d)  # measure of how good this current finalRank is
        i = 1  # will use to iterate through places climbers could be in in their finalRank
        better = False  # true if there is a better rank than finalRank
        goodTestRank = finalRank.copy()  # will save ranks that are more optimal than finalRank
        goodSum = sum  # saves the optimal sum that goes with the optimal rank (goodTestRank)
        while (i < len(finalRank)):
            tiedIndicesi = self.__getIndicesOfNum(finalRank, i)  # which climbers finished in ith place
            tiedIndicesi1 = self.__getIndicesOfNum(finalRank, i + 1)  # which climbers finished in place i+1
            if (len(tiedIndicesi) > 1):  # tie for place i - we will see if one of the climbers should be in the next possible place instead
                nextPlace = i + len(tiedIndicesi) - 1  # next place one climber could go (if three people tied for first, next place for one of them is third)
                tiedClimbers = []  # list of climbers tied for place i
                for index in tiedIndicesi:
                    tiedClimbers.append(climbers[index])
                for j in range(0, len(tiedIndicesi)):  # loops through tied climbers
                    testRank = finalRank.copy()
                    testRank[tiedIndicesi[
                        j]] = nextPlace  # give one of the climbers tied for ith place next possible place place
                    testSum = self.__calcSum(testRank, bd.d)
                    if (testSum < goodSum):
                        goodTestRank = testRank.copy()
                        goodSum = testSum
                        better = True
                        break
                if (i + len(tiedIndicesi) >= len(finalRank)):  # no better ranking close by
                    if better:
                        return self.__locallyKemenize(goodTestRank, ranks, tops, climbers, True)
                    else:
                        return finalRank
            elif (len(
                    tiedIndicesi1) > 1):  # tie for place i+1 - will see if we can switch climber in ith position with one tied for i+1 place
                if (tops[finalRank.index(i)] != tops[
                    finalRank.index(i + 1)]):  # can't switch because different numbers of tops
                    i += 1
                    continue
                tiedClimbers = []  # list of climbers tied for place i+1
                for index in tiedIndicesi1:
                    tiedClimbers.append(climbers[index])
                for j in range(0, len(tiedIndicesi1)):
                    testRank = finalRank.copy()
                    testRank[tiedIndicesi1[j]] = i
                    testRank[finalRank.index(i)] = i + 1
                    testSum = self.__calcSum(testRank, bd.d)
                    if (testSum < goodSum):  # more optimal ranking
                        goodTestRank = testRank.copy()
                        goodSum = testSum
                        better = True
                if (i == len(finalRank) - 1):  # no better final rankings close by
                    if better:
                        return self.__locallyKemenize(goodTestRank, ranks, tops, climbers, True)
                    else:
                        return finalRank
            else:
                higher = finalRank.index(i)  # climber who finished in ith place
                lower = finalRank.index(i + 1)  # climber who finish in i+1 place
                if (tops[higher] == tops[lower]):  # same number of tops so rankings can be switched
                    # try fully switching them
                    testRank = finalRank.copy()
                    testRank[higher] = i + 1  # climber who finished in ith place now in place i+1
                    testRank[lower] = i  # climber who finihsed in place i+1 now in place i
                    testSum = self.__calcSum(testRank, bd.d)
                    if (testSum < goodSum):  # if the new testRank is "better" than the other finalRank
                        goodTestRank = testRank.copy()  # save this testRank because it is optimal
                        goodSum = testSum  # update optimal sum
                        better = True
                    else:
                        # try having them both finish in ith place
                        testRank[higher] = i
                        testSum = self.__calcSum(testRank, bd.d)
                        if (testSum < goodSum):  # if the new testRank is "better" than the other finalRank
                            goodTestRank = testRank.copy()  # save this testRank because it is optimal
                            goodSum = testSum  # update optimal sum
                            better = True
                if (i == len(finalRank) - 1):  # ranking is fixed because of number of tops and reached end of list
                    if (better):
                        return self.__locallyKemenize(goodTestRank, ranks, tops, climbers, True)
                    else:
                        return finalRank
            i += len(tiedIndicesi)

    def __getIndicesOfNum(self, finalRank, i):
        """return list of all the indices in finalRank i appears at"""
        indices = []
        for j in range(0, len(finalRank)):
            if (finalRank[j] == i):
                indices.append(j)
        return indices

    def runMethod(self, num):
        """
        runs method that is at index num in the list of methods (see list below)
        if num is larger than len(methods)-1 then locally kememize the method that corresponds to num-16
        0 = l2NormMethodNoTops
        1 = l2NormMethod
        2 = geometricMeanMethod,
        3 = geometricMeanMethodNoTops
        4 = usacMethod
        5 = usacMethodNoTops
        6 = bordaMethodNoTops
        7 = bordaMethod
        8 = bordaMethodTraditionalTies
        9 = mergedOldMethod
        10 = abs10Method
        11 = topScoreMethod
        12 = wAlgorithmInteger
        13 = wAlgorithmOptimalInteger
        14 = wAlgorithmNoTops
        15 = linearProgrammingOptimalSplit
        """
        if(num<len(self.methods)):
            method = self.methods[num]
            return method()
        else:
            method = self.locallyKemenize(self.methods[num-len(self.methods)])
            return method

    def getMethod(self, num):
        """
        returns the name of the method that is called by num
        :param num: which method you want
        :return: the name of the method that num calls
        """
        if(num<len(self.methods)):
            return self.methods[num].__name__
        else:
            return "lk " + self.methods[num-len(self.methods)].__name__

def getMethod(num):
    """
    returns the name of the method that is called by num (same as above but a static method)
    :param num: which method you want
    :return: the name of the method that num calls
    """
    ranker = ClimbingRanker("fyaBNatsQualis2016.csv",0)
    return ranker.getMethod(num)

# ranker = ClimbingRanker("fybBNatsSemis2016.csv")
# print(ranker.ranks)
# print(ranker.points)
# print(ranker.l2NormMethodNoTops())
# print(ranker.l2NormMethod())
# print(ranker.geometricMeanMethodNoTops())
# print(ranker.geometricMeanMethod())
# print(ranker.bordaMethodNoTops())
# print(ranker.bordaMethod())
# print(ranker.bordaMethodUsacRankingPoints())
# print(ranker.abs10Method())
# print(ranker.topScoreMethod())
# print(ranker.mergedOldMethod())
# print(ranker.wAlgorithmInteger())
# print(ranker.wAlgorithmOptimalInteger())
# print(ranker.wAlgorithmNoTops())
# print(ranker.linearProgrammingOptimal())
# print(ranker.linearProgrammingOptimalSplit())
