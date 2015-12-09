class Actor:
    def __init__(self, id):
        self.name = None
        self.id   = id

    def setName(self, name):
        self.name = name

class ActorGroup:
    def __init__(self, id, actors = []):
        self.name   = None,
        self.id     = id
        self.actors = set(actors)
 
    def setName(self, name):
        self.name = name

    def addActors(self, actors):
        self.actors |= set(actors)
