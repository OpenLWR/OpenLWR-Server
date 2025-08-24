class Model:
    def __init__(self):
        # do what you need to do here to get your model ready
        self.replicated_data = {}

    # check __init__.py for setting how often these run
    def step(self, delta):
        print("Hello, World!")

    def step_slow(self, delta):
        print("Hello, World! but slower")