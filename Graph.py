import matplotlib.pyplot as plot
import matplotlib.lines as lines
import matplotlib.patches as mpatch
from matplotlib.widgets import Button, LassoSelector, Lasso, CheckButtons
from matplotlib.pyplot import arrow
from matplotlib.collections import PatchCollection
from matplotlib.artist import Artist
import matplotlib.path
import math
import matplotlib
#Boteh

verbose = 2

def printf(text, text_verbosity):
    if text_verbosity <= verbose:
        print(text)

class Graph(object):
    def create_graph(self, zerox=1, zeroy=1, sizex=3, sizey=2, vertex=[], edges=[], mode_setting=1, vertex_default_radius=0.1, vertex_default_alpha=0.5):
        printf("Function Graph.create_graph("+str(zerox)+", "+str(zeroy)+", "+str(sizex)+", "+str(sizey)+", "+str(vertex)+", "+str(edges)+", "+str(mode_setting)+", "+str(vertex_default_radius)+")",2)
        self.objects = []
        self.vertex = []
        self.drawn_vertex = []
        self.edges = []
        self.drawn_edges = []
        self.selected = []
        self.buttons=[]
        self.mode = mode_setting
        self.center = (zerox,zeroy)
        self.size = (sizex,sizey)
        self.vertex_radius = vertex_default_radius
        self.vertex_radius_lock = False
        self.vertex_default_alpha = .5
        self.figure = plot.figure()
        self.figure.canvas.mpl_connect('button_press_event', self.on_click)
        self.frame = None
        self.new_to_draw = []
        #mode0:  nothing                        //any mode on
        #mode1:  add vertex/                   //default
        #mode2:  create lines/arrows
        #mode3:  select vertex
        #mode4:  move vertex
        #mode5:  delete objects

    def vertex_auto_position(self,radius=0.5):
        printf("Function Graph.vertex_auto_position("+str(radius)+")",2)
        if len(self.vertex) < 1: return -1
        perimeter = 2*math.pi*radius
        #En un radiox hay dos cuartos
        #Se deben poner la mitad de los vertices entre x
        vertex_num = len(self.vertex)
        angle = perimeter/vertex_num
        if(not self.vertex_radius_lock):
            self.vertex_radius = ((self.size[0]*self.size[1]/vertex_num)**(1/2))/2
        for vertex_counter in range(vertex_num):
            x = radius*cos(angle) + self.center[0];
            y = radius*sin(angle) + self.center[1];
            self.vertex[vertex_counter].set_vertex_pos(x,y)
            self.vertex[vertex_counter].set_circle(self.vertex_size)

    def setup_graph(self, border_t=0.98, border_r=0.98, border_b=0.12, border_l=0.07, vert_alpha=0.6, start_button_posx=0.1, start_button_posy=0.015, button_sizex=0.1, button_sizey=0.05):
        printf("Function Graph.setup_graph("+str(border_t)+", "+str(border_r)+", "+str(border_b)+", "+str(border_l)+", "+str(vert_alpha)+")",2)
        plot.subplots_adjust(left=border_l, bottom=border_b, right=border_r, top=border_t)
        zerox,zeroy = self.center
        sizex,sizey = self.size
        plot.axis([zerox-(sizex),zerox+(sizex),zeroy-(sizey),zeroy+(sizey)])
        self.add_button('Clear', self.on_click)
        self.add_button('Add vert', self.on_click)
        self.add_button('Organize', self.on_click)
        self.add_button('Lasso', self.on_click)
        
    def add_button(self, name, function, start_button_posx=0.1, start_button_posy=0.015, button_sizex=0.1, button_sizey=0.05):
        new_button_pos = plot.axes([start_button_posx+(button_sizex*(len(self.buttons)*1.5)), start_button_posy, button_sizex, button_sizey])
        new_button = Button(new_button_pos, name)
        new_button.on_clicked(function)
        self.buttons.append(new_button)
        
    def show_graph(self):
        printf("Function Graph.show_graph()",2)
        to_draw = PatchCollection(self.new_to_draw, alpha=self.vertex_default_alpha)
        self.frame = self.figure.add_subplot(111)
        #frame = ax
        self.frame.add_collection(to_draw)
        #self.frame.append(new_to_draw)
        print(self.new_to_draw)
        self.new_to_draw = []
        plot.show()
        matplotlib.axes.Axes.draw_idle()

    def on_click(self, event):
        coordx, coordy = event.xdata, event.ydata
        printf("Function Graph.on_click("+str(coordx)+", "+str(coordy)+", "+str(event)+")",2)
        frame_identifier = str(event.inaxes)[str(event.inaxes).find('('):]
        print(self.mode, frame_identifier, plot.get_current_fig_manager().toolbar.mode)
        if(frame_identifier == "(0.07,0.12;0.91x0.86)"):     
            if(plot.get_current_fig_manager().toolbar.mode == ''):
                if(self.mode == 1):
                    self.add_vertex(coordx,coordy)
                elif(self.mode == 2 and len(self.vertex)>=2):
                    self.connect_vertex(self.vertex[len(self.vertex)-2],self.vertex[len(self.vertex)-1])
                elif(self.mode ==3 and len(self.objects) >= 1):
                    Lasso(event.inaxes, (event.xdata, event.ydata), self.select_lasso)
            else: self.selected = []
            self.show_graph()
        elif(frame_identifier == "(0.1,0.015;0.1x0.05)"):
            self.clear()
        elif(frame_identifier == "(0.25,0.015;0.1x0.05)"):
            self.set_mode(1)
        elif(frame_identifier == "(0.4,0.015;0.1x0.05)"):
            self.vertex_auto_position()
        elif(frame_identifier == "(0.55,0.015;0.1x0.05)"):
            self.set_mode(3)
        else: self.selected = []
            
    def select_lasso(self, lasso_return):
        printf("Function Graph.select_lasso("+str(lasso_return)+")",2)
        self.set_mode(3)
        lasso_obj = matplotlib.path.Path(self.vertex)
        bool_list = lasso_obj.contains_points(lasso_return)
        for obj_bool in range(len(bool_list)):
            if bool_list[obj_bool]:
                self.selected.append(self.objects[obj_bool])

    def add_vertex(self,posx=1,posy=1):
        printf("Function Graph.add_vertex("+str(posx)+", "+str(posy)+")",2)
        new_vertex=self.Vertex()
        new_vertex.create_vertex(len(self.objects),posx,posy)
        self.vertex.append(new_vertex)
        self.objects.append(new_vertex)
        if(not self.vertex_radius_lock):
                self.vertex_radius = ((self.size[0]*self.size[1]/len(self.vertex))**(1/2))/2
        self.new_to_draw.append(new_vertex.get_circle())
        return new_vertex

    def add_edge(self,segments=2):
        printf("Function Graph.add_edge("+str(segments)+")",2)
        new_edge = self.Edge()
        new_edge.create_edge(len(self.objects),segments)
        self.edges.append(new_edge)
        self.objects.append(new_edge)
        return new_edge

    def connect_vertex(self,vert1,vert2,weight=1,directed=False,edge=False):
        printf("Function Graph.connect_vertex("+str(vert1)+", "+str(vert2)+", "+str(weight)+", "+str(directed)+", "+str(edge)+")",2)
        if(not edge): edge = self.add_edge()
        edge.connect_edge(vert1,vert2,weight,directed)
        edge.set_lines()
        self.new_to_draw.extend(edge.get_lines())
        return edge

    def remove_vertex(self,vert):
        printf("Function Graph.remove_vertex("+str(vert)+")",2)
        #try:
        print("Try to remove " + str(vert.get_circle()))
        vert.get_circle().remove()
        #except: print("Not drawn")
        vert.remove_self()
        self.objects.remove(vert)
        self.vertex.remove(vert)
        del vert
        self.selected = []

    def set_mode(self,new_mode):
        printf("Function Graph.set_mode("+str(new_mode)+")",2)
        self.mode = new_mode

    def get_adjacency_table(self):
        table = ([[0]*len(self.vertex)]*len(self.vertex))
        for edge in self.edges:
            vert_from = edge.get_vertex_from()
            vert_to = edge.get_vertex_to()
            table[vert_from.get_vertex_num()][vert_to.get_vertex_num()] += 1
        del vert_from, vert_to
        return table

    def print_adjacency_table(self):
        for vert in self.get_adjacency_table():
            print(vert)
            
    def clear(self):
        printf("Function Graph.clear()",2)
        for vert in self.vertex:
            self.remove_vertex(vert)
        for edge in self.edges:
            self.figure.axes.remove(edge)
        self.show_graph()
        #self.figure.axes.remove(vert)

    class Vertex(object):
        def create_vertex(self,num,posx=1,posy=1,vertex_radius=0.1):
            printf("Function Graph.Vertex.create_vertex("+str(num)+", "+str(posx)+", "+str(posy)+", "+str(vertex_radius)+")",2)
            self.number_vert = num
            self.position_x = posx
            self.position_y = posy
            self.circle = []
            self.set_circle(vertex_radius)
            self.adjacent_edges = []

        def set_vertex_pos(self,posx,posy):
            printf("Function Graph.Vertex.set_vertex_pos("+str(posx)+", "+str(posy)+")",2)
            self.position_x = posx
            self.position_y = posy

        def get_vertex_position(self):
            printf("Function Graph.Vertex.get_vertex_position()",3)
            return(self.position_x, self.position_y)

        def get_circle(self):
            printf("Function Graph.Vertex.get_circle()",3)
            return self.circle
        
        def set_circle(self, radius, main_color="#ff0000", round_color='#ffffff', circle_alpha=0.5):
            printf("Function Graph.Vertex.set_circle("+str(radius)+")",2)
            print(self.position_x,self.position_y)
            self.circle = mpatch.Circle((self.position_x,self.position_y),radius,alpha=circle_alpha,color=main_color,edgecolor=round_color,visible=True,fill=False)
            
        def add_adjacent(self,new_adj_edge):
            self.adjacent_edges.append(new_adj_edge)
                
        def get_vertex_num(self):
            return self.number_vert
        
        def remove_adj_edge(self, edge):
            self.adjacent_edges.remove(edge)
            
        def remove_self(self):
            for edge in self.adjacent_edges:
                edge.remove_self()
                    
    class Edge(object):
        def create_edge(self,num,edge_segments=2):
            printf("Function Graph.Edge.create_edge("+str(num)+", "+str(edge_segments)+")",2)
            self.segments_num = edge_segments
            self.segments_pos = []
            self.lines = []
            self.number_edge=num
                                                       
        def connect_edge(self,vert1,vert2,edge_weight=1,directed_bool=False):
            printf("Function Graph.Edge.connect_edge("+str(vert1)+", "+str(vert2)+", "+str(edge_weight)+", "+str(directed_bool)+")",2)
            self.connected_from = vert1
            self.connected_to = vert2
            self.weight = edge_weight
            self.directed = directed_bool
            vert1.add_adjacent(self)
            if(not self.directed):
                vert2.add_adjacent(self)
            
        def set_lines(self,edge_alpha=0.5,edge_color="0000FF"):
            printf("Function Graph.Edge.set_lines()",2)
            from_pos = self.connected_from.get_vertex_position()
            to_pos = self.connected_to.get_vertex_position()
            if self.directed==True: style="<-"
            else: style="<->"
            new_line = mpatch.FancyArrowPatch(path=[(from_pos[0],from_pos[1]),(to_pos[0],to_pos[1])],arrow_style=style,alpha=edge_alpha,color=edge_color)
            self.lines.append(new_line)
            #ax.annotate("", xy=(0.5, 0.5), xytext=(0, 0),arrowprops=dict(arrowstyle="->"))
            
        def get_lines(self):
            printf("Function Graph.Edge.get_lines()",3)
            return self.lines
            
        def get_edge(self):
            printf("Function Graph.Edge.get_edge()",3)
            return(self.connected_from,self.connected_to,self.weight,self.directed)
            
        def get_edge_num():
            return self.numbre_edge
        
        def get_vertex_from():
            return self.connected_from
        
        def get_vertex_to():
            return self.connected_to
        
        def remove_self(self):
            self.connected_to.remove_adj_edge(self)
            self.connected_from.remove_adj_edge(self)

    #def apply_algorithm(

#ax = plot.axes()
#ax.arrow(0, 0, 0.5, 0.5, head_width=0.05, head_length=0.1, fc='k', ec='k')
ex = Graph()
ex.create_graph(mode_setting=0)
ex.setup_graph()
ex.show_graph()
