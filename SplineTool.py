from OpenGL.GL import *
import glfw
import math
import sys

# get commandline inputs from user
w = int(sys.argv[1])
h = int(sys.argv[2])

# initialize our list object
nodes = []

# creating our class objects to help manipulate nodes
class Node :
    def __init__(self, point, handle1=None, handle2=None):
        self.handle1 = handle1
        self.point = point
        self.handle2 = handle2

    # set handle position to new location, maintaining the same offset from the node
    def moveHandle1(self, location):
        self.handle1 = (location[0] - self.point[0], location[1] - self.point[1])
        if self.handle2 is not None:
            self.handle2 = (-1 * self.handle1[0], -1 * self.handle1[1])  # modify handle 2 position

    # set handle to the opposite location of handle 1
    def setHandle2(self):
        if self.handle2 is None:
            self.handle2 = (-1 * self.handle1[0], -1 * self.handle1[1])

    # set handle position to new location, maintaining the same offset from the node
    def moveHandle2(self, location):
        self.handle2 = (location[0] - self.point[0], location[1] - self.point[1])
        self.handle1 = (-1 * self.handle2[0], -1 * self.handle2[1])  # modify handle 1 position


# function that renders the nodes
def render_node(n):
    # define point size and colour
    glPointSize(20)
    glColor3f(0 , 0, 1)
    # begin immediate mode with gl point
    glBegin(GL_POINTS)

    for node in n:  # loop through all of the nodes objects in the list and plot them as points
        first_node = node
        glVertex2f(first_node.point[0], first_node.point[1]) # plot x,y values of the node

    glEnd()  # end immediate mode

# function that renders the bezier curve for  two nodes
def create_beziercurve(A, B, C1, C2):
    glLineWidth(1.5)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor3f(0,0,0)
    glBegin(GL_LINE_STRIP)
    for t in range(0,200):
        x, y = cubic_interpolation(A, B, C1, C2, t)
        glVertex2f(x, y)
    glEnd()
    glDisable(GL_LINE_SMOOTH)
    glDisable(GL_BLEND)

# function that does the cubic interpolation and returns the x,y points
def cubic_interpolation(A, B, C1, C2, n):
    t = n/200
    C1 = (A[0]+C1[0],A[1]+C1[1])
    C2 = (B[0] + C2[0], B[1] + C2[1])
    px = A[0]*(1-t)**3 + 3*((1-t)**2)*t*C1[0] + 3*(1-t)*(t**2)*C2[0] + B[0]*(t**3)
    py = A[1]*(1 - t) ** 3 + 3*((1 - t) ** 2) * t * C1[1] + 3*(1 - t) * (t ** 2) * C2[1] + B[1] * (t ** 3)
    return px, py

# function to render the control points or the "handles"
def render_control_points(c):
    glColor(0, 0, 0)
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBegin(GL_POINTS)

    # loop through our list and plot the handles
    for a in c:
        control = a
        if control.handle1 is not None:
            glVertex2f(control.handle1[0]+control.point[0], control.handle1[1]+control.point[1])
        if control.handle2 is not None:
            glVertex2f(control.handle2[0]+control.point[0], control.handle2[1]+control.point[1])

    # end immediate mode, point smooth, and blend
    glEnd()
    glDisable(GL_POINT_SMOOTH)
    glDisable(GL_BLEND)
    # create the stipple line
    stipple()

# function to render the stipple pattern to connect the nodes and handles
def stipple():
    for a in nodes:

        glColor(0, 0.3, 0.9)  # set colour
        # set stipple pattern
        glEnable(GL_LINE_STIPPLE)
        glLineStipple(3, 0xAAAA)

        glBegin(GL_LINES)  # begin immediate mode
        # define vertex points of handle and node
        glVertex2f(a.handle1[0]+a.point[0], a.handle1[1] +a.point[1])
        glVertex2f(a.point[0], a.point[1])

        # if handle 2 exists, connect the stipple pattern line to it
        if a.handle2 is not None:
            glVertex2f(a.handle2[0] + a.point[0], a.handle2[1] + a.point[1])
            glVertex2f(a.point[0], a.point[1])
        glEnd()
    glDisable(GL_LINE_STIPPLE)

# function creating our node objects and associated handles
def create_node(xpos, ypos):

    # create the new node objects based on positions
    node1 = Node((xpos, ypos))

    h1 = (0, 50)  # create handle
    node1.handle1 = h1  # add handle
    nodes.append(node1)  # append the node object to the nodes list

    # add handles to nodes that are not the endpoints
    if len(nodes) > 2:
        add_h2 = nodes[nodes.index(node1) - 1]
        add_h2.setHandle2()


# function to help calculate euclidean distance between two points
def euclidean(a, b):
    d_x = abs(a[0]-b[0])  # determine change in x
    d_y = abs(a[1]-b[1])  # determine change in y
    distance = math.sqrt(d_x ** 2 + d_y ** 2)  # calculate distance
    return distance


# global variable initialization
isPressed = True
isReleased = True
add_node = True


#  Callback function for mouse button events
def mouse_button_callback(window, button, action, mods):

  # declare global variables
  global isPressed, isReleased,add_node


# check if the mouse is clicked
  if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
    # initialize variables and get cursor position
        dx_h2 = 0
        dy_h2 = 0
        xpos, ypos = glfw.get_cursor_pos(window)
        ypos = h-ypos

    # loop through all of our nodes and determine the location of the cursor with respect to the points and handles
        for node in nodes:

            # determine distance between the node and cursor
            dx = abs(xpos - node.point[0])
            dy = abs(ypos - node.point[1])
            # determine distance between handle1 and cursor
            dx_h1 = abs(xpos - node.handle1[0])
            dy_h1 = abs(ypos - node.handle1[1])

            # determine distance between the cursor and the second handle if it exists
            if node.handle2 is not None:
                dx_h2 = abs(xpos - node.handle2[0])
                dy_h2 = abs(ypos - node.handle2[1])

            # if cursor is within a 20 pixel radius of the node, disable adding new nodes
            if 0 <= dx < 20 or 0 <= dy < 20:
                add_node = False
                isPressed = True
                isReleased = True
                break
            # if cursor is within a 20 pixel radius of the node, disable adding new nodes
            if 0 <= dx_h1 < 20 or 0 <= dy_h1 < 20:
                add_node = False
                isPressed = True
                isReleased = True
                break
            # if a cursor is within 20 pixel radius of the node, disable adding new nodes
            if (dx_h2 != 0 and dy_h2 != 0) and (dx_h2 < 20 or dy_h2 < 20):
                add_node = False
                isPressed = True
                isReleased = True
                break

        # only add a new node if add_node == true
        if add_node:
            create_node(xpos, ypos)
            # add flags to determine the eligibility of adding new nodes vs translating nodes/ adjusting control points
            isPressed = True
            isReleased = True

 # check if button is released, allow for adding a new node
  if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.RELEASE:
      isPressed = False
      isReleased = True
      add_node = True

 # check if mouse is being held but not released, disable adding new nodes
  if button == glfw.MOUSE_BUTTON_LEFT and action != glfw.RELEASE and action == glfw.PRESS:
      isPressed = True
      isReleased = False
      add_node = False


def cursor_pos_callback(window, xpos, ypos):
    # determine x position and y position
    x, y = xpos, h-ypos

    # only drag nodes/ adjust control points if mouse is pressed but not released
    if isPressed and not isReleased:

        # set the closest node to be "None"
        closest_node = None
        # assume the starting closest distance to a node is a large number
        closest_distance = 1000

        # loop through all existing nodes
        for i in nodes:
            distance = euclidean((x,y),i.point)  # determine the euclidean distance between the cursor and the nodes
            if distance < closest_distance:  # determine if the distance is closer than the closest distance
                closest_node = i  # closest node is the i'th node in the nodes list
                closest_distance = distance  # set distance to new distance

        # determine handle distance
        handle2_distance = 0
        handle1_distance = euclidean((x,y),(closest_node.handle1[0]+closest_node.point[0], closest_node.handle1[1]+closest_node.point[1]))

        # determine if the closest node has a second handle
        if closest_node.handle2 is not None:
            handle2_distance = euclidean((x,y),(closest_node.handle2[0]+closest_node.point[0],closest_node.handle2[1]+closest_node.point[1]))

        # check what the user is adjusting and reflect those changes by modifying the class object
        if handle1_distance < 20 and closest_node.handle1 is not None:
            closest_node.moveHandle1((x, y))
        elif handle2_distance < 20 and closest_node.handle2 is not None:
            closest_node.moveHandle2((x, y))
        elif closest_distance < 20:
            closest_node.point = (x, y)

# key callback function to clear the window
def key_callback(window, key, scancode, action, mods):

    if key == glfw.KEY_E and action == glfw.PRESS and action != glfw.RELEASE:  # check if "E" is pressed
        del nodes[:]  # reset our spline tool by deleting all existing nodes


# initalize glfw and create our window based on commandline inputs
glfw.init()
window = glfw.create_window(w, h, "A Spline Tool", None, None)
glfw.make_context_current(window)

# Register the mouse button callback function
glfw.set_mouse_button_callback(window, mouse_button_callback)
glfw.set_cursor_pos_callback(window, cursor_pos_callback)
glfw.set_key_callback(window, key_callback)


# specify the viewing volume
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
glOrtho(0, w, 0, h, -1, 1)

# map screen coordinates to pixel coordinates, (used a retina display which made it)
width, height = glfw.get_framebuffer_size(window)

# define the viewport based on the retrieved width and height size
glViewport(0, 0, width, height)

# enable 4x multisampling for anti-aliasing
glfw.window_hint(glfw.SAMPLES, 4)


# loop to keep the window open
while not glfw.window_should_close(window):
    # watch out for any events
    glfw.poll_events()

    # set background colour to white
    glClearColor(1, 1, 1, 1)
    glClear(GL_COLOR_BUFFER_BIT)

    # render the nodes and associated control points
    render_node(nodes)
    render_control_points(nodes)

    # render the bezier curve
    for i in range(0, len(nodes)-1, 1):

        # define two end points of a curve
        point1 = nodes[i]
        point2 = nodes[i+1]

    # determine the control points of the associated with the end points of a single curve

        if point1.handle2 is None:
            create_beziercurve(point1.point, point2.point, point1.handle1, point2.handle1)

        elif point1.handle2 is not None:
            create_beziercurve(point1.point, point2.point, point1.handle2, point2.handle1)

    # swap the front and back buffer
    glfw.swap_buffers(window)

# close window
glfw.terminate()
