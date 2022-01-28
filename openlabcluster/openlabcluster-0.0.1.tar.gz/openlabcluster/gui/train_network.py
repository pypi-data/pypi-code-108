"""
DeepLabCut2.0 Toolbox (deeplabcut.org)
© A. & M. Mathis Labs
https://github.com/AlexEMG/DeepLabCut
Please see AUTHORS for contributors.

https://github.com/AlexEMG/DeepLabCut/blob/master/AUTHORS
Licensed under GNU Lesser General Public License v3.0

"""

import os
import sys
import pydoc
from pathlib import Path

import subprocess
import webbrowser
import traceback
import wx
from wx.lib.pubsub import pub
from wx.lib.scrolledpanel import ScrolledPanel

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import openlabcluster
from openlabcluster.utils.plotting import format_axes
from openlabcluster.utils import auxiliaryfunctions
from wx.lib.pubsub import pub
from wx.lib.scrolledpanel import ScrolledPanel
from openlabcluster.gui.scatter_plot_extract import transform_hidden
media_path = os.path.join(openlabcluster.__path__[0], "gui", "media")

from openlabcluster.gui.media.label_video import video_display_window

from matplotlib.backends.backend_wxagg import (
    NavigationToolbar2WxAgg as NavigationToolbar,
)

logo = os.path.join(media_path, "logo.png")


class WidgetPanel(wx.Panel):
    def __init__(self, parent):
        self.panel = wx.Panel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

# not used here
class ProgressDialog(wx.Dialog):
    def __init__(self,parent):
        wx.Dialog.__init__(self, parent)
        self.parent = parent
        self.abort = False
        self.progress = 0

        bSizer2 = wx.BoxSizer(wx.VERTICAL)
        self.gauge = wx.Gauge(self, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL)
        self.gauge.SetValue(0)

        self.m_button1 = wx.Button(self, wx.ID_ANY, u"Stop Training", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer2.Add(self.gauge, 0, 0, 5)
        bSizer2.Add(self.m_button1, 0, 0, 5)

        self.SetSizer(bSizer2)
        self.Layout()
        self.Centre(wx.BOTH)

        ## Connect Events

        self.m_button1.Bind(wx.EVT_BUTTON, self.on_cancel)
        pub.subscribe(self.updateProgress, "update")
        pub.subscribe(self.on_finish, "finish")


    def on_cancel(self, event):
        """Cancels the conversion process"""
        self.parent.work.stop()
        self.parent.work.join()
        pub.unsubscribe(self.on_finish, "finish")
        self.Destroy()
        # pub.unsubscribe(self.if_abort, 'cancel')

    def on_finish(self):
        """conversion process finished"""
        pub.unsubscribe(self.updateProgress, "update")
        pub.unsubscribe(self.on_finish, "finish")
        self.Close()

    def __del__(self):
        pass

class ImagePanel(wx.Panel):
    def __init__(self, parent, gui_size=None,  projection='2D', **kwargs):
        self.parent = parent
        if gui_size:
            h = gui_size[0] # / 2
            w = gui_size[1] #/ 3

            wx.Panel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER,size=(h, w))
        else:
            wx.Panel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        # topSplitter = wx.SplitterWindow(self)

        self.figure = Figure()
        if projection =='2D':
            self.axes = self.figure.add_subplot(1, 1, 1)
        else:
            self.axes = self.figure.add_subplot(projection='3d')

        # self.canvas = FigureCanvas(topSplitter, -1, self.figure)
        # self.canvas = FigureCanvas(self.sizer, -1, self.figure)
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.toolbar = NavigationToolbar(self.canvas)

        # self.widget_panel = WidgetPanel(topSplitter)
        # self.widget_panel = WidgetPanel(self.sizer)
        # topSplitter.SplitHorizontally(
        #     self.canvas, self.widget_panel
        # )  # 0.9
        # topSplitter.SetSashGravity(0.28)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        # self.sizer.Add(self.widget_panel)

        # self.widgetsizer = wx.WrapSizer(orient=wx.HORIZONTAL)
        self.widgetsizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.zoom = wx.ToggleButton(self, label="Zoom")
        self.zoom.Bind(wx.EVT_TOGGLEBUTTON, self.zoomButton)
        self.widgetsizer.Add(self.zoom, wx.ALL, 15)
        self.zoom.Enable(True)
        # self.widget_panel.SetSizer(self.widgetsizer)

        self.pan = wx.ToggleButton(self, id=wx.ID_ANY, label="Pan")
        self.widgetsizer.Add(self.pan,  wx.ALL, 15)
        self.pan.Bind(wx.EVT_TOGGLEBUTTON, self.panButton)
        # self.widget_panel.SetSizer(self.widgetsizer)
        self.pan.Enable(True)

        self.orig_xlim = [-60, 60]
        self.orig_ylim = [-60, 60]
        # self.sizer.Add(topSplitter, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.sizer.Add(self.widgetsizer)
        #self.sizer.Add(self.canvas, pos = (1, 0), span = (1, 5), flag = wx.EXPAND | wx.BOTTOM, border = 10)
        #self.sizer.Add(widgetsizer, pos = (2, 0), span = (1, 5), flag = wx.EXPAND | wx.BOTTOM, border = 10)

        self.SetSizer(self.sizer)
        self.resetView()
        self.Fit()

    def renew_sizer(self):
        self.SetSizer(self.sizer)

    def refresh(self, projection):
        wx.Panel.__init__(self, self.parent, -1, style=wx.SUNKEN_BORDER)
        topSplitter = wx.SplitterWindow(self)
        self.axes.remove()
        if projection == '2d':
            self.axes = self.figure.add_subplot(1, 1, 1)
        else:
            from mpl_toolkits.mplot3d import Axes3D  # <--- This is important for 3d plotting
            self.axes = self.figure.add_subplot(projection='3d')
        self.canvas.draw_idle()
        # self.sizer.Add(self.canvas, pos = (1, 0), span = (1, 5), flag = wx.EXPAND | wx.BOTTOM, border = 10)
        # self.sizer.Add(widgetsizer, pos = (2, 0), span = (1, 5), flag = wx.EXPAND | wx.BOTTOM, border = 10)
        self.toolbar = NavigationToolbar(self.canvas)
        self.resetView()
        self.Fit()

    def getfigure(self):
        return self.figure

    def resetView(self):
        self.axes.set_xlim(self.orig_xlim)
        self.axes.set_ylim(self.orig_ylim)

    def zoomButton(self, event):
        if self.zoom.GetValue():
            # Save pre-zoom xlim and ylim values
            self.prezoom_xlim = self.axes.get_xlim()
            self.prezoom_ylim = self.axes.get_ylim()
            self.toolbar.zoom()
            #self.statusbar.SetStatusText("Zoom On")
            self.pan.SetValue(False)
        else:
            self.toolbar.zoom()
            #self.statusbar.SetStatusText("Zoom Off")

    def panButton(self, event):
        if self.pan.GetValue():
            self.toolbar.pan()
            #self.statusbar.SetStatusText("Pan On")
            self.zoom.SetValue(False)
        else:
            self.toolbar.pan()
            #self.statusbar.SetStatusText("Pan Off")
# class Train_network(wx.Panel):
class Train_network(wx.lib.scrolledpanel.ScrolledPanel):
    """
    """

    def __init__(self, parent, gui_size, cfg, statusBar):
        """Constructor"""
        # wx.Panel.__init__(self, parent=parent)
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent=parent)
        displays = (
            wx.Display(i) for i in range(wx.Display.GetCount())
        )  # Gets the number of displays
        screenSizes = [
            display.GetGeometry().GetSize() for display in displays
        ]  # Gets the size of each display
        index = 0  # For display 1.
        screenWidth = screenSizes[index][0]
        screenHeight = screenSizes[index][1]
        self.gui_size = (screenWidth * 0.7, screenHeight * 0.85)
        # variable initilization
        self.method = "automatic"
        self.config = cfg
        self.statusBar = statusBar
        self.initial = True
        # design the panel
        self.parent = parent

        self.sizer = wx.GridBagSizer(6, 5)
        text = wx.StaticText(self)
        text.SetLabelText("DeepLabCluster - Step 2. Form Data into Clusters (Train Predict&Cluster Net)")
        self.sizer.Add(text, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=15)
        # Add logo of DLC
        icon = wx.StaticBitmap(self, bitmap=wx.Bitmap(logo))
        self.sizer.Add(
            icon, pos=(0, 4), flag=wx.TOP | wx.RIGHT | wx.ALIGN_RIGHT, border=5
        )

        line1 = wx.StaticLine(self)
        self.sizer.Add(
            line1, pos=(1, 0), span=(1, 5), flag=wx.EXPAND | wx.BOTTOM, border=10
        )

        vbox1 = wx.BoxSizer(wx.VERTICAL)
        self.pose_cfg_text = wx.Button(self, label="Click to open the pose config file")
        self.pose_cfg_text.Bind(wx.EVT_BUTTON, self.edit_pose_config)
        vbox1.Add(self.pose_cfg_text, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)

        self.update_params_text = wx.Button(self, label="Update the parameters")
        self.update_params_text.Bind(wx.EVT_BUTTON, self.update_params)
        vbox1.Add(self.update_params_text, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)

        self.pose_cfg_text.Hide()
        self.update_params_text.Hide()

        sb = wx.StaticBox(self, label="")
        boxsizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        pose_cfg = auxiliaryfunctions.read_config(self.config)
        display_iters = str(pose_cfg["display_iters"])
        save_iters = str(pose_cfg["save_iters"])
        max_iters = str(pose_cfg["su_epoch"])

        self.sizer.AddGrowableCol(2)

        self.oper_1 = wx.BoxSizer(wx.HORIZONTAL)
        self.image_panel = ImagePanel(self)
        self.video_display = video_display_window(self,self.gui_size, pose_cfg)
        self.sizer.Add(self.image_panel, pos=(3,0), span=(1,2))
        self.sizer.Add(self.video_display, pos=(3, 2), span=(1, 1))
        scroll_panel_sizer = wx.BoxSizer( wx.VERTICAL )
        scroll_panel_sizer.Add(self.image_panel)

        self.scroll_panel = ScrolledPanel(self)
        self.scroll_panel.SetSizer(scroll_panel_sizer)
        display_iters_text = wx.StaticBox(self, label="Update Cluster Map Every (Epochs)")
        display_iters_text_boxsizer = wx.StaticBoxSizer(display_iters_text, wx.VERTICAL)
        self.display_iters = wx.SpinCtrl(
            self, value=display_iters, min=1, max=1000
        )
        display_iters_text_boxsizer.Add(
            self.display_iters, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 10
        )

        save_iters_text = wx.StaticBox(self, label="Save Cluster Map Every (Epochs)")
        save_iters_text_boxsizer = wx.StaticBoxSizer(save_iters_text, wx.VERTICAL)
        # save_iters_text.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEntersave_iters)
        # save_iters_text.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)
        self.save_iters = wx.SpinCtrl(self, value=save_iters, min=1, max=1000)
        save_iters_text_boxsizer.Add(
            self.save_iters, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 10
        )

        max_iters_text = wx.StaticBox(self, label="Maximum Epochs")
        max_iters_text_boxsizer = wx.StaticBoxSizer(max_iters_text, wx.VERTICAL)
        # max_iters_text.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEntermax_iters)
        # max_iters_text.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)

        self.max_iters = wx.SpinCtrl(self, value=max_iters, min=1, max=1000)
        max_iters_text_boxsizer.Add(
            self.max_iters, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 10
        )

        dim_text = wx.StaticBox(self, label="Cluster Map Dimension")
        dimboxsizer = wx.StaticBoxSizer(dim_text, wx.VERTICAL)
        self.dim_choice = wx.ComboBox(self, style=wx.CB_READONLY)
        self.dim_choice.Bind(wx.EVT_COMBOBOX, self.update_image_panel)
        options = ["2d", "3d"]
        self.dim_choice.Set(options)
        self.dim_choice.SetValue("2d")
        dimboxsizer.Add(self.dim_choice, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)

        reducer_text = wx.StaticBox(self, label="Dimension Reduction Method" )
        reducerboxsizer = wx.StaticBoxSizer(reducer_text, wx.VERTICAL)
        self.reducer_choice = wx.ComboBox(self, style=wx.CB_READONLY)
        self.reducer_choice.Bind(wx.EVT_COMBOBOX, self.update_image_panel)
        reducer_options = ["PCA", "tSNE", "UMAP"]
        self.reducer_choice.Set(reducer_options)
        self.reducer_choice.SetValue("PCA")
        reducerboxsizer.Add(self.reducer_choice, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)

        hbox2.Add(display_iters_text_boxsizer, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        hbox2.Add(save_iters_text_boxsizer, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        hbox2.Add(max_iters_text_boxsizer, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        hbox2.Add(dimboxsizer,10, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        hbox2.Add(reducerboxsizer, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        boxsizer.Add(hbox2, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)

        self.sizer.Add(
            boxsizer,
            pos=(2, 0),
            span=(1, 5),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=10,
        )
        # clustering stage butto
        botton_box = wx.BoxSizer(wx.HORIZONTAL)
        self.ok = wx.Button(self, label="Start Clustering")
        botton_box.Add(self.ok, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        self.ok.Bind(wx.EVT_BUTTON, self.train_network)

        self.continue_but = wx.Button(self, label="Continue Clustering")
        self.continue_but.Bind(wx.EVT_BUTTON, self.continue_train)
        botton_box.Add(self.continue_but, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)

        self.stop = wx.Button(self, label="Stop Clustering")
        self.stop.Bind(wx.EVT_BUTTON, self.stop_train)
        botton_box.Add(self.stop, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)


        self.cancel = wx.Button(self, label="Reset")
        self.cancel.Bind(wx.EVT_BUTTON, self.cancel_train_network)
        botton_box.Add(self.cancel, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)

        self.action = wx.Button(self, label="Go to Action Recognition")
        self.action.Bind(wx.EVT_BUTTON, self.action_recognition_panel)
        botton_box.Add(self.action, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)

        self.help_button = wx.Button(self, label="Help")
        botton_box.Add(self.help_button, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        self.help_button.Bind(wx.EVT_BUTTON, self.help_function)
        self.sizer.Add(botton_box, pos=(4, 0),
                       span=(1, 5),
                       flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
                       border=10, )

        self.SetSizer(self.sizer)
        self.sizer.Fit(self)
        self.selected_id = []

        self.work = transform_hidden(self.config, reducer_name=self.reducer_choice.GetValue())
        transform = self.work.transformed()
        self.sc = self.image_panel.axes.scatter(transform[:,0], transform[:,1],s=10, picker=True, color='k')
        self.annot = self.image_panel.axes.annotate("", xy=(0, 0), xytext=(5, 5), textcoords="offset points")
        self.annot.set_visible(False)

        self.image_panel.canvas.mpl_connect('pick_event', self.display_data)
        self.image_panel.canvas.mpl_connect("motion_notify_event", self.hover)
        self.image_panel.axes.set_xlim([-10, 20])
        self.image_panel.axes.set_ylim([-10, 20])

        if type(pose_cfg['train_videolist']) is str:
            if pose_cfg['train_videolist'].endswith('.text') or pose_cfg['train_videolist'].endswith('.txt'):
                with open(pose_cfg['train_videolist'], 'r') as f:
                    self.videpaths = f.readlines()
            elif pose_cfg['train_videolist'].endswith('.npy'):
                self.videpaths = np.load(pose_cfg['train_videolist'], allow_pickle=True)

        self.image_panel.axes.set_title('Cluster Map')

        format_axes(self.image_panel.axes)
        pub.subscribe(self.on_finish, "finish")

        self.SetupScrolling()

    def OnMouseEntersave_iters(self, event):
        self.statusBar.SetStatusText("Set the interval to save trained model")

    def OnMouseLeave(self, event):
        self.statusBar.SetStatusText("")

    def help_function(self, event):

        # filepath = "help.txt"
        # f = open(filepath, "w")
        # sys.stdout = f
        # fnc_name = "openlabcluster.train_network"
        # pydoc.help(fnc_name)
        # f.close()
        # sys.stdout = sys.__stdout__
        # help_file = open("help.txt", "r+")
        # help_text = help_file.read()
        help_text = """
       Set the Training Parameters:
        1. Update Cluster Map Every (Epochs): this helps you to decide when to update the Cluster Map, e.g. set 1 to update Cluster Map every training epoch, set to 5, update every 5 epoch.
        2. Save Cluster Map Every (Epochs): this decides when to save Cluster Maps, e.g. if it is 1, update the Cluster Map every training epoch.
        3. Maximum Epochs: the number of epoches perform training.
        4. Cluster Map Dimension: you can choose "2d" or "3d", if it is "2d" the Cluster Map will be shown in 2D dimension, otherwise it is 3D dimension.
        5. Dimension Reduction Methods: possible choices are "PCA", "tSNE", "UMAP". The GUI will use the choosen reduction method to perform dimension reduction and show results in Cluster Map.
        
        
        Buttons:
        After setting the parameters you can perform analysis:
        
        1. Start Clustering: perform unsupervised sequence regneration task.
        2. Continue Clustering: if you stopped the clustering at some stage and want to perform clustering with ealier clustering results, click this button.
        3. Stop clustering: usually the clustering will stop when it reaches the maximum epochs, but if you want to stop at itermediate stage, click this button.
        4. Reset: Reset the earlier defined trainign parameters to default.
        5. Go to Action Recognition: after the unsupervised clustering we go to the next step which includes: i) sample labeling suggestion, ii) sample laebling and iii) semi-supervised action recognition training with labeled samples.

        """
        wx.MessageBox(help_text, "Help", wx.OK | wx.ICON_INFORMATION)
        # help_file.close()
        # os.remove("help.txt")

    def chooseOption(self, event):
        if self.pose_cfg_choice.GetStringSelection() == "Yes":
            self.shuffles.Enable(False)
            self.trainingindex.Enable(False)
            self.pose_cfg_text.Show()
            self.update_params_text.Show()
            self.SetSizer(self.sizer)
            self.sizer.Fit(self)
        else:
            self.shuffles.Enable(True)
            self.trainingindex.Enable(True)
            self.pose_cfg_text.Hide()
            self.update_params_text.Hide()
            self.SetSizer(self.sizer)
            self.sizer.Fit(self)

    def select_config(self, event):
        """
        """
        self.config = self.sel_config.GetPath()

    def edit_pose_config(self, event):
        """
        """
        self.shuffles.Enable(True)
        self.trainingindex.Enable(True)
        self.display_iters.Enable(True)
        self.save_iters.Enable(True)
        self.max_iters.Enable(True)
        self.snapshots.Enable(True)
        # Read the pose config file
        cfg = auxiliaryfunctions.read_config(self.config)
        trainFraction = cfg["TrainingFraction"][self.trainingindex.GetValue()]
        #        print(os.path.join(cfg['project_path'],auxiliaryfunctions.GetModelFolder(trainFraction, self.shuffles.GetValue(),cfg),'train','pose_cfg.yaml'))
        self.pose_cfg_path = os.path.join(
            cfg["project_path"],
            auxiliaryfunctions.GetModelFolder(
                trainFraction, self.shuffles.GetValue(), cfg
            ),
            "train",
            "pose_cfg.yaml",
        )
        # let the user open the file with default text editor. Also make it mac compatible
        if sys.platform == "darwin":
            self.file_open_bool = subprocess.call(["open", self.pose_cfg_path])
            self.file_open_bool = True
        else:
            self.file_open_bool = webbrowser.open(self.pose_cfg_path)
        if self.file_open_bool:
            self.pose_cfg = auxiliaryfunctions.read_plainconfig(self.pose_cfg_path)
        else:
            raise FileNotFoundError("File not found!")

    def update_params(self, event):
        # update the variables with the edited values in the pose config file
        if self.file_open_bool:
            self.pose_cfg = auxiliaryfunctions.read_plainconfig(self.pose_cfg_path)
            display_iters = str(self.pose_cfg["display_iters"])
            save_iters = str(self.pose_cfg["save_iters"])
            max_iters = str(self.pose_cfg["multi_step"][-1][-1])
            self.display_iters.SetValue(display_iters)
            self.save_iters.SetValue(save_iters)
            self.max_iters.SetValue(max_iters)
            self.shuffles.Enable(True)
            self.trainingindex.Enable(True)
            self.display_iters.Enable(True)
            self.save_iters.Enable(True)
            self.max_iters.Enable(True)
            self.snapshots.Enable(True)
        else:
            raise FileNotFoundError("File not found!")

    def train_network(self, event):

        if self.display_iters.Children:
            displayiters = int(self.display_iters.Children[0].GetValue())
        else:
            displayiters = int(self.display_iters.GetValue())

        if self.save_iters.Children:
            saveiters = int(self.save_iters.Children[0].GetValue())
        else:
            saveiters = int(self.save_iters.GetValue())

        if self.max_iters.Children:
            maxiters = int(self.max_iters.Children[0].GetValue())
        else:
            maxiters = int(self.max_iters.GetValue())
        self.ok.Enable(False)


        try:
            self.work=openlabcluster.train_network(
                self.config,
                self.image_panel,
                gputouse=None,
                autotune=None,
                displayiters=displayiters,
                saveiters=saveiters,
                maxiters=maxiters,
                reducer_name=self.reducer_choice.GetValue(),
                dimension= self.dim_choice.GetValue()
            )
        except Exception as e:
            print(traceback.format_exc())
            wx.MessageBox('Error while training. Look in terminal for more information', 'Training Error', wx.OK | wx.ICON_ERROR) 


    def stop_train(self, event):
        self.work.stop()
        self.ok.Enable(True)
        self.continue_but.Enable(True)
        wx.MessageBox('Training Stopped', 'Message')
        # self.work.join()
        # pub.unsubscribe(self.on_finish, "finish")
        # self.Destroy()

    def continue_train(self, event):
        self.ok.Enable(False)
        if self.display_iters.Children:
            displayiters = int(self.display_iters.Children[0].GetValue())
        else:
            displayiters = int(self.display_iters.GetValue())

        if self.save_iters.Children:
            saveiters = int(self.save_iters.Children[0].GetValue())
        else:
            saveiters = int(self.save_iters.GetValue())

        if self.max_iters.Children:
            maxiters = int(self.max_iters.Children[0].GetValue())
        else:
            maxiters = int(self.max_iters.GetValue())
        self.ok.Enable(False)

        try:
            self.work=openlabcluster.train_network(
                self.config,
                self.image_panel,
                gputouse=None,
                autotune=None,
                displayiters=displayiters,
                saveiters=saveiters,
                maxiters=maxiters,
                continue_training=True,
                reducer_name=self.reducer_choice.GetValue(),
                dimension=self.dim_choice.GetValue()
            )
        except Exception as e:
            print(traceback.format_exc())
            wx.MessageBox('Error while training. Look in terminal for more information', 'Training Error', wx.OK | wx.ICON_ERROR)

    def update_image_panel(self, event):
        dim = self.dim_choice.GetValue()
        self.image_panel.refresh(dim)
        method = self.reducer_choice.GetValue()
        self.work = transform_hidden(self.config, reducer_name = method, dimension=dim)
        transform = self.work.transformed()
        if dim =='2d':
            self.sc = self.image_panel.axes.scatter(transform[:,0], transform[:,1],s=10, picker=True, color='k')
        else:
            self.sc = self.image_panel.axes.scatter(transform[:,0], transform[:,1],transform[:,2], s=10, picker=True, color='k')
        font = {'family': 'sans-serif',
                'color': 'darkred',
                'weight': 'normal',
                'size': 16,
                }
        self.image_panel.axes.set_title('Cluster Map', fontdict=font)
        self.image_panel.axes.autoscale()

    def on_finish(self):
        """conversion process finished"""
        pub.unsubscribe(self.on_finish, "finish")
        self.ok.Enable(True)
        self.Close()

    def cancel_train_network(self, event):
        """
        Reset to default
        """
        self.config = []
        self.sel_config.SetPath("")
        self.pose_cfg_text.Hide()
        self.update_params_text.Hide()
        self.pose_cfg_choice.SetSelection(1)
        self.display_iters.SetValue(1)
        self.save_iters.SetValue(1)
        self.max_iters.SetValue(1)
        self.snapshots.SetValue(5)
        self.SetSizer(self.sizer)
        self.sizer.Fit(self)

    def action_recognition_panel(self, event):

        from openlabcluster.gui.sample_labeling_new import Sample_labeling
        #self.config = auxiliaryfunctions.read_config(self.config)
        page5 = Sample_labeling(self.parent, self.gui_size, self.config)
        self.parent.AddPage(page5, "Behavior Identification")

    def display_data(self, event):
        thisline = event.artist

        inarray = np.asarray(event.ind)
        print(inarray)
        if len(inarray) > 0:
            # x_tmp = xdata[inarray]
            # y_tmp = ydata[inarray]
            # dist = (x_tmp - cur_pos[0])**2 + (y_tmp - cur_pos[1])**2
            # ind = inarray[np.argmin(dist)]
            ind = inarray[0]
        else:
            ind = inarray
        self.video_display.load_video(ind)

    def hover(self, event):
        if event.inaxes == self.image_panel.axes:
            # get the points contained in the event
            cont, ind = self.sc.contains(event)
            print(ind)
            if cont:
                # change annotation position
                self.annot.xy = (event.xdata, event.ydata)
                # write the name of every point contained in the event
                if type(self.videpaths[0]) == list:
                    self.statusBar.SetStatusText("{}".format(','.join([f'ID {n}, Path {self.videpaths[n][0]}' for n in ind["ind"]])))
                    #self.annot.set_text("{}".format(', '.join([self.videpaths[n][0] for n in ind["ind"]])))
                else:
                    self.statusBar.SetStatusText("{}".format(','.join([f'ID {n}, Path {self.videpaths[n]}' for n in ind["ind"]])))
                    #self.annot.set_text("{}".format(', '.join([self.videpaths[n] for n in ind["ind"]])))

            else:
                self.statusBar.SetStatusText('')