import matplotlib.pyplot as plot
import matplotlib.lines as lines
"""
import matplotlib
matplotlib.use('GTK3Cairo')
matplotlib.rcParams['toolbar'] = 'toolmanager'
from matplotlib.backend_tools import ToolBase, ToolToggleBase
from matplotlib.backend_tools import ToolBase
from matplotlib.backend_managers import ToolManager as toolmanager
"""
#from matplotlib.backend_bases import NavigationToolbar2 as NTB2
from matplotlib.patches import Circle
from matplotlib.pyplot import arrow
from matplotlib.collections import PatchCollection
import math

verbose = 2

def printf(text, text_verbosity):
    if text_verbosity <= verbose:
        print(text)

class Graph(object):
    def create_graph(self, zerox=1, zeroy=1, sizex=3, sizey=2, vertex=[], edges=[], mode_setting=1, vertex_default_radius=0.1, vertex_default_alpha=0.5):
        printf("Function Graph.create_graph("+str(zerox)+", "+str(zeroy)+", "+str(sizex)+", "+str(sizey)+", "+str(vertex)+", "+str(edges)+", "+str(mode_setting)+", "+str(vertex_default_radius)+")",2)
        self.vertex = []
        self.drawn_vertex = []
        self.edges = []
        self.drawn_edges = []
        self.mode = mode_setting
        self.center = (zerox,zeroy)
        self.size = (sizex,sizey)
        self.vertex_radius = vertex_default_radius
        self.vertex_radius_lock = False
        self.vertex_default_alpha = .5
        self.figure = plot.figure()
        self.figure.canvas.mpl_connect('button_press_event', self.on_click)
        self.new_to_draw = []
        #mode0:  nothing                        //any mode on
        #mode1:  add vertex/connect vertex     //default
        #mode2:  create lines/arrows
        #mode3:  move vertex
        #mode4:  delete objects
        
    def vertex_auto_position(self,radius=0.5):
        printf("Function Graph.vertex_auto_position("+str(radius)+")",2)
        perimeter = 2*math.pi()*radius
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
            
    def setup_graph(self, border_t=0.98, border_r=0.98, border_b=0.06, border_l=0.07, vert_alpha=0.6)  :
        printf("Function Graph.setup_graph("+str(border_t)+", "+str(border_r)+", "+str(border_b)+", "+str(border_l)+", "+str(vert_alpha)+")",2)
        plot.subplots_adjust(left=border_l, bottom=border_b, right=border_r, top=border_t)
        zerox,zeroy = self.center
        sizex,sizey = self.size
        plot.axis([zerox-(sizex),zerox+(sizex),zeroy-(sizey),zeroy+(sizey)])
        #http://dalelane.co.uk/blog/?p=778
        #cid = self.figure.canvas.mpl_connect('button_press_event', on_press)
        #NTB2(UI("Add vertex","hi"))
        #NTB2.__init__toolbar()
        #print(toolmanager().tools)
        #toolmanager().update_keymap("pan/zoom", "m")
        #toolmanager().add_tool("Add vertex", UI)
        #toolmanager().trigger_tool("Add vertex", self, "tool_trigger", data=None)
        #print(toolmanager().tools)
        #toolmanager().update_keymap("Add vertex", "v")
        #ToolBase(UI,"tool1")
        #toolbar = self.figure.navtbar
        #self.figure.canvas.manager.toolmanager.add_tool('List', ListTools)

    def show_graph(self):
        printf("Function Graph.show_graph()",2)
        to_draw = PatchCollection(self.new_to_draw, alpha=self.vertex_default_alpha)
        print(self.new_to_draw)
        self.new_to_draw = []
        frame = self.figure.add_subplot(111)
        frame.add_collection(to_draw)
        plot.show()
        
    def on_click(self, coordinates):
        coordx, coordy = coordinates.xdata, coordinates.ydata
        printf("Function Graph.on_click("+str(coordx)+", "+str(coordy)+")",2)
        print(plot.get_current_fig_manager().toolbar.mode)
        if(plot.get_current_fig_manager().toolbar.mode == ''):    
            if(self.mode == 1 or len(self.vertex)<2):
                self.add_vertex(coordx,coordy)
            elif(self.mode == 2 and len(self.vertex)>=2):
                self.connect_vertex(self.vertex[len(self.vertex)-2],self.vertex[len(self.vertex)-1])
            self.show_graph()
            
    def add_vertex(self,posx=1,posy=1):
        printf("Function Graph.add_vertex("+str(posx)+", "+str(posy)+")",2)
        new_vertex=self.Vertex()
        new_vertex.create_vertex(posx,posy)
        self.vertex.append(new_vertex)
        if(not self.vertex_radius_lock):
                self.vertex_radius = ((self.size[0]*self.size[1]/len(self.vertex))**(1/2))/2
        self.new_to_draw.append(new_vertex.get_circle())
        return new_vertex
    
    def add_edge(self,segments=2):
        printf("Function Graph.add_edge("+str(segments)+")",2)
        new_edge = self.Edge()
        new_edge.create_edge(segments)
        self.edges.append(new_edge)
        return new_edge
    
    def connect_vertex(self,vert1,vert2,weight=1,directed=False,edge=False):
        printf("Function Graph.connect_vertex("+str(vert1)+", "+str(vert2)+", "+str(weight)+", "+str(directed)+", "+str(edge)+")",2)
        if(not edge): edge = self.add_edge()
        edge.connect_edge(vert1,vert2,weight,directed)
        edge.set_lines()
        self.new_to_draw.extend(edge.get_lines())
        return edge
        
    def remove_vertex(vert_num):
        print()
        
    def set_mode(self,new_mode):
        self.mode = new_mode
            
    class Vertex(object):     
        def create_vertex(self,posx=1,posy=1,vertex_radius=0.1):
            printf("Function Graph.Vertex.create_vertex("+str(posx)+", "+str(posy)+", "+str(vertex_radius)+")",2)
            self.position_x = posx
            self.position_y = posy
            self.set_circle(vertex_radius)
            self.adjacent_edges = {}
                    
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
        
        def set_circle(self, radius):
            printf("Function Graph.Vertex.set_circle("+str(radius)+")",2)
            print(self.position_x,self.position_y)
            self.circle = Circle((self.position_x,self.position_y),radius)
            
        def add_adjacent(new_adj_edge):
            try:
                self.adjacent_edges[new_adj_edge] += 1
            except:
                self.adjacent_edges[new_adj_edge] = 1
                    
    class Edge(object):
        def create_edge(self,edge_segments=2):
            printf("Function Graph.Edge.create_edge("+str(edge_segments)+")",2)
            self.segments_num = edge_segments
            self.segments_pos = []
            self.lines = []
                                                       
        def connect_edge(self,vert1,vert2,edge_weight=1,directed_bool=False):
            printf("Function Graph.Edge.connect_edge("+str(vert1)+", "+str(vert2)+", "+str(edge_weight)+", "+str(directed_bool)+")",2)
            self.connected_from = vert1
            self.connected_to = vert2
            self.weight = edge_weight
            self.directed = directed_bool
            
        def set_lines(self):
            printf("Function Graph.Edge.set_lines()",2)
            from_pos = self.connected_from.get_vertex_position()
            to_pos = self.connected_to.get_vertex_position()
            new_line = arrow(from_pos[0],from_pos[1],to_pos[0]-from_pos[0],to_pos[1]-from_pos[1],length_includes_head=True)
            self.lines.append(new_line)
            #ax.annotate("", xy=(0.5, 0.5), xytext=(0, 0),arrowprops=dict(arrowstyle="->"))
            
        def get_lines(self):
            printf("Function Graph.Edge.get_lines()",3)
            return self.lines
            
        def get_edge(self):
            printf("Function Graph.Edge.get_edge()",3)
            return(self.connected_from,self.connected_to,self.weight,self.directed)

    #def apply_algorithm(
    
def on_press(event):
    print('you pressed', event.button, event.xdata, event.ydata)   

class UI(object):
    default_keymap = "v"
    description = "Add vertices on click (v)"
    image = "draw_vertex.png"
    def __init__(self, toolmanager, name):
        print("##########")
        self._name = name
        self._toolmanager = toolmanager
        self._figure = None
        
    @property
    def figure(self):
        return self._figure

    @figure.setter
    def figure(self, figure):
        self.set_figure(figure)

    @property
    def canvas(self):
        if not self._figure:
            return None
        return self._figure.canvas

    @property
    def toolmanager(self):
        return self._toolmanager

    def set_figure(self, figure):
        self._figure = figure
            
    def trigger(self, sender, event, data=None):
        """
        Called when this tool gets used
        This method is called by
        `matplotlib.backend_managers.ToolManager.trigger_tool`
        Parameters
        ----------
        event : `Event`
            The Canvas event that caused this tool to be called
        sender : object
            Object that requested the tool to be triggered
        data : object
            Extra data
        """
        print("trigger("+str(sender)+", "+str(event)+", "+str(data)+")")

        pass

    @property
    def name(self):
        return self._name

    def destroy(self):
        """
        Destroy the tool
        This method is called when the tool is removed by
        `matplotlib.backend_managers.ToolManager.remove_tool`
        """
        pass
            
#ax = plot.axes()
#ax.arrow(0, 0, 0.5, 0.5, head_width=0.05, head_length=0.1, fc='k', ec='k')
ex = Graph()
ex.create_graph(mode_setting=2)
ex.setup_graph()
ex.show_graph()
