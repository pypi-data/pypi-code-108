"""
OpenGL GUI
"""
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class Init:
    def __init__(self, win_name, size=(1000, 500), encoding='utf-8'):
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_SINGLE)
        glutInitWindowSize(size[0], size[1])
        glutCreateWindow(bytes(win_name, encoding))


class MainWindow:
    def __init__(self, color=(1.0, 1.0, 1.0)):
        super(MainWindow, self).__init__()
        self.Color = color
        glClearColor(0.0, 0.0, 0.0, 1.0)
        gluOrtho2D(-1.0, 1.0, -1.0, 1.0)

    def background(self):
        color = self.Color
        glClear(GL_COLOR_BUFFER_BIT)

        glColor3f(color[0], color[1], color[2])
        glPolygonMode(GL_FRONT, GL_LINE)
        glPolygonMode(GL_BACK, GL_FILL)
        glBegin(GL_QUADS)
        glVertex2f(-1.0, -1.0)
        glVertex2f(-1.0, 1.0)
        glVertex2f(1.0, 1.0)
        glVertex2f(1.0, -1.0)
        glEnd()

        glFlush()

    @staticmethod
    def draw_line():
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT)

        glColor3f(0.0, 1.0, 0.0)
        glLineWidth(2)
        glBegin(GL_LINES)
        glVertex3f(-0.5, -0.5, 0.0)
        glVertex3f(-0.5, 0.5, 0.0)
        glVertex3f(0.5, -0.5, 0.0)
        glVertex3f(0.5, 0.5, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glEnd()

        glFlush()


class Text:
    def __init__(self, text):
        self.Text = text


class Run:
    def __init__(self, win_name, widget):
        Init(win_name)
        glutDisplayFunc(widget)
        glutMainLoop()
