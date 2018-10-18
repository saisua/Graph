import matplotlib.pyplot as plot
import matplotlib.lines as lines

class Graph(object):

    def __init__(self, data=[]):
        self.table=data
        
    def add_vertex(self,num_vert=1):
        for times in range(num_vert):
            self.table.append([])
        for vert in list(range(len(self.table))):
            len_dif = len(self.table)-len(self.table[vert])
            if(not len_dif==0):
            self.table[vert].append(list([[0,0]]*len_dif)[0])
            
    def connect_vertex(self,vert1,vert2,peso=1,directed=False):
        self.table[vert1][vert2][0] +=1
        self.table[vert1][vert2][1] = peso
        if(not directed):
            self.table[vert2][vert1][0] +=1
            self.table[vert2][vert1][1] = peso

    def show_graph(self,zerox,zeroy):
        ax = plt.axes()
        ax.arrow(0, 0, 0.5, 0.5, head_width=0.05, head_length=0.1, fc='k', ec='k')

        plt.show()
    #def apply_algorithm(

print("log")
ex = Graph()
ex.show_graph()