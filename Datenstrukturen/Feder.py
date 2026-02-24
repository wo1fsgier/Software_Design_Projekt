import numpy as np
import math

class Feder:
    def __init__(self, knoten1, knoten2, EA=1):
        self.knoten1 = knoten1
        self.knoten2 = knoten2
        self.EA = float(EA)

    def length(self):
        dx = self.knoten2.x - self.knoten1.x
        dy = self.knoten2.y - self.knoten1.y
        return math.sqrt(dx*dx + dy*dy)
    
    def direction(self):
        dx = self.knoten2.x - self.knoten1.x
        dy = self.knoten2.y - self.knoten1.y
        Length = math.sqrt(dx*dx + dy*dy)
        if Length == 0:
            return (0, 0)
        c= dx/Length
        s=dy/Length
        return c,s,Length  
    
    def k (self):
        return self.EA / self.length()
         
    def matrix(self):
        c, s, L = self.direction()
        k = self.k()
        return k * np.array([[c*c, c*s, -c*c, -c*s],
                             [c*s, s*s, -c*s, -s*s],
                             [-c*c, -c*s, c*c, c*s],
                             [-c*s, -s*s, c*s, s*s]])