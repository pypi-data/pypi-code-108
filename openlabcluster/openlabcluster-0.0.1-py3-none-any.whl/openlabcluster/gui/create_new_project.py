"""
DeepLabCut2.0 Toolbox (deeplabcut.org)
© A. & M. Mathis Labs
https://github.com/AlexEMG/DeepLabCut
Please see AUTHORS for contributors.

https://github.com/AlexEMG/DeepLabCut/blob/master/AUTHORS
Licensed under GNU Lesser General Public License v3.0

"""

import os
import numpy as np
import platform
import pydoc
from re import T
import subprocess
import sys
import webbrowser
import traceback

import wx
import wx.lib.scrolledpanel


#from openlabcluster.gui.sample_labeling_new import
import openlabcluster
from openlabcluster.gui.train_network import Train_network
from openlabcluster.utils import auxiliaryfunctions
from openlabcluster.training_utils.ssl.data_loader import DataFileLoadingError, FeatureNameKeyError, add_videonames_to_h5, downsample_frames, get_data_list, get_data_paths, save_compiled_h5_datafile
from openlabcluster.gui.sample_labeling_new import selection_method_options

media_path = os.path.join(openlabcluster.__path__[0], "gui", "media")
logo = os.path.join(media_path, "logo.png")


# class Create_new_project(wx.Panel):
class Create_new_project(wx.lib.scrolledpanel.ScrolledPanel):

    def __init__(self, parent, gui_size, statusBar):
        self.gui_size = gui_size
        self.parent = parent
        self.statusBar = statusBar
        h = gui_size[0]
        w = gui_size[1]
        print('size', h ,w)
        # wx.Panel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER, size=(h, w))
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER, size=(h, w))
        # variable initilization
        self.filelist = []
        self.filelistnew = []
        self.traininglist = None
        self.testinglist = None
        self.trainvideo_list = None
        self.testvideo_list = None
        self.dir = None
        self.copy = False
        self.cfg = None
        self.loaded = False

        # design the panel
        self.sizer = wx.GridBagSizer(14, 15)

        title_text = "OpenLabCluster - Step 1. Create a New Project or Load a Project"

        documentation_text = """Documentation:
        1. Project Name - name for the project
        2. If you just have videos, use DeepLabCut to extract keypoints. If you already have DeepLabCut-like formatted files,
            select them with "Load Keypoints Data"
        3. Select your videos with "Choose Training Videos List". There should be one video for each keypoint file. Make sure
            the videos and keypoints files are in the same order.
        4. Optionally set a directory for the project to be created (the default is the working directory of this project).
        5. Keep the box checked if you have a GPU in your computer you would like to use to train the model.
        6. Enter the feature length (number of body parts * number of dimensions per body part, i.e. (x,y) -> 2).
        7. Press "Okay", then "Okay" again on the pop up box to create the project.
        8. If you would like to edit the config (i.e. change class names, change video cropping), press "Edit Config File"."""

        
        title = wx.StaticText(
            self, label=title_text, 
        )
        #font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.NORMAL)
        #title.SetFont(font)

        # documentation = wx.StaticText(
        #     self, label=documentation_text
        # )
        #
        documentation_sizer = wx.BoxSizer(orient=wx.VERTICAL)
        documentation_sizer.Add(title)
        # documentation_sizer.Add(documentation)

        self.sizer.Add(documentation_sizer, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=15)

        # Add logo of DLC
        # icon = wx.StaticBitmap(self, bitmap=wx.Bitmap(logo))
        # self.sizer.Add(icon, pos=(0,10), flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT,border=10)

        line = wx.StaticLine(self)
        self.sizer.Add(
            line, pos=(1, 0), span=(1, 15), flag=wx.EXPAND | wx.BOTTOM, border=5
        )

        # store radio box options
        self.new_project_rbo = "New Project"
        self.load_project_rbo = "Load Project"

        # Add all the options
        self.proj = wx.RadioBox(
            self,
            label="Please choose an option:",
            choices=[self.new_project_rbo, self.load_project_rbo],
            majorDimension=0,
            style=wx.RA_SPECIFY_COLS,
        )
        self.sizer.Add(self.proj, pos=(2, 0), span=(1, 2), flag=wx.LEFT, border=5)
        self.proj.Bind(wx.EVT_RADIOBOX, self.chooseOption)

        #        line = wx.StaticLine(self)
        #        self.sizer.Add(line, pos=(3, 0), span=(1, 8),flag=wx.EXPAND|wx.BOTTOM, border=10)



        self.proj_name = wx.StaticText(self, label="Project Name:")
        self.sizer.Add(self.proj_name, pos=(3, 0), flag=wx.TOP | wx.LEFT, border=10)

        self.proj_name_txt_box = wx.TextCtrl(self)
        self.sizer.Add(self.proj_name_txt_box, pos=(3, 1), span=(1, 5), flag=wx.TOP | wx.EXPAND, border=10)

        self.trds= wx.StaticText(self, label="Keypoints Data (launch DeepLabCut if you don't have data):")
        self.sizer.Add(self.trds, pos=(4, 0), flag=wx.TOP | wx.LEFT, border=10)

        self.launch_deeplabcut_btn = wx.Button(self, label="Launch DeepLabCut")
        self.sizer.Add(self.launch_deeplabcut_btn,  pos=(4, 1), span=(1, 1.5), flag=wx.TOP | wx.EXPAND, border=5)
        self.launch_deeplabcut_btn.Bind(wx.EVT_BUTTON, self.launch_deeplabcut)

        # self.launch_deeplabcut_btn.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnterdeeplabcut)
        # self.launch_deeplabcut_btn.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)

        self.sel_trds_label = "Load DeepLabCut Keypoints"
        self.sel_trds = wx.Button(self, label=self.sel_trds_label)
        self.sizer.Add(self.sel_trds, pos=(4, 2.5), span=(1,2), flag=wx.TOP | wx.EXPAND, border=5)
        self.sel_trds.Bind(wx.EVT_BUTTON, self.select_training_data)

        self.sel_pp_data_label = "Load Preprocessed Keypoints"
        self.sel_pp_data = wx.Button(self, label=self.sel_pp_data_label)
        self.sizer.Add(self.sel_pp_data, pos=(4, 4.5), span=(1,2), flag=wx.TOP | wx.EXPAND, border=5)
        self.sel_pp_data.Bind(wx.EVT_BUTTON, self.select_training_data)

        self.sel_data_btn_list = [self.sel_trds, self.sel_pp_data]
        self.sel_data_btn_lbl_list = [self.sel_trds_label, self.sel_pp_data_label]

        #self.sel_trds.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEntersel_trds)
        #self.sel_trds.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)

        self.trvl = wx.StaticText(self, label="Choose Training Videos List File:")
        self.sizer.Add(self.trvl, pos=(5, 0), flag=wx.TOP | wx.LEFT, border=10)

        self.sel_trvl = wx.Button(self, label="Choose Training Videos List")
        self.sizer.Add(
            self.sel_trvl, pos=(5, 1), span=(1, 5), flag=wx.TOP | wx.EXPAND, border=10
        )
        self.sel_trvl.Bind(wx.EVT_BUTTON, self.select_training_video_list)
        #self.sel_trvl.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEntersel_trvl)
        #self.sel_trvl.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)
        sb = wx.StaticBox(self, label="Optional Attributes")
        self.boxsizer = wx.StaticBoxSizer(sb, wx.VERTICAL)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        self.change_workingdir = wx.CheckBox(
            self, label="Select the directory where project will be created"
        )
        hbox2.Add(self.change_workingdir)
        hbox2.AddSpacer(20)
        self.change_workingdir.Bind(wx.EVT_CHECKBOX, self.activate_change_wd)
        self.sel_wd = wx.Button(self, label="Browse")
        self.sel_wd.Enable(False)
        self.sel_wd.Bind(wx.EVT_BUTTON, self.select_working_dir)
        hbox2.Add(self.sel_wd, 0, wx.ALL, -1)
        self.sel_wd_text = wx.TextCtrl(self, size=(400,20))
        hbox2.Add(self.sel_wd_text, 0, wx.LEFT, border=10)
        self.boxsizer.Add(hbox2)

        self.sizer.Add(
            self.boxsizer,
            pos=(6, 0),
            span=(1, 10),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=10,
        )

        self.hardware_type = wx.CheckBox(self, label="Check to use GPU", )
        self.sizer.Add(self.hardware_type, pos=(7, 0), span=(1, 1), flag=wx.TOP | wx.LEFT, border=10)
        self.hardware_type.SetValue(True)

        self.feature_length = wx.StaticText(self, label="Feature length (int)")
        self.sizer.Add(self.feature_length, pos=(7, 1), span=(1, 1), flag=wx.TOP | wx.LEFT, border=10)
        self.feature_length_txt_box = wx.TextCtrl(self)
        self.sizer.Add(self.feature_length_txt_box, pos=(7, 2), span=(1, 1), flag=wx.TOP | wx.EXPAND, border=10)

        self.cfg_text = wx.StaticText(self, label="Select the Config File")
        self.sizer.Add(self.cfg_text, pos=(8, 0), flag=wx.TOP | wx.EXPAND, border=15)

        if sys.platform == "darwin":
            self.sel_config = wx.FilePickerCtrl(
                self,
                path="",
                style=wx.FLP_USE_TEXTCTRL,
                message="Choose the config.yaml file",
                wildcard="*.yaml",
                size=(300,50),
            )
        else:
            self.sel_config = wx.FilePickerCtrl(
                self,
                path="",
                style=wx.FLP_USE_TEXTCTRL,
                message="Choose the config.yaml file",
                wildcard="config.yaml",
            )

        self.sizer.Add(self.sel_config, pos=(8, 1), span=(1, 7), flag=wx.TOP | wx.EXPAND, border=5)
        self.sel_config.Bind(wx.EVT_BUTTON, self.create_new_project)
        self.sel_config.SetPath("")

        # Hide the button as this is not the default option
        self.sel_config.Hide()
        self.cfg_text.Hide()
        
        self.advanced_options = wx.CollapsiblePane(self, wx.ID_ANY, "Advanced Options")
        self.advanced_options_sizer = wx.GridBagSizer(8, 8)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_advanced_options_change)
        advanced_options_win = self.advanced_options.GetPane()

        select_text = wx.StaticBox(advanced_options_win, label="Selection Method")
        selectboxsizer = wx.StaticBoxSizer(select_text, wx.VERTICAL)
        self.select_choice = wx.ComboBox(advanced_options_win, style=wx.CB_READONLY)
        self.select_choice.Set(selection_method_options)
        self.select_choice.SetValue(selection_method_options[0])
        selectboxsizer.Add(self.select_choice)

        self.advanced_options_sizer.Add(selectboxsizer, pos=(0,0))
        advanced_options_win.SetSizer(self.advanced_options_sizer)
        self.sizer.Add(self.advanced_options, pos=(9, 0))

        # start the project go to clustering step
        self.ok = wx.Button(self, label="Ok")
        self.sizer.Add(self.ok, pos=(9, 5))
        self.ok.Bind(wx.EVT_BUTTON, self.create_new_project)
        #self.ok.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnterok)
        #self.ok.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)

        self.help_button = wx.Button(self, label="Help")
        self.sizer.Add(self.help_button, pos=(2, 3), flag=wx.LEFT, border=10)
        self.help_button.Bind(wx.EVT_BUTTON, self.help_function)

        self.edit_config_file = wx.Button(self, label="Edit Config File")
        self.sizer.Add(self.edit_config_file, pos=(9, 3))
        self.edit_config_file.Bind(wx.EVT_BUTTON, self.edit_config)
        self.edit_config_file.Enable(False)

        self.reset = wx.Button(self, label="Reset")
        self.sizer.Add(self.reset, pos=(2, 5), flag=wx.BOTTOM | wx.RIGHT, border=10)
        self.reset.Bind(wx.EVT_BUTTON, self.reset_project)
        #self.reset.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnterreset)
        #self.reset.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)
        self.sizer.AddGrowableCol(2)

        self.SetSizer(self.sizer)
        self.sizer.Fit(self)
        self.SetupScrolling()
        self.SetAutoLayout(1)

        self.Scroll(0,0)

    def launch_deeplabcut(self, event):
        from sys import platform
        if platform == "linux" or platform == "linux2":
            # linux
            command = 'python -m deeplabcut'
        elif platform == "darwin":
            # OS X
            command = 'pythonw -m deeplabcut'
        elif platform == "win32":
            # Windows...
            # TODO: MOISHE: NO IDEA!!!!!
            command = 'python -m deeplabcut'
        
        import subprocess
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)

    def select_new_videos(self, event):
        """
        Selects the videos from the directory
        """
        cwd = os.getcwd()
        dlg = wx.FileDialog(
            self, "Select new videos to load", cwd, "", "*.*", wx.FD_MULTIPLE
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.addvids = dlg.GetPaths()
            self.filelistnew = self.filelistnew + self.addvids
            self.sel_vids_new.SetLabel(
                "Total %s Videos selected" % len(self.filelistnew)
            )

    def help_function(self, event):

        # filepath = "help.txt"
        # f = open(filepath, "w")
        # sys.stdout = f
        # fnc_name = "openlabcluster.create_new_project"
        # pydoc.help(fnc_name)
        # f.close()
        # sys.stdout = sys.__stdout__
        # help_file = open("help.txt", "r+")
        # help_text = help_file.read()
        help_text = """Documentation:
        1. Project Name - name for the project
        2. If you just have videos, use DeepLabCut to extract keypoints. If you already have DeepLabCut-like formatted files,
            select them with "Load Keypoints Data"
        3. Select your videos with "Choose Training Videos List". There should be one video for each keypoint file. Make sure
            the videos and keypoints files are in the same order.
        4. Optionally set a directory for the project to be created (the default is the working directory of this project).
        5. Keep the box checked if you have a GPU in your computer you would like to use to train the model.
        6. Enter the feature length (number of body parts * number of dimensions per body part, i.e. (x,y) -> 2).
        7. Press "Okay", then "Okay" again on the pop up box to create the project.
        8. If you would like to edit the config (i.e. change class names, change video cropping), press "Edit Config File"."""
        wx.MessageBox(help_text, "Help", wx.OK | wx.ICON_INFORMATION)
        # help_file.close()
        # os.remove("help.txt")

    def on_advanced_options_change(self, event):
        self.FitInside()

    def chooseOption(self, event):
        def show_hide_load_project(should_show:bool):
            self.proj_name_txt_box.Enable(should_show)
            self.proj_name.Enable(should_show)
            self.trds.Enable(should_show)
            self.trvl.Enable(should_show)
            self.sel_trvl.Enable(should_show)
            self.sel_trds.Enable(should_show)
            self.sel_pp_data.Enable(should_show)
            self.change_workingdir.Enable(should_show)
            self.launch_deeplabcut_btn.Enable(should_show)
            self.hardware_type.Enable(should_show)
            self.feature_length.Enable(should_show)
            self.feature_length_txt_box.Enable(should_show)
            self.sel_wd_text.Enable(should_show)

        def show_hide_config(should_show:bool):
            if should_show:
                self.sel_config.Show()
                self.cfg_text.Show()
            else:
                if self.sel_config.IsShown():
                    self.sel_config.Hide()
                    self.cfg_text.Hide()

        if self.proj.GetStringSelection() == self.load_project_rbo:

            if self.loaded:
                self.sel_config.SetPath(self.cfg)

            show_hide_load_project(False)
            show_hide_config(True)

            self.sizer.Fit(self)
        else:
            show_hide_load_project(True)
            show_hide_config(False)

            self.SetSizer(self.sizer)
            self.sizer.Fit(self)

        self.parent.Parent.Layout()

    def OnMouseEnterdeeplabcut(self, event):
        self.statusBar.SetStatusText("Start DeepLabCut to acquire body keypoints position.")

    def OnMouseLeave(self, event):
        self.statusBar.SetStatusText("")

    def OnMouseEntersel_trvl(self, event):
        self.statusBar.SetStatusText("Choose videos or videolist file corresponding to keypoints.")

    def OnMouseEntersel_trds(self, event):
        self.statusBar.SetStatusText("Load keypoints files.")

    def OnMouseEnterok(self, event):
        self.statusBar.SetStatusText('Go the the next step: clustering.')

    def OnMouseEnterreset(self, reset):
        self.statusBar.SetStatusText('Reset all the inputs.')


    def edit_config(self, event):
        """
        """
        if self.cfg != "":
            # For mac compatibility
            if platform.system() == "Darwin":
                self.file_open_bool = subprocess.call(["open", self.cfg])
                self.file_open_bool = True
            else:
                self.file_open_bool = webbrowser.open(self.cfg)

            if self.file_open_bool:
                pass
            else:
                raise FileNotFoundError("File not found!")

    def select_videos(self, event:wx.Event):
        """
        Selects the videos from the directory
        """
        cwd = os.getcwd()
        dlg = wx.FileDialog(
            self, "Select videos to add to the project", cwd, "", "*.*", wx.FD_MULTIPLE
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.vids = dlg.GetPaths()
            self.filelist = self.filelist + self.vids
            self.sel_vids.SetLabel("Total %s Videos selected" % len(self.filelist))

    def select_training_data(self, event:wx.Event):
        """
        Selects the videos from the directory
        """
        cwd = os.getcwd()
        dlg = wx.FileDialog(
            self, "Select training data for training", cwd, "", "*.*", wx.FD_MULTIPLE
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.traininglist = dlg.GetPaths()

            for btn, lbl in zip(self.sel_data_btn_list, self.sel_data_btn_lbl_list):
                btn.SetLabel(lbl)

            event.GetEventObject().SetLabel(f"{len(self.traininglist)} files selected")

            if event.GetEventObject() is self.sel_pp_data:
                self.traininglist = self.traininglist[0]

    def select_testing_data(self, event):
        """
        Selects the videos from the directory
        """
        cwd = os.getcwd()
        dlg = wx.FileDialog(
            self, "Select testing data for testing", cwd, "", "*.*", wx.FD_MULTIPLE
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.testinglist = dlg.GetPaths()

            self.sel_teds.SetLabel("Test selected: %s" % self.testinglist[0])

    def select_training_video_list(self, event):
        """
        Selects the videos from the directory
        """
        cwd = os.getcwd()
        dlg = wx.FileDialog(
            self, "Select training data for training", cwd, "", "*.*", wx.FD_MULTIPLE
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.trainvideo_list = dlg.GetPaths()
            self.sel_trvl.SetLabel(f"{len(self.trainvideo_list)} videos selected")

    def select_testing_video_list(self, event):
        """
        Selects the videos from the directory
        """
        cwd = os.getcwd()
        dlg = wx.FileDialog(
            self, "Select testing video list", cwd, "", "*.*", wx.FD_MULTIPLE
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.testvideo_list = dlg.GetPaths()
            self.sel_tevl.SetLabel("Test Video List selectetd: %s" % (self.testvideo_list[0]))

    def activate_copy_videos(self, event):
        """
        Activates the option to copy videos
        """
        self.change_copy = event.GetEventObject()
        if self.change_copy.GetValue() == True:
            self.copy = True
        else:
            self.copy = False

    def activate_change_wd(self, event):
        """
        Activates the option to change the working directory
        """
        self.change_wd = event.GetEventObject()
        if self.change_wd.GetValue() == True:
            self.sel_wd.Enable(True)
        else:
            self.sel_wd.Enable(False)

    def select_working_dir(self, event):
        cwd = os.getcwd()
        dlg = wx.DirDialog(
            self,
            "Choose the directory where your project will be saved:",
            cwd,
            style=wx.DD_DEFAULT_STYLE,
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.dir = dlg.GetPath()
            self.sel_wd_text.SetLabelText(self.dir)

    def create_new_project(self, event):
        """
        Finally create the new project
        """
        if self.sel_config.IsShown():
            self.cfg = self.sel_config.GetPath()
            if self.cfg == "":
                wx.MessageBox(
                    "Please choose the config.yaml file to load the project",
                    "Error",
                    wx.OK | wx.ICON_ERROR,
                )
                self.loaded = False
            else:
                wx.MessageBox("Project Loaded! Wait for Loading Model", "Info", wx.OK | wx.ICON_INFORMATION)
                self.loaded = True
                self.edit_config_file.Enable(True)
        else:
           # load early project
            self.task = self.proj_name_txt_box.GetValue()

            if self.task != ""  and self.traininglist != None and self.trainvideo_list!=None :
                self.cfg = openlabcluster.create_new_project(
                    self.task,
                    self.traininglist,  
                    # self.trainvideo_list[0], 
                    self.trainvideo_list, 
                    self.dir, 
                    working_directory=self.dir,
                    copy_videos=self.copy,
                    use_gpu=self.hardware_type.GetValue(),
                    feature_length=int(self.feature_length_txt_box.GetValue()),
                    sample_method=self.select_choice.GetStringSelection(),
                )
            else:
                wx.MessageBox(
                    "Some of the enteries are missing.\n\nMake sure that the task and experimenter name are specified and training data are selected!",
                    "Error",
                    wx.OK | wx.ICON_ERROR,
                )
                self.cfg = False
            if self.cfg:
                wx.MessageBox(
                    "New Project Created", "Info", wx.OK | wx.ICON_INFORMATION
                )
                self.loaded = True
                self.edit_config_file.Enable(True)

        # Remove the pages in case the user goes back to the create new project and creates/load a new project
        if self.parent.GetPageCount() > 3:
            for i in range(2, self.parent.GetPageCount()):
                self.parent.RemovePage(2)
                self.parent.Layout()

        # Add all the other pages
        if self.loaded:
            self.edit_config_file.Enable(True)
            cfg = auxiliaryfunctions.read_config(self.cfg)

            # load data
            train_files = 'train_files'

            if cfg.get(train_files) is not None:
                # deeplabcluster data turn deeplabcut files into one preprocessed file
                paths = get_data_paths(cfg["project_path"], cfg['data_path'], cfg[train_files])
                
                try:
                    data_list, label_list, datafile_list = get_data_list(paths, keypoint_names=cfg.get('feature_names'), return_video=True)
                    
                    if (len(data_list) == 0):
                        # data doesnt exist or its empty
                        wx.MessageBox("Empty dataset", 'Error', wx.OK | wx.ICON_ERROR)  
                        return
                except FeatureNameKeyError as e:
                    wx.MessageBox("Following feature_name doesn't exist in the dataset:\n" + str(e) + "\n\nPlease check your dataset and/or your config", 'Error', wx.OK | wx.ICON_ERROR)  
                    return  
                except DataFileLoadingError as e:
                    # failed to load a data file
                    wx.MessageBox("File failed to load: \n" + str(e) + "\n\nPlease check that it exists and it can be loaded", 'Error', wx.OK | wx.ICON_ERROR)  
                    return

                data_list, label_list, datafile_list = downsample_frames(data_list, label_list, datafile_list, cfg['train_videos'], cfg['video_path'], cfg['train_videolist'],
                    is_multi_action=not cfg['is_single_action'], single_action_crop=cfg['single_action_crop'], multi_action_crop=cfg['multi_action_crop']
                ) # multi_action_crop how to crop the video with multi-action    single_action_crop downsample the video.
                save_compiled_h5_datafile(os.path.join(cfg['data_path'], cfg['train']), data_list, label_list, datafile_list)
            else:
                # TODO: insert video names into compiled h5 file
                if cfg['train_videolist'].endswith('.npy'):
                    frame_names = np.load(cfg['train_videolist'])
                    add_videonames_to_h5(os.path.join(cfg['data_path'], cfg['train']), frame_names[:,0].tolist())
                else:
                    with open(cfg['train_videolist'], 'r') as f:
                        video_list = f.readlines()
                        add_videonames_to_h5(os.path.join(cfg['project_path'], cfg['data_path'], cfg['train']), video_list)
                

            if self.parent.GetPageCount() < 3:
                # no clustering page set up
                try:
                    page6 = Train_network(self.parent, self.gui_size, self.cfg, self.statusBar)
                    #page6 = Sample_labeling(self.parent, self.gui_size, self.cfg)
                except Exception as e:
                    wx.MessageBox(str(e), 'Error', wx.OK | wx.ICON_ERROR)  
                    print(traceback.format_exc())
                    return

                self.parent.AddPage(page6, "Cluster Data")

                self.edit_config_file.Enable(True)

    def add_videos(self, event):
        print("adding new videos to be able to label ...")
        self.cfg = self.sel_config.GetPath()
        if len(self.filelistnew) > 0:
            self.filelistnew = self.filelistnew + self.addvids
            openlabcluster.add_new_videos(self.cfg, self.filelistnew)
        else:
            print("Please select videos to add first. Click 'Load New Videos'...")

    def reset_project(self, event):
        self.loaded = False
        if self.sel_config.IsShown():
            self.sel_config.SetPath("")
            self.proj.SetSelection(0)
            self.sel_config.Hide()
            self.cfg_text.Hide()

        self.sel_config.SetPath("")
        self.proj_name_txt_box.SetValue("")
        # self.exp_txt_box.SetValue("")
        self.filelist = []
        # self.sel_vids.SetLabel("Load Videos")
        self.dir = os.getcwd()
        self.edit_config_file.Enable(False)
        self.proj_name.Enable(True)
        self.proj_name_txt_box.Enable(True)

        self.change_workingdir.Enable(True)
        # self.copy_choice.Enable(True)

        try:
            self.change_wd.SetValue(False)
        except:
            pass
        try:
            self.change_copy.SetValue(False)
        except:
            pass
        self.sel_wd.Enable(False)
