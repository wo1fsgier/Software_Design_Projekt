class Knoten:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        
        # Kräfte (initial 0)
        self.force_x = 0.0
        self.force_y = 0.0
        
        # Freiheitsgrade (initial frei)
        self.fixed_x = False
        self.fixed_y = False

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