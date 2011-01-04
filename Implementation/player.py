class Player(object) :
    """The player object represents a (possibly remote) player interacting with the system"""
    
    def __init__(self, name) :
        self.name = name

    def get_name(self) : 
        return self.name
