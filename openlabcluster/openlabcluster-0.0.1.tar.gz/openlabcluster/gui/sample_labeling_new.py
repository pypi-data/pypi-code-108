"""
DeepLabCut2.0 Toolbox (deeplabcut.org)
© A. & M. Mathis Labs
https://github.com/AlexEMG/DeepLabCut
Please see AUTHORS for contributors.

https://github.com/AlexEMG/DeepLabCut/blob/master/AUTHORS
Licensed under GNU Lesser General Public License v3.0

"""

import os
import traceback
import cv2

import wx
import wx.lib.scrolledpanel

import openlabcluster
from openlabcluster.training_utils.ssl.data_loader import get_data_list
from openlabcluster.utils import auxiliaryfunctions
from wx.lib.pubsub import pub
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score
from sklearn.cluster import KMeans

media_path = os.path.join(openlabcluster.__path__[0], "gui", "media")
logo = os.path.join(media_path, "logo.png")

selection_method_options = ["Cluster Center", "Cluster Random", "Cluter Uncertainty", "Uniform", "Core Set"]

# class Sample_labeling(wx.Panel):
class Sample_labeling(wx.lib.scrolledpanel.ScrolledPanel):
    """
    """

    def __init__(self, parent, gui_size, cfg):
        """Constructor"""
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent=parent)
        self.progress = 0
        self.method = "automatic"
        self.config = cfg
        self.sizer = wx.GridBagSizer(9, 5)
        text = wx.StaticText(self, label="OpenLabCluster - Step 3. Behavior Identification with Sampled Annotation")
        self.sizer.Add(text, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=10)
        # Add logo of DLC
        icon = wx.StaticBitmap(self, bitmap=wx.Bitmap(logo))
        self.sizer.Add(
            icon, pos=(0, 4), flag=wx.TOP | wx.RIGHT | wx.ALIGN_RIGHT, border=5
        )

        line1 = wx.StaticLine(self)
        self.sizer.Add(
            line1, pos=(1, 0), span=(1, 5), flag=wx.EXPAND | wx.BOTTOM, border=10
        )

        # select model
        sb = wx.StaticBox(self, label="")
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL) # selection and plot parameter
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL) # used for metrics 
        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL) # gauge
        self.hbox6 = wx.BoxSizer(wx.HORIZONTAL) # training parameter
        self.config_file = auxiliaryfunctions.read_config(self.config)

        select_text = wx.StaticBox(self, label="Selection Method")
        selectboxsizer = wx.StaticBoxSizer(select_text, wx.VERTICAL)
        self.select_choice = wx.ComboBox(self, style=wx.CB_READONLY)
        self.select_choice.Set(selection_method_options)
        self.select_choice.SetValue(self.config_file['sample_method'])
        self.select_choice.Bind(wx.EVT_COMBOBOX, self.nextSelection)
        selectboxsizer.Add(self.select_choice, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        self.hbox1.Add(selectboxsizer, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)

        trainingindex_box = wx.StaticBox(self, label="# Samples per Selection")
        trainingindex_boxsizer = wx.StaticBoxSizer(trainingindex_box, wx.VERTICAL)
        self.trainingindex = wx.SpinCtrl(self, value=str(self.config_file.get('label_budget', 10)), min=1)
        trainingindex_boxsizer.Add(self.trainingindex, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        self.hbox1.Add(trainingindex_boxsizer, 10, wx.EXPAND | wx.TOP | wx.BOTTOM|wx.RIGHT, 2)

        epoch_box = wx.StaticBox(self, label="Maximum Epochs")
        epoch_boxizer = wx.StaticBoxSizer(epoch_box, wx.VERTICAL)
        self.epoch = wx.SpinCtrl(self, value="10", min=1)
        epoch_boxizer.Add(self.epoch, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        self.hbox1.Add(epoch_boxizer, 10, wx.EXPAND | wx.TOP | wx.BOTTOM|wx.RIGHT, 2)

        dim_text = wx.StaticBox(self, label="Cluster Map Dimension")
        dimboxsizer = wx.StaticBoxSizer(dim_text, wx.VERTICAL)
        self.dim_choice = wx.ComboBox(self, style=wx.CB_READONLY)
        self.dim_choice.Bind(wx.EVT_COMBOBOX, self.update_image_panel)
        options = ["2d", "3d"]
        self.dim_choice.Set(options)
        self.dim_choice.SetValue("2d")
        dimboxsizer.Add(self.dim_choice, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        self.hbox1.Add(dimboxsizer, 10, wx.EXPAND | wx.TOP | wx.BOTTOM|wx.RIGHT, 2)

        reducer_text = wx.StaticBox(self, label="Dimension Reduction Method")
        reducerboxsizer = wx.StaticBoxSizer(reducer_text, wx.VERTICAL)
        self.reducer_choice = wx.ComboBox(self, style=wx.CB_READONLY)
        self.reducer_choice.Bind(wx.EVT_COMBOBOX, self.update_image_panel)
        reducer_options = ["PCA", "tSNE", "UMAP"]
        self.reducer_choice.Set(reducer_options)
        self.reducer_choice.SetValue("PCA")
        reducerboxsizer.Add(self.reducer_choice, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        self.hbox1.Add(reducerboxsizer, 10, wx.EXPAND | wx.TOP | wx.BOTTOM|wx.RIGHT, 2)

        # self.startselection = wx.Button(self, label="View and Select Samples")
        #
        # self.startselection.Bind(wx.EVT_BUTTON, self.selecting_samples)
        # self.hbox1.Add(self.startselection, 10, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)

        # label_path = wx.StaticText(self, label='Selected Sequence Path')
        # self.labpath_btn = wx.Button(self, label='Change Selected Sequence Path')
        # self.labpath_btn.Bind(wx.EVT_BUTTON, self.change_sampath)
        # if sys.platform == "darwin":
        #     self.sel_labelpath = wx.FilePickerCtrl(
        #         self,
        #         path="",
        #         style=wx.FLP_USE_TEXTCTRL,
        #         message="Choose the samply.npy file",
        #         wildcard="*.npy",
        #     )
        # else:
        #     self.sel_labelpath = wx.FilePickerCtrl(
        #         self,
        #         path="",
        #         style=wx.FLP_USE_TEXTCTRL,
        #         message="Choose the samply.npy file",
        #         wildcard="*.npy",
        #     )
        # self.sel_labelpath.Enable(False)

        # self.labeling = wx.Button(self, label='Annotate Samples')
        # self.labeling.Bind(wx.EVT_BUTTON, self.labeling_video
        #                    )


        self.sizer.Add(
            self.hbox1,
            pos=(2, 0),
            span=(1, 4),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=10,
        )

        self.metrics_box = wx.BoxSizer(wx.HORIZONTAL)
        
        font = wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.NORMAL)

        labelled_points = wx.StaticText(self, label=" points labelled")
        labelled_points_num = wx.StaticText(self, label="0")
        labelled_points_num.SetFont(font)

        unlabelled_points = wx.StaticText(self, label=" points unlabelled")
        unlabelled_points_num = wx.StaticText(self, label="0")
        unlabelled_points_num.SetFont(font)

        self.cal_har_index = wx.StaticText(self, label=" Calinski-Harabasz Index")
        self.cal_har_index_num = wx.StaticText(self, label="0")
        self.cal_har_index_num.SetFont(font)

        self.dav_bould_index = wx.StaticText(self, label=" Davies-Bouldin Index")
        self.dav_bould_index_num = wx.StaticText(self, label="0")
        self.dav_bould_index_num.SetFont(font)

        self.train_acc = wx.StaticText(self, label=" Training Accuracy")
        self.train_acc_num = wx.StaticText(self, label="0.00")
        self.train_acc_num.SetFont(font)

        self.metrics_box.Add(labelled_points_num,   flag=wx.TOP | wx.LEFT | wx.EXPAND, border=15)
        self.metrics_box.Add(labelled_points,       flag=wx.TOP | wx.EXPAND, border=15)
        self.metrics_box.Add(unlabelled_points_num, flag=wx.TOP | wx.LEFT | wx.EXPAND, border=15)
        self.metrics_box.Add(unlabelled_points,     flag=wx.TOP | wx.EXPAND, border=15)
        self.metrics_box.Add(self.cal_har_index_num,     flag=wx.TOP | wx.LEFT | wx.EXPAND, border=15)
        self.metrics_box.Add(self.cal_har_index,         flag=wx.TOP | wx.EXPAND, border=15)
        self.metrics_box.Add(self.dav_bould_index_num,   flag=wx.TOP | wx.LEFT | wx.EXPAND, border=15)
        self.metrics_box.Add(self.dav_bould_index,       flag=wx.TOP | wx.EXPAND, border=15)
        self.metrics_box.Add(self.train_acc,  flag=wx.TOP | wx.EXPAND, border=15 )
        self.metrics_box.Add(self.train_acc_num, flag=wx.TOP | wx.EXPAND, border=15)
        self.sizer.Add(self.metrics_box, pos=(3,0))

        pub.subscribe(self.updateProgress, "update")
        pub.subscribe(self.on_finish, "finish_iter")

        self.help_button = wx.Button(self, label="Help")
        #self.sizer.Add(self.help_button, pos=(8, 5), flag=wx.LEFT, border=10)
        self.help_button.Bind(wx.EVT_BUTTON, self.help_function)

        self.evaluation_button = wx.Button(self, label="Get Results")
        self.evaluation_button.Bind(wx.EVT_BUTTON, self.evaluation_function)

        # self.reset = wx.Button(self, label="Reset")
        # self.sizer.Add(
        #     self.reset, pos=(7, 5), span=(1, 1), flag=wx.BOTTOM | wx.RIGHT, border=10
        # )
        # self.reset.Bind(wx.EVT_BUTTON, self.reset_create_training_dataset)

        self.sizer.AddGrowableCol(2)
        #from deeplabcut.gui.train_network import ImagePanel
        from openlabcluster.gui.labeling_toolbox_ic import PlotGUI_panel
        from openlabcluster.gui.media.label_video import Labeling_panel
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

        #sb = wx.StaticBox(self, label="Interative Action Recognition")
        self.oper_1 = wx.BoxSizer(wx.HORIZONTAL)
        self.oper_2 = wx.BoxSizer(wx.HORIZONTAL)
        # modeltype is essentially based on value in config (one of "seq2seq", "semi_seq2seq"). It needs to be "semi_seq2seq to get class values"
        self.image_panel = PlotGUI_panel(self, self.config, self.select_choice.GetValue(), self.trainingindex.GetValue())
        self.video_panel = None
        
        def current_sample_wrapper(*args, **kwargs):
            self.image_panel.current_sample(*args, **kwargs)
            labelled_points_num.SetLabelText(str(self.video_panel.total_labelled))
            unlabelled_points_num.SetLabelText(str(self.image_panel.extracted.dataset_size_train - self.video_panel.total_labelled))
            self.metrics_box.Layout()
            self.sizer.Layout()
            self.Layout()
            # self.parent.Layout()

        # self.video_panel = Labeling_panel(self, self.config, self.image_panel.current_sample, self.image_panel.update_labeled) # every time click load video will reload the configure file
        self.video_panel = Labeling_panel(self, self.config, current_sample_wrapper, self.image_panel.update_labeled) # every time click load video will reload the configure file
        self.image_panel.initialize_video_coonection(self.video_panel.load_video)

        self.oper_1.Add(self.image_panel,8, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)
        self.oper_1.Add(self.video_panel,  12, wx.EXPAND | wx.TOP | wx.BOTTOM,10)

        self.gauge = wx.Gauge(self, wx.ID_ANY, self.config_file['su_epoch'])
        self.retrain = wx.Button(self, label='Perform Action Recognition')
        self.retrain.Bind(wx.EVT_BUTTON, self.retrain_network)

        # , wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL)

        self.stop = wx.Button(self, label="Stop Action Recognition")
        self.stop.Bind(wx.EVT_BUTTON, self.stop_train)

        self.next_selection = wx.Button(self, label='Next Selection')
        self.next_selection.Bind(wx.EVT_BUTTON, self.nextSelection)



        self.oper_2.Add(self.retrain,        1,   flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=5)
        self.oper_2.Add(self.stop,            1, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=5)
        self.oper_2.Add(self.next_selection,   1, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=5)
        # self.oper_2.Add(self.reset,            1, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=5)
        self.oper_2.Add(self.help_button,       1,flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=5)
        self.oper_2.Add(self.evaluation_button, 1, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=5)

        self.sizer.Add(self.oper_1, pos=(4,0), span=(4,5))
        self.sizer.Add(self.gauge, pos=(8,0), span=(1,4))
        self.sizer.Add(self.oper_2, pos=(9,0), span= (1,5))
        self.SetSizer(self.sizer)
        self.sizer.Fit(self)

        font = {'family': 'serif',
                'color': 'darkred',
                'weight': 'normal',
                'size': 16,
                }
        # self.image_panel.axes.set_title('Cluster Map Epoch 0',fontdict=font)

        self.image_panel.savelabel(None)

        self.SetSizer(self.sizer)
        self.sizer.Fit(self)
        self.Layout()

        self.SetupScrolling()

    def on_focus(self, event):
        pass

    def help_function(self, event):
        help_text = """
        Iterative Action Recognition
        Set the Training Parameters
        1. Seletction Method: In this part, your selection will decide which method GUI use to select samples for annotation. there are four possible choices ("Cluster Center", "Cluster Random", "Cluster Uncertainty", "Unifrom").
        2. # Samples per Selection: how many samples you want to label in current selection stage.
        3. Maimum Epochs: when perform the action recogntion, the maximum epoch the netwrok will be trained.
        4. Cluster Map Dimension: you can choose "2d" or "3d", if it is "2d" the Cluster Map will be shown in 2D dimension, otherwise it is 3D dimension.
        5. Dimension Reduction Methods: possible choices are "PCA", "tSNE", "UMAP". The GUI will use the choosen reduction method to perform dimension reduction and show results in Cluster Map.
        
        Plots
        1. Cluter Map Plot:
            
            i. The will be dots in different color in the Cluter Map plot.
        Red: current sample for labeling and its corresponding video is shown on the rigth.
        Blue: the suggested samples for labling in this iteration.
        Green: samples already been labeled.
            
            ii Zoom: zoom in or zoom out the plot
            
            iii Pan: move the plot around.
            
            iv Update selection: save the suggeted sample id and start labeling
            
        2. Video Plot:
            
            i left panal: show corresponding video for the sample in red color shown in Cluster Map
            
            ii right panel: the class name and class id, according to the video, select the class.
            
            iii Previous: load the previous video
            
            iv Play: paly the video
            
            vi next: go to the next video 
        
        3. Buttons:
            
            i perform Action Recognition: save labeling results and train action recognition model.
            
            ii Stop Action Recognition: stop training
            
            iv Next Seelction: go the next iteration of label selection, labeling and training.
            
            vi Get Results: get the prediction from trained model on unlabeled samples. 

        """
        wx.MessageBox(help_text, "Help", wx.OK | wx.ICON_INFORMATION)

    def evaluation_function(self, event):
        '''
        Create excel file with results from running model on data 
        '''
        self.image_panel.extract_hiddenstate()
        labels = self.image_panel.extracted.pred_label

        import pandas as pd
        import yaml

        f = open(self.config, 'r')
        config = yaml.safe_load(f)

        _, _, names = get_data_list([os.path.join(config['data_path'], config['train'])], return_video=True, videos_exist=True)
        names = [name.decode('UTF-8') for name in names]

        print(len(names), names)
        print(len(labels), labels)

        label_names = [config['class_name'][int(i)-1] for i in labels]

        df = pd.DataFrame({'video_names': names, 'labels': labels, 'label_names': label_names})

        df.to_excel(os.path.join(config['output_path'], 'output.xlsx'))

        # TODO: Moishe: make a config parameter for this stuff
        # for video, label in zip(names, label_names):
        #     output_video = os.path.join(config['output_path'], os.path.basename(video))[:-4] + '.mp4'
        #
        #     if os.path.exists(output_video):
        #         os.remove(output_video)
        #
        #     cap = cv2.VideoCapture(video)
        #
        #     fps = cap.get(cv2.CAP_PROP_FPS)
        #     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        #     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        #     num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        #
        #     from sys import platform
        #     if platform == "linux" or platform == "linux2":
        #         # linux
        #         fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        #     elif platform == "darwin":
        #         # OS X
        #         fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        #     elif platform == "win32":
        #         # Windows...
        #         fourcc = cv2.VideoWriter_fourcc(*'XVID')
        #
        #     out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
        #
        #     for i in range(num_frames):
        #         ret, frame = cap.read()
        #         cv2.putText(frame, label, (0, 30), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 0, 0), thickness=1, lineType=2)
        #         out.write(frame)
        #
        #     out.release()
        #     out = None

    def select_config(self, event):
        """
        """
        self.config = self.sel_config.GetPath()

    def select_trml(self, event):
        """
        """
        if self.sel_trml.IsShown():
            self.trml = self.sel_trml.GetPath()
            if self.trml == "":
                wx.MessageBox(
                    "Please choose the trained model to load the project",
                    "Error",
                    wx.OK | wx.ICON_ERROR,
                )
                self.loaded = False

    def chooseOption(self, event):
        if self.model_comparison_choice.GetStringSelection() == "Yes":
            self.network_box.Show()
            self.networks_to_compare.Show()
            self.augmentation_box.Show()
            self.augmentation_to_compare.Show()
            self.shuffles_text.Show()
            self.shuffles.Show()
            self.net_choice.Enable(False)
            self.select_choice.Enable(False)
            self.shuffle.Enable(False)
            self.SetSizer(self.sizer)
            self.sizer.Fit(self)
            self.get_network_names(event)
            self.get_augmentation_method_names(event)
        else:
            self.net_choice.Enable(True)
            self.select_choice.Enable(True)
            self.shuffle.Enable(True)
            self.shuffles_text.Hide()
            self.shuffles.Hide()
            self.network_box.Hide()
            self.networks_to_compare.Hide()
            self.augmentation_box.Hide()
            self.augmentation_to_compare.Hide()
            self.SetSizer(self.sizer)
            self.sizer.Fit(self)

    def get_network_names(self, event):
        self.net_type = list(self.networks_to_compare.GetCheckedStrings())

    def get_augmentation_method_names(self, event):
        self.aug_type = list(self.augmentation_to_compare.GetCheckedStrings())

    def selecting_samples(self, event):
        """
        """
        from openlabcluster.gui.labeling_toolbox_ic import show

        show(self.config, self.trml, self.net_choice.GetValue(), self.select_choice.GetValue(), self.trainingindex.GetValue())

    def labeling_video(self, event):
        from openlabcluster.gui.media.label_video import show
        if self.sel_labelpath.GetPath():
            show(self.config, self.sel_labelpath.GetPath())
        else:
            config_file = auxiliaryfunctions.read_config(self.config)
            show(self.config, config_file['selected_path'])

    def retrain_network(self, event):
        try:
            self.video_panel.sample
            self.video_panel.savelabel()
        except:
            pass
        from openlabcluster.training_utils.itertrain import train_network
        wx.MessageBox('Action Recognition Start', "Information")
        self.btn = event.GetEventObject()
        self.gauge.SetRange(self.epoch.GetValue())
        self.gauge.SetValue(0)
        self.progress = 0
        pub.subscribe(self.updateProgress, "update")
        pub.subscribe(self.on_finish, "finish_iter")
        self.retrain.Enable(False)

        try:
            self.work = train_network(self.config, self.image_panel.image_panel, epochs=int(self.epoch.GetValue()), acc_text = self.train_acc_num)
        except Exception as e:
            print(traceback.format_exc())
            wx.MessageBox('Error while training. Look in terminal for more information', 'Training Error', wx.OK | wx.ICON_ERROR) 


    def stop_train(self, event):
        self.work.stop()

        wx.MessageBox('Training Stopped', 'Message')
        pub.unsubscribe(self.updateProgress, "update")
        pub.unsubscribe(self.on_finish, "finish_iter")
        self.retrain.Enable(True)

    def nextSelection(self, event):
        self.image_panel.refresh(event, self.select_choice.GetValue())

    def updateProgress(self, step):
        self.progress += step
        self.gauge.SetValue(self.progress)

        # print('gt_label', self.image_panel.extracted.gt_label)
        # print('hidarry', self.image_panel.extracted.hidarray.numpy().shape)
        # print('pred_label', self.image_panel.extracted.pred_label.numpy().shape)

        # kmeans = KMeans(n_clusters=self.video_panel.list.GetItemCount()).fit(self.image_panel.extracted.transformed) # using 2 features 
        kmeans = KMeans(n_clusters=self.video_panel.list.GetItemCount()).fit(self.image_panel.extracted.hidarray) # using entire hidden state
        # calculate scores
        labels = kmeans.labels_
        data = self.image_panel.extracted.transformed
        self.cal_har_index_num.SetLabelText(str(round(calinski_harabasz_score(data, labels ))))
        self.dav_bould_index_num.SetLabelText(str(round(davies_bouldin_score(data, labels), 2)))
        self.train_acc_num.SetLabelText(f'{self.work.acc:.2f}')
        self.metrics_box.Layout()
        self.sizer.Layout()
        self.Layout()
        
        # # calculate scores ---- with full data 
        # self.cal_har_index_num.SetLabelText(str(round(calinski_harabasz_score(self.image_panel.extracted.hidarray.numpy(), self.image_panel.extracted.pred_label.numpy()))))
        # self.dav_bould_index_num.SetLabelText(str(round(davies_bouldin_score(self.image_panel.extracted.hidarray.numpy(), self.image_panel.extracted.pred_label.numpy()))))

    def on_finish(self):
        """conversion process finished"""
        pub.unsubscribe(self.updateProgress, "update")
        pub.unsubscribe(self.on_finish, "finish_iter")
        self.retrain.Enable(True)
        self.Close()

    def update_image_panel(self, event):
        dim = self.dim_choice.GetValue()
        method = self.reducer_choice.GetValue()
        self.image_panel.update_image_panel(dim, method)

    def change_model(self, event):
        self.sel_trml.Enable(True)

    def change_net(self, event):
        self.net_choice.Enable(True)

    def change_sammethod(self, event):
        self.select_choice.Enable(True)

    def change_sampath(self, event):
        self.sel_labelpath.Enable(True)

    def reset_create_training_dataset(self, event):
        """
        Reset to default
        """
        # self.config = []
        self.sel_config.SetPath("")
        # self.shuffles.SetValue("1")
        self.net_choice.SetValue("resnet_50")
        self.select_choice.SetValue("default")
        self.model_comparison_choice.SetSelection(1)
        self.network_box.Hide()
        self.networks_to_compare.Hide()
        self.augmentation_box.Hide()
        self.augmentation_to_compare.Hide()
        self.shuffles_text.Hide()
        self.shuffles.Hide()
        self.net_choice.Enable(True)
        self.select_choice.Enable(True)
        self.SetSizer(self.sizer)
        self.sizer.Fit(self)
        self.Layout()


if __name__ == '__main__':
    class MainFrame(wx.Frame):
        def __init__(self):
            displays = (
                wx.Display(i) for i in range(wx.Display.GetCount())
            )  # Gets the number of displays
            screenSizes = [
                display.GetGeometry().GetSize() for display in displays
            ]  # Gets the size of each display
            index = 0  # For display 1.
            screenWidth = screenSizes[index][0]
            screenHeight = screenSizes[index][1]
            self.gui_size = (screenWidth * 0.7, screenHeight * 0.55)
            wx.Frame.__init__(
                self,
                None,
                wx.ID_ANY,
                "IterativeClutering",
                size=wx.Size(self.gui_size),
                pos=wx.DefaultPosition,
                style=wx.RESIZE_BORDER | wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL,
            )

            self.panel = wx.Panel(self)
            self.nb = wx.Notebook(self.panel)
            cfg = '/home/ws2/Documents/jingyuan/IC_GUI/deeplabcut/gui/test-j-2021-02-04/config.yaml'
            page5 = Sample_labeling(self.nb, None, cfg)
            self.nb.AddPage(page5, "Iterative Action Recognition")


    app = wx.App()
    frame = MainFrame().Show()
    app.MainLoop()


