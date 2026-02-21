class Feder:
    def __init__(self, knoten1, knoten2, steifigkeit=1.0):
        self.knoten1 = knoten1
        self.knoten2 = knoten2
        self.steifigkeit = steifigkeit
        
        # Registriere diese Feder automatisch in beiden Knoten
        knoten1.add_feder(self)
        knoten2.add_feder(self)

    def remove_from_nodes(self):
        """Entfernt diese Feder aus beiden Knoten."""
        self.knoten1.remove_feder(self)
        self.knoten2.remove_feder(self) 