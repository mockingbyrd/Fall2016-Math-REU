import csv
import numpy as np

class ClimbingDataFile:

    def __init__(self, fileName, n): #reads in first n climbers from fileName (if you want all climbers n=0)
        """
        creates a new ClimbingDataFile object
        :param fileName: file where data will be read in from
        :param n: how many climbers will be read in from the data set (n=0 reads in all climbers)
        """
        self.fileName = fileName
        self.openFile(n)
        self.calcNumProblems()

    def openFile(self, n): #n = number of lines to be read
        """
        reads in data from file and stores it in self.climbingData (2D list)
        :param n: number of lines to be read from file (n=0 means read all lines)
        """
        path = "csvFiles/" + self.fileName
        with open(path, 'r') as f:
            reader = csv.reader(f)
            self.climbingData = list(reader)
        if(n == 0):
            return self.climbingData
        for i in range(n+1,len(self.climbingData)):
            self.climbingData.pop()
        return self.climbingData

    def calcNumProblems(self):
        """
        calculates number of problems in data set and stores as self.numProblems
        """
        temp = (len(self.climbingData[0])-4)/4
        if(not(temp == int(temp))):
            raise Exception("not integer number of problems: ", temp)
        else:
            self.numProblems = int(temp)

    def getClimbers(self):
        """
        :return: 1D list of climbers in the order they appear in data set
        """
        self.climbers = []
        for row in range(1,len(self.climbingData)): #row 0 just has column headers - don't need those
            self.climbers.append(self.climbingData[row][1])
        return self.climbers

    def getTops(self):
        """
        :return: 1D list of tops for each climber in order of climbers list
        """
        self.tops = []
        for row in range(1,len(self.climbingData)):
            try:
                self.tops.append(int(self.climbingData[row][-2]))
            except ValueError:
                self.tops.append(0) #for some reason there is just ,, in the file instead of ,0,
        return self.tops

    def getRanks(self):
        """
        :return: numpy matrix where each column corresponds to the rank of a climber on each problem
        """
        self.ranks = np.zeros(shape=(len(self.climbingData)-1, self.numProblems))
        for row in range(0,len(self.climbingData)-1):
            for col in range(0,self.numProblems):
                self.ranks[row][col] = self.climbingData[row+1][col*4+4]
        return self.ranks

    def getPoints(self):
        """
        :return: 1D list where each entry corresponds to the total number of points (holds) of that climber
        """
        self.points = []
        for row in range(0,len(self.climbingData)-1):
            p = 0
            for col in range(0,self.numProblems):
                p += int(self.climbingData[row+1][col*4+2])
            self.points.append(p)
        return self.points

    def getPointsPerProblem(self):
        """
        :return: numpy matrix where each column corresponds to the number of points a climber got on the problem
        """
        self.probPoints = np.zeros(shape=(len(self.climbingData) - 1, self.numProblems))
        for row in range(0, len(self.climbingData) - 1):
            for col in range(0, self.numProblems):
                self.probPoints[row][col] = self.climbingData[row + 1][col * 4 + 2]
        return self.probPoints

    def getAttempts(self):
        """
        :return: 1D list of total number of attempts for each climber in order of climbers list
        """
        self.attempts = []
        for row in range(0,len(self.climbingData)-1):
            sum = 0
            for col in range(0,self.numProblems):
                sum+= int(self.climbingData[row+1][col*4+3])
            self.attempts.append(sum)
        return self.attempts

    def getAttemptsPerProblem(self):
        """
        :return: numpy matrix where each column corresponds to the number of attempts a climber had on the problem
        """
        self.probAttempts = np.zeros(shape=(len(self.climbingData) - 1, self.numProblems))
        for row in range(0, len(self.climbingData) - 1):
            for col in range(0, self.numProblems):
                self.probAttempts[row][col] = self.climbingData[row + 1][col * 4 + 3]
        return self.probAttempts


