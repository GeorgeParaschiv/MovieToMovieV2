from solver import MovieSolver, Node
from dailyChallenge import DailyChallenge
import config, textwrap
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
            self.custom()
            return False
        else:
            raise

    def printLines(self):

        print(f"\nSolutions of length {self.DEPTH}:")
        
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

        print(f"\nTime Elapsed: {int(endTime/3600)}h {int((endTime%3600)/60)}m {int(endTime%60)}s {int((endTime-int(endTime))*1000)}ms")

    def search(self):

        daily = self.getStartEnd()

        self.solver.start.name = re.sub(r"(?u)[^-\w.,\s]", "", self.solver.start.name)
        self.solver.end.name = re.sub(r"(?u)[^-\w.,\s]", "", self.solver.end.name) 

        if (daily):
            filePath = f"{os.getcwd()}\\Logs\\Daily Challenges\\#{self.challenge[0]} {self.solver.start.name} - {self.solver.end.name}.txt"
        else:
            filePath = f"{os.getcwd()}\\Logs\\Custom Challenges\\{self.solver.start.name} - {self.solver.end.name}.txt"

        with Logging(filePath):
                if (daily):
                    print(f"Daily Challenge #{self.challenge[0]}: ", end="")
                else:
                    print("Custom Challenge: ", end="")
                print(self.solver.start.name + " -> " + self.solver.end.name)

                depth = 1
                while (not self.solver.lines):
                    self.findSolutions(depth, True)
                    depth += 1                

    def displayResults(self, search, startIndex):  

        if(startIndex >= len(search)):
            startIndex = 0

        endIndex = (startIndex + 5) if (startIndex + 5) <= len(search) else len(search)

        for index in range(startIndex, endIndex):
            if (index >= len(search)):
                break
            
            print("%s%i. Name: %s (%s)" %("\n", index + 1, search[index]['title'], search[index]['release_date'][0:4]))
            wrapper=textwrap.TextWrapper(initial_indent = ('   ' if index < 9 else '    '), 
                                        subsequent_indent = (('\t' + '     ') if index < 9 else ('\t' + '      ')), 
                                        width = 120)
            print(wrapper.fill("Overview: " + ("None" if search[index]['overview'] == "" else search[index]['overview'])))

        return startIndex, endIndex     

    def custom(self):
        
        cycling = False
        while (not self.solver.end):

            if (not cycling):
                print("\nSearch for the %s movie: " %("start" if not self.solver.start else "end"))
                search = self.solver.searchMovies(input())
                endIndex = 0
            
            if (not search):
                print("\nThe search yielded no options.\n")
            else:
                startIndex, endIndex = self.displayResults(search, endIndex)

                if (len(search) == 1):
                    print("\nThere is only one option. Press ENTER to select it or 0 to search again:")
                    selection = input()
                    if (selection != "0"):
                        movie = Node([search[0]['id'], search[0]['original_title'], search[0]['popularity']])
                        if (not self.solver.start):
                            self.solver.start = movie
                        else:
                            self.solver.end = movie
                else:
                    print("\nPick a movie (%i-%i), press ENTER to see more results, or 0 to search again:" %(startIndex+1, endIndex))
                    selection = input()
                    if (not selection.isnumeric()):
                        cycling = True
                    else:
                        selection = int(selection)
                        if (selection == "0"):
                            cycling = False
                        elif(int(selection) >= startIndex+1 and int(selection) <= endIndex):
                            cycling = False
                            movie = Node([search[selection-1]['id'], search[selection-1]['original_title'], search[selection-1]['popularity']])
                            if (not self.solver.start):
                                self.solver.start = movie
                            else:
                                self.solver.end = movie
                        else:
                            cycling=True

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