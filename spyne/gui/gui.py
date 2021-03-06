## ---------------------------------------------------------------- ##
## GUI.PY
## ---------------------------------------------------------------- ##
## This file describes a simple wxPython-based GUI for Spyne.
## ---------------------------------------------------------------- ##
## Requires:
##    * wxPython
##    * PyOpenGL  -- maybe not
## ---------------------------------------------------------------- ##

from visualize import SPyNECanvas

try:
    import wx
    from   wx import glcanvas
except ImportError:
    print """ERROR: Cannot find wxPython. """

class SPyNEFrame(wx.Frame):
    """The Main Window for SPyNE"""
    def __init__(self, obj, runFunction=None):
        wx.Frame.__init__(self, None, -1, 'SPyNE', wx.DefaultPosition,
                          wx.Size(400,400))
        self.object = obj
        self.InitUI()
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.runFunction = runFunction
        self.Centre()
        self.Show(True)

    def RedrawCanvas(self):
        """Calls the Canvas's OnDraw function"""
        self.canvas.OnDraw()

        
    def InitUI(self):
        """Initializes the GUI"""
        # --- Create widgets ---------------------
        layout   = wx.BoxSizer(wx.VERTICAL)
        controls = wx.BoxSizer(wx.HORIZONTAL)
        main     = wx.BoxSizer(wx.HORIZONTAL)
        shoulder = wx.BoxSizer(wx.VERTICAL)
        canvas   = SPyNECanvas(self, self.object)

        # --- What the neurons represent ------------------------
        rbPanel  = wx.Panel(self, wx.ID_ANY)
        rbBox    = wx.BoxSizer(wx.VERTICAL)
        rbActvt  = wx.RadioButton(rbPanel, 1, 'Activations',
                                  style=wx.RB_GROUP)
        rbInpts  = wx.RadioButton(rbPanel, 2, 'Inputs')
        rbThrshs = wx.RadioButton(rbPanel, 3, 'Thresholds')
        
        # --- Group and Projection viewer --------
        G        = [x.name for x in self.object.GetGroups()]
        P        = ["%s-%s" % (x.groupFrom.name, x.groupTo.name)  \
                    for x in self.object.GetProjections(True)]
        G.sort()
        P.sort()
        
        gList    = wx.ListBox(self, wx.ID_ANY, choices=G)
        pList    = wx.ListBox(self, wx.ID_ANY, choices=P)
        
        # --- 3D point control ----------
        povCtrl  = Point3DControl(self, canvas.pov, rate=10,
                                  main="Position",
                                  updateFunction=self.RedrawCanvas)
        rotCtrl  = Point3DControl(self, canvas.rot,
                                  main="Rotation",
                                  updateFunction=self.RedrawCanvas)

        # --- Add controls -----------------------
        rbBox.Add(rbActvt, 1, wx.EXPAND, 10)
        rbBox.Add(rbInpts, 1, wx.EXPAND, 10)
        rbBox.Add(rbThrshs, 1, wx.EXPAND, 10)
        rbPanel.SetSizer(rbBox)
        
        # --- Main control buttons (top row) -----
        bRun    = wx.Button(self, 10, "Run")
        bUpdate = wx.Button(self, 11, "Update")

        controls.Add(bRun, 1, wx.EXPAND, 20)
        controls.Add(bUpdate, 1, wx.EXPAND, 20)
        
        #controls.Add(rbPanel)

        shoulder.Add(rbPanel, 1)
        shoulder.Add(povCtrl, 1, wx.EXPAND)
        shoulder.Add(rotCtrl, 1, wx.EXPAND)
        shoulder.Add(gList)
        shoulder.Add(pList)
        
        main.Add(canvas, 1, wx.EXPAND, 20)
        main.Add(shoulder)

        layout.Add(controls)
        layout.Add(main, 1, wx.EXPAND, 20)
        
        self.canvas = canvas
        self.rbInpts = rbInpts
        self.SetSizer(layout)
        
        self.Bind(wx.EVT_BUTTON, self.OnClick, bRun)
        self.Bind(wx.EVT_BUTTON, self.OnClick, bUpdate)
        canvas.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioSelect, rbActvt)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioSelect, rbInpts)
        

    def OnClick(self, event):
        """When the button is pressed, run the given function"""
        i = event.GetId()
        if i == 10 and self.runFunction != None:
            self.runFunction()
        elif i == 11:
            self.object.Update()
            self.canvas.OnDraw()

    def OnRadioSelect(self, event):
        """
        Updates the view mode---inputs, activations, or thresholds
        """
        if self.rbInpts.GetValue():
            self.canvas.SetVisibleValues(self.canvas.INPUTS)
        else:
            self.canvas.SetVisibleValues(self.canvas.ACTIVATIONS)
        self.canvas.OnDraw()
    
    def OnKeyDown(self, event):
        code = event.GetKeyCode()
        if code in [wx.WXK_DOWN, wx.WXK_RIGHT, wx.WXK_UP, wx.WXK_LEFT]:
            if code == wx.WXK_DOWN:
                self.canvas.pov.Translate(0, -1*self.canvas.step, 0.)
            elif code == wx.WXK_RIGHT:
                self.canvas.pov.Translate(-1*self.canvas.step, 0., 0.)
            elif code == wx.WXK_UP:
                self.canvas.pov.Translate(0., self.canvas.step, 0.)
            else:
                self.canvas.pov.Translate(self.canvas.step, 0., 0.)
            self.canvas.OnDraw()
            #print self.canvas.rot
        else:
            event.Skip()

    def OnKeyDown(self, event):
        code = event.GetKeyCode()
        print "Rotating:"
        if code in [wx.WXK_DOWN, wx.WXK_RIGHT, wx.WXK_UP, wx.WXK_LEFT]:
            if code == wx.WXK_RIGHT:
                self.canvas.rot.Translate(0, 5, 0.)
            elif code == wx.WXK_DOWN:
                self.canvas.rot.Translate(5, 0., 0.)
            elif code == wx.WXK_LEFT:
                self.canvas.rot.Translate(0., -5, 0.)
            else:
                self.canvas.rot.Translate(-5, 0., 0.)

            # --- Re-adjust values to 360 degrees.
                
            self.canvas.rot.x = self.canvas.rot.x % 360
            self.canvas.rot.y = self.canvas.rot.y % 360
            self.canvas.rot.z = self.canvas.rot.z % 360

            # --- Trigger redraw
            
            self.canvas.OnDraw()
            
        else:
            event.Skip()
        print self.canvas.rot


    # ----------------------------------------------------------------
    # Clean up when closing the window
    def OnClose(self, event):
        self.object.RemoveUpdateListener(self.canvas.OnUpdate)
        self.Destroy()

class Point3DControl(wx.Panel):
    """A Panel that controls the coordinates of a point"""
    def __init__(self, parent, point, labels=("X", "Y", "Z"),
                 main="Point", rate=1, updateFunction=None):
        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_SIMPLE)
        self.point     = point
        self.rate      = rate
        self.main      = main
        self.SetSpins([])
        self.SetLabels(labels)
        self.SetUpdateFunction(updateFunction)
        self.InitUI()


    def SetLabels(self, labels):
        if len(labels) == 3:
            self._labels = labels

    def Labels(self):
        return self._labels

    def SetSpins(self, spins):
        self._spins = spins

    def Spins(self):
        return self._spins

    def SetUpdateFunction(self, function):
        self._updateFunction = function

    def Sync(self):
        """Reloads the values from the point"""
        for sc, i, in zip(self._spins, \
                          (self.point.x, self.point.y, self.point.z)):
            sc.SetValue(i*self.rate)

    def OnNotify(self, obj):
        self.Sync()
    
    def InitUI(self):
        """Initializes the Spin controls"""
        self.point.AddNotifiable(self.OnNotify)
        
        mainLbl = wx.StaticText(self, wx.ID_ANY, self.main)
        
        gbLayout = wx.GridBagSizer(3, 2)
        # Create the spins
        for i in range(3):
            self._spins.append(wx.SpinCtrl(self, i))
            
        # Initialize the spins
        for sc, i in zip(self._spins, range(3)):
            sc.SetRange(-10000, 10000)
            sc.SetValue(0)
            gbLayout.Add(sc, (i, 1))
        
        for l, i in zip(self.Labels(), range(3)):
            st = wx.StaticText(self, -1, l)
            gbLayout.Add(st, (i,0))

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(mainLbl)
        box.Add(gbLayout)
        
        self.Sync()
        #self.SetSizerAndFit(gbLayout)
        self.SetSizerAndFit(box)
        
        for s in self._spins:
            self.Bind(wx.EVT_SPINCTRL, self.OnSpin, s)

    
    def OnSpin(self, evt):
        """Updates the internal point"""
        i = evt.GetId()    # Spin identifier (x, y, z)
        v = evt.GetInt()   # Value
        
        if i == 0:
            self.point.x = float(v) / self.rate
        elif i == 1:
            self.point.y = float(v) / self.rate
        elif i == 2:
            self.point.z = float(v) / self.rate

        self.Sync()
        if self._updateFunction is not None:
            self._updateFunction()
        
    
class PyNNGroupPanel(wx.Panel):
    """
A panel for visualizing information about a given group
(still unimplemented)
    """
    def __init__(self, group=None):
        self.group=None
        
    

def Show(obj=None, runFunction=None):
    app    = wx.App(redirect=False)
    frame  = SPyNEFrame(obj, runFunction)
    frame.Show()
    app.MainLoop()
