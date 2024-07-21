import matplotlib.pyplot as plt

class Transient:
    def __init__(self):
        self.graphs = {}
        self.shown = False

    def add_graph(self,name):
        x = self.graphs.copy()
        x[name] = []
        y = x
        self.graphs = y

    def add(self,name,value):
        self.graphs[name].append(value)

    def generate_plot(self):
        if self.shown: return
        self.shown = True

        fig, ax = plt.subplots()
        
        for plot in self.graphs:
            plot = self.graphs[plot]

            ax.plot(plot)
            
        plt.show()