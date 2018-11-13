import matplotlib.pyplot as plot
import matplotlib.lines as lines
import matplotlib.patches as mpatch
import numpy as np
from matplotlib.widgets import Button, LassoSelector, Lasso, CheckButtons
from matplotlib.pyplot import arrow
from matplotlib.collections import PatchCollection, RegularPolyCollection
from matplotlib.artist import Artist
from matplotlib.patches import ArrowStyle
from matplotlib.colors import colorConverter
from matplotlib import animation
import matplotlib.path
import math
import matplotlib
import random
#Para hacer:
#Anadir grupos de vertex
#Ordenar en base a los grupos
#Anadir nombre vertex, wei edge
#Anadir bidirecc edge

print("\n\n")
print("All libraries imported")
print("######################")
print("    Program  start    ")
print("######################")

verbose = 2

def printf(text, text_verbosity, endf="\n"):
    if text_verbosity <= verbose:
        print(text,end=endf)

class Graph(object):
    def create_graph(self, zerox=1, zeroy=1, sizex=3, sizey=2, vertex=[], edges=[], mode_setting=1, vertex_default_radius=0.1, vertex_default_alpha=0.5, renderer='TkAgg'):
        printf("Function Graph.create_graph("+str(zerox)+", "+str(zeroy)+", "+str(sizex)+", "+str(sizey)+", "+str(vertex)+", "+str(edges)+", "+str(mode_setting)+", "+str(vertex_default_radius)+")",2)
        self.figure = plot.figure()        
        self.frame = self.figure.add_subplot(111,picker=True,autoscale_on=True)
        #ax    ^
        self.objects = []
        self.object_pos = []
        self.vertex = vertex
        self.edges = edges
        matplotlib.use(renderer)
        """
        renderer = 1>['GTK3Cairo', 'Qt4Cairo',
         *'cairo', 'Qt5Agg', 'pgf', 'nbAgg', 'Qt5Cairo',
          *'svg', 'GTK3Agg', 'MacOSX', *'agg', 'WebAgg',
           'TkCairo', *'ps', 'TkAgg', 'WX', *'pdf', 'WXCairo',
            'template', 'Qt4Agg', 'WXAgg']
        *No interactivos (Solo generan un archivo)
        """

        self.selected = []
        self.mode = mode_setting
        self.center = (zerox,zeroy)
        self.size = (sizex,sizey)
        self.vertex_radius = vertex_default_radius
        self.vertex_radius_lock = False
        self.vertex_default_alpha = .5
        self.new_to_draw = []
        self.background_color = (1,1,1)
        self.buttons = []
        self.history = []
        self.history.append(self.objects)
        self.history_at = 0
        #mode0:  nothing                        //any mode on
        #mode1:  add vertex/                   //default
        #mode2:  create lines/arrows
        #mode3:  select lasso
        #mode4:  select vertex
        #mode5:  move objects

    def vertex_auto_position(self,radius=1):
        printf("Function Graph.vertex_auto_position("+str(radius)+")",2)
        if(len(self.vertex) < 1): return 
        #En un radiox hay dos cuartos
        #Se deben poner la mitad de los vertices entre x
        vertex_num = len(self.vertex)
        angle = 2*math.pi/vertex_num
        if(not self.vertex_radius_lock):
            self.vertex_radius = angle/2
        self.clear(False)
        for vertex_counter in range(vertex_num):
            self.vertex[vertex_counter].set_vertex_pos(radius*math.cos(angle*vertex_counter) + self.center[0],radius*math.sin(angle*vertex_counter) + self.center[1])
            self.vertex[vertex_counter].set_circle(self.vertex_radius)
            self.new_to_draw.append(self.vertex[vertex_counter].get_circle())
        self.new_to_draw.extend([edge_artist.get_line() for edge_artist in self.edges])
        plot.axes.Axes.relim()
        #self.clear()
        #self.objects=self.history[self.history_at]
        #self.new_to_draw=self.objects

    def setup_graph(self, border_t=0.98, border_r=0.98, border_b=0.12, border_l=0.07, vert_alpha=0.6, start_button_posx=0.1, start_button_posy=0.015, button_sizex=0.1, button_sizey=0.05, bg_color=False):
        printf("Function Graph.setup_graph("+str(border_t)+", "+str(border_r)+", "+str(border_b)+", "+str(border_l)+", "+str(vert_alpha)+")",2)
        plot.subplots_adjust(left=border_l, bottom=border_b, right=border_r, top=border_t)
        zerox,zeroy = self.center
        sizex,sizey = self.size
        plot.axis([zerox-(sizex),zerox+(sizex),zeroy-(sizey),zeroy+(sizey)])
        self.last_click = (0,0)
        self.lasso = False
        self.keep_selected = False
        self.click_sel = []
        self.release_sel = []
        self.border_b = border_b
        self.border_l = border_l
        self.keybindings = {"x":"self.clear()", 
                            "a":"self.add_vertex(coordx,coordy)",
                            "1":"self.set_mode(1)","w":"self.set_mode(3)",
                            "b":"self.vertex_auto_position()","escape":"self.set_selected([])",
                            "q":"self.show_graph()","2":"self.set_mode(2)",
                            "shift":"self.keep_selected = not self.keep_selected",
                            "3":"self.set_mode(3)","4":"self.set_mode(4)","5":"self.set_mode(5)",
                            "z":"self.history_change(-1)","y":"self.history_change(1)",
                            "backspace":"self.remove_selected()"}
        #qcvsplo, 1:mode_v, w:lasso, z:ctrlz, y:ctrly
        #b:organize, "delete":remo_sel, "escape":select_none
        #m:move_selected, x:clear, a:add_vertex
        #"shift":keep_sel, "enter":finish, "backspace":remove_selected
        
        self.figure.canvas.mpl_connect('button_press_event', self.on_click)
        self.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.figure.canvas.mpl_connect('key_press_event', self.on_key)
        self.figure.canvas.mpl_connect('key_notify_event', self.on_motion)
        self.add_button('Clear', self.on_click,"self.clear()")
        self.add_button('Add vert', self.on_click,"self.set_mode(1)")
        self.add_button('Organize', self.on_click,"self.vertex_auto_position()")
        self.add_button('Lasso', self.on_click,"self.set_mode(3)")
        if(not bg_color): bg_color=self.background_color
        else: self.background_color = bg_color
        #self.figure.patch.set_facecolor((.9, 0.9, 0.9)
        self.frame.set_facecolor(self.background_color)

    def add_button(self, name, function, on_release_func, start_button_posx=0.1, start_button_posy=0.015, button_sizex=0.1, button_sizey=0.05):
        x = start_button_posx+(button_sizex*(len(self.buttons)*1.5))
        y = start_button_posy
        new_button_pos = plot.axes([x, y, button_sizex, button_sizey])
        new_button = Button(new_button_pos, name)
        #new_button.on_clicked(function)
        self.buttons.append([new_button,str(x)+","+str(y),on_release_func])
        
    def show_graph(self):
        printf("Function Graph.show_graph()",2)
        #to_draw = PatchCollection(self.new_to_draw, alpha=self.vertex_default_alpha)
        #frame = ax
        printf("To draw: " + str(self.new_to_draw),2)
        for to_draw in self.new_to_draw:
            self.frame.add_artist(to_draw)
        self.history_check()
        self.new_to_draw = []
        plot.show()
        #matplotlib.axes.Axes.draw_idle()

    def history_check(self):
        printf("Function Graph.history_check()",2,endf=" : ")
        #print(self.history)
        #print(self.objects)
        try:
            if (self.objects != self.history[self.history_at+1]):
                self.history[self.history_at+1] = self.objects
                self.history_at+=1
                printf("overwritten ("+str(self.history_at)+")",2)
            else: self.history_at+=1
        except:
            if (self.objects != self.history[self.history_at]):
                self.history.append(self.objects)
                self.history_at+=1
                printf("added ("+str(self.history_at)+")",2)
        printf("",2)

    def on_click(self,event):
        coordx, coordy = event.xdata, event.ydata
        printf("Function Graph.on_click("+str(coordx)+", "+str(coordy)+", "+str(event)+")",2)
        frame_identifier = str(event.inaxes)[str(event.inaxes).find('('):]
        if(frame_identifier == "("+str(self.border_l)+","+str(self.border_b)+";0.91x0.86)" and len(self.objects) >= 1): 
            self.last_click=(coordx,coordy) 
            if(self.mode ==3 and plot.get_current_fig_manager().toolbar.mode == ''):
                self.lasso = self.LassoManager(self.frame, self.object_pos, self)     
                self.lasso.onpress(event)
            elif(self.mode == 2 or self.mode == 4):
                self.click_sel = self.select_return(event)
                if(len(self.click_sel)):
                    self.click_sel[0].get_circle().set_animated(True)
        else:
            try:
                eval([button[2] for button in self.buttons if frame_identifier == "("+button[1]+";0.1x0.05)"][0])
            except: pass

    def on_release(self, event):
        coordx, coordy = event.xdata, event.ydata
        printf("Function Graph.on_release("+str(coordx)+", "+str(coordy)+", "+str(event)+")",2)
        frame_identifier = str(event.inaxes)[str(event.inaxes).find('('):]
        if(frame_identifier == "("+str(self.border_l)+","+str(self.border_b)+";0.91x0.86)"):     
            if(plot.get_current_fig_manager().toolbar.mode == ''):
                if(self.mode == 1):
                    self.add_vertex(coordx,coordy)
                elif((self.mode == 2)and len(self.objects) >= 1):
                    self.release_sel = self.select_return(event)
                    if(len(self.click_sel)):
                        self.connect_selected()
                elif(self.mode == 3): self.lasso.onpress(event)
                elif(self.mode == 5):
                    try:
                        obj = self.select_return(event)[0]
                        eval("self.remove_"+str(type(obj).__name__).lower()+"(obj)")
                    except: pass
                elif(self.mode == 4):
                    if(len(self.click_sel)):
                        self.click_sel[0].set_vertex_pos(coordx,coordy)
                        self.new_to_draw.append(self.click_sel[0].get_artist())
        self.show_graph()

    def on_key(self, event):
        key, coordx, coordy = event.key, event.xdata, event.ydata
        printf("Function Graph.on_key("+str(key)+", "+str(coordx)+", "+str(coordy)+", "+str(event)+")",2)
        try:
            eval(self.keybindings[key])
        except: pass
        self.show_graph()

    def on_motion(self, event):
        coordx, coordy = event.xdata, event.ydata
        printf("Function Graph.on_motion("+str(coordx)+", "+str(coordy)+", "+str(event)+")",2)
        if (plot.get_current_fig_manager().toolbar.mode == ''):
            if(self.mode == 4):
                self.click_sel[0].set_vertex_pos(coordx,coordy)
                self.click_sel[0].set_circle(self.vertex_radius)
        plot.draw()

    def lasso_return(self, vert_list):        
        printf("Function Graph.lasso_return("+str(vert_list)+")",2)
        for vert in range(len(vert_list)):
            if vert:
                self.selected.append(self.objects[vert])
                self.select_color(self.objects[vert])

    def select_return(self, event, pol_size=0.25):
        printf("Function select_return("+str(event)+", "+str(pol_size)+")",2)
        coordx, coordy = event.xdata, event.ydata
        axind = [self.frame].index(event.inaxes)
        select_square = matplotlib.path.Path([(coordx+pol_size,coordy+pol_size),(coordx-pol_size,coordy+pol_size),(coordx-pol_size,coordy-pol_size),(coordx+pol_size,coordy-pol_size)])
        ind = self.obj_from_ind(select_square.contains_points([self.object_pos][axind]))
        self.set_selected(ind)
        for obj in ind:
            self.select_color(obj,(1,0,0))
        printf("return "+str(ind),3)
        plot.draw()
        return ind

    def add_vertex(self,posx=1,posy=1):
        printf("Function Graph.add_vertex("+str(posx)+", "+str(posy)+")",2)
        new_vertex=self.Vertex()
        new_vertex.create_vertex(len(self.objects),posx,posy)
        self.vertex.append(new_vertex)
        self.objects.append(new_vertex)
        self.object_pos.append((posx,posy))
        if(not self.vertex_radius_lock):
            self.vertex_radius = ((self.size[0]*self.size[1]/len(self.vertex))**(1/2))/2
        self.new_to_draw.append(new_vertex.get_circle())
        return new_vertex

    def add_edge(self,segments=1):
        printf("Function Graph.add_edge("+str(segments)+")",2)
        new_edge = self.Edge()
        new_edge.create_edge(len(self.objects),segments)
        self.edges.append(new_edge)
        self.objects.append(new_edge)
        return new_edge

    def connect_vertex(self,vert1,vert2,weight=1,directed=True,edge=False):
        printf("Function Graph.connect_vertex("+str(vert1)+", "+str(vert2)+", "+str(weight)+", "+str(directed)+", "+str(edge)+")",2)
        if(not edge): edge = self.add_edge()
        edge.connect_edge(vert1,vert2,weight,directed)
        edge.set_line()
        self.new_to_draw.append(edge.get_line())
        return edge

    def connect_selected(self,selected_from=False,selected_to=False,weight=1):
        printf("Function Graph.connect_selected("+str(selected_from)+", "+str(selected_to)+", "+str(weight)+")",2)
        if not selected_from:
            selected_from = self.type_from_ind(self.click_sel,g_type="Vertex")
        if not selected_to: 
            selected_to = self.type_from_ind(self.release_sel,g_type="Vertex")
        for vert_from in selected_from:
            for vert_to in selected_to:
                self.connect_vertex(vert_from, vert_to, weight, directed=True)

    def hide_vertex(self,vert):
        vert.get_circle().set_alpha(0)

    def hide_edge(self,edge):
        edge.get_line().set_alpha(0)

    def select_color(self,obj,fcolor=(1,0,0),ecolor=(1,0,0)):
        printf("Function Graph.select_color("+str(obj)+", "+str(fcolor)+", "+str(ecolor)+")",2)
        artist = obj.get_artist()
        artist.set_facecolor(fcolor)
        #self.new_to_draw.append(artist)
        #obj.get_artist().remove()
        if(ecolor): 
            artist.set_facecolor(ecolor)

    def remove_vertex(self,vert):
        printf("Function Graph.remove_vertex("+str(vert)+")",2)
        #self.hide_vertex(vert)
        vert.remove_self()
        try:
            self.objects.remove(vert)
        except: printf("[-]vert not removed from self.objects",1)
        try:
            self.vertex.remove(vert)
        except: printf("[-]vert not removed from self.vertex",1)
        try:
            self.selected.remove(vert)
        except: printf("[-]vert not removed from self.selected",2)
        try:
            vert.get_circle().remove()
        except: printf("[-]circle not removed",0)
        del vert

    def remove_edge(self,edge):
        printf("Function Graph.remove_edge("+str(edge)+")",2)
        print("Try to remove " + str(edge))
        #self.hide_edge(edge)
        edge.remove_self()
        try:
            self.objects.remove(edge)
        except: printf("[-]edge not removed from self.objects",1)
        try:
            self.edges.remove(edge)
        except: printf("[-]edge not removed from self.edges",1)
        try:
            self.selected.remove(edge)
        except: printf("[-]edge not removed from self.selected",2)
        try:
            edge.get_line().remove()
        except: printf("[-]line not removed",0)
        del edge

    def set_mode(self,new_mode):
        printf("Function Graph.set_mode("+str(new_mode)+")",2)
        self.mode = new_mode

    def get_adjacency_table(self):
        printf("Function get_adjacency_table()",2)
        table = ([[0]*len(self.vertex)]*len(self.vertex))
        for edge in self.edges:
            vert_from = edge.get_vertex_from()
            vert_to = edge.get_vertex_to()
            table[vert_from.get_vertex_num()][vert_to.get_vertex_num()] += 1
        return table

    def print_adjacency_table(self):
        printf("Function print_adjacency_table()",2)
        for vert in self.get_adjacency_table():
            print(vert)
            
    def clear(self, remove=True):
        printf("Function Graph.clear("+str(remove)+")",2)
        if(remove):    
            try:
                print("self.vertex: " + str(self.vertex))
                while(len(self.vertex)):
                    self.remove_vertex(self.vertex[0])
            except:
                while(len(self.edges)):
                    self.remove_edge(self.edges[0])
            self.show_graph()
        else:
            for artist in self.objects:
                try:
                    artist.get_artist().remove()
                except: printf("[-]artist not removed",0)
        
        #self.figure.axes.remove(vert)

    def set_selected(self, selection):
        printf("Function Graph.set_selected("+str(selection)+")",2)
        if(not len(selection)): 
            for sel in self.selected: self.select_color(sel,(.2,.2,.2))
            self.selected = []
            return
        select = self.obj_from_ind(selection)
        if(self.keep_selected): self.selected.append(sel for sel in select if not sel in self.selected)
        else: 
            for sel in self.selected: self.select_color(sel,(.2,.2,.2))
            self.selected = select
        for sel in select: self.select_color(sel,(1,0,0))
        printf("Selected " + str(self.selected),3)

    def obj_from_ind(self, ind):
        printf("Function Graph.obj_from_ind("+str(ind)+")",2)
        if(len(self.objects) == 0): return [] 
        selected = [self.objects[sel] for sel in range(len(ind)-1) if ind[sel]]
        return selected
    
    def type_from_ind(self, ind, g_type="Vertex"):
        printf("Function Graph.type_from_ind("+str(ind)+", "+str(g_type)+")",2)
        selected = [vert for vert in self.obj_from_ind(ind) if type(vert).__name__ == g_type]
        return selected

    def remove_selected(self):
        printf("Function Graph.remove_selected()",2)
        verts = self.type_from_ind(self.selected,"Vertex")
        for vert in verts:
            self.remove_vertex(vert)
        edges = self.type_from_ind(self.selected,"Edge")
        for edge in edges:
            self.remove_edge(edge)
        plot.draw()

    def history_change(self,chan=-1):
        printf("Function Graph.history_changer("+str(chan)+")",2)
        try:
            self.clear(False)
            self.objects=[obj.get_artist() for obj in self.history[self.history_at+chan]]
            self.new_to_draw=self.objects
            self.history_at+=chan
            self.show_graph()
        except: pass

    class Vertex(object):
        def create_vertex(self,num,posx=1,posy=1,vertex_radius=0.1):
            printf("Function Graph.Vertex.create_vertex("+str(num)+", "+str(posx)+", "+str(posy)+", "+str(vertex_radius)+")",2)
            self.number_vert = num
            self.position_x = posx
            self.position_y = posy
            self.radius = vertex_radius
            self.set_circle(vertex_radius)
            self.adjacent_edges = []
            self.to_vert_counter = {}

        def set_vertex_pos(self,posx,posy):
            printf("Function Graph.Vertex.set_vertex_pos("+str(posx)+", "+str(posy)+")",2)
            self.position_x = posx
            self.position_y = posy
            for edge in self.adjacent_edges:
                edge.set_line()

        def get_vertex_position(self):
            printf("Function Graph.Vertex.get_vertex_position()",3)
            return(self.position_x, self.position_y)

        def get_circle(self):
            printf("Function Graph.Vertex.get_circle()",3)
            return self.circle

        def get_artist(self):
            printf("Function Graph.Vertex.get_artist()",2)
            return self.get_circle()

        def set_circle(self, radius=False, main_color=(.1,.1,.1), round_color=(0.0,0.0,0.0), circle_alpha=0.5):
            printf("Function Graph.Vertex.set_circle("+str(radius)+")",2)
            print(self.position_x,self.position_y)
            if (not radius): radius = self.radius
            self.circle = mpatch.Circle((self.position_x,self.position_y),radius,alpha=circle_alpha,facecolor=main_color,edgecolor=round_color,visible=True,fill=False,picker=True)
  
        def add_adjacent(self,new_adj_edge):
            self.adjacent_edges.append(new_adj_edge)
            try:
                self.to_vert_counter[new_adj_edge] += 1
            except:
                self.to_vert_counter[new_adj_edge] = 1

        def get_counter(self):
            return self.to_vert_counter
                
        def get_vertex_num(self):
            return self.number_vert

        def get_vertex_radius(self):
            return self.radius
        
        def remove_adj_edge(self, edge):
            self.adjacent_edges.remove(edge)
            
        def remove_self(self):
            while(len(self.adjacent_edges)):
                self.adjacent_edges[0].remove_self()
                self.adjacent_edges.pop(0)
                    
    class Edge(object):
        def create_edge(self,num,edge_segments=2):
            printf("Function Graph.Edge.create_edge("+str(num)+", "+str(edge_segments)+")",2)
            self.segments_num = edge_segments
            self.segments_pos = []
            self.line = None
            self.number_edge=num

        def connect_edge(self,vert1,vert2,edge_weight=1,directed_bool=False):
            printf("Function Graph.Edge.connect_edge("+str(vert1)+", "+str(vert2)+", "+str(edge_weight)+", "+str(directed_bool)+")",2)
            self.connected_from = vert1
            self.connected_to = vert2
            pos = (vert1.get_vertex_position(),vert2.get_vertex_position())
            self.length = (((pos[0][0]-pos[1][0])**2)+((pos[0][1]-pos[0][1])**2))**(1/2)
            self.weight = edge_weight
            if(not self.length): self.length=abs(self.weight)+1
            self.directed = directed_bool
            vert1.add_adjacent(self)
            if(not self.directed):
                vert2.add_adjacent(self)

        def set_line(self,edge_alpha=1,face_color=(0.0,.4,.4),edge_color=(0.0,0.0,0.0),radius=1):
            printf("Function Graph.Edge.set_lines()",2)
            from_pos = self.connected_from.get_vertex_position()
            to_pos = self.connected_to.get_vertex_position()
            if self.directed: style="Simple"
            else: style="Simple"
            style+=",head_width=.1,head_length=.2,tail_width=0.05"
            kw = dict(arrowstyle=style, alpha=edge_alpha, linestyle=None, lw=5,facecolor=face_color,edgecolor=edge_color,picker=True,connectionstyle="arc3,rad="+str(2*from_pos.get_counter()[to_pos]*radius/(self.length+1)))
            #                                                                                                                           2*edges connecting same vert ^
            new_line = mpatch.FancyArrowPatch(posA=from_pos, posB=to_pos,shrinkA=self.connected_from.get_vertex_radius(),shrinkB=self.connected_to.get_vertex_radius(), **kw)
            self.line = new_line

        def get_line(self):
            printf("Function Graph.Edge.get_lines()",3)
            return self.line
            
        def get_artist(self):
            printf("Function Graph.Edge.get_artist()",2)
            return self.line

        def get_edge(self):
            printf("Function Graph.Edge.get_edge()",3)
            return(self.connected_from,self.connected_to,self.weight,self.directed)
            
        def get_edge_num(self):
            return self.number_edge
        
        def get_vertex_from(self):
            return self.connected_from
        
        def get_vertex_to(self):
            return self.connected_to
        
        def remove_self(self):
            if(not self.directed):
                self.connected_to.remove_adj_edge(self)
            self.connected_from.remove_adj_edge(self)

    #def apply_algorithm(

    class LassoManager(object):
        def __init__(self, ax, data, graphclass):
            print("LassoManager")
            self.axes = [ax]
            self.graph = graphclass
            self.canvas = ax.figure.canvas
            self.data = [data]
            self.Nxy = [ len(data) ]
            self.xys = [ [d for d in data] ]

        def callback(self, verts):
            printf("callback",2)
            self.canvas.draw_idle()
            self.canvas.widgetlock.release(self.lasso)
            if not(verts): 
                self.canvas.widgetlock.release(self.lasso)
            selection = matplotlib.path.Path(verts)
            try:
                axind = self.axes.index(self.current_axes)
                ind = selection.contains_points(self.xys[axind])
                del self.lasso
                self.graph.lasso_return(ind)
            except Exception as error: 
                print(error)
                del self.lasso

        def onpress(self, event):
            print(event)
            if self.canvas.widgetlock.locked(): 
                self.callback(None)
                return
            if event.inaxes is None:    return
            self.current_axes = event.inaxes
            self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata), self.callback)
            self.canvas.widgetlock(self.lasso)

        def get_lasso(self):
            return self.lasso

graph1 = Graph()
graph1.create_graph(mode_setting=4)
graph1.setup_graph(bg_color=(.8,.8,.8))
graph1.show_graph()