import matplotlib.pyplot as plt

class Transient:
    def __init__(self,name):
        self.graphs = {}
        self.shown = False
        self.name = name

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
        ax.set_title(self.name)
        
        for plot_name in self.graphs:
            plot = self.graphs[plot_name]

            ax.plot(plot,label=plot_name)

        ax.legend()
            
            
        plt.show()