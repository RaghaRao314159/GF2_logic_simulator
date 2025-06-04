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
from OpenGL import GL, GLUT

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
        self.grid_color = (0.9, 0.9, 0.9)  # Lighter grey
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
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, text=""):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        
        # Enable line smoothing for better appearance
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
        
        # Draw grid
        self.draw_grid()
        
        # Draw time axis
        self.draw_time_axis()
        
        # Draw signals
        self.draw_signals()
        
        # Draw signal names
        self.draw_signal_names()

        # Render any status text
        if text:
            self.render_text(text, 10, 10)

        GL.glFlush()
        self.SwapBuffers()

    def draw_grid(self):
        """Draw the background grid."""
        size = self.GetClientSize()
        GL.glColor3f(*self.grid_color)
        GL.glLineWidth(self.grid_line_width)
        GL.glBegin(GL.GL_LINES)
        
        # Calculate the maximum number of time units to display - either 50 or the length of the longest signal trace
        max_time_units = max(50, max((len(signal_list) for signal_list in self.signal_data.values()), default=0))
        num_signals = len(self.signal_data)
        total_height = max((num_signals + 1) * self.signal_height, size.height)
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
            
            GL.glBegin(GL.GL_LINE_STRIP)
            
            for t, value in enumerate(values):
                x = t * self.time_unit_width
                y = y_base + (self.signal_height * 0.8 if value else self.signal_height * 0.2)
                
                # Draw vertical line if value changed
                if value != last_value:
                    GL.glVertex2f(x, y_base + (self.signal_height * 0.2))
                    GL.glVertex2f(x, y_base + (self.signal_height * 0.8))
                
                GL.glVertex2f(x, y)
                GL.glVertex2f(x + self.time_unit_width, y)
                
                last_value = value
            
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
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))


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
            'x1': 400,  # 400ms
            'x2': 200,  # 200ms
            'x4': 100,  # 100ms
            'x8': 50    # 50ms
        }
        self.current_speed = 'x1'  # Start at slowest speed

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
        
        self.SetMenuBar(menuBar)

        # Create status bar
        self.CreateStatusBar()
        self.SetStatusText("Ready")

        # Create main panel
        main_panel = wx.Panel(self)
        
        # Configure the widgets with better styling
        control_panel = wx.Panel(main_panel, style=wx.BORDER_THEME)
        # Colour of the control panel set to light grey
        control_panel.SetBackgroundColour(wx.Colour(240, 240, 240))
        
        # Canvas for drawing signals
        self.canvas = MyGLCanvas(main_panel, devices, monitors)
        
        # Simulation controls
        sim_box = wx.StaticBox(control_panel, label="Simulation Controls")
        sim_sizer = wx.StaticBoxSizer(sim_box, wx.VERTICAL)
        
        # Add speed control at the top
        speed_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.speed_btn = wx.Button(control_panel, label=self.current_speed, size=(60, 25))
        speed_label = wx.StaticText(control_panel, label="Speed:")
        speed_sizer.Add(speed_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        speed_sizer.Add(self.speed_btn, 0)
        sim_sizer.Add(speed_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        
        # Cycles control
        cycles_label = wx.StaticText(control_panel, label="Number of Cycles:")
        self.cycles_spin = wx.SpinCtrl(control_panel, value="10", min=1, max=1000)
        
        # Buttons with better styling
        self.run_button = wx.Button(control_panel, label="Run Simulation")
        self.stop_button = wx.Button(control_panel, label="Stop")
        self.reset_button = wx.Button(control_panel, label="Reset")
        
        # Add simulation controls
        sim_sizer.Add(cycles_label, 0, wx.ALL, 5)
        sim_sizer.Add(self.cycles_spin, 0, wx.EXPAND | wx.ALL, 5)
        sim_sizer.Add(self.run_button, 0, wx.EXPAND | wx.ALL, 5)
        sim_sizer.Add(self.stop_button, 0, wx.EXPAND | wx.ALL, 5)
        sim_sizer.Add(self.reset_button, 0, wx.EXPAND | wx.ALL, 5)

        # Add switch controls section
        switch_box = wx.StaticBox(control_panel, label="Switch Controls")
        switch_sizer = wx.StaticBoxSizer(switch_box, wx.VERTICAL)
        
        # Create a list control for switches
        self.switch_list = wx.ListCtrl(control_panel, style=wx.LC_REPORT)
        self.switch_list.InsertColumn(0, "Switch")
        self.switch_list.InsertColumn(1, "State")
        # Enable multiple selection
        current_style = self.switch_list.GetWindowStyle()
        self.switch_list.SetWindowStyle(current_style | wx.LC_SINGLE_SEL)
        self.switch_list.SetWindowStyle(current_style & ~wx.LC_SINGLE_SEL)
        
        # Add toggle button
        self.toggle_switch_btn = wx.Button(control_panel, label="Toggle Selected")
        self.toggle_switch_btn.Disable()  # Initially disabled until switches are selected
        
        # Add components to switch sizer
        switch_sizer.Add(self.switch_list, 1, wx.EXPAND | wx.ALL, 5)
        switch_sizer.Add(self.toggle_switch_btn, 0, wx.EXPAND | wx.ALL, 5)

        # Monitor controls
        monitor_box = wx.StaticBox(control_panel, label="Monitors")
        monitor_sizer = wx.StaticBoxSizer(monitor_box, wx.VERTICAL)
        
        self.monitor_list = wx.ListCtrl(control_panel, style=wx.LC_REPORT)
        self.monitor_list.InsertColumn(0, "Device")
        self.monitor_list.InsertColumn(1, "Output")
        self.monitor_list.InsertColumn(2, "State")
        # Enable multiple selection
        current_style = self.monitor_list.GetWindowStyle()
        self.monitor_list.SetWindowStyle(current_style | wx.LC_SINGLE_SEL)
        self.monitor_list.SetWindowStyle(current_style & ~wx.LC_SINGLE_SEL)
        
        # Add/Remove monitor buttons
        monitor_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add_monitor_btn = wx.Button(control_panel, label="Add Monitor")
        self.remove_monitor_btn = wx.Button(control_panel, label="Zap Monitor")
        monitor_btn_sizer.Add(self.add_monitor_btn, 1, wx.RIGHT, 5)
        monitor_btn_sizer.Add(self.remove_monitor_btn, 1)
        monitor_sizer.Add(self.monitor_list, 1, wx.EXPAND | wx.ALL, 5)
        monitor_sizer.Add(monitor_btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Build the control panel
        control_sizer = wx.BoxSizer(wx.VERTICAL)
        control_sizer.Add(sim_sizer, 0, wx.EXPAND | wx.ALL, 5)
        control_sizer.Add(switch_sizer, 0, wx.EXPAND | wx.ALL, 5)
        control_sizer.Add(monitor_sizer, 1, wx.EXPAND | wx.ALL, 5)
        control_panel.SetSizer(control_sizer)
        
        # Build the main layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(control_panel, 0, wx.EXPAND | wx.ALL, 5)
        
        main_panel.SetSizer(main_sizer)
        
        # Set the main panel as the top-level sizer
        top_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(main_panel, 1, wx.EXPAND)
        self.SetSizer(top_sizer)
        
        # Bind events
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.stop_button.Bind(wx.EVT_BUTTON, self.on_stop_button)
        self.reset_button.Bind(wx.EVT_BUTTON, self.on_reset_button)
        self.add_monitor_btn.Bind(wx.EVT_BUTTON, self.on_add_monitor)
        self.remove_monitor_btn.Bind(wx.EVT_BUTTON, self.on_remove_monitor)
        self.toggle_switch_btn.Bind(wx.EVT_BUTTON, self.on_toggle_switch)
        self.switch_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_switch_selected)
        self.speed_btn.Bind(wx.EVT_BUTTON, self.on_speed_button)
        
        # Initialize lists
        self.update_switch_list()
        
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

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by:\nAyoife Dada\nNarmeephan Arunthavarajah\nRaghavendra Narayan Rao\n2025",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)

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
        
        # Clear the monitor list
        self.monitor_list.DeleteAllItems()
        
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
        # Update the monitor list
        self.update_monitor_list()
        
        # Update the canvas with new signal data
        self.update_signal_display()
        
    def update_monitor_list(self):
        """Update the monitor list with current monitor states."""
        self.monitor_list.DeleteAllItems()
        
        # Get monitored signals
        monitored_signals, _ = self.monitors.get_signal_names()
        
        # Find the corresponding device IDs and output IDs
        for i, signal_name in enumerate(monitored_signals):
            # Add to list
            index = self.monitor_list.InsertItem(i, signal_name)
            # Get the last signal value for this monitor
            for (device_id, output_id), signal_list in self.monitors.monitors_dictionary.items():
                if signal_name == self.devices.get_signal_name(device_id, output_id):
                    # Get current signal value directly from the network
                    current_signal = self.monitors.get_monitor_signal(device_id, output_id)
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
                    else:
                        state = "N/A"
                    self.monitor_list.SetItem(index, 1, state)
                    break
                    
    def update_signal_display(self):
        """Update the signal display on the canvas."""
        signal_data = {}
        
        # Get all monitored signals
        for (device_id, output_id), signal_list in self.monitors.monitors_dictionary.items():
            signal_name = self.devices.get_signal_name(device_id, output_id)
            # Convert signal values to binary (0 or 1)
            binary_signals = []
            for signal in signal_list:
                if signal == self.devices.HIGH or signal == self.devices.RISING:
                    binary_signals.append(1)
                elif signal == self.devices.LOW or signal == self.devices.FALLING:
                    binary_signals.append(0)
                else:
                    # For any other signal state, treat as low
                    binary_signals.append(0)
            signal_data[signal_name] = binary_signals
            
        # Update the canvas
        self.canvas.signal_data = signal_data
        self.canvas.render()
        
    def on_add_monitor(self, event):
        """Handle adding a new monitor."""
        # Create a dialog to select device and output
        dialog = wx.Dialog(self, title="Add Monitor")
        dialog_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Get all available signals
        _, non_monitored = self.monitors.get_signal_names()
        
        # Add signal selection
        signal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        signal_label = wx.StaticText(dialog, label="Signal:")
        signal_choice = wx.Choice(dialog, choices=non_monitored)
        signal_sizer.Add(signal_label, 0, wx.ALL | wx.CENTER, 5)
        signal_sizer.Add(signal_choice, 1, wx.ALL | wx.EXPAND, 5)
        
        # Add buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(dialog, wx.ID_OK, "Add")
        cancel_button = wx.Button(dialog, wx.ID_CANCEL, "Cancel")
        button_sizer.Add(ok_button, 1, wx.ALL, 5)
        button_sizer.Add(cancel_button, 1, wx.ALL, 5)
        
        # Build dialog layout
        dialog_sizer.Add(signal_sizer, 0, wx.ALL | wx.EXPAND, 5)
        dialog_sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER, 5)
        
        dialog.SetSizer(dialog_sizer)
        
        if dialog.ShowModal() == wx.ID_OK and signal_choice.GetSelection() != -1:
            signal_name = signal_choice.GetString(signal_choice.GetSelection())
            
            # Find the device and output IDs for this signal
            for device_id in self.devices.find_devices():
                device = self.devices.get_device(device_id)
                for output_id in device.outputs:
                    if signal_name == self.devices.get_signal_name(device_id, output_id):
                        # Add the monitor
                        if self.monitors.make_monitor(device_id, output_id) == self.monitors.NO_ERROR:
                            self.update_display()
                            self.SetStatusText(f"Added monitor for {signal_name}")
                        else:
                            wx.MessageBox("Failed to add monitor", "Error",
                                        wx.OK | wx.ICON_ERROR)
                        break
                
        dialog.Destroy()
        
    def on_remove_monitor(self, event):
        """Handle removing multiple selected monitors."""
        # Get all selected monitors
        selected = []
        item = self.monitor_list.GetFirstSelected()
        while item != -1:
            selected.append(item)
            item = self.monitor_list.GetNextSelected(item)
            
        if not selected:
            wx.MessageBox("Please select monitors to zap", "Error",
                         wx.OK | wx.ICON_ERROR)
            return
            
        for selection in selected:
            signal_name = self.monitor_list.GetItem(selection, 0).GetText()
            
            # Find the device and output IDs for this signal
            for (device_id, output_id) in self.monitors.monitors_dictionary.keys():
                if signal_name == self.devices.get_signal_name(device_id, output_id):
                    # Remove the monitor
                    if self.monitors.remove_monitor(device_id, output_id):
                        self.SetStatusText(f"Zapped monitor for {signal_name}")
                    else:
                        wx.MessageBox(f"Failed to zap monitor {signal_name}", "Error",
                                    wx.OK | wx.ICON_ERROR)
                    break
                    
        # Update display after all monitors are removed
        self.update_display()

    def update_switch_list(self):
        """Update the list of switches and their states."""
        self.switch_list.DeleteAllItems()
        
        # Find all switch devices
        switch_ids = self.devices.find_devices(self.devices.SWITCH)
        
        for i, switch_id in enumerate(switch_ids):
            # Get switch name
            switch_name = self.devices.get_signal_name(switch_id, None)
            
            # Get switch state
            device = self.devices.get_device(switch_id)
            state = "HIGH" if device.switch_state == self.devices.HIGH else "LOW"
            
            # Add to list
            index = self.switch_list.InsertItem(i, switch_name)
            self.switch_list.SetItem(index, 1, state)
            
    def on_switch_selected(self, event):
        """Handle switch selection event."""
        # Enable toggle button when any switches are selected
        self.toggle_switch_btn.Enable(self.switch_list.GetSelectedItemCount() > 0)
        
    def on_toggle_switch(self, event):
        """Handle toggling multiple switch states."""
        # Get all selected switches
        selected = []
        item = self.switch_list.GetFirstSelected()
        while item != -1:
            selected.append(item)
            item = self.switch_list.GetNextSelected(item)
            
        if not selected:
            return
            
        for selection in selected:
            switch_name = self.switch_list.GetItem(selection, 0).GetText()
            current_state = self.switch_list.GetItem(selection, 1).GetText()
            
            # Get device ID
            [device_id, _] = self.devices.get_signal_ids(switch_name)
            
            # Toggle state
            new_state = self.devices.LOW if current_state == "HIGH" else self.devices.HIGH
            
            if self.devices.set_switch(device_id, new_state):
                self.SetStatusText(f"Toggled {switch_name} to {new_state}")
            else:
                wx.MessageBox(f"Failed to toggle switch {switch_name}", "Error",
                            wx.OK | wx.ICON_ERROR)
                
        # Update display after all switches are toggled
        self.update_switch_list()
        
        # Execute network to propagate changes
        if self.network.execute_network():
            self.update_display()
        else:
            wx.MessageBox("Error: Network oscillating", "Error",
                        wx.OK | wx.ICON_ERROR)

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
