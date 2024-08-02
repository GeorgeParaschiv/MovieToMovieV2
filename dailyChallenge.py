import requests, datetime, re

class DailyChallenge:

    def __init__(self):

        self.session = requests.Session()
        self.mainURL = "https://movietomovie.com/"

        self.mainRegex = r"_app/immutable/entry/app.*?js"
        self.appRegex = r"_app/immutable/chunks/dailyChallenge.*?js"
        self.challengeRegex = r'{start:{id:(.*?),title:\"(.*?)\",poster:.*?},end:{id:(.*?),title:\"(.*?)\",poster:.*?},shortest_path:{path:\[.*?\],score:(\d).*?}}'

        self.dailyChallengeData = self.getDailyChallengeData()

    # Returns the URL where the list of daily challenges is contained
    def getDailyChallengeData(self):

        mainResponse = self.session.get(self.mainURL)
        mainMatch = re.search(self.mainRegex, mainResponse.text)
        appURL = self.mainURL + mainMatch.group(0)

        appResponse = self.session.get(appURL)
        appMatch = re.search(self.appRegex, appResponse.text)
        challengeURL = self.mainURL + appMatch.group(0)

        return self.session.get(challengeURL)

    # Returns the start and end movies of the Daily Challenge from movietomovie.com
    def getDailyChallenge(self, challengeIndex = None):

        # Extract all Daily Challenges from Javascript File using Regular Expressions
        challengeMatches = re.findall(self.challengeRegex, self.dailyChallengeData.text)

        # Number of Challenges Depends on Number of Matches
        NUMBER_OF_CHALLENGES = len(challengeMatches)

        # Calculating the challenge index based on days since the source date
        if (challengeIndex == None):
            time = datetime.datetime.strptime("01 Nov 2022 10:00:00", "%d %b %Y %H:%M:%S")
            daysSince = (datetime.datetime.now() - time).days
            challengeIndex = daysSince % NUMBER_OF_CHALLENGES

        # Parsing the Daily Challenge into a list
        challenge = challengeMatches[challengeIndex]
        start = {"ID" : int(challenge[0]),  "NAME" : challenge[1]}
        end = {"ID" : int(challenge[2]),  "NAME" : challenge[3]}
        shortest = challenge[4]

        return [challengeIndex, start, end, shortest]
       