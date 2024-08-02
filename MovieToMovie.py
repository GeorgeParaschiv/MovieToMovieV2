from solver import MovieSolver, Node
from dailyChallenge import DailyChallenge
import config
import time, ctypes, sys, os, re

class Logging:
    def __init__(self, filename):
        self.outFile = open(filename, "w", encoding="utf-8")
        self.stdout = sys.stdout
        sys.stdout = self

    def write(self, text):
        self.stdout.write(text)
        self.outFile.write(text)

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        sys.stdout = self.stdout

class MovieToMovie():

    def __init__(self, choice, index=None):
        self.solver = MovieSolver(config.api_key)

        self.challenge = DailyChallenge().getDailyChallenge(index)
        self.daily = [Node((self.challenge[1]['ID'], self.challenge[1]['NAME'], self.solver.getMoviePopularity(self.challenge[1]['ID']))),
                      Node((self.challenge[2]['ID'], self.challenge[2]['NAME'], self.solver.getMoviePopularity(self.challenge[2]['ID'])))]
        
        self.choice = choice

    def getStartEnd(self):

        if (self.choice == "D"):
            self.solver.start = self.daily[0]
            self.solver.end = self.daily[1]
            return True
        elif (self.choice == "C"):
            print("WIP")
            return False
        else:
            raise

    def printLines(self):

        print(f"Solutions of length {self.DEPTH}:")
        
        if self.solver.lines:
            for index, line in enumerate(self.solver.lines):
                print(f"{index+1}. " + line[0])

            print("\nSolutions sorted by popularity:")
            self.solver.lines.sort(key = lambda x : -x[1])
            for index, line in enumerate(self.solver.lines):
                print(f"{index+1}. {line[1]:.2f} | " + line[0])
        else:
            print("No solutions found.")

    def findSolutions(self, depth, cont=False):

        self.DEPTH = depth

        startTime  = time.time()

        self.solver.constructGraph(self.DEPTH, cont)
        self.solver.findLines(self.solver.start, self.DEPTH)
        self.printLines()

        endTime = time.time() - startTime

        print(f"\nTime Elapsed: {int(endTime/3600)}h {int((endTime%3600)/60)}m {int(endTime%60)}s {int((endTime-int(endTime))*1000)}ms\n")

    def search(self):

        daily = self.getStartEnd()

        self.solver.start.name = re.sub(r"(?u)[^-\w.,\s]", "", self.solver.start.name)
        self.solver.end.name = re.sub(r"(?u)[^-\w.,\s]", "", self.solver.end.name) 

        if (daily):
            with Logging(f"{os.getcwd()}\\Logs\\Daily Challenges\\#{self.challenge[0]} {self.solver.start.name} - {self.solver.end.name}.txt"):

                print(f"Daily Challenge #{self.challenge[0]}: ", end="")
                print(self.solver.start.name + " -> " + self.solver.end.name +"\n")

                depth = 1
                while (not self.solver.lines):
                    self.findSolutions(depth, True)
                    depth += 1
        else:
            with Logging(f"{os.getcwd()}\\Logs\\Custom Challenges\\{self.solver.start.name} - {self.solver.end.name}.txt"):
                print("Custom Challenge: ", end="")

                print(self.solver.start.name + " -> " + self.solver.end.name +"\n")

                while (not self.solver.lines):
                    self.findSolutions(depth, True)
                    depth += 1

"""----------------------------------------------- MAIN ---------------------------------------------------"""

if __name__ == '__main__':

    ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)

    if (len(sys.argv) == 1):
        print("\nDo you want to solve the daily challenge, or make your own custom challenge to solve? (D/C)")
        daily = input()
    else:
        daily = sys.argv[1]

    
    M2M = MovieToMovie(daily)
    M2M.search()

