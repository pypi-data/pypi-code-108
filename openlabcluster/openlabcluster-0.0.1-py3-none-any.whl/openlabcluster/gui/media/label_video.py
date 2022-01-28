import numpy as np
import wx
from wx.core import BoxSizer
import wx.lib.scrolledpanel as SP
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import sys
import cv2
import os
import matplotlib.animation as animation
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
from wx.lib.scrolledpanel import ScrolledPanel

class WidgetPanel(wx.Panel):
    def __init__(self, parent):
        self.panel = wx.Panel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        # self.box = wx.StaticBox(self.panel, -1, "StaticBox")
        # text = wx.StaticText(self.box, -1, "This window is a child of the staticbox")
packages = [('abiword', '5.8M', 'base'), ('adie', '145k', 'base'),
    ('airsnort', '71k', 'base'), ('ara', '717k', 'base'), ('arc', '139k', 'base'),
    ('asc', '5.8M', 'base'), ('ascii', '74k', 'base'), ('ash', '74k', 'base')]

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent, W, H):

        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(W,H))
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)


class ImagePanel(wx.Panel):
    def __init__(self, parent, gui_size, **kwargs):
        h = gui_size[0] / 2
        w = gui_size[1] / 3
        wx.Panel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER, size=(h, w))

        self.figure = Figure()
        self.axes = self.figure.add_subplot(1, 1, 1)
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.widgetsizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.orig_xlim = []
        self.orig_ylim = []
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.sizer.Add(self.widgetsizer)
        self.SetSizer(self.sizer)
        self.axes.set_axis_off()
        self.Fit()

    def getfigure(self):
        return self.figure

    def resetView(self):
        self.axes.set_xlim(self.orig_xlim)
        self.axes.set_ylim(self.orig_ylim)

    def renew_sizer(self):
        self.SetSizer(self.sizer)

class custom_objects_to_plot:
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name


class ScrollPanel(SP.ScrolledPanel):
    def __init__(self, parent):
        SP.ScrolledPanel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        self.SetupScrolling(scroll_x=True, scroll_y=True, scrollToTop=False)
        self.Layout()
        self.box = wx.StaticBox(parent, -1, "StaticBox")
        text = wx.StaticText(self.box, -1, "This window is a child of the staticbox")

    def on_focus(self, event):
        pass

    def addRadioButtons(self, bodyparts, fileIndex, markersize):
        """
        Adds radio buttons for each bodypart on the right panel
        """
        self.choiceBox = wx.BoxSizer(wx.VERTICAL)
        choices = [l for l in bodyparts]
        self.fieldradiobox = wx.RadioBox(
            self,
            label="Select a bodypart to label",
            style=wx.RA_SPECIFY_ROWS,
            choices=choices,
        )
        self.slider = wx.Slider(
            self,
            -1,
            markersize,
            1,
            markersize * 3,
            size=(250, -1),
            style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS,
        )

        self.slider.Enable(False)
        self.checkBox = wx.CheckBox(self, id=wx.ID_ANY, label="Adjust marker size.")
        self.choiceBox.Add(self.slider, 0, wx.ALL, 5)
        self.choiceBox.Add(self.checkBox, 0, wx.ALL, 5)
        self.choiceBox.Add(self.fieldradiobox, 0, wx.EXPAND | wx.ALL, 10)
        self.SetSizerAndFit(self.choiceBox)
        self.Layout()
        return (self.choiceBox, self.fieldradiobox, self.slider, self.checkBox)

    def clearBoxer(self):
        self.choiceBox.Clear(True)

    def printTest(self, test):
        text = wx.StaticText(self.box, -1, "This window is a child of the staticbox")

    def openDialog(self, event):
        data = wx.PrintDialogData()
        data.EnableSelection(True)
        data.EnablePrintToFile(True)
        data.EnablePageNumbers(True)
        data.SetMinPage(1)
        data.SetMaxPage(10)

        dialog = wx.PrintDialog(self, data)
        # dialog.ShowModal()

        if dialog.ShowModal() == wx.ID_OK:
            data = dialog.GetPrintDialogData()
            print('GetAllPages: %d\n' % data.GetAllPages())

            dialog.Destroy()



class PlotGUI(wx.Frame):
    """Class to display basic GUI elements."""

    def __init__(self, parent, cfg, sample):
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

        wx.Frame.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title="Iterative Cluster Selecting Samples",
            size=wx.Size(self.gui_size),
            pos=wx.DefaultPosition,
            style=wx.RESIZE_BORDER | wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL,
        )
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText(
            "Looking for a folder to start labeling. Click 'Load frames' to begin."
        )
        from openlabcluster.utils.auxiliaryfunctions import read_config
        self.cfg_file = cfg
        self.cfg = read_config(cfg)
        self.sample = np.load(sample)

        class_name = self.cfg['class_name']
        f = open(self.cfg['train_videolist'], 'r')
        self.videpaths = f.readlines()
        f.close()
        self.label = np.zeros(len(self.sample))
        self.current = 0

        self.SetSizeHints(
            wx.Size(self.gui_size)
        )  # This sets the minimum size of the GUI. It can scale now!
        ###################################################################################################################################################

        # Spliting the frame into top and bottom panels. Bottom panels contains the widgets. The top panel is for showing images and plotting!

        topSplitter = wx.SplitterWindow(self)
        vSplitter = wx.SplitterWindow(topSplitter)

        self.image_panel = ImagePanel(vSplitter, self.gui_size)
        self.choice_panel = WidgetPanel(vSplitter)  # ScrollPanel(vSplitter)
        vSplitter.SplitVertically(
            self.image_panel, self.choice_panel, sashPosition=self.gui_size[0] * 0.8
        )
        vSplitter.SetSashGravity(1)
        self.widget_panel = WidgetPanel(topSplitter)
        topSplitter.SplitHorizontally(
            vSplitter, self.widget_panel, sashPosition=self.gui_size[1] * 0.83
        )  # 0.9
        topSplitter.SetSashGravity(1)
        # sizer = wx.BoxSizer(wx.VERTICAL)
        # sizer.Add(topSplitter, 1, wx.EXPAND)
        # self.SetSizer(sizer)
        # choice label
        self.checked = []
        self.log = wx.TextCtrl(self.choice_panel, -1, style=wx.TE_MULTILINE, )
        self.list = CheckListCtrl(self.choice_panel, self.gui_size[0]*0.78, self.gui_size[1]*0.8)
        self.list.InsertColumn(0, 'Class name', width=120)
        self.list.InsertColumn(1, 'Class label')
        self.list.OnCheckItem = self.OnCheckItem

        for i in range(len(class_name)):
            index = self.list.InsertItem(sys.maxsize, class_name[i])
            self.list.SetItem(index, 1, str(i+1))
        self.choice_panel.sizer.Add(self.list)

        widgetsizer = wx.WrapSizer(orient=wx.HORIZONTAL)
        self.load = wx.Button(self.widget_panel, id=wx.ID_ANY, label="Load videos")

        widgetsizer.Add(self.load, 1, wx.ALL, 15)
        self.load.Bind(wx.EVT_BUTTON, self.load_video)

        self.prev = wx.Button(self.widget_panel, id=wx.ID_ANY, label="Replay")
        widgetsizer.Add(self.prev, 1, wx.ALL, 15)
        self.prev.Bind(wx.EVT_BUTTON, self.replay)
        self.prev.Enable(True)

        self.prev = wx.Button(self.widget_panel, id=wx.ID_ANY, label=">>Next")
        widgetsizer.Add(self.prev, 1, wx.ALL, 15)
        self.prev.Bind(wx.EVT_BUTTON, self.next)
        self.prev.Enable(True)

        self.ok = wx.Button(self.widget_panel, label="Save Labeling Result")
        widgetsizer.Add(self.ok, 1, wx.ALL, 15)
        self.ok.Bind(wx.EVT_BUTTON, self.savelabel)

        self.widget_panel.SetSizer(widgetsizer)


    def OnCheckItem(self, index, flage):
        print('here')
        if len(self.checked):
            if self.checked[0] == index:
                self.list.CheckItem(self.checked[0], False)
                self.checked = []
            else:
                self.list.CheckItem(index, True)
                self.list.CheckItem(self.checked[0], False)
                self.checked = [index]
        else:
            self.list.CheckItem(index, True)
            self.checked = [index]
        print('video_name:%s' % self.videpaths[self.current])
        self.label[self.current] = index+1


    def animate(self, i):
        self.videohandle.set_array(self.imgs[i])
        return self.videohandle,



    def load_video(self, event):
        print(os.getcwd())
        path = self.videpaths[self.current][:-1]
        cap = cv2.VideoCapture(path
                               )
        self.imgs = []
        while (cap.isOpened()):
            ret, frame = cap.read()
            if ret:
                self.imgs.append(frame)
            else:
                break

        self.videohandle = self.image_panel.axes.imshow(self.imgs[0])
        print(len(self.imgs))
        print(path)
        animation.FuncAnimation(self.image_panel.figure, self.animate, frames=len(self.imgs),
                                interval=1, blit=True, repeat=False)

    def next(self, event):
        self.current+=1
        if self.current < len(self.label):
            if len(self.checked):
                self.list.CheckItem(self.checked[0], False)
            path = self.videpaths[self.current][:-1]
            cap = cv2.VideoCapture(path
                                   )
            self.imgs = []
            while (cap.isOpened()):
                ret, frame = cap.read()
                if ret:
                    self.imgs.append(frame)
                else:
                    break

            self.videohandle = self.image_panel.axes.imshow(self.imgs[0])
            print(len(self.imgs))
            animation.FuncAnimation(self.image_panel.figure, self.animate, frames=len(self.imgs),
                                    interval=1, blit=True, repeat=False)
        else:
            wx.MessageBox(
                "This is the End of Sampling list",
                "Error",
                wx.OK | wx.ICON_ERROR,
            )
            return

    def replay(self, event):
        if len(self.imgs) == 0:
            wx.MessageDialog(self, 'Load video first', 'Error',
                          style=wx.OK | wx.CENTRE)

    def savelabel(self,event):
        import h5py
        train_data = os.path.join(self.cfg['data_path'], self.cfg['train'])
        from openlabcluster.training_utils.ssl.data_loader import UnsupData
        dataset_train = UnsupData(os.path.join( self.cfg['data_path'], self.cfg['train']))
        f = h5py.File(train_data, 'r')
        label_path = self.cfg['label_path']
        if os.path.exists(os.path.join(label_path, 'label.npy')):
            label_full = np.load(os.path.join(label_path, 'label.npy'))
        else:
            dataszie = len(f['label'])
            label_full = np.zeros(dataszie)
        for i in range(len(self.sample)):
            #label_full[self.sample[i]] = self.label[i]
            label_full[self.sample[i]] = dataset_train.label[self.sample[i]]
        np.save(os.path.join(label_path, 'label.npy'), label_full)
        # wx.MessageBox('Label Saved! Go to Action Recognition')
        # wx.MessageDialog(self, 'Label Saved!')

class Labeling_panel(wx.Panel):
    """Class to display basic GUI elements."""

    def __init__(self, parent, cfg, current_label, update_label):
        wx.Panel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        displays = (
            wx.Display(i) for i in range(wx.Display.GetCount())
        )  # Gets the number of displays
        screenSizes = [
            display.GetGeometry().GetSize() for display in displays
        ]  # Gets the size of each display
        index = 0  # For display 1.
        screenWidth = screenSizes[index][0]
        screenHeight = screenSizes[index][1]
        self.gui_size = (screenWidth * 0.4, screenHeight * 0.5)

        from openlabcluster.utils.auxiliaryfunctions import read_config
        self.cfg_file = cfg
        self.cfg = read_config(cfg)
        # methods to update plot
        self.current_label = current_label
        self.update_label = update_label

        self.total_labelled = 0

        class_name = self.cfg['class_name']

        self.SetSizeHints(
            wx.Size(self.gui_size)
        )  # This sets the minimum size of the GUI. It can scale now!
        ###################################################################################################################################################

        # Spliting the frame into top and bottom panels. Bottom panels contains the widgets. The top panel is for showing images and plotting!

        #topSplitter = wx.SplitterWindow(self)
        vSplitter = wx.SplitterWindow(self)

        self.image_panel = ImagePanel(vSplitter, self.gui_size)
        # self.choice_panel = WidgetPanel(vSplitter)  # ScrollPanel(vSplitter)
        self.choice_panel = ScrolledPanel(vSplitter)  # ScrollPanel(vSplitter)
        vSplitter.SplitVertically(
            self.image_panel, self.choice_panel, sashPosition=self.gui_size[0] * 0.8
        )
        vSplitter.SetSashGravity(1)
        self.widget_panel = self.image_panel.widgetsizer  #WidgetPanel(topSplitter)
        # topSplitter.SplitHorizontally(
        #     vSplitter, self.widget_panel
        # )  # 0.9,, sashPosition=self.gui_size[1] * 0.83
        # topSplitter.SetSashGravity(0.91)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(vSplitter, 1, wx.EXPAND)
        self.SetSizer(sizer)
        # choice label
        self.checked = []
        self.log = wx.TextCtrl(self.choice_panel, -1, style=wx.TE_MULTILINE, )
        self.list = CheckListCtrl(self.choice_panel, self.gui_size[0]*0.78, self.gui_size[1]*0.8)
        self.list.InsertColumn(0, 'Class name', width=180)
        self.list.InsertColumn(1, 'C')
        self.list.OnCheckItem = self.OnCheckItem

        list_sizer = BoxSizer()

        for i in range(len(class_name)):
            index = self.list.InsertItem(sys.maxsize, class_name[i])
            self.list.SetItem(index, 1, str(i+1))
        list_sizer.Add(self.list)
        
        self.choice_panel.SetSizer(list_sizer)

        self.choice_panel.SetupScrolling()

        self.pre = wx.Button(self.image_panel, id=wx.ID_ANY, label="   <<Previous<<   ")
        self.widget_panel.Add(self.pre, 1, wx.EXPAND)
        self.pre.Bind(wx.EVT_BUTTON, self.previous)
        self.image_panel.renew_sizer()

        self.prev = wx.Button(self.image_panel, id=wx.ID_ANY, label="Play")
        self.widget_panel.Add(self.prev, 1, wx.EXPAND)
        self.prev.Bind(wx.EVT_BUTTON, self.replay)
        self.prev.Enable(True)
        self.image_panel.renew_sizer()

        self.next_btn = wx.Button(self.image_panel, id=wx.ID_ANY, label=">>Next>>")
        self.widget_panel.Add(self.next_btn, 1, wx.EXPAND)
        self.next_btn.Bind(wx.EVT_BUTTON, self.next)
        self.next_btn.Enable(True)
        self.image_panel.renew_sizer()
        # self.ok = wx.Button(self.widget_panel, label="Save Labeling Result")
        # widgetsizer.Add(self.ok, 1, wx.ALL, 15)
        # self.ok.Bind(wx.EVT_BUTTON, self.savelabel)


    def OnCheckItem(self, index, flage):
        print('here')
        if len(self.checked):
            if self.checked[0] == index:
                self.list.CheckItem(self.checked[0], False)
                self.checked = []
            else:
                self.list.CheckItem(index, True)
                self.list.CheckItem(self.checked[0], False)
                self.checked = [index]
                self.label[self.current] = index + 1
        else:
            self.list.CheckItem(index, True)
            self.checked = [index]
            self.label[self.current] = index + 1
        print('video_name:%s' % self.videpaths[self.sample[self.current]])

    def animate(self, i):
        self.videohandle.set_array(self.imgs[i])
        # return self.videohandle,
        #self.videohandle.set_array(self.imgs[i])
        return self.videohandle,

        #self.videohandle = self.image_panel.axes.plot(np.array([1,2,3]), np.array([1,2,3])**i)

    def load_video(self):
        self.current = 0
        print('current from load video', self.current)
        from openlabcluster.utils.auxiliaryfunctions import read_config
        self.cfg = read_config(self.cfg_file)
        if 'selected_path' in self.cfg.keys():
            self.sample = np.load(self.cfg['selected_path'])
            self.current_label(self.sample[self.current])
            self.label = np.zeros(len(self.sample))

        else:
            wx.MessageBox('Save Label First!')

        # get all images for a video
        if self.cfg['train_videolist'].endswith('.text') or self.cfg['train_videolist'].endswith('.txt'):
            with open(self.cfg['train_videolist'], 'r') as f:
                self.videpaths = f.readlines()
            # selection start from self.current so set 0 here
            print(self.cfg['train_videolist'])
            print(self.sample[self.current])
            path = self.videpaths[self.sample[self.current]][:-1]
            print(path)
            cap = cv2.VideoCapture(path)
            self.imgs = []
            while (cap.isOpened()):
                ret, frame = cap.read()
                if ret:
                    self.imgs.append(frame)
                else:
                    break
        elif self.cfg['train_videolist'].endswith('.npy'):
            self.videpaths = np.load(self.cfg['train_videolist'], allow_pickle=True)
            path = self.videpaths[self.sample[self.current]]
            self.imgs = []
            for i in range(len(path)):
                self.imgs.append(cv2.imread(path[i]))

        if len(self.imgs) > 0:
            self.videohandle = self.image_panel.axes.imshow(self.imgs[0])

        print(len(self.imgs))
        animation.FuncAnimation(self.image_panel.figure, self.animate, frames=len(self.imgs),
                                interval=1, blit=True, repeat=False)
        self.image_panel.canvas.draw_idle()


    def next(self, event):
        print('current from next', self.current)
        if not len(self.checked):
            return

        self.current += 1
        self.total_labelled += 1

        print('current', self.current)
        print('len(self.label)', len(self.label))


        if self.current < len(self.label):
            self.current_label(self.sample[self.current])
            self.update_label(self.sample[self.current-1])
            if len(self.checked):
                self.list.CheckItem(self.checked[0], False)
            if self.cfg['train_videolist'].endswith('.text') or self.cfg['train_videolist'].endswith('.txt'):
                path = self.videpaths[self.current][:-1]
                cap = cv2.VideoCapture(path
                                       )
                self.imgs = []
                while (cap.isOpened()):
                    ret, frame = cap.read()
                    if ret:
                        self.imgs.append(frame)
                    else:
                        break
            elif self.cfg['train_videolist'].endswith('.npy'):
                self.videpaths = np.load(self.cfg['train_videolist'], allow_pickle=True)
                path = self.videpaths[self.sample[self.current]]
                self.imgs = []
                for i in range(len(path)):
                    self.imgs.append(cv2.imread(path[i]))


            self.videohandle = self.image_panel.axes.imshow(self.imgs[0])
            print(len(self.imgs))
            animation.FuncAnimation(self.image_panel.figure, self.animate, frames=len(self.imgs),
                                    interval=1, blit=True, repeat=False)
        else:
            wx.MessageBox(
                "This is the End of Sampling list",
                "Error",
                wx.OK | wx.ICON_ERROR,
            )
            return

    def previous(self, event):

        self.current -= 1
        if self.current >=0:
            self.current_label(self.sample[self.current])
            if len(self.checked):
                self.list.CheckItem(self.checked[0], False)
            if self.cfg['train_videolist'].endswith('.text') or self.cfg['train_videolist'].endswith('.txt'):
                path = self.videpaths[self.current][:-1]
                cap = cv2.VideoCapture(path
                                       )
                self.imgs = []
                while (cap.isOpened()):
                    ret, frame = cap.read()
                    if ret:
                        self.imgs.append(frame)
                    else:
                        break
            elif self.cfg['train_videolist'].endswith('.npy'):
                self.videpaths = np.load(self.cfg['train_videolist'], allow_pickle=True)
                path = self.videpaths[self.sample[self.current]]
                self.imgs = []
                for i in range(len(path)):
                    self.imgs.append(cv2.imread(path[i]))


            self.videohandle = self.image_panel.axes.imshow(self.imgs[0])
            print(len(self.imgs))
            animation.FuncAnimation(self.image_panel.figure, self.animate, frames=len(self.imgs),
                                    interval=1, blit=True, repeat=False)
        else:
            wx.MessageBox(
                "This is the End of Sampling list",
                "Error",
                wx.OK | wx.ICON_ERROR,
            )
            return

    def replay(self, event):
        if len(self.imgs) == 0:
            wx.MessageDialog(self, 'Load video first', 'Error', style=wx.OK | wx.CENTRE)
        else:
            animation.FuncAnimation(self.image_panel.figure, self.animate, frames=len(self.imgs),
                                    interval=1, blit=True, repeat=False)

    def savelabel(self):
        from openlabcluster.training_utils.ssl.data_loader import UnsupData, get_data_paths
        
        dataset_train = UnsupData(get_data_paths('', self.cfg['data_path'], self.cfg['train']))

        label_path = os.path.join(self.cfg['project_path'], self.cfg['label_path'])
        if not os.path.exists(label_path):
            os.mkdir(label_path)
        if os.path.exists(os.path.join(label_path, 'label.npy')):
            label_full = np.load(os.path.join(label_path, 'label.npy'))
        else:
            import h5py

            train_data = get_data_paths('', self.cfg['data_path'], self.cfg['train'])

            datasize = 0

            for train_data_item in train_data:
                f = h5py.File(train_data_item, 'r')

                if 'label' in list(f.keys()):
                    datasize += len(f['label'])
                else:
                    datasize += 1

            label_full = np.zeros(datasize)

        for i in range(len(self.sample)):
            print('sample length', len(self.sample))
            label_full[self.sample[i]] = self.label[i]
            #label_full[self.sample[i]] = dataset_train.label[self.sample[i]]
            print('save sample %d with label %d' %(self.sample[i], self.label[i]))
        
        #label_full[self.sample[self.current]] = self.label[self.current]
        np.save(os.path.join(label_path, 'label.npy'), label_full)
        # wx.MessageBox('Label Saved! Go to Action Recognition')
        # wx.MessageDialog(self, 'Label Saved!')


class video_display_window(wx.Panel):
    """Class to display basic GUI elements."""
    def __init__(self, parent, gui_size, cfg, **kwargs):
        # h = gui_size[0] / 5
        # w = gui_size[1] / 4
        wx.Panel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)

        self.figure = Figure()
        self.axes = self.figure.add_subplot(1, 1, 1)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.orig_xlim = []
        self.orig_ylim = []
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.axes.set_axis_off()
        self.Fit()
        self.cfg = cfg
        # methods to update plot

    def animate(self, i, vid_id):
        if vid_id == self.animation_vid_id:
            self.videohandle.set_array(self.imgs[i])
        return self.videohandle,

    def load_video(self, sequence_id):
        fps = 10
        if type(self.cfg['train_videolist']) is str: # TODO: this line should be removed 
            if self.cfg['train_videolist'].endswith('.text') or self.cfg['train_videolist'].endswith('.txt'):
                with open(self.cfg['train_videolist'], 'r') as f:
                    self.videpaths = f.readlines()
                # selection start from self.current so set 0 here
                path = self.videpaths[sequence_id].replace('\n', '').encode('ascii', 'ignore').decode('utf-8')
                cap = cv2.VideoCapture(path)
                fps = cap.get(cv2.CAP_PROP_FPS)
                self.imgs = []
                while (cap.isOpened()):
                    ret, frame = cap.read()
                    if ret:
                        self.imgs.append(frame)
                    else:
                        break
            elif self.cfg['train_videolist'].endswith('.npy'):
                self.videpaths = np.load(self.cfg['train_videolist'], allow_pickle=True)
                paths = self.videpaths[sequence_id]
                self.imgs = []
                for i in range(len(paths)):
                    self.imgs.append(cv2.imread(paths[i]))

        try:
            self.videohandle = self.axes.imshow(self.imgs[0])
        except:
            wx.MessageBox("Failed to load video", 'Error', wx.OK | wx.ICON_ERROR)

        print(len(self.imgs))
        self.animation_vid_id = np.random.randint(0, 1000000)
        self.animation = animation.FuncAnimation(self.figure, self.animate, frames=len(self.imgs),
                                interval=1000/fps, blit=True, repeat=False, fargs=(self.animation_vid_id,))
        self.canvas.draw_idle()

def show(cfg, sample):
    app = wx.App(redirect=0)
    GUI = PlotGUI(None, cfg, sample)
    GUI.Show()
    app.MainLoop()


if __name__ == '__main__':
    cfg = '/home/ws2/Documents/jingyuan/IC_GUI/deeplabcut/gui/demo-j-2021-02-03/config.yaml'
    sample = '/home/ws2/Documents/jingyuan/IC_GUI/deeplabcut/gui/demo-j-2021-02-03/sample/label2.npy'
    app = wx.App(redirect=0)
    GUI = PlotGUI(None, cfg, sample)
    GUI.Show()
    app.MainLoop()





