import datetime, json, os, requests, re, sys, textwrap, time
from dailyChallenge import *
import ctypes

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
    
    def constructGraph(self, depth, cont=False):
        
        if not cont:
            self.clear()

            # Add Start and End Movies
            self.movies[self.start] = []
            self.movies[self.end] = []

            # Add all Actors from Start and End Movies
            self.addMovies()

            # Add until depth reached
            if (depth > 1):
                for i in range(0, int(depth/2)):
                    self.addActors()
                    self.addMovies()
                
                if (depth % 2 == 1):
                    self.addActors()

        else:
            if depth == 1:
                self.movies[self.start] = []
                self.movies[self.end] = []
                self.addMovies()
            elif depth == 2:
                self.addActors()
                self.addMovies()
            elif depth == 3:
                self.addActors()

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