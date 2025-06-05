"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT, GLU

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser

class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.
    """

    def __init__(self, parent, devices, monitors):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                        attribList=[wxcanvas.WX_GL_RGBA,
                                    wxcanvas.WX_GL_DOUBLEBUFFER,
                                    wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Store devices and monitors
        self.devices = devices
        self.monitors = monitors

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0
        self.last_mouse_y = 0

        # Initialise variables for zooming
        self.zoom = 1

        # Signal display properties
        self.signal_height = 60  # Increased height of each signal track
        self.time_unit_width = 30  # Increased width of each time unit
        self.grid_color = (0.9, 0.9, 0.9)  # Will be updated by theme
        self.background_color = (1.0, 1.0, 1.0)  # Will be updated by theme
        self.text_color = (0.0, 0.0, 0.0)  # Will be updated by theme
        self.signal_colors = [
            (0.0, 0.0, 1.0),  # Blue
            (0.0, 0.7, 0.0),  # Green
            (1.0, 0.0, 0.0),  # Red
            (0.7, 0.0, 0.7),  # Purple
        ]
        
        # Signal line properties
        self.signal_line_width = 4.0  # Thicker signal lines
        self.grid_line_width = 1.0  # Standard grid lines
        
        # Initialize empty signal data
        self.signal_data = {}

        # Status text
        self.status_text = ""
        
        # Grid margin to leave space for status text
        self.bottom_margin = 30  # pixels for status text

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y + self.bottom_margin, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, text=""):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Store status text
        self.status_text = text

        # Get size and calculate grid dimensions
        size = self.GetClientSize()
        max_time_units = max(50, max((len(signal_list) for signal_list in self.signal_data.values()), default=0))
        num_signals = len(self.signal_data)
        total_height = max((num_signals + 1) * self.signal_height, size.height - self.bottom_margin)
        total_width = max(max_time_units * self.time_unit_width, size.width)

        # Clear with current background color
        GL.glClearColor(*self.background_color, 0.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        
        # Enable line smoothing for better appearance
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
        
        # Apply pan and zoom for the grid and signals
        GL.glPushMatrix()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)
        
        # Draw grid with current grid color
        GL.glColor3f(*self.grid_color)
        self.draw_grid()
        
        # Draw time axis
        self.draw_time_axis()
        
        # Draw signals
        self.draw_signals()
        
        # Draw signal names
        self.draw_signal_names()
        
        GL.glPopMatrix()
        
        # Draw status text at fixed position below x-axis
        if self.status_text:
            # Calculate position in screen coordinates
            text_x = self.pan_x + 10  # Small offset from left edge
            text_y = self.pan_y - 25  # Fixed distance below x-axis
            
            self.render_text(self.status_text, text_x, text_y)

        GL.glFlush()
        self.SwapBuffers()

    def draw_grid(self):
        """Draw the background grid."""
        size = self.GetClientSize()
        GL.glLineWidth(self.grid_line_width)
        GL.glBegin(GL.GL_LINES)
        
        # Calculate the maximum number of time units to display
        max_time_units = max(50, max((len(signal_list) for signal_list in self.signal_data.values()), default=0))
        num_signals = len(self.signal_data)
        total_height = max((num_signals + 1) * self.signal_height, size.height - self.bottom_margin)
        total_width = max(max_time_units * self.time_unit_width, size.width)
        
        # Vertical grid lines
        for x in range(0, int(total_width), self.time_unit_width):
            GL.glVertex2f(x, 0)
            GL.glVertex2f(x, total_height)
            
        # Horizontal grid lines
        for y in range(0, int(total_height), self.signal_height):
            GL.glVertex2f(0, y)
            GL.glVertex2f(total_width, y)
            
        GL.glEnd()

    def draw_time_axis(self):
        """Draw the time axis with numbers."""
        size = self.GetClientSize()
        max_time_units = max(50, max((len(signal_list) for signal_list in self.signal_data.values()), default=0))
        
        for i in range(max_time_units):
            x = i * self.time_unit_width
            self.render_text(str(i), x + 5, 5)

    def draw_signals(self):
        """Draw all signal waveforms."""
        if not self.signal_data:  # If no signals to draw
            return
            
        y_offset = self.signal_height
        GL.glLineWidth(self.signal_line_width)  # Set thicker line width for signals
        
        for i, (signal_name, values) in enumerate(self.signal_data.items()):
            if not values:  # Skip empty signal lists
                continue
                
            color = self.signal_colors[i % len(self.signal_colors)]
            GL.glColor3f(*color)
            
            y_base = y_offset + (i * self.signal_height)
            last_value = values[0]
            last_valid_value = 0  # Default to low for the first valid signal
            first_valid_found = False  # Track if we've found the first valid signal
            
            GL.glBegin(GL.GL_LINE_STRIP)
            
            for t, value in enumerate(values):
                x = t * self.time_unit_width
                
                # Skip drawing if this is a blank signal
                if value is None:
                    if t > 0 and values[t-1] is not None:
                        # If previous signal wasn't blank, end the line here
                        GL.glEnd()
                        GL.glBegin(GL.GL_LINE_STRIP)
                    continue
                
                # If we're coming from a blank signal, start a new line
                if t > 0 and values[t-1] is None:
                    GL.glEnd()
                    GL.glBegin(GL.GL_LINE_STRIP)
                    # Start from the current position
                    last_valid_value = value
                
                y = y_base + (self.signal_height * 0.8 if value else self.signal_height * 0.2)
                
                # Draw vertical line if value changed and neither current nor previous is blank
                # But only if this isn't the first valid signal we've encountered
                if value != last_valid_value and last_value is not None and first_valid_found:
                    GL.glVertex2f(x, y_base + (self.signal_height * 0.2))
                    GL.glVertex2f(x, y_base + (self.signal_height * 0.8))
                
                GL.glVertex2f(x, y)
                GL.glVertex2f(x + self.time_unit_width, y)
                
                if not first_valid_found and value is not None:
                    first_valid_found = True
                
                last_value = value
                if value is not None:
                    last_valid_value = value
            
            GL.glEnd()
            
    def draw_signal_names(self):
        """Draw the signal names on the left side."""
        if not self.signal_data:  # If no signals to draw
            return
            
        y_offset = self.signal_height
        
        for i, signal_name in enumerate(self.signal_data.keys()):
            y = y_offset + (i * self.signal_height) + (self.signal_height // 2)
            self.render_text(signal_name, 10, y)

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        # Calculate object coordinates of the mouse position
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(*self.text_color)  # Use theme text color
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

    def update_colors(self, background_color, grid_color):
        """Update the canvas colors based on the current theme."""
        self.background_color = (
            background_color.Red() / 255.0,
            background_color.Green() / 255.0,
            background_color.Blue() / 255.0
        )
        self.grid_color = (
            grid_color.Red() / 255.0,
            grid_color.Green() / 255.0,
            grid_color.Blue() / 255.0
        )
        self.init = False  # Force canvas redraw
        self.render()

class CustomListCtrl(wx.ListCtrl):
    """A custom ListCtrl with better dark mode support."""
    def __init__(self, parent, style, gui=None):
        style |= wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES
        super().__init__(parent, style=style)
        self.gui = gui
        
        # Initialize colors
        self.base_color = None
        self.alt_color = None
        self.header_color = None
        
        # Initialize switch renderers dictionary
        self.switch_renderers = {}
        
        # Set better row height using image list trick
        image_list = wx.ImageList(1, 28)  # 1 pixel wide, 28 pixels high
        self.AssignImageList(image_list, wx.IMAGE_LIST_SMALL)
        
        # Bind events for custom drawing
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_item_selected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_item_selected)
        self.Bind(wx.EVT_SCROLLWIN, self.on_scroll)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_click)  # Add click handling
        
        # Create a timer for delayed refresh
        self.refresh_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_refresh_timer)
        
    def on_scroll(self, event):
        """Handle scroll events."""
        event.Skip()
        self.schedule_refresh()
        
    def schedule_refresh(self):
        """Schedule a refresh after a short delay."""
        if self.refresh_timer.IsRunning():
            return  # Don't schedule if already pending
        self.refresh_timer.StartOnce(50)  # 50ms delay
        
    def on_refresh_timer(self, event):
        """Handle the refresh timer event."""
        if self.switch_renderers:  # Only redraw if we have switches
            self.draw_all_switches()
        
    def on_paint(self, event):
        """Handle painting of the list control."""
        event.Skip()
        if self.switch_renderers:  # Only schedule if we have switches
            self.schedule_refresh()
            
    def draw_all_switches(self):
        """Draw all visible switches."""
        if not self.switch_renderers:
            return
            
        dc = wx.ClientDC(self)
        
        # Get visible range
        top = self.GetTopItem()
        visible_count = self.GetCountPerPage() + 1
        bottom = min(top + visible_count, self.GetItemCount())
        
        # Draw each visible switch
        for index in range(top, bottom):
            if index in self.switch_renderers:
                self.draw_switch(dc, index)
                
    def draw_switch(self, dc, index):
        """Draw a single switch."""
        # Get item rectangle
        item_rect = self.GetItemRect(index)
        
        # Calculate switch column rectangle
        first_col_width = self.GetColumnWidth(0)
        switch_col_width = self.GetColumnWidth(1)
        
        switch_rect = wx.Rect(
            item_rect.x + first_col_width,
            item_rect.y,
            switch_col_width,
            item_rect.height
        )
        
        # Draw the switch
        renderer = self.switch_renderers[index]
        renderer.DrawItem(dc, switch_rect, None)
        
    def on_item_selected(self, event):
        """Handle item selection to ensure switches stay visible."""
        event.Skip()
        self.schedule_refresh()
        
    def set_colors(self, base_color, alt_color, header_color=None, header_text_color=None):
        """Set all colors for the list control."""
        self.base_color = base_color
        self.alt_color = alt_color
        self.header_color = header_color or base_color
        
        # Set the background color of the list control itself
        self.SetBackgroundColour(base_color)
        
        # Update existing items
        for i in range(self.GetItemCount()):
            self.update_item_color(i)
            
        # Force a refresh to update the appearance
        self.Refresh()
        self.schedule_refresh()
        
    def update_item_color(self, index):
        """Update the color of a specific item."""
        if self.base_color is None or self.alt_color is None:
            return
            
        if index % 2 == 0:
            self.SetItemBackgroundColour(index, self.base_color)
        else:
            self.SetItemBackgroundColour(index, self.alt_color)
            
    def Refresh(self):
        """Override refresh to ensure proper redraw."""
        super().Refresh()
        self.schedule_refresh()
        
    def __del__(self):
        """Clean up timer on deletion."""
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.Stop()
            del self.refresh_timer

    def on_left_click(self, event):
        """Handle left mouse clicks to toggle switches."""
        # Get click position
        x, y = event.GetPosition()
        
        # Get the item at this position
        item, flags = self.HitTest((x, y))
        subitem = None
        if item != -1:
            # Calculate which column was clicked
            x_offset = 0
            for col in range(self.GetColumnCount()):
                col_width = self.GetColumnWidth(col)
                if x < x_offset + col_width:
                    subitem = col
                    break
                x_offset += col_width
        
        if item != -1 and subitem == 1 and hasattr(self, 'switch_renderers') and item in self.switch_renderers:
            # Get the item rectangle
            rect = self.GetItemRect(item)
            
            # Calculate switch column position
            first_col_width = self.GetColumnWidth(0)
            switch_col_width = self.GetColumnWidth(1)
            
            # Calculate switch dimensions
            switch_width = min(48, switch_col_width - 8)
            switch_height = min(24, rect.height - 8)
            
            # Calculate switch position
            switch_x = rect.x + first_col_width + (switch_col_width - switch_width) // 2
            switch_y = rect.y + (rect.height - switch_height) // 2
            
            # Check if click was within switch bounds
            if (switch_x <= x <= switch_x + switch_width and 
                switch_y <= y <= switch_y + switch_height):
                # Use the gui reference instead of navigating parents
                parent = self.gui
                
                # Get switch name from the first column
                switch_name = self.GetItem(item, 0).GetText()
                
                # Get device ID and current state
                [device_id, _] = parent.devices.get_signal_ids(switch_name)
                device = parent.devices.get_device(device_id)
                current_state = device.switch_state
                
                # Toggle state
                new_state = parent.devices.LOW if current_state == parent.devices.HIGH else parent.devices.HIGH
                
                if parent.devices.set_switch(device_id, new_state):
                    # Update the renderer for this switch
                    switch_theme = {
                        'background': parent.current_theme['list']['background'],
                        'switch_on': parent.current_theme['switch']['on'],
                        'switch_off': parent.current_theme['switch']['off'],
                        'switch_bg': parent.current_theme['switch']['handle']
                    }
                    self.switch_renderers[item] = SwitchRenderer(
                        new_state == parent.devices.HIGH,
                        switch_theme
                    )
                    parent.SetStatusText(f"Toggled {switch_name} to {'HIGH' if new_state == parent.devices.HIGH else 'LOW'}")
                    
                    # Force a refresh to update the switches
                    self.Refresh()
                    
                    # Execute network to propagate changes
                    if parent.network.execute_network():
                        parent.update_display()
                    else:
                        wx.MessageBox("Error: Network oscillating", "Error",
                                    wx.OK | wx.ICON_ERROR)
                else:
                    wx.MessageBox(f"Failed to toggle switch {switch_name}", "Error",
                                wx.OK | wx.ICON_ERROR)
        
        event.Skip()

class SwitchRenderer(wx.ItemAttr):
    """Custom renderer for switch state column to show a toggle switch."""
    def __init__(self, is_on=False, theme=None):
        super().__init__()
        self.is_on = is_on
        self.theme = theme or {
            'background': wx.Colour(240, 240, 240),
            'switch_on': wx.Colour(0, 184, 148),  # Green when ON
            'switch_off': wx.Colour(200, 200, 200),  # Grey when OFF
            'switch_bg': wx.Colour(255, 255, 255)  # White background
        }

    def DrawItem(self, dc, rect, item):
        """Draw the toggle switch."""
        # Set up colors based on state
        switch_color = self.theme['switch_on'] if self.is_on else self.theme['switch_off']
        
        # Calculate switch dimensions - make it slightly larger
        switch_width = min(48, rect.width - 8)  # Max width of 48px, with 4px padding on each side
        switch_height = min(24, rect.height - 8)  # Max height of 24px, with 4px padding
        
        # Center the switch in the cell
        x = rect.x + (rect.width - switch_width) // 2
        y = rect.y + (rect.height - switch_height) // 2
        
        # Draw switch background (rounded rectangle) with thicker border
        dc.SetPen(wx.Pen(switch_color, 2))  # Thicker border
        dc.SetBrush(wx.Brush(switch_color))
        dc.DrawRoundedRectangle(x, y, switch_width, switch_height, switch_height // 2)
        
        # Draw the toggle circle - slightly larger
        circle_size = switch_height - 6  # Slightly smaller than height for padding
        circle_x = x + 3 + (switch_width - circle_size - 6) * (1 if self.is_on else 0)
        circle_y = y + 3
        
        # Add a subtle shadow effect
        shadow_color = wx.Colour(0, 0, 0, 30)  # Semi-transparent black
        dc.SetPen(wx.Pen(shadow_color, 1))
        dc.SetBrush(wx.Brush(shadow_color))
        dc.DrawCircle(circle_x + circle_size // 2 + 1, circle_y + circle_size // 2 + 1, circle_size // 2)
        
        # Draw the main circle
        dc.SetPen(wx.Pen(self.theme['switch_bg'], 2))  # Thicker border for the circle
        dc.SetBrush(wx.Brush(self.theme['switch_bg']))
        dc.DrawCircle(circle_x + circle_size // 2, circle_y + circle_size // 2, circle_size // 2)

class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.

    on_stop_button(self, event): Event handler for when the user clicks the stop
                                button.

    on_reset_button(self, event): Event handler for when the user clicks the reset
                                button.

    on_add_monitor(self, event): Event handler for when the user clicks the add
                                monitor button.

    on_remove_monitor(self, event): Event handler for when the user clicks the
                                remove monitor button.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(1024, 768))
        
        # Store instances
        self.devices = devices
        self.monitors = monitors
        self.network = network
        
        # Add simulation speed settings
        self.speed_settings = {
            'x0.5': 400,  # 800ms
            'x1': 200,  # 400ms
            'x2': 100,  # 200ms
            'x4': 50,  # 100ms
            'x8': 25    # 50ms
        }
        self.current_speed = 'x1'  # Start at normal speed

        # Initialize theme colors
        self.light_theme = {
            'background': wx.Colour(240, 240, 240),
            'text': wx.Colour(0, 0, 0),
            'button': {
                'run': wx.Colour(0, 184, 148),
                'stop': wx.Colour(255, 159, 26),
                'reset': wx.Colour(255, 71, 87)
            },
            'canvas': {
                'background': wx.Colour(255, 255, 255),
                'grid': wx.Colour(220, 220, 220)
            },
            'list': {
                'background': wx.Colour(255, 255, 255),
                'text': wx.Colour(0, 0, 0),
                'header_background': wx.Colour(240, 240, 240),
                'header_text': wx.Colour(0, 0, 0),
                'alternate': wx.Colour(250, 250, 250)
            },
            'static_box': {
                'background': wx.Colour(240, 240, 240),  # Slightly darker than control panel
                'text': wx.Colour(0, 0, 0)
            },
            'switch': {
                'on': wx.Colour(0, 184, 148),  # Green
                'off': wx.Colour(200, 200, 200),  # Grey
                'handle': wx.Colour(255, 255, 255)  # White
            }
        }
        
        self.dark_theme = {
            'background': wx.Colour(32, 33, 36),       # Google Dark Grey
            'text': wx.Colour(232, 234, 237),         # Google Light Grey Text
            'button': {
                'run': wx.Colour(0, 184, 148),        # Green color for run button
                'stop': wx.Colour(234, 179, 8),       # Warm Yellow
                'reset': wx.Colour(234, 67, 53)       # Google Red
            },
            'canvas': {
                'background': wx.Colour(32, 33, 36),  # Same as main background
                'grid': wx.Colour(48, 49, 52)        # Slightly lighter grid lines
            },
            'list': {
                'background': wx.Colour(41, 42, 45),   # Slightly lighter than background
                'text': wx.Colour(232, 234, 237),      # Google Light Grey Text
                'header_background': wx.Colour(35, 36, 39),  # Dark header background
                'header_text': wx.Colour(232, 234, 237),     # Light text for header
                'alternate': wx.Colour(45, 46, 49)     # Alternate row color
            },
            'static_box': {
                'background': wx.Colour(28, 29, 32),   # Slightly darker than control panel
                'text': wx.Colour(232, 234, 237)       # Google Light Grey Text
            },
            'switch': {
                'on': wx.Colour(0, 184, 148),  # Green
                'off': wx.Colour(64, 65, 68),  # Darker grey for dark mode
                'handle': wx.Colour(255, 255, 255)  # White
            }
        }
        
        self.current_theme = self.light_theme
        
        # Add signal color sets for light and dark mode
        self.light_signal_colors = [
            (0.95, 0.65, 0.60),  # Soft Coral Pink (a gentle start to the spectrum)
            (1.00, 0.75, 0.50),  # Soft Peach Orange (a light, warm orange)
            (0.95, 0.80, 0.40),  # Pale Canary Yellow (a delicate, light yellow)
            (0.60, 0.85, 0.60),  # Minty Green (a fresh, light green)
            (0.55, 0.80, 0.85),  # Light Aqua (a soft, airy blue-green)
            (0.60, 0.75, 0.95),  # Powder Blue (a gentle, light blue)
            (0.75, 0.65, 0.90),  # Soft Lavender (a pale, calming purple)
            (0.85, 0.60, 0.80),  # Pale Mauve (a muted, light violet-pink)
        ]
        self.dark_signal_colors = [
            (1.00, 0.05, 0.65),  # Neon Magenta (a vibrant, hot pink to kick off)
            (1.00, 0.10, 0.10),  # Neon Red (a bright, intense red)
            (1.00, 0.50, 0.00),  # Neon Orange (a vivid, fiery orange)
            (1.00, 1.00, 0.00),  # Neon Yellow (a pure, dazzling yellow)
            (0.20, 1.00, 0.20),  # Neon Lime Green (an electric, bright green)
            (0.00, 0.80, 1.00),  # Neon Cyan (a brilliant, striking blue)
            (0.50, 0.20, 1.00),  # Neon Indigo (a deep, electric blue-purple)
            (0.80, 0.00, 1.00),  # Neon Violet (a radiant, intense purple)
        ]
        
        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        
        # File Menu
        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_HELP, "&Help\tF1")
        fileMenu.AppendSeparator()
        fileMenu.Append(wx.ID_EXIT, "E&xit\tAlt+F4")
        menuBar.Append(fileMenu, "&File")
        
        # Theme Menu
        self.themeMenu = wx.Menu()
        self.LIGHT_MODE_ID = wx.NewId()
        self.DARK_MODE_ID = wx.NewId()
        self.light_mode_item = self.themeMenu.AppendRadioItem(self.LIGHT_MODE_ID, "Light Mode")
        self.dark_mode_item = self.themeMenu.AppendRadioItem(self.DARK_MODE_ID, "Dark Mode")
        menuBar.Append(self.themeMenu, "&Theme")
        
        self.SetMenuBar(menuBar)
        
        # Create status bar
        self.CreateStatusBar()
        self.SetStatusText("Ready")
        
        # Create main panel
        main_panel = wx.Panel(self)
        
        # Configure the widgets with better styling
        self.control_panel = wx.Panel(main_panel, style=wx.BORDER_NONE)
        
        # Canvas for drawing signals
        self.canvas = MyGLCanvas(main_panel, devices, monitors)
        self.canvas.signal_colors = self.light_signal_colors  # Set initial signal colors
        
        # Create bold Arial font for box titles
        title_font = wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        
        # Simulation controls
        self.sim_box = wx.StaticBox(self.control_panel, label="Simulation Controls")
        self.sim_box.SetFont(title_font)
        sim_sizer = wx.StaticBoxSizer(self.sim_box, wx.VERTICAL)
        
        # Add speed control at the top
        speed_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.speed_btn = wx.Button(self.control_panel, label=self.current_speed, size=(60, 25))
        speed_label = wx.StaticText(self.control_panel, label="Speed:")
        speed_sizer.Add(speed_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        speed_sizer.Add(self.speed_btn, 0)
        sim_sizer.Add(speed_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        
        # Cycles control
        cycles_label = wx.StaticText(self.control_panel, label="Number of Cycles:")
        self.cycles_spin = wx.SpinCtrl(self.control_panel, value="10", min=1, max=1000)
        
        # Buttons with better styling
        button_style = wx.BORDER_NONE
        self.run_button = wx.Button(self.control_panel, label="▶ Run Simulation", style=button_style)
        self.stop_button = wx.Button(self.control_panel, label="❚❚ Pause", style=button_style)
        self.reset_button = wx.Button(self.control_panel, label="■ Reset", style=button_style)
        
        # Set button colors and style
        self.run_button.SetBackgroundColour(wx.Colour(0, 184, 148))  # Green
        self.stop_button.SetBackgroundColour(wx.Colour(255, 159, 26))  # Orange
        self.reset_button.SetBackgroundColour(wx.Colour(255, 71, 87))  # Red
        
        # Set text color to white for better contrast
        self.run_button.SetForegroundColour(wx.WHITE)
        self.stop_button.SetForegroundColour(wx.WHITE)
        self.reset_button.SetForegroundColour(wx.WHITE)
        
        # Add simulation controls with more padding for better appearance
        sim_sizer.Add(cycles_label, 0, wx.ALL, 5)
        sim_sizer.Add(self.cycles_spin, 0, wx.EXPAND | wx.ALL, 5)
        sim_sizer.Add(self.run_button, 0, wx.EXPAND | wx.ALL, 8)
        sim_sizer.Add(self.stop_button, 0, wx.EXPAND | wx.ALL, 8)
        sim_sizer.Add(self.reset_button, 0, wx.EXPAND | wx.ALL, 8)

        # Add switch controls section
        self.switch_box = wx.StaticBox(self.control_panel, label="Switch Controls")
        self.switch_box.SetFont(title_font)
        switch_sizer = wx.StaticBoxSizer(self.switch_box, wx.VERTICAL)
        
        # Create a list control for switches
        self.switch_list = CustomListCtrl(self.control_panel, style=wx.LC_REPORT, gui=self)
        self.switch_list.InsertColumn(0, "Switch", width=150)  # Switch name column
        self.switch_list.InsertColumn(1, "State", width=80)  # State column
        
        # Enable multiple selection
        current_style = self.switch_list.GetWindowStyle()
        self.switch_list.SetWindowStyle(current_style | wx.LC_SINGLE_SEL)
        self.switch_list.SetWindowStyle(current_style & ~wx.LC_SINGLE_SEL)
        
        # Add toggle buttons for all on/off
        self.all_on_btn = wx.Button(self.control_panel, label="All On")
        self.all_off_btn = wx.Button(self.control_panel, label="All Off")
        self.all_on_btn.Enable(True)
        self.all_off_btn.Enable(True)
        
        # Add components to switch sizer
        switch_sizer.Add(self.switch_list, 1, wx.EXPAND | wx.ALL, 5)
        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        btn_row.Add(self.all_on_btn, 1, wx.EXPAND | wx.RIGHT, 5)
        btn_row.Add(self.all_off_btn, 1, wx.EXPAND)
        switch_sizer.Add(btn_row, 0, wx.EXPAND | wx.ALL, 5)

        # Monitor controls
        self.monitor_box = wx.StaticBox(self.control_panel, label="Monitors")
        self.monitor_box.SetFont(title_font)
        monitor_sizer = wx.StaticBoxSizer(self.monitor_box, wx.VERTICAL)
        
        # Create monitor list with proper columns - only one set of columns
        self.monitor_list = CustomListCtrl(self.control_panel, style=wx.LC_REPORT, gui=self)
        self.monitor_list.InsertColumn(0, "", width=20)   # Narrow column for color indicator
        self.monitor_list.InsertColumn(1, "Signal", width=140)  # Device name column
        self.monitor_list.InsertColumn(2, "State", width=55)  # State column, narrower
        self.monitor_list.InsertColumn(3, "", width=45)  # Zap button column, even wider for scroll bar
        
        # Set column widths
        self.monitor_list.SetColumnWidth(0, 20)   # Narrow column for color indicator
        self.monitor_list.SetColumnWidth(1, 140)  # Fixed width for device name
        self.monitor_list.SetColumnWidth(2, 55)   # Fixed width for state, narrower
        self.monitor_list.SetColumnWidth(3, 45)   # Fixed width for zap button, even wider for scroll bar
        
        # Enable multiple selection
        current_style = self.monitor_list.GetWindowStyle()
        self.monitor_list.SetWindowStyle(current_style | wx.LC_SINGLE_SEL)
        self.monitor_list.SetWindowStyle(current_style & ~wx.LC_SINGLE_SEL)
        
        # Add/Remove monitor buttons
        monitor_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add_monitor_btn = wx.Button(self.control_panel, label="Add Monitor/s")
        self.remove_monitor_btn = wx.Button(self.control_panel, label="Zap All")
        monitor_btn_sizer.Add(self.add_monitor_btn, 1, wx.RIGHT, 5)
        monitor_btn_sizer.Add(self.remove_monitor_btn, 1)
        
        # Add components to monitor sizer
        monitor_sizer.Add(self.monitor_list, 1, wx.EXPAND | wx.ALL, 5)
        monitor_sizer.Add(monitor_btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Bind selection event for color update
        self.monitor_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_monitor_selected)
        self.monitor_list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_monitor_selected)

        # Build the control panel
        control_sizer = wx.BoxSizer(wx.VERTICAL)
        control_sizer.Add(sim_sizer, 0, wx.EXPAND | wx.ALL, 5)
        control_sizer.Add(switch_sizer, 0, wx.EXPAND | wx.ALL, 5)
        control_sizer.Add(monitor_sizer, 1, wx.EXPAND | wx.ALL, 5)
        self.control_panel.SetSizer(control_sizer)
        
        # Build the main layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.control_panel, 0, wx.EXPAND | wx.ALL, 5)
        
        main_panel.SetSizer(main_sizer)
        
        # Set the main panel as the top-level sizer
        top_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(main_panel, 1, wx.EXPAND)
        self.SetSizer(top_sizer)
        
        # Bind events
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.Bind(wx.EVT_MENU, self.on_light_mode, id=self.LIGHT_MODE_ID)
        self.Bind(wx.EVT_MENU, self.on_dark_mode, id=self.DARK_MODE_ID)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.stop_button.Bind(wx.EVT_BUTTON, self.on_stop_button)
        self.reset_button.Bind(wx.EVT_BUTTON, self.on_reset_button)
        self.add_monitor_btn.Bind(wx.EVT_BUTTON, self.on_add_monitor)
        self.remove_monitor_btn.Bind(wx.EVT_BUTTON, self.on_remove_monitor)
        self.all_on_btn.Bind(wx.EVT_BUTTON, self.on_all_on)
        self.all_off_btn.Bind(wx.EVT_BUTTON, self.on_all_off)
        self.speed_btn.Bind(wx.EVT_BUTTON, self.on_speed_button)
        
        # Add accelerator table for F1 (Help), Alt+F4 (Exit), and Spacebar (Run/Pause)
        self.SPACEBAR_ID = wx.NewId()
        accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL, wx.WXK_F1, wx.ID_HELP),
            (wx.ACCEL_ALT, wx.WXK_F4, wx.ID_EXIT),
            (wx.ACCEL_NORMAL, wx.WXK_SPACE, self.SPACEBAR_ID),  # Spacebar for run/pause
        ])
        self.SetAcceleratorTable(accel_tbl)

        # Bind spacebar to run/pause
        self.Bind(wx.EVT_MENU, self.on_spacebar_toggle, id=self.SPACEBAR_ID)
        
        # Initialize lists
        self.update_switch_list()
        self.update_monitor_list(show_states=False)  # Don't show states on startup
        
        # Set minimum window size
        self.SetMinSize((800, 600))
        
        # Center the window
        self.Centre()

        # Add simulation state variables
        self.is_running = False
        self.current_cycle = 0
        self.simulation_timer = wx.Timer(self)
        
        # Bind the timer event
        self.Bind(wx.EVT_TIMER, self.on_simulation_tick, self.simulation_timer)

        # Apply initial theme
        self.apply_theme()

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by:\nAyoife Dada\nNarmeephan Arunthavarajah\nRaghavendra Narayan Rao\n2025",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)
        if Id == wx.ID_HELP:
            wx.MessageBox(
                """
How to Use the Logic Simulator GUI

---

**Keybinds**
- **F1:** Show this Help window
- **Alt+F4:** Exit the application
- **Spacebar:** Run/Pause the simulation

**Simulation Controls**
- **Number of Cycles:** Set how many cycles to run the simulation for.
- **▶ Run Simulation:** Start the simulation for the chosen number of cycles.
- **❚❚ Pause:** Pause the simulation at any time.
- **■ Reset:** Reset the simulation and clear all monitor data.
- **Speed:** Click to cycle through simulation speeds (x0.5, x1, x2, x4, x8).

**Switch Controls**
- Toggle individual switches by clicking the switch in the list.
- Use **All On** or **All Off** to set all switches high or low.

**Monitors**
- Add a monitor to track a signal by clicking **Add Monitor** and selecting a signal.
- Use **Add All** in the dialog to monitor all available signals.
- Remove a monitor by clicking the ✕ button next to it, or **Zap All** to remove all monitors.
- The monitor list shows the current state of each monitored signal.

**Signal Display Canvas**
- The main area shows waveforms for all monitored signals.
- **Pan:** Click and drag to move the view.
- **Zoom:** Use the mouse wheel to zoom in/out.
- Signal colors match the color bars in the monitor list.

**Themes**
- Switch between Light and Dark mode from the Theme menu.

**Status Bar**
- The status bar at the bottom shows helpful messages and feedback.

For more help, see the project documentation or contact the authors.
                """,
                "Help: How to Use the Logic Simulator",
                wx.ICON_INFORMATION | wx.OK
            )

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.cycles_spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        if not self.is_running:
            cycles = self.cycles_spin.GetValue()
            self.start_simulation(cycles)
        else:
            self.SetStatusText("Simulation already running")
            
    def on_stop_button(self, event):
        """Handle the event when the user clicks the stop button."""
        self.stop_simulation()
        self.SetStatusText("Simulation stopped")
        
    def on_reset_button(self, event):
        """Handle the event when the user clicks the reset button."""
        self.reset_simulation()
        self.SetStatusText("Simulation reset")
        
    def start_simulation(self, num_cycles):
        """Start running the simulation for the specified number of cycles."""
        if not self.is_running:
            self.is_running = True
            self.target_cycles = num_cycles
            self.current_cycle = 0
            
            # Enable/disable appropriate buttons
            self.run_button.Disable()
            self.stop_button.Enable()
            self.reset_button.Disable()
            self.cycles_spin.Disable()
            
            # Start the simulation timer with current speed setting
            self.simulation_timer.Start(self.speed_settings[self.current_speed])
            self.SetStatusText(f"Running simulation for {num_cycles} cycles...")
            
    def stop_simulation(self):
        """Stop the currently running simulation."""
        if self.is_running:
            self.simulation_timer.Stop()
            self.is_running = False
            self.run_button.Enable()
            self.stop_button.Disable()
            self.reset_button.Enable()
            self.cycles_spin.Enable()
            
    def reset_simulation(self):
        """Reset the simulation to its initial state."""
        self.stop_simulation()
        self.current_cycle = 0
        
        # Reset all monitors
        self.monitors.reset_monitors()
        
        # Update the monitor list without states
        self.update_monitor_list(show_states=False)
        
        # Reset the canvas
        self.canvas.signal_data = {}  # Clear existing signals
        self.canvas.render()
        
        self.SetStatusText("Simulation reset")
        
    def on_simulation_tick(self, event):
        """Handle a single simulation step."""
        if self.is_running and self.current_cycle < self.target_cycles:
            # Execute one cycle of the simulation
            if self.execute_cycle():
                self.current_cycle += 1
                self.update_display()
                
                if self.current_cycle >= self.target_cycles:
                    self.stop_simulation()
                    self.SetStatusText("Simulation completed")
            else:
                self.stop_simulation()
                self.SetStatusText("Simulation error occurred")
                
    def execute_cycle(self):
        """Execute a single cycle of the simulation."""
        try:
            # Execute the network for one cycle
            self.network.execute_network()
            # Record the signals in monitors
            self.monitors.record_signals()
            return True
        except Exception as e:
            wx.MessageBox(f"Error during simulation: {str(e)}", 
                         "Simulation Error",
                         wx.OK | wx.ICON_ERROR)
            return False
            
    def update_display(self):
        """Update the display with current simulation state."""
        # Update the monitor list with states since we're running
        self.update_monitor_list(show_states=True)
        
        # Update the canvas with new signal data
        self.update_signal_display()
        
    def update_monitor_list(self, show_states=False):
        """Update the monitor list with current monitor states."""
        # Clean up existing zap buttons
        if hasattr(self.monitor_list, 'zap_buttons'):
            for button in self.monitor_list.zap_buttons.values():
                button.Destroy()
            self.monitor_list.zap_buttons = {}
            
        self.monitor_list.DeleteAllItems()
        
        # Get monitored signals and maintain original order from monitors dictionary
        monitored_signals = []
        for i, (device_id, output_id) in enumerate(self.monitors.monitors_dictionary):
            signal_name = self.devices.get_signal_name(device_id, output_id)
            # Store original index to maintain color consistency
            monitored_signals.append((signal_name, device_id, output_id, i))
        
        # Sort signals alphabetically but keep track of original index
        monitored_signals.sort(key=lambda x: x[0])  # Sort by signal name
        
        # Add to list
        for list_index, (signal_name, device_id, output_id, original_index) in enumerate(monitored_signals):
            # Get color based on index
            color_index = original_index % len(self.canvas.signal_colors)
            color = self.canvas.signal_colors[color_index]
            wx_color = wx.Colour(int(color[0] * 255), int(color[1] * 255), int(color[2] * 255))
            
            # Add items with default colors first
            index = self.monitor_list.InsertItem(list_index, "║")
            self.monitor_list.SetItem(index, 1, signal_name)
            
            # Set the background color based on alternating rows
            if list_index % 2 == 0:
                self.monitor_list.SetItemBackgroundColour(index, self.current_theme['list']['background'])
            else:
                self.monitor_list.SetItemBackgroundColour(index, self.current_theme['list']['alternate'])
            
            # Then set color only for the vertical bar
            item = self.monitor_list.GetItem(index, 0)
            item.SetTextColour(wx_color)
            self.monitor_list.SetItem(item)
            
            # Clear any text colors first
            for col in [1,2,3]:  # For all columns including zap button
                for i in range(self.monitor_list.GetItemCount()):
                    item = self.monitor_list.GetItem(i, col)
                    item.SetTextColour(wx.NullColour)  # Reset to default
                    self.monitor_list.SetItem(item)

            # Only show states if we're running
            if show_states:
                # Get current signal value
                current_signal = self.network.get_output_signal(device_id, output_id)
                if current_signal is not None:
                    if current_signal == self.devices.HIGH:
                        state = "HIGH"
                    elif current_signal == self.devices.LOW:
                        state = "LOW"
                    elif current_signal == self.devices.RISING:
                        state = "RISING"
                    elif current_signal == self.devices.FALLING:
                        state = "FALLING"
                    else:
                        state = str(current_signal)
                    self.monitor_list.SetItem(index, 2, state)
            
            # Add zap button with adjusted position to account for scroll bar
            zap_button = wx.Button(self.monitor_list, id=index, label="✕", size=(25, 20), style=wx.NO_BORDER)
            zap_button.SetBackgroundColour(self.current_theme['button']['reset'])  # Red color
            zap_button.SetForegroundColour(wx.BLACK)  # Black text for contrast
            bold_font = zap_button.GetFont()
            bold_font.SetWeight(wx.FONTWEIGHT_BOLD)
            zap_button.SetFont(bold_font)
            zap_button.Bind(wx.EVT_BUTTON, lambda evt, signal=signal_name: self.on_zap_button(evt, signal))
            
            # Get the item rect for the zap button column
            rect = self.monitor_list.GetItemRect(index, wx.LIST_RECT_BOUNDS)
            col_width = self.monitor_list.GetColumnWidth(3)
            button_x = rect.x + self.monitor_list.GetColumnWidth(0) + self.monitor_list.GetColumnWidth(1) + self.monitor_list.GetColumnWidth(2)
            zap_button.SetPosition((button_x + 5, rect.y + 2))
            
            # Store the button reference to prevent garbage collection
            if not hasattr(self.monitor_list, 'zap_buttons'):
                self.monitor_list.zap_buttons = {}
            self.monitor_list.zap_buttons[index] = zap_button
            
        # Adjust column widths
        self.monitor_list.SetColumnWidth(0, 20)   # Narrow column for color indicator
        self.monitor_list.SetColumnWidth(1, 140)  # Fixed width for device name
        self.monitor_list.SetColumnWidth(2, 55)   # Fixed width for state, narrower
        self.monitor_list.SetColumnWidth(3, 45)   # Fixed width for zap button, even wider for scroll bar

    def on_zap_button(self, event, signal_name):
        """Handle clicking the zap button for a specific monitor."""
        # Find the device and output IDs for this signal
        for (device_id, output_id) in list(self.monitors.monitors_dictionary.keys()):
            if signal_name == self.devices.get_signal_name(device_id, output_id):
                # Remove the monitor
                if self.monitors.remove_monitor(device_id, output_id):
                    self.SetStatusText(f"Zapped monitor for {signal_name}")
                else:
                    wx.MessageBox(f"Failed to zap monitor {signal_name}", "Error",
                                wx.OK | wx.ICON_ERROR)
                break
                
        # Update display after monitor is removed
        self.update_monitor_list(show_states=self.is_running)
        self.update_signal_display()

    def update_signal_display(self):
        """Update the signal display on the canvas."""
        signal_data = {}
        
        # Get all monitored signals
        for (device_id, output_id), signal_list in self.monitors.monitors_dictionary.items():
            signal_name = self.devices.get_signal_name(device_id, output_id)
            # Convert signal values to binary (0 or 1) or None for BLANK
            binary_signals = []
            for signal in signal_list:
                if signal == self.devices.HIGH or signal == self.devices.RISING:
                    binary_signals.append(1)
                elif signal == self.devices.LOW or signal == self.devices.FALLING:
                    binary_signals.append(0)
                elif signal == self.devices.BLANK:
                    binary_signals.append(None)  # Use None to represent blank/no signal
                else:
                    # For any other signal state, treat as blank
                    binary_signals.append(None)
            signal_data[signal_name] = binary_signals
            
        # Update the canvas
        self.canvas.signal_data = signal_data
        self.canvas.render()
        
    def on_add_monitor(self, event):
        """Handle adding a new monitor."""
        # Create a dialog to select device and output
        dialog = wx.Dialog(self, title="Add Monitor", size=(300, 150))
        dialog_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Get all available signals
        _, non_monitored = self.monitors.get_signal_names()
        
        if not non_monitored:
            wx.MessageBox("No more signals available to monitor", "Information",
                         wx.OK | wx.ICON_INFORMATION)
            dialog.Destroy()
            return
        
        # Add signal selection
        signal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        signal_label = wx.StaticText(dialog, label="Signal:")
        signal_choice = wx.Choice(dialog, choices=non_monitored)
        signal_sizer.Add(signal_label, 0, wx.ALL | wx.CENTER, 5)
        signal_sizer.Add(signal_choice, 1, wx.ALL | wx.EXPAND, 5)
        
        # Add buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(dialog, wx.ID_OK, "Add")
        add_all_button = wx.Button(dialog, wx.NewId(), "Add All")
        cancel_button = wx.Button(dialog, wx.ID_CANCEL, "Cancel")
        
        button_sizer.Add(ok_button, 1, wx.ALL, 5)
        button_sizer.Add(add_all_button, 1, wx.ALL, 5)
        button_sizer.Add(cancel_button, 1, wx.ALL, 5)
        
        # Build dialog layout
        dialog_sizer.Add(signal_sizer, 0, wx.ALL | wx.EXPAND, 5)
        dialog_sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER, 5)
        
        dialog.SetSizer(dialog_sizer)
        
        # Enable Add button only when a signal is selected
        ok_button.Enable(False)
        signal_choice.Bind(wx.EVT_CHOICE, lambda evt: ok_button.Enable(evt.GetSelection() != -1))
        
        # Bind Add All button
        add_all_button.Bind(wx.EVT_BUTTON, lambda evt: self.on_add_all_monitors(evt, dialog))
        
        if dialog.ShowModal() == wx.ID_OK and signal_choice.GetSelection() != -1:
            signal_name = signal_choice.GetString(signal_choice.GetSelection())
            self.add_single_monitor(signal_name)
                
        dialog.Destroy()

    def add_single_monitor(self, signal_name):
        """Add a single monitor for the given signal name."""
        # Get current signal history length from any existing monitor
        current_cycles = 0
        if self.monitors.monitors_dictionary:
            # Get the length of signal history from the first monitor
            first_monitor = next(iter(self.monitors.monitors_dictionary.values()))
            current_cycles = len(first_monitor)
        
        # Find the device and output IDs for this signal
        for device_id in self.devices.find_devices():
            device = self.devices.get_device(device_id)
            for output_id in device.outputs:
                if signal_name == self.devices.get_signal_name(device_id, output_id):
                    # Add the monitor with current signal history length
                    if self.monitors.make_monitor(device_id, output_id, current_cycles) == self.monitors.NO_ERROR:
                        self.update_monitor_list(show_states=self.is_running)  # Update the list immediately
                        self.update_signal_display()  # Update the canvas
                        self.SetStatusText(f"Added monitor for {signal_name}")
                        return True
                    else:
                        wx.MessageBox(f"Failed to add monitor for {signal_name}", "Error",
                                    wx.OK | wx.ICON_ERROR)
                        return False
        return False

    def on_add_all_monitors(self, event, dialog):
        """Handle adding all available monitors."""
        _, non_monitored = self.monitors.get_signal_names()
        
        if not non_monitored:
            wx.MessageBox("No signals available to monitor", "Error",
                         wx.OK | wx.ICON_ERROR)
            return
            
        # Ask for confirmation
        dlg = wx.MessageDialog(dialog, 
                             f"Add all {len(non_monitored)} available signals?",
                             "Confirm Add All",
                             wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        
        if dlg.ShowModal() == wx.ID_YES:
            success_count = 0
            for signal_name in non_monitored:
                if self.add_single_monitor(signal_name):
                    success_count += 1
            
            self.SetStatusText(f"Added {success_count} monitors")
            dialog.EndModal(wx.ID_CANCEL)  # Close the add monitor dialog
            
        dlg.Destroy()

    def on_remove_monitor(self, event):
        """Handle removing all monitors."""
        if not self.monitors.monitors_dictionary:
            wx.MessageBox("No monitors to zap", "Error",
                         wx.OK | wx.ICON_ERROR)
            return
            
        # Ask for confirmation
        dlg = wx.MessageDialog(None, 
                             "Are you sure you want to zap all monitors?",
                             "Confirm Zap All",
                             wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        
        if dlg.ShowModal() == wx.ID_YES:
            # Get all monitors before removing them
            monitor_count = len(self.monitors.monitors_dictionary)
            
            # Remove all monitors
            for (device_id, output_id) in list(self.monitors.monitors_dictionary.keys()):
                self.monitors.remove_monitor(device_id, output_id)
                    
            # Update display after all monitors are removed
            self.update_monitor_list(show_states=self.is_running)
            self.update_signal_display()
            
            self.SetStatusText(f"Zapped all {monitor_count} monitors")
        
        dlg.Destroy()

    def update_switch_list(self):
        """Update the list of switches and their states."""
        self.switch_list.DeleteAllItems()
        self.switch_list.switch_renderers.clear()
        
        # Find all switch devices
        switch_ids = self.devices.find_devices(self.devices.SWITCH)
        
        for i, switch_id in enumerate(switch_ids):
            # Get switch name
            switch_name = self.devices.get_signal_name(switch_id, None)
            
            # Get switch state
            device = self.devices.get_device(switch_id)
            is_high = device.switch_state == self.devices.HIGH
            
            # Add to list
            index = self.switch_list.InsertItem(i, switch_name)
            self.switch_list.SetItem(index, 1, "")  # Empty string as we'll draw custom switch
            
            # Set text color based on current theme
            item = self.switch_list.GetItem(index, 0)
            item.SetTextColour(self.current_theme['text'])
            self.switch_list.SetItem(item)
            
            # Create and store renderer for this switch with current theme colors
            switch_theme = {
                'background': self.current_theme['list']['background'],
                'switch_on': self.current_theme['switch']['on'],
                'switch_off': self.current_theme['switch']['off'],
                'switch_bg': self.current_theme['switch']['handle']
            }
            renderer = SwitchRenderer(is_high, switch_theme)
            self.switch_list.switch_renderers[index] = renderer
            
            # Force background color update for this row
            self.switch_list.update_item_color(index)
        
        # Adjust column widths
        self.switch_list.SetColumnWidth(0, 150)  # Fixed width for name column
        self.switch_list.SetColumnWidth(1, 80)   # Fixed width for switch column
        
        # Force a refresh to update the switches
        self.switch_list.Refresh()
        wx.CallAfter(self.switch_list.draw_all_switches)

    def on_all_on(self, event):
        """Set all switches to HIGH."""
        switch_ids = self.devices.find_devices(self.devices.SWITCH)
        for switch_id in switch_ids:
            self.devices.set_switch(switch_id, self.devices.HIGH)
        self.update_switch_list()
        if self.network.execute_network():
            self.update_display()
        else:
            wx.MessageBox("Error: Network oscillating", "Error", wx.OK | wx.ICON_ERROR)
        self.SetStatusText("All switches set to ON")

    def on_all_off(self, event):
        """Set all switches to LOW."""
        switch_ids = self.devices.find_devices(self.devices.SWITCH)
        for switch_id in switch_ids:
            self.devices.set_switch(switch_id, self.devices.LOW)
        self.update_switch_list()
        if self.network.execute_network():
            self.update_display()
        else:
            wx.MessageBox("Error: Network oscillating", "Error", wx.OK | wx.ICON_ERROR)
        self.SetStatusText("All switches set to OFF")

    def on_speed_button(self, event):
        """Handle the speed button click to cycle through simulation speeds."""
        speeds = list(self.speed_settings.keys())
        current_index = speeds.index(self.current_speed)
        next_index = (current_index + 1) % len(speeds)
        self.current_speed = speeds[next_index]
        self.speed_btn.SetLabel(self.current_speed)
        
        # Update timer if simulation is running
        if self.is_running:
            self.simulation_timer.Stop()
            self.simulation_timer.Start(self.speed_settings[self.current_speed])

    def apply_theme(self):
        """Apply the current theme to all widgets."""
        # Apply to main window and panel backgrounds
        self.SetBackgroundColour(self.current_theme['background'])
        
        # Apply to control panel and its background
        self.control_panel.SetBackgroundColour(self.current_theme['background'])
        
        # Apply to buttons with consistent white text
        button_text_color = wx.Colour(255, 255, 255)
        
        # Main control buttons
        self.run_button.SetBackgroundColour(self.current_theme['button']['run'])
        self.stop_button.SetBackgroundColour(self.current_theme['button']['stop'])
        self.reset_button.SetBackgroundColour(self.current_theme['button']['reset'])
        
        for btn in [self.run_button, self.stop_button, self.reset_button]:
            btn.SetForegroundColour(button_text_color)
        
        # Secondary buttons with theme-based background
        secondary_buttons = [
            self.all_on_btn,
            self.all_off_btn,
            self.add_monitor_btn,
            self.remove_monitor_btn,
            self.speed_btn
        ]
        
        for btn in secondary_buttons:
            btn.SetBackgroundColour(self.current_theme['list']['background'])
            btn.SetForegroundColour(self.current_theme['text'])
        
        # Apply to lists - only set background colors, let text inherit from theme
        for lst in [self.switch_list, self.monitor_list]:
            lst.set_colors(
                self.current_theme['list']['background'],
                self.current_theme['list']['alternate']
            )
            lst.SetBackgroundColour(self.current_theme['list']['background'])
            
            # Update text color for all items in the list
            if lst == self.switch_list:
                for i in range(lst.GetItemCount()):
                    item = lst.GetItem(i, 0)  # Get first column
                    item.SetTextColour(self.current_theme['text'])
                    lst.SetItem(item)
                # --- Begin: Update switch renderers with new theme ---
                for index, renderer in lst.switch_renderers.items():
                    # Get current state
                    is_high = renderer.is_on
                    switch_theme = {
                        'background': self.current_theme['list']['background'],
                        'switch_on': self.current_theme['switch']['on'],
                        'switch_off': self.current_theme['switch']['off'],
                        'switch_bg': self.current_theme['switch']['handle']
                    }
                    lst.switch_renderers[index] = SwitchRenderer(is_high, switch_theme)
                lst.Refresh()
                wx.CallAfter(lst.draw_all_switches)
                # --- End: Update switch renderers with new theme ---
        
        # Apply to static boxes and their backgrounds
        for box in [self.sim_box, self.switch_box, self.monitor_box]:
            box.SetBackgroundColour(self.current_theme['static_box']['background'])
            box.SetForegroundColour(self.current_theme['text'])
            # Update the label color
            box.SetLabel(box.GetLabel())  # This triggers a label refresh
            
            # Force the label to update its color
            label = box.GetLabel()
            box.SetLabel("")  # Clear the label
            box.SetLabel(label)  # Set it back
        
        # Apply to spin control and its text
        self.cycles_spin.SetBackgroundColour(self.current_theme['list']['background'])
        self.cycles_spin.SetForegroundColour(self.current_theme['text'])
        
        # Apply to all static text controls in the panel
        for child in self.control_panel.GetChildren():
            if isinstance(child, wx.StaticText):
                child.SetForegroundColour(self.current_theme['text'])
        
        # Update canvas colors and text colors
        self.canvas.background_color = (
            self.current_theme['canvas']['background'].Red() / 255.0,
            self.current_theme['canvas']['background'].Green() / 255.0,
            self.current_theme['canvas']['background'].Blue() / 255.0
        )
        self.canvas.grid_color = (
            self.current_theme['canvas']['grid'].Red() / 255.0,
            self.current_theme['canvas']['grid'].Green() / 255.0,
            self.current_theme['canvas']['grid'].Blue() / 255.0
        )
        # Set text color for canvas
        self.canvas.text_color = (
            self.current_theme['text'].Red() / 255.0,
            self.current_theme['text'].Green() / 255.0,
            self.current_theme['text'].Blue() / 255.0
        )
        # Set signal colors based on theme
        if self.current_theme == self.dark_theme:
            self.canvas.signal_colors = self.dark_signal_colors
        else:
            self.canvas.signal_colors = self.light_signal_colors
        self.canvas.render()  # Force canvas redraw to update signal colors
        self.update_monitor_list(show_states=self.is_running)  # Refresh monitor table colors
        
        # Refresh all widgets
        self.control_panel.Refresh()
        self.canvas.render()
        self.Update()  # Ensure the frame updates completely

    def on_light_mode(self, event):
        """Handle switching to light mode."""
        self.current_theme = self.light_theme
        self.apply_theme()
        self.SetStatusText("Switched to Light Mode")

    def on_dark_mode(self, event):
        """Handle switching to dark mode."""
        self.current_theme = self.dark_theme
        self.apply_theme()
        self.SetStatusText("Switched to Dark Mode")

    def on_monitor_selected(self, event):
        """Handle monitor selection event."""
        # Get the selected item
        index = event.GetIndex()
        if index != -1:
            # Enable zap button when monitors are selected
            self.remove_monitor_btn.Enable(self.monitor_list.GetSelectedItemCount() > 0)
        event.Skip()

    def on_spacebar_toggle(self, event):
        """Toggle simulation run/pause with spacebar."""
        if self.is_running:
            self.on_stop_button(None)
        else:
            self.on_run_button(None)
