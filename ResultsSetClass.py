import numpy as np
import RankingMethodsClass as rmc

class ResultSet:
    def __init__(self, numClimbers, numProblems, randomNumberGenerator, haveClimberAbilities = True):
        """
        Creates a set of results for numClimbers on numProblems
        :param numClimbers: number of climbers
        :param numProblems: number of problems
        :param randomNumberGenerator: instance of numpy's RandomState class that generates random numbers
        :param haveClimberAbilities: true if climber abilities are taken into account, false otherwise (high point
        on each problem is random and not tied to previous highpoints at all)
        """
        self.numClimbers = numClimbers
        self.numProblems = numProblems
        self.randomNumberGenerator = randomNumberGenerator
        self.haveClimberAbilities = haveClimberAbilities
        if (self.haveClimberAbilities):
            self.__generateClimberAbilityList() #vector containing the ability for each climber (number generally between 0 and 1)
        self.__generateMaxPointsPerProblem() #vector containing the maximum possible points for each problem (of length numProblems)
        self.__generatePointsPerProblem() #matrix with each climber's high point on each problem (rows = climbers)
        self.__generateAttemptsPerProblem() #matrix with each climber's number of attempts on each problem (rows = climbers)
        #print("tops 1")
        self.__generateTopsPerProblem() #matrix with the tops of each climber on each problem (rows = climbers, columns = problems)
        #print("ranks matrix 1")
        self.__generateRanksMatrix() #matrix with the rank of each climber on each problem (rows = climbers, columns = problems)

    def returnResultSet(self):
        """
        :return: all the information about this set of results
        """
        return self.ranks, self.pointsPerProblem, self.attemptsPerProblem, self.topsPerProblem, self.maxPointsPerProblem

    def generateResultSetTwo(self, numClimbersChanged, numProblemsChanged, randomNumberGenerator):
        """
        Generates a second result set where the performance of the first numClimbersChanged climbers is altered on the first
        numProblemsChanged problemsand the rest remain the same.
        FYI these input matrices are altered in the program - if this is not desired they must be passed as deep copies
        :param numClimbersChanged: number of climbers whose score will be changed (score of climber at index numClimbersChanged will remain unchanged)
        :param numProblemsChanged: number of problems on which the chosen climbers' scores will be changed
        :return: the ranks matrix, points matrix, attempts matrix, tops matrix. maxPointsPerProblem shouldn't change so
        it is not returned.
        """
        if (numClimbersChanged >= self.numClimbers - 1):
            raise ValueError("At least two climbers must have their performance unchanged")
        elif (numProblemsChanged > self.numProblems):
            raise ValueError("Performance cnanot be changed on more problems than exist")

        # alter the points and attempts of the first numClimbersChanged climbers on the first numProblemsChanged problems
        for row in range(0, numClimbersChanged):
            for col in range(0, numProblemsChanged):
                self.pointsPerProblem[row][col] = self.__generateHighPoint(self.maxPointsPerProblem[col], row)
                self.attemptsPerProblem[row][col] = self.__generateNumberOfAttempts()

        # calculate the new tops matrix
        #print("tops two")
        self.__generateTopsPerProblem()

        # calculate the new ranks matrix
        #print("ranks matrix two")
        self.__generateRanksMatrix()

        return self.ranks, self.pointsPerProblem, self.attemptsPerProblem, self.topsPerProblem

    ##################HELPER GENERATING FUNCTIONS#######################################
    def __generateClimberAbilityList(self):
        """
        Creates a list of the ability for each climber. List is of length numClimbers and the abilites are between 0 and 1+.
        When determining high point, this score will be taken into account as a multiplier.
        """
        self.climberAbilities = [0]*self.numClimbers
        for index in range(0, self.numClimbers):
            self.climberAbilities[index] = self.__generateClimberAbility()

    def __generateClimberAbility(self):
        """
        Generates a random number between 0 and 1+ (based on a normal distribution with mean .5 and std .25). If the random
        number is less than 0, sets it to zero. Otherwise, returns the number as is.
        :return: ability of the climber
        """
        if (self.randomNumberGenerator == None):
            ability = np.random.normal(.5, .25)
        else:
            ability = self.randomNumberGenerator.normal(.5, .25)
        if (ability < 0):  # cannot have negative ability
            ability = 0
        return ability

    def __generateRanksMatrix(self):
        """
        Creates the ranks matrix for the given matrices of points and attempts
        :return: ranks matrix (rows = climbers, columns = problems)
        """
        self.ranks = np.zeros(shape=(self.numClimbers, self.numProblems))
        for col in range(0, self.numProblems):
            points = [0] * self.numClimbers
            attempts = [0] * self.numClimbers
            for row in range(0, self.numClimbers):
                points[row] = self.pointsPerProblem[row][col]
                attempts[row] = self.attemptsPerProblem[row][col]
            rank = self.__createRank(points, attempts)  # create one column of the rank matrix (rank for one problem)
            for row in range(0, self.numClimbers):
                self.ranks[row][col] = rank[row]
        #print(self.ranks)

    def __generatePointsPerProblem(self):
        """
        We will assume points per problem is normally distributed and that people's performance on one problem is independent of their
        performance on another climb
        :return: matrix of points per problem for each climber (rows = climbers)
        """
        self.pointsPerProblem = np.zeros(shape=(self.numClimbers, self.numProblems))
        for col in range(0, self.numProblems):
            maxPoint = self.maxPointsPerProblem[col]
            for row in range(0, self.numClimbers):
                self.pointsPerProblem[row][col] = self.__generateHighPoint(maxPoint, row)

    def __generateHighPoint(self, maxPoint, climberIndex):
        """
        Generates a high point for some climber on some problem with the given maximum possible points
        :param maxPoint: maximum point value of the climb (point value associated with finishing the climb)
        :return: high point for some climber on the problem
        """
        if(self.haveClimberAbilities):
            climberAbility = self.climberAbilities[climberIndex]
            # climber ability varies on different problems, this is how we account for that
            if(self.randomNumberGenerator == None):
                variedClimberAbility = np.random.normal(climberAbility, .1)
            else:
                variedClimberAbility = self.randomNumberGenerator.normal(climberAbility, .1)
            pointValue = int(maxPoint*variedClimberAbility)
            if (pointValue < 0):  # cannot have negative high points
                pointValue = 0
            elif (pointValue > maxPoint):  # cannot have a higher high point than the max number of holds on the climb
                pointValue = maxPoint
            return pointValue
        else:
            if (self.randomNumberGenerator == None):
                pointValue = int(np.random.normal(2 * (maxPoint / 3), maxPoint / 3))
            else:
                pointValue = int(self.randomNumberGenerator.normal(2 * (maxPoint / 3), maxPoint / 3))
            if (pointValue < 0):  # cannot have negative high points
                pointValue = 0
            elif (pointValue > maxPoint):  # cannot have a higher high point than the max number of holds on the climb
                pointValue = maxPoint
            return pointValue

    def __generateMaxPointsPerProblem(self):
        """
        Creates a vector of maximum points possible per problem
        """
        self.maxPointsPerProblem = [20] * self.numProblems

    def __generateAttemptsPerProblem(self):
        """
        Generates a matrix of attempts per problem where the rows correspond to the climbers and the columns are the problems.
        """
        self.attemptsPerProblem = np.zeros(shape=(self.numClimbers, self.numProblems))
        for row in range(0, self.numClimbers):
            for col in range(0, self.numProblems):
                self.attemptsPerProblem[row][col] = self.__generateNumberOfAttempts()

    def __generateNumberOfAttempts(self):
        """
        Generates a random number of attempts for some climber on some problem based on a poisson distribution with
        lambda = 1 (use of this distribution is supported with data analysis). Since having 0 attempts on a problem makes
        no sense, we add 1 to the random number produced using the poisson distribution.
        This generation is in a separate method for ease of changing later on.
        :return: number of attempts for one climber on one problem
        """
        if (self.randomNumberGenerator == None):
            return np.random.poisson() + 1
        else:
            return self.randomNumberGenerator.poisson() + 1

    def __generateTopsPerProblem(self):
        """
        Generates a matrix of tops
        """
        self.topsPerProblem = np.zeros(shape=(self.numClimbers, self.numProblems))
        for row in range(0, self.numClimbers):
            for col in range(0, self.numProblems):
                if (self.pointsPerProblem[row][col] == self.maxPointsPerProblem[col]):
                    self.topsPerProblem[row][col] = 1
                else:
                    self.topsPerProblem[row][col] = 0
        #print("tops", self.topsPerProblem)

    ##################HELPER METHODS##########################################
    def __createRank(self, pointsList, attemptsList):
        """
        Creates a rank of climbers on one problem based on pointsList and attemptsList (called by generateRanksMatrix
        to create the rank for each problem)
        :param pointsList: list of high point for each climber on the given problem
        :param attemptsList: list of attempts for each climber on the given problem
        :return: list with rank for each climber on that problem
        """
        finalNumRank = [0] * self.numClimbers  # aggregated rank where climbers are listed in original order and these are their places
        i = 0  # what place the climber is in in the final rank
        while (i < self.numClimbers):
            indices = self.__getMinIndexWithTieBreaker(pointsList, attemptsList)
            j = 0
            while (j < len(indices)):  # climbers whose indices are in indices list all tie
                finalNumRank[indices[j]] = i + 1  # +1 because rank from 1 to numClimbers
                j += 1
            i += len(indices)
        return finalNumRank

    def __getMinIndexWithTieBreaker(self, points, attempts):
        """
        Finds the indices of climbers with the highest number of points and lowest number of attempts and then
        sets those indices in points to -1 and in attempts to 1000
        :param points: 1D list of high points for each climber on a problem
        :param attempts: 1D list with attempts for each climber on a problem
        :return: indices of climbers with the highest number of points and lowest number of attempts (in list)
        """
        # find the maximum number of points and if there are multiple climbers with that number of points
        count = 1
        max = [0]  # stores indices of maximum values
        for i in range(1, len(points)):
            if (points[i] > points[max[0]]):
                max = [i]
                count = 1
            elif (points[i] == points[max[0]]):
                count += 1
                max.append(i)
        minPointIndices = [max[0]]  # index of climber(s) with minimum number of attempts
        if (count > 1):  # out of the climbers with maximum number of points find one with fewest attempts
            for index in max:
                if (attempts[index] < attempts[minPointIndices[0]]):
                    minPointIndices = [index]
                elif (attempts[index] == attempts[minPointIndices[0]] and index != minPointIndices[0]):  # two climbers have same points & same attempts
                    minPointIndices.append(index)
        # now get rid of maximum point value and that climber's score in attempts list
        for index in minPointIndices:
            attempts[index] = 100  # since looking for smallest value, make it big so we don't hit it again
            points[index] = -1  # since looking for highest number of tops, make it small so we don't hit it again
        return minPointIndices
