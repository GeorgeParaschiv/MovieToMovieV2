import datetime, json, os, requests, re, sys, textwrap, time
from dailyChallenge import *
import popularity as p

# API Key 
import config

class MovieSolver:

    def __init__(self, API_KEY):
        self.key = API_KEY
        self.headers = {"accept": "application/json", "Authorization": ("Bearer " + self.key)}
        self.session = requests.Session()

        # First authenticate the session before pulling data
        self.authenticate()

        challenge = DailyChallenge().dailyChallenge
        self.daily = [(challenge[0]['ID'], challenge[0]['NAME'], self.getMoviePopularity(challenge[0]['ID'])),
                      (challenge[1]['ID'], challenge[1]['NAME'], self.getMoviePopularity(challenge[1]['ID']))]

    def __del__(self):
        self.session.close()

    def authenticate(self):
        authenticateURL = "https://api.themoviedb.org/3/authentication"
        response = self.session.get(authenticateURL, headers=self.headers)
        
        if (json.loads(response.text)["success"] != True):
            print("Failed to Authenticate!")
            sys.exit()

    # Returns a list of the the cast members that act in a movie (id, name, popularity)
    def getCast(self, movie_id):
        movieURL = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?language=en-US"
        
        credits = json.loads(self.session.get(movieURL, headers=self.headers).text)
        cast = [(x["id"], x["original_name"], x["popularity"]) for x in credits["cast"]]

        return cast

    # Returns a list of the movies that the actor has acted in (id, name, popularity)
    def getMovies(self, actor_id):
        actorURL = f"https://api.themoviedb.org/3/person/{actor_id}/movie_credits?language=en-US"

        movie_credits = json.loads(self.session.get(actorURL, headers=self.headers).text)
        movies = [(x["id"], x["original_title"], x["popularity"]) for x in movie_credits["cast"]]

        return movies

    # Returns popularity of a movie given its id
    def getMoviePopularity(self, movie_id):
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"

        movie_details = json.loads(self.session.get(url, headers=self.headers).text)
        popularity = movie_details["popularity"]

        return popularity

"""----------------------------------------------- MAIN ---------------------------------------------------"""

if __name__ == '__main__':
 
    solver = MovieSolver(config.api_key)
    print(solver.daily)