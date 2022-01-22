import js
import inspect
from math import cos, sin, pi, sqrt, atan2
import time

class Turtle:

    """ TODO : les indicateurs de position ne fonctionnent pas car on ne renvoie rien.
    Par exemple, self.state fixe l'appel à self._xcor qui renvoie une donnée.
    Même problème pour l'animation du cercle. self.angle et self.x changent, ce qui pose problème.
    """

    parent = js.document.activeElement.parentNode
    while "term" not in parent.id:
        parent = parent.parentNode
    EDITOR_ID = parent.id[5:]

    def __init__(self, x = 0, y = 0, angle = 0):
        self.canvas = js.document.getElementById(f"gui_{self.EDITOR_ID}_tracer")
        self.ctx = self.canvas.getContext("2d")
        self.delta_x = self.canvas.width / 2
        self.delta_y = self.canvas.height / 2
        self.canvas_pt = js.document.getElementById(f"gui_{self.EDITOR_ID}_pointer")
        self.ctx_pt = self.canvas_pt.getContext("2d")
        self.x, self.y = x + self.delta_x, y + self.delta_y
        self.angle = angle
        self.init_angle = angle
        self.pen_color = 'black'
        self.fill_color = 'black'
        self._pen_down = True
        self.width_ = 2
        self.__set_default()
        self.state = list()     # queue
        self.on_draw = 0
        self.stamp_number = 0
        self.fill = False
        self._speed = 5
        self._hide = False

    def __set_default(self):
        self.ctx.lineJoin = "miter"
        self.ctx.lineCap = "round"
        self.ctx.strokeStyle = self.pen_color
        self.ctx.lineWidth = self.width_
        self.style = self.triangle

    def _basic_pointer_draw(function):

        def wrapper(self):
            self.ctx_pt.clearRect(0, 0, self.canvas_pt.width, self.canvas_pt.height)
            self.ctx_pt.beginPath()
            function(self)
            self.ctx_pt.fill()
            self.ctx_pt.stroke()

        return wrapper

    def speed(self, number):
        assert 0 <= number <= 10
        self._speed = number

    def rad2deg(self, angle):
        return angle / pi *180

    def deg2rad(self, angle):
        return angle / 180 * pi

    def hideturtle(self):
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}""", "hide" : True})

    def ht(self):
        self.hideturtle()
    
    def _hideturtle(self, params):
        self._hide = params['hide']

    def showturtle(self):
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}""", "hide" : False})

    def st(self):
        self.hideturtle()
    
    def _showturtle(self, params):
        self._hide = params['hide']

    def goto(self, x, y):
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}""", "x" : x + self.delta_x, "y" : y + self.delta_y})

    def _goto(self, params):
        x, y = params["x"], params["y"]
        if self._pen_down : 
            self.ctx.beginPath()
            self.ctx.moveTo(self.x, self.y)
            self.ctx.lineTo(x, y)
            self.ctx.stroke()
        self.x, self.y = x, y
        if (not self._hide): self.style()

    def _get_parameters(self, x, y):
        if y is not None : 
            x2, y2 = x, y
        elif isinstance(x, Turtle): 
            x2, y2 = Turtle.x, Turtle.y 
        else :
            x2, y2 = x
        return x2, y2

    def towards(self, x, y = None):
        """ Fonction à revoir ?"""
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}""", "x" : x + self.delta_x, "y" : y + self.delta_y})

    def _towards(self, params):
        x2, y2 = self._get_parameters(params["x"], params["y"])
        return (self.rad2deg(atan2(self.y-y2, self.x-x2)) + 180) % 360

    def distance(self, x, y = None):
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}""", "x" : x + self.delta_x, "y" : y + self.delta_y})

    def _distance(self, x, y = None):
        x2, y2 = self._get_parameters(params["x"], params["y"])
        return sqrt((self.x-x2)**2 + (self.y-y2)**2)

    def pencolor(self, r = None, g = None, b = None):
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}""", "r" : r, "g" : g, "b" : b})

    def _pencolor(self, params):
        r, g, b = params["r"], params["g"], params["b"]
        if isinstance(r, str) :
            color = r
        elif isinstance(r, tuple) :
            rr, g, b = r
            color = self.rgb2hex(rr, g, b)
        elif g is not None and b is not None :
            color = self.rgb2hex(r, g, b)
        elif r is None:
            return self.pen_color
        self.pen_color = color
        self.ctx.strokeStyle = color
        self.ctx_pt.strokeStyle = color
        if (not self._hide): self.style()

    def fillcolor(self, r = None, g = None, b = None):
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}""", "r" : r, "g" : g, "b" : b})

    def _fillcolor(self, params):
        r, g, b = params["r"], params["g"], params["b"]
        if isinstance(r, str) :
            color = r
        elif isinstance(r, tuple) :
            rr, g, b = r
            color = self.rgb2hex(rr, g, b)
        elif g is not None and b is not None :
            color = self.rgb2hex(r, g, b)
        elif r is None:
            return self.fill_color
        self.fill_color = color
        self.ctx.fillStyle = color
        self.ctx_pt.fillStyle = color
        if (not self._hide): self.style()

    def color(self, r1 = None, g1 = None, b1 = None, r2 = None, g2 = None, b2 = None):
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}""", \
                            "r1" : r1, "g1" : g1, "b1" : b1, "r2" : r2, "g2" : g2, "b2" : b2 })

    def _color(self, params):
        r1, g1, b1 = params["r1"], params["g1"], params["b1"]
        r2, g2, b2 = params["r2"], params["g2"], params["b2"]
        if r1 is None and r2 is None:
            return self.pen_color, self.fill_color
        elif isinstance(r1, str) and isinstance(g1, str): 
            new_pen_params = {"r" : r1, "g":None, "b": None}
            new_fill_params = {"r" : g1, "g":None, "b": None}
            self._pencolor(new_pen_params)
            self._fillcolor(new_fill_params)
        elif isinstance(r1, tuple) and isinstance(g1, tuple): 
            new_pen_params = {"r" : r1, "g":None, "b": None}
            new_fill_params = {"r" : g1, "g":None, "b": None}
            self._pencolor(new_pen_params)
            self._fillcolor(new_fill_params)
        elif isinstance(r1, str) and g1 is None:
            new_params = {"r" : r1, "g":None, "b": None}
            self._pencolor(new_params)
            self._fillcolor(new_params)
        elif isinstance(r1, tuple) and g1 is None:
            new_params = {"r" : r1, "g":None, "b": None}
            self._pencolor(new_params)
            self._fillcolor(new_params)
        elif r1 is not None and g1 is not None and b1 is not None and r2 is None: 
            new_params = {"r" : r1, "g":g1, "b": b1}
            self._pencolor(new_params)
            self._fillcolor(new_params)

    def rgb2hex(self, r, g, b):
        for i in [r, g, b]:
            assert 0 <= i <= 255, "Wrong color code"
        return '#%02x%02x%02x' % (r, g, b)

    def pensize(self, width_ = None):
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}""", "width_" : width_ })

    def width(self, width_ = None):
        self.pensize(width_)

    def _pensize(self, params):
        width_ = params["width_"]
        if (width_ is None): return self.ctx.lineWidth
        self.ctx.lineWidth = width_

    def pendown(self):
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}"""})

    def pd(self):
        self.pendown()

    def down(self):
        self.pendown()

    def _pendown(self, params):
        self._pen_down = True

    def penup(self):
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}"""})

    def up(self):
        self.penup()

    def pu(self):
        self.penup()

    def _penup(self, params):
        self._pen_down = False

    def shape(self, style = None):
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}""", "sh" : style})
    
    def _shape(self, params):
        style = params["sh"]
        dico_style = {'arrow' : self.arrow, 'turtle' : self.turtle, \
            'circle' : self.cercle, 'square' : self.square, \
            'triangle' : self.triangle, 'classic': self.arrow}
        self.style = dico_style[style]
        if (not self._hide): self.style()

    def forward(self, L):
        if L < 0 : self.backward(-L)
        if self._speed == 0 : 
            self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}""", "L" : L })
        else :
            for _ in range(0, L, self._speed):
                self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}""", "L" : self._speed})
            self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}""", "L" : L % self._speed})

    def fd(self, L):
        self.forward(L)
                
    def _forward(self, params):
        L = params["L"]
        if self.fill : self.fill_coordinates.append((self.x, self.y))
        self.ctx.beginPath()
        if (not self._hide): self.style()
        self.ctx.moveTo(self.x, self.y)
        self.ctx.lineTo(self.x + L * cos(self.deg2rad(self.angle)), \
                        self.y + L * sin(self.deg2rad(self.angle)))
        if self._pen_down: self.ctx.stroke()
        self.x += L * cos(self.deg2rad(self.angle))
        self.y += L * sin(self.deg2rad(self.angle))

    def backward(self, L):
        if L < 0 : self.forward(-L)
        if self._speed == 0 : 
            self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}""", "L" : -L })
        else :
            for _ in range(0, L, self._speed):
                self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}""", "L" : -self._speed})
            self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}""", "L" : -L % self._speed})

    def back(self, L):
        self.backward(L)

    def bk(self, L):
        self.backward(L)

    def _backward(self, params):
        L = params["L"]
        if self.fill : self.fill_coordinates.append((self.x, self.y))
        self.ctx.beginPath()
        if (not self._hide): self.style()
        self.ctx.moveTo(self.x, self.y)
        self.ctx.lineTo(self.x + L * cos(self.deg2rad(self.angle)), \
                        self.y + L * sin(self.deg2rad(self.angle)))
        if self._pen_down: self.ctx.stroke()
        self.x += L * cos(self.deg2rad(self.angle))
        self.y += L * sin(self.deg2rad(self.angle))

    def xcor(self):
        """ non fonctionnel """
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}"""})

    def _xcor(self, params):
        return self.x + self.delta_x

    def ycor(self):
        """ non fonctionnel """
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}"""})

    def _ycor(self):
        return self.y + self.delta_y

    def heading(self):
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}"""})

    def _heading(self):
        return self.angle

    def setheading(self, angle):
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}""", "a" : angle})

    def seth(self, angle):
        self.setheading(angle)

    def _setheading(self, params):
        angle = params["a"]
        self.angle = angle

    def setx(self, x):
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}""", "x" : x + self.delta_x})

    def _setx(self, params):
        x = params["x"]
        self.x = x
        
    def sety(self, y):
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}""", "y" : y + self.delta_y})

    def _setx(self, params):
        y = params["y"]
        self.y = y

    def home(self):
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}"""})

    def _home(self, params):
        self.x, self.y, self.angle = self.delta_x, self.delta_y, self.init_angle

    def begin_fill(self):
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}"""})

    def _begin_fill(self, *args):
        self.fill_coordinates = []
        self.fill = True

    def end_fill(self):
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}"""})

    def _end_fill(self, *args):
        self.ctx.fillStyle = self.fill_color
        for ptX, ptY in self.fill_coordinates:
            self.ctx.lineTo(ptX, ptY)
        self.ctx.fill("evenodd")
        self.fill = False

    def filling(self):
        return self.fill

    @_basic_pointer_draw
    def triangle(self):
        x, y = self.x, self.y
        x1, y1 = self.rotation(-15, -10)
        x2, y2 = self.rotation(-15, 10)
        self.ctx_pt.moveTo(x, y)
        self.ctx_pt.lineTo(x+x1, y+y1)
        self.ctx_pt.lineTo(x+x2, y+y2)

    @_basic_pointer_draw
    def arrow(self):
        x, y = self.x, self.y
        x1, y1 = self.rotation(-15, -8)
        x2, y2 = self.rotation(-15, 8)
        x3, y3 = self.rotation(-10, 0)
        self.ctx_pt.moveTo(x, y)
        self.ctx_pt.lineTo(x+x1, y+y1)
        self.ctx_pt.lineTo(x+x3, y+y3)
        self.ctx_pt.lineTo(x+x2, y+y2)

    @_basic_pointer_draw
    def turtle(self):
        x, y = self.x, self.y
        quarter_turtle = [(-5,2), (-6,4), (-5,5), (-4,3)] 
        half_head = [(5,1), (7,2)] 
        half_turtle = quarter_turtle + [(-1,4)] \
            + [self._x_symmetry(p, q, -1) for (p,q) in quarter_turtle[::-1]] \
            + half_head
        full_turtle = [(-6,0)] + half_turtle + [(9,0)] \
            + [self._y_symmetry(p, q, 0) for (p,q) in half_turtle[::-1]]
        rotated_full_turtle = [self.rotation(p, q) for (p, q) in full_turtle]
        rotated_full_turtle = [self._stretch(p, q) for (p, q) in rotated_full_turtle]
        
        self.ctx_pt.moveTo(x + rotated_full_turtle[0][0], y + rotated_full_turtle[0][1])
        for (p,q) in rotated_full_turtle:
            self.ctx_pt.lineTo(x + p, y + q)
    
    def _stretch(self, x, y, stretch_factor=2):
        return (x*stretch_factor, y*stretch_factor)

    @_basic_pointer_draw            
    def cercle(self):
        rad = 15
        x, y = self.x, self.y
        self.ctx_pt.arc(x, y, rad, 0, 2*pi)

    @_basic_pointer_draw
    def square(self):
        side = 15
        x, y = self.x, self.y
        x0, y0 = self.rotation(-side/2, -side/2)
        x1, y1 = self.rotation(-side/2, side/2)
        x2, y2 = self.rotation(side/2, -side/2)
        x3, y3 = self.rotation(side/2, side/2)
        self.ctx_pt.moveTo(x+x0, y+y0)
        self.ctx_pt.lineTo(x+x1, y+y1)
        self.ctx_pt.lineTo(x+x3, y+y3)
        self.ctx_pt.lineTo(x+x2, y+y2)

    def _x_symmetry(self, x, y, x_axis):
        return (2*x_axis-x, y)

    def _y_symmetry(self, x, y, y_axis):
        return (x, 2*y_axis-y)

    def rotation(self, x, y):
        inv_rot_mat = [[cos(self.deg2rad(self.angle)), -sin(self.deg2rad(self.angle))], \
                    [sin(self.deg2rad(self.angle)), cos(self.deg2rad(self.angle))]]
        new_x = inv_rot_mat[0][0]*x + inv_rot_mat[0][1]*y
        new_y = inv_rot_mat[1][0]*x + inv_rot_mat[1][1]*y
        return new_x, new_y

    def circle(self, radius, extent = None, steps = None):
        self.state.append({"code": f"""self._{inspect.currentframe().f_code.co_name}""", \
                                "r": radius, "e":extent , "s":steps})
              
    def _circle(self, params):
        radius, extent, steps = params["r"], params["e"], params["s"]
        eps = 1
        if radius < 0 : eps = -1
        center = [self.x+abs(radius)*cos(self.deg2rad(self.angle - 90)), \
                        self.y+abs(radius)*sin(self.deg2rad(self.angle - 90))]

        if extent is None : extent = 360
        
        extent = int(extent)
        list_divisor = self._get_diviseur(extent)
        quality_values = list(filter(lambda x: x>=10, list_divisor)) # number of values above 10
    
        if len(list_divisor) == 2 : n = extent
        elif quality_values == 0 : n = extent
        else : n = min(quality_values)

        if steps is not None : n = steps
        angle = [90-eps*i*extent/n for i in range(n+1)]
        coords = [(abs(radius)*cos(self.deg2rad(angle[i])), abs(radius)*sin(self.deg2rad(angle[i]))) for i in range(n+1)]

        self.ctx.beginPath()
        self.ctx.moveTo(self.x, self.y)
        for i in range(n+1):
            self.ctx.lineTo(center[0]+coords[i][0], center[1]+coords[i][1])
        self.ctx.stroke()
        self.x, self.y = center[0]+coords[-1][0], center[1]+coords[-1][1]
        self.angle -= extent
        if (not self._hide): self.style()

    def circle_animated(self, radius, extent = None, steps = None):
        """ Problem : the coordinates NOT being taken at the beginning of the program and before the STACK """
        n, coords = self._get_circle_coordinates_animated(radius, extent, steps)
        for i, (p, q) in enumerate(coords):
            self.state.append({"code": f"""self._{inspect.currentframe().f_code.co_name}""", \
                                "radius" : radius, "coords": (p, q), "flag": (i, extent/n)})

    def _get_circle_coordinates_animated(self, radius, extent, steps):
        eps = 1
        if radius < 0 : eps = -1
        if extent is None : extent = 360

        extent = int(extent)
        list_divisor = self._get_diviseur(extent)
        quality_values = list(filter(lambda x: x>=10, list_divisor)) # number of values above 10
    
        if len(list_divisor) == 2 : n = extent
        elif quality_values == 0 : n = extent
        else : n = min(quality_values)

        if steps is not None : n = steps
        angle = [90-eps*i*extent/n for i in range(n+1)]
        coords = [(abs(radius)*cos(self.deg2rad(angle[i])), abs(radius)*sin(self.deg2rad(angle[i]))) for i in range(n+1)]
        return n, coords
        
    def _circle_animated(self, params):
        radius, x, y, i, extent = params["radius"], *params["coords"], *params["flag"]
        center = [self.x+abs(radius)*cos(self.deg2rad(self.angle+i*extent - 90)), \
                  self.y+abs(radius)*sin(self.deg2rad(self.angle+i*extent - 90))]
        self.ctx.beginPath()
        self.ctx.moveTo(self.x, self.y)
        self.ctx.lineTo(center[0]+x, center[1]+y)
        self.ctx.stroke()
        self.x, self.y = center[0]+x, center[1]+y
        self.angle -= extent
        if (not self._hide): self.style()        

    def _get_diviseur(self, x):
        return [i for i in range(1,x+1) if x%i == 0]

    #def _get_circle_coordinates(self, radius):
    #   n = 12
    #   eps = 1
    #   if radius < 0 : radius, eps = -radius, -1
    #   center = [self.x+radius*cos(self.deg2rad(self.angle - 90)), \
        #           self.y+radius*sin(self.deg2rad(self.angle - 90))]
        #angle = [eps*i*360/n-90 for i in range(n)]
        #coords = [(center[0] +radius*cos(self.deg2rad(angle[i])), center[1] +radius*sin(self.deg2rad(angle[i]))) for i in range(n)]
        #return coords

    def right(self, angle):
        if angle < 0 : self.left(-angle)
        if self._speed == 0 : 
            self.state.append({"code": f"""self._{inspect.currentframe().f_code.co_name}""", "a": angle})
        else :
            for _ in range(angle//self._speed):
                self.state.append({"code": f"""self._{inspect.currentframe().f_code.co_name}""", "a": self._speed})
            self.state.append({"code": f"""self._{inspect.currentframe().f_code.co_name}""", "a": int(angle) % (self._speed)})

    def rt(self, angle):
        self.right(angle)

    def left(self, angle):
        if angle < 0 : self.right(-angle)
        if self._speed == 0 : 
            self.state.append({"code": f"""self._{inspect.currentframe().f_code.co_name}""", "a": angle})
        else :
            for _ in range(angle//self._speed):
                self.state.append({"code": f"""self._{inspect.currentframe().f_code.co_name}""", "a": self._speed})
            self.state.append({"code": f"""self._{inspect.currentframe().f_code.co_name}""", "a": int(angle) % (self._speed)})

    def lt(self, angle):
        self.left(angle)

    def _right(self, params):
        angle = params["a"]
        self.angle += angle
        if (not self._hide): self.style()

    def _left(self, params):
        angle = params["a"]
        self.angle -= angle
        if (not self._hide): self.style()

    #def stamp(self):
    #    self.stamp_number += 1
    #    self.ctx.triangle()
    #    return self.stamp_number

    def dot(self, size = None, color = None):
        if isinstance(size, str) : size, color = None, size
        self.state.append({"code": f"""self._{inspect.currentframe().f_code.co_name}""", "size": size, "color": color})

    def _dot(self, params):
        # dot is not always on top of the line
        color = params["color"]
        size = params["size"]/2 if params["size"] is not None else max(self.ctx.lineWidth+4, self.ctx.lineWidth*2)
        assert size >= 1, f"""bad screen distance {size}"""
        self.ctx.beginPath()
        self.ctx.arc(self.x, self.y, size, 0, 2*pi)
        self.ctx.fillStyle = color if color is not None else self.color
        self.ctx.fill()

    def position(self):
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}"""})
    
    def _position(self, *args):
        return (self.x, self.y)

    def pos(self):
        self.position()     

    def clear(self):
        self.state.append({"code" : f"""self._{inspect.currentframe().f_code.co_name}"""})
    
    def _clear(self):
        self.ctx.clearRect(0, 0, self.canvas.width, self.canvas.height)
        self.ctx_pt.clearRect(0, 0, self.canvas_pt.width, self.canvas_pt.height)
        self.x, self.y, self.angle = self.delta_x, self.delta_y, self.initangle

    def tick(self):
        # Clear canvas
        if len(self.state) > 0 :	
            # Draw current state
            commands = self.state.pop(0)
            command = commands.pop("code")
            params = commands
            eval(command)(params)
        else : 
            js.clearInterval(self.on_draw)

    def mainloop(self):
        self.ctx.clearRect(0, 0, self.canvas.width, self.canvas.height)
        self.ctx_pt.clearRect(0, 0, self.canvas_pt.width, self.canvas_pt.height)
        self._animate()

    def _mainloop_noclear(self):
        self._animate()            

    def _animate(self):
        self.on_draw = js.window.setInterval(lambda x=2 : self.tick(), 10)

    """
    def get_id_editor(self, id_editor):
        self.canvas = js.document.getElementById(f'gui_{id_editor}_tracer')
        self.ctx = js.document.getElementById(f'gui_{id_editor}_tracer').getContext("2d")
        self.canvas_pt = js.document.getElementById(f'gui_{id_editor}_pointer')
        self.ctx_pt = js.document.getElementById(f'gui_{id_editor}_pointer').getContext("2d")
    """

_direct_access_turtle = Turtle()    # instanciation d'un objet invisible à l'utilisateur
def _deco_direct_access(function):

    def wrapper(*args):
        global _direct_access_turtle
        function(*args)
        _direct_access_turtle._mainloop_noclear()

    return wrapper

method_list = [func for func in dir(Turtle) if callable(getattr(Turtle, func)) and not func.startswith("_")]

for nom in method_list:
    exec(f"""@_deco_direct_access\ndef {nom}(*args):\n\t_direct_access_turtle.{nom}(*args)""")