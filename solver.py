import datetime, json, os, requests, re, sys, textwrap, time
from dailyChallenge import *
import ctypes, threading, queue

# API Key 
import config

ACTOR = "Actor"
MOVIE = "Movie"
THREADS = 20

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
        
        self.start = None
        self.end = None

        self.movies = {}
        self.actors = {}
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

        try:
            return [(actor["id"], actor["original_name"], actor["popularity"]) for actor in credits["cast"]]
        except:
            return []

    # Returns a list of the movies that the actor has acted in (id, name, popularity)
    def getMovies(self, actor_id):
        """Method to get movie credits of an actor given its ID. Returns list of (Movie ID, Movie Name, Movie Popularity)."""

        actorURL = f"https://api.themoviedb.org/3/person/{actor_id}/movie_credits?language=en-US"


        movieCredits = json.loads(self.session.get(actorURL, headers=self.headers).text)
        
        movies = []

        if "cast" not in movieCredits.keys():
            return []
        
        for movie in movieCredits["cast"]:
            try:
                movies.append((movie["id"], movie["original_title"], movie["popularity"]))
            except:
                movies.append((movie["id"], movie["original_title"], 0))

        return movies

    # Returns popularity of a movie given its id
    def getMoviePopularity(self, movie_id):
        """Method to get popularity of a movie given its ID. Returns Movie Popularity."""

        popURL = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"

        movieDetails = json.loads(self.session.get(popURL, headers=self.headers).text)
        popularity = movieDetails["popularity"]

        return popularity
    
    def searchMovies(self, query):
        searchURL = f"https://api.themoviedb.org/3/search/movie?query={query}&include_adult=false&language=en-US&page=1"

        search = json.loads(self.session.get(searchURL, headers=self.headers).text)

        try:
            return search['results']
        except:
            return []
    
    def clear(self):
        self.movies = {}
        self.actors = {}
        self.lines = []

        self.start.explored = False
        self.end.explored = False

    def getSearchList(self, TYPE):
        self.queue = queue.Queue()

        if (TYPE == MOVIE):
            for node in self.movies.keys():
                if node.explored == False:
                    node.explored = True
                    self.queue.put(node, block=True)
        else:
            for node in self.actors.keys():
                if node.explored == False:
                    node.explored = True
                    self.queue.put(node, block=True)
    
    def add(self, TYPE):
        if TYPE == MOVIE:
            self.getSearchList(MOVIE)
        else:
            self.getSearchList(ACTOR)
        
        max = self.queue.qsize() if self.queue.qsize() < THREADS else THREADS
            
        for i in range(0, max):
            threading.Thread(target=(self.addMovies if TYPE == MOVIE else self.addActors), daemon=True).start()

        self.queue.join()
        self.queue
    
    def addMovies(self):
        while True:
            movie = self.queue.get()
            for actor in self.getCast(movie.id):
                newNode = Node(actor)
                self.movies[movie] += [newNode]
                if newNode not in self.actors:
                    self.actors[newNode] = []
            self.queue.task_done()

    def addActors(self):
        while True:
            actor = self.queue.get()
            for movie in self.getMovies(actor.id):
                newNode = Node(movie)
                self.actors[actor] += [newNode]
                if newNode not in self.movies:
                    self.movies[newNode] = []
            self.queue.task_done()
    
    def constructGraph(self, depth, cont=False):
        
        if not cont:
            self.clear()

            # Add Start and End Movies
            self.movies[self.start] = []
            self.movies[self.end] = []

            # Add all Actors from Start and End Movies
            self.add(MOVIE)

            # Add until depth reached
            if (depth > 1):
                for i in range(0, int(depth/2)):
                    self.add(ACTOR)
                    self.add(MOVIE)
                
                if (depth % 2 == 1):
                    self.add(ACTOR)

        else:
            if depth == 1:
                self.movies[self.start] = []
                self.movies[self.end] = []
                self.add(MOVIE)
            elif depth == 2:
                self.add(ACTOR)
                self.add(MOVIE)
            elif depth == 3:
                self.add(ACTOR)
            elif depth == 4:
                self.add(MOVIE)
            elif depth == 5:
                self.add(ACTOR)

    def findLines(self, current : Node, depth, type=MOVIE, line="", visited = set(), popularity=0):
        
        line += (current.name + " -> ")
        popularity += current.popularity

        visited = visited.copy()
        visited.add(current)

        if (type == ACTOR):
            if (depth == 1):
                for actor in self.movies[self.end]:
                    if (actor == current):
                        line += self.end.name
                        self.lines.append((line, popularity + self.end.popularity))
            else:          
                for movie in self.actors[current]:
                    if (movie not in visited):
                        self.findLines(movie, depth-1, MOVIE, line, visited, popularity)                        
        else:                      
            for actor in self.movies[current]:
                if actor not in visited:
                    self.findLines(actor, depth, ACTOR, line, visited, popularity)