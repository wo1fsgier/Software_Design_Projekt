class Knoten:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.federn = []  # Liste der Federn, die an diesem Knoten hängen
        
        # Kräfte (initial 0)
        self.force_x = 0.0
        self.force_y = 0.0
        
        # Fixierungen (initial False = verschiebbar)
        self.fixed_x = False
        self.fixed_y = False

    def add_feder(self, feder):
        """Registriert eine Feder an diesem Knoten."""
        if feder not in self.federn:
            self.federn.append(feder)

    def remove_feder(self, feder):
        """Entfernt eine Feder von diesem Knoten."""
        if feder in self.federn:
            self.federn.remove(feder)

    def set_force(self, force_x=None, force_y=None):
        
        if force_x is not None:
            self.force_x = force_x
        if force_y is not None:
            self.force_y = force_y

    def set_fixed(self, fixed_x=None, fixed_y=None):
       
        if fixed_x is not None:
            self.fixed_x = fixed_x
        if fixed_y is not None:
            self.fixed_y = fixed_y

    def get_dofs(self):
       
        return [not self.fixed_x, not self.fixed_y]