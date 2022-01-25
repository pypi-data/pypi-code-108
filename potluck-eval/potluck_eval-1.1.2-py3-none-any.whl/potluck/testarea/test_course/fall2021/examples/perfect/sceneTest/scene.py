"""
scene.py

Your name: Peter Mawhorter
Your username: pmwh
Submission date: 2021-6-28
"""

from turtle import (
    penup, pendown, pensize, fd, bk, lt, color, begin_fill, end_fill
)
from turtleBeads import drawCircle

penup()
lt(90)
bk(50)
pendown()

pensize(8)
color("brown")
fd(140)
color("DarkGreen", "Green")
begin_fill()
drawCircle(50)
end_fill()
