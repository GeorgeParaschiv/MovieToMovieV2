import datetime, json, os, requests, re, sys, textwrap, time
from dailyChallenge import *
import popularity as p


# API Key 
import config

ACTOR = "Actor"
MOVIE = "Movie"

class Node:

    def __init__(self, info):
        self.id = info[0]
        self.name = info[1]
        self.popularity = info[2]
        self.explored = False

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id
    
    # def __ne__(self, other):
    #     return self.id == other.id
    
    def __str__(self):
        return f"{self.id} | {self.name} | {self.popularity} | {self.explored}"


class MovieSolver:

    def __init__(self, API_KEY):
        self.key = API_KEY
        self.headers = {"accept": "application/json", "Authorization": ("Bearer " + self.key)}
        self.session = requests.Session()

        # First authenticate the session before pulling data
        self.authenticate()

        challenge = DailyChallenge().dailyChallenge
        self.daily = [Node((challenge[0]['ID'], challenge[0]['NAME'], self.getMoviePopularity(challenge[0]['ID']))),
                      Node((challenge[1]['ID'], challenge[1]['NAME'], self.getMoviePopularity(challenge[1]['ID'])))]
        
        self.movies = {}
        self.actors = {}

        self.DEPTH = 2
        self.lines = []

    def __del__(self):
        self.session.close()

    def authenticate(self):
        """Method to authenticate the user. 
        Exits the program if authentication fails."""

        authURL = "https://api.themoviedb.org/3/authentication"
        auth = json.loads(self.session.get(authURL, headers=self.headers).text)
        
        if (auth["success"] != True):
            print("Failed to Authenticate!")
            sys.exit()


    def getCast(self, movie_id):
        """Method to get cast of a movie given its ID. Returns list of (Actor ID, Actor Name, Actor Popularity)."""

        movieURL = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?language=en-US"
        
        credits = json.loads(self.session.get(movieURL, headers=self.headers).text)
        cast = [(actor["id"], actor["original_name"], actor["popularity"]) for actor in credits["cast"]]

        return cast

    # Returns a list of the movies that the actor has acted in (id, name, popularity)
    def getMovies(self, actor_id):
        """Method to get movie credits of an actor given its ID. Returns list of (Movie ID, Movie Name, Movie Popularity)."""

        actorURL = f"https://api.themoviedb.org/3/person/{actor_id}/movie_credits?language=en-US"


        movieCredits = json.loads(self.session.get(actorURL, headers=self.headers).text)
        movies = [(movie["id"], movie["original_title"], movie["popularity"]) for movie in movieCredits["cast"]]

        return movies

    # Returns popularity of a movie given its id
    def getMoviePopularity(self, movie_id):
        """Method to get popularity of a movie given its ID. Returns Movie Popularity."""

        popURL = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"

        movieDetails = json.loads(self.session.get(popURL, headers=self.headers).text)
        popularity = movieDetails["popularity"]

        return popularity
    
    def clear(self):
        self.movies = {}
        self.actors = {}
        self.lines = []

        self.start.explored = False
        self.end.explored = False
    
    def getStartEnd(self, daily):

        if (daily):
            self.start = self.daily[0]
            self.end = self.daily[1]

    def getSearchList(self, TYPE):
        search = []

        if (TYPE == MOVIE):
            for node in self.movies.keys():
                if node.explored == False:
                    node.explored = True
                    search.append(node)
        else:
            for node in self.actors.keys():
                if node.explored == False:
                    node.explored = True
                    search.append(node)
        
        return search
    
    def addMovies(self):
        search = self.getSearchList(MOVIE)
        for movie in search:
            for actor in self.getCast(movie.id):
                newNode = Node(actor)
                self.movies[movie] += [newNode]
                if newNode not in self.actors:
                    self.actors[newNode] = []

    def addActors(self):
        search = self.getSearchList(ACTOR)
        for actor in search:
            for movie in self.getMovies(actor.id):
                newNode = Node(movie)
                self.actors[actor] += [newNode]
                if newNode not in self.movies:
                    self.movies[newNode] = []
    
    def constructGraph(self):
        self.clear()

        # Add Start and End Movies
        self.movies[self.start] = []
        self.movies[self.end] = []

        # Add all Actors from Start and End Movies
        self.addMovies()

        # Add until depth reached
        for repeat in range(0, self.DEPTH-1):
            self.addActors()
            self.addMovies()

    def findLines(self, current : Node, TYPE = MOVIE, line="", depth=1):
        
        line += (current.name + " -> ")

        if (TYPE == ACTOR):
            if (depth == 1):
                for actor in self.movies[self.end]:
                    if (actor == current):
                        line += self.end.name
                        self.lines.append(line)
            else:          
                for movie in self.actors[current]:
                    if (movie != self.start and movie != self.end):
                        self.findLines(movie, MOVIE, line, depth-1)                        
        else:                      
            for actor in self.movies[current]:
                self.findLines(actor, ACTOR, line, depth)
    
    def printLines(self):

        print(f"Solutions of length {self.DEPTH}:")
        
        if self.lines:
            for index, line in enumerate(self.lines):
                print(f"{index+1}. " + line)
        else:
            print("No solutions found.")

    def findSolutions(self, depth):
        self.DEPTH = depth

        startTime  = time.time()

        self.constructGraph()
        self.findLines(self.start, depth = self.DEPTH)
        solver.printLines()

        endTime = time.time()

        print(f"\nTime Elapsed: {endTime-startTime}\n")

    def challenge(self, daily):

        solver.getStartEnd(daily)

        if (daily):
            print("Daily Challenge: ", end="")
        else:
            print("Custom Challenge: ", end="")

        print(solver.start.name + " -> " + solver.end.name +"\n")

"""----------------------------------------------- MAIN ---------------------------------------------------"""

if __name__ == '__main__':

    solver = MovieSolver(config.api_key)
    solver.challenge(True)
    solver.findSolutions(1)
    solver.findSolutions(2)
    