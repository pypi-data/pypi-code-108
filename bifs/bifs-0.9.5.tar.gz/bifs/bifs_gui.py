###                       BIFS GUI                 ###
###                                                ###
###        This file contains the GUI interface    ###
###        for the BIFS package                    ###
###                                                ###

import cProfile, pstats
try:
    # new in 3.7
    from pstats import SortKey
    newProfile = True
except:
    newProfile = False

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox
# docs for PySide2 say import Slot would do for next line
from PyQt5.QtCore import pyqtSlot as Slot
# next is not currently needed but for future-proofing
# also likely different in PySide2
from PyQt5.QtCore import pyqtSignal as Signal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.colors import NoNorm 
import matplotlib.pyplot as plt
from pylab import *
import numpy as np
from scipy import misc
import bifs
from bifs.bifsexception import *
import jsonpickle
import os
import itertools
import re

from bifs.pset_dialogs import Param_Fourier_Space_Dialog,Prior_Dialog
from bifs.pset_dialogs import Likelihood_Dialog,Slice3D_Dialog
from bifs.pset_dialogs import AddBump_Dialog,DeleteBump_Dialog

import logging
# the default log does not display anything graphically, which is not ideal. RB
log = logging.getLogger("Bifs")

# gastly hack
# but currently if this is run in debug mode it has a different working directory than
# if run from command line.  To avoid problems, hard code whole path.  Path removed for public release.
# Empirical Prior file
EPFILE = r"ep1.npz"


class MainWindow(QtWidgets.QMainWindow):
    """

    Class that generates the main BIFS GUI window

    Methods corresponding to QtActions are wrapped with @catcher; nothing else should be.
 
    """
    def __init__(self, app):
        super(MainWindow, self).__init__()
        self.main_widget = QtWidgets.QWidget(self)
        # Initialize bifs object
        self.mybifs = bifs.BIFS()
        self.myapp = app
        # use self.myapp.quit() for successful completion or
        # self.myapp.exit(code) for errors
        # No sys.exit is necessary.
        self.filename = None
        self.didMAP = False
        self.setWindowTitle("Bayesian Imaging in Fourier Space")
        self.fig = Figure()
        plt.rcParams["axes.grid"] = False # turn off grid lines for images
        plt.rcParams["xtick.color"] = (1,1,1,0)
        plt.rcParams["ytick.color"] = (1,1,1,0)
        self.ax1 = self.fig.add_subplot(221,adjustable='box')
        self.ax2 = self.fig.add_subplot(222,adjustable='box')
        self.ax3 = self.fig.add_subplot(223,adjustable='box')
        self.ax4 = self.fig.add_subplot(224,adjustable='box')
        self.axes=[self.ax1, self.ax2, self.ax3, self.ax4]
        self.canvas = FigureCanvas(self.fig)

        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding, 
                                   QtWidgets.QSizePolicy.Expanding)
        self.canvas.updateGeometry()
        self.layout = QtWidgets.QGridLayout(self.main_widget)
        self.layout.addWidget(self.canvas,0,0,5,5)
        self.createActions()
        self.createMenus()

        # left, top, width, height
        self.setGeometry(30,30,850,850)
        self.setCentralWidget(self.main_widget)
        self._signal_setup()
        self.show()
        self.update()

    def _signal_setup(self):
        "connect myself to current mybifs object"
        self.mybifs.image_loaded.connect(self.set_image_loaded)
        self.mybifs.image_unloaded.connect(self.set_image_unloaded)

    @Slot()
    def set_image_loaded(self):
        #enable menu
        self.loadEmpiricalPriorAct.setEnabled(True)  # must have loaded image
        self.loadEmpiricalPriorAct.setText("&Load Empirical Prior")


    @Slot()
    def set_image_unloaded(self):
        # disable menu
       self.loadEmpiricalPriorAct.setEnabled(False)  # must have loaded image
       self.loadEmpiricalPriorAct.setText("&Load Empirical Prior (requires loaded image)")

    @catcher
    def getImage(self):
        self.getImage_real()


    @catcher
    def getEmpiricalPrior(self):
        """

        Prompt for root directory of images.
        Scan each, FFT, and get mean and sd of values in k-space
        """
        docDir = QtCore.QStandardPaths.standardLocations(QtCore.QStandardPaths.DocumentsLocation)[0]
        topDirDlg = QtWidgets.QFileDialog(self, caption="Top Directory for Images",
                                         directory = docDir)
        topDirDlg.setFileMode(QtWidgets.QFileDialog.Directory)
        if topDirDlg.exec_():
            topDir = topDirDlg.selectedFiles()[0]
        else:
            return

        ## actual computation
        if self._scanImages(topDir):
            self._statsPost()
        else:
            # something funky in images
            pass
        return

    def _scanImages(self, rootDir):
        """
        Read in all the images under rootDir
        Fourier transform them

        self._mbifs  is a collection of the resulting bifs objects

        If headers of images are inconsistent, report error and return False.
        Otherwise return True.

        May operate in parallel.
        """

        self.nImages = 0
        benchmarkHdr = None
        mismatch = set()  # holds keys that had a mismatch
        reFile = re.compile(r"^mniwSUVR_.*\.nii(\.gz)?$", re.I)

        for root, dirs, files in os.walk(rootDir):
            # avoid our target case for whom we are trying to predict
            iKill = [ i for i, d in zip(itertools.count(), dirs) if d.find("10933")>=0]
            if iKill:
                nKill = 0
                for i in iKill:
                    i -= nKill
                    log.info("Skipping {}".format(dirs[i]))
                    del dirs[i-nKill]
                    nKill += 1
            # look for files to import
            if files:
                for f in files:
                    #if not f.endswith(".nii"):
                    if not reFile.match(f):
                        continue
                    if f.find("10933")>=0:
                        log.info("Skipping {}".format(f))
                        continue
                    self.nImages += 1
                    b = self.mybifs.copy_params()
                    b.load_image_file(os.path.join(root, f))
                    self._statsAccumulate(b.mod_image())
                    hdr = b.read_imfile.header
                    del b
                    if not benchmarkHdr:
                        # first header encountered
                        benchmarkHdr = hdr
                        # could not delete the following key
                        # it actually doesn't appear in the objects attributes
                        #del benchmarkHdr.__dict__['db_name']  # differences expected and no concern
                    else:
                        for key in benchmarkHdr:
                            if key == 'db_name':
                                continue

                            if key.startswith("scl_"):
                                # values were array(nan, dtype=float32) and I had no luck testing for them
                                # in various ways
                                continue
                            v1 = benchmarkHdr[key]
                            v2 = hdr[key]
                            if (v1 != v2).any():
                                mismatch.add(key)
        if mismatch:
            msgb = QMessageBox()
            msgb.setText("Warning: The following keys were not uniform in the files scanned: {}.".format(mismatch))
            msgb.setInformativeText("Do you want to proceed anyway?")
            msgb.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgb.setIcon(QMessageBox.Warning)
            msgb.setDefaultButton(QMessageBox.No)
            return msgb.exec() == QMessageBox.Yes
        return True

    def _statsAccumulate(self, m):
        """
        Accumulate running statistics on the values of m in different images
        self.nImages gives the current image number; it starts at 1.
        m is ordinarily the modulus, and must conform to numpy array protocols

        Updates self._mns and self._ss currently.
        """
        if self.nImages == 1:
            self._mns = m
            # ss will turn into a matrix later
            self._ss = 0.0
        else:
            lastdelta = m-self._mns
            self._mns += (lastdelta)/self.nImages
            # element by element multiplication in next line
            self._ss += lastdelta*(m-self._mns)

    def _statsPost(self):
        """
        Finalize computation of voxel by voxel statistics for all images.
        Call after all images have been seen.

        Results returned as arrays self.mns and self.sds.
        Also writes these results to disk.

        Note the assumption that all images have the same dimensions.
        Also, images should be aligned with each other for this to be meaningful

        """
        self.mns = self._mns
        # element by element square root
        self.sds = np.sqrt(self._ss/(self.nImages-1))
        del self._mns
        del self._ss
        np.savez(EPFILE, mean=self.mns, sd=self.sds)
        log.info("{} has means and sds for modulus of {} PET scans".format(EPFILE, self.nImages))
        #np.savez_compressed("ep1_compressed.npz", mean=mns, sd=sds)

    @catcher
    def loadEmpiricalPrior(self):
        """
        Load a previously computed empirical prior and use it as the prior for image reconstruction.

        getEmpiricalPrior scans through directories of images to build up the prior.
        Ultimately it saves the mean and sd of the modulus, as seen in the code immediately above.

        In contrast, this function reads those values that were written out and instructs
        mybifs to use those, rather than functional shortcuts, for the prior in reconstructing
        a particular image.
        """
        if not self.mybifs.image_file_loaded:
            # should never happen since action should be disabled
            QtWidgets.QMessageBox.information(self,"Empirical Prior", "You must load image using Load Initial Image... option from BIFS menu before loading the empirical prior.")
            return
        self.mybifs.load_empirical(EPFILE)

    def getImage_real(self):
        """
    
        function that calls the BIFS function load_image_file()
        to load an image file.  

        """
        # self.__init__()

        self.fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Open File",
                                                     QtCore.QDir.currentPath())[0]
        # Qt docs say return value is a string, but it is tuple whose first element we want

        self.mybifs.load_image_file(self.fileName)
        self.show_initial_image()
        return


    @catcher
    def doMAP(self):
        """
    
        function that calls the BIFS function BIFS_MAP()
        to perform a MAP analysis.  

        """
        log.info("Performing k-space MAP estimation")
        # RB: original version of code created a new bifs instance.
        # I changed that to making one with copy_params.
        # Then I had it reload the image.  But under the current scheme that
        # will eliminate all customizations, which copy_params mostly does anyway.
        # Hopefully the original invalidity with mutliple image loads will no longer 
        # be possible in the new scheme.  Although loading a new image will destroy 
        # all customization in the new scheme.

        #self.mybifs.BIFS_MAP() should now happen implicitly
        self.show_post_proc_images()
        self.didMAP = True

        return
            
    def show_initial_image(self):
        """
    
        function that displays the initial image.  

        """
        if self.mybifs.image_file_loaded == True:
            self.ax1.clear()
            self.canvas.draw()
            self.ax1.set_title("Initial Image")
            if self.mybifs.imdim == 1:
                self.ax1.plot(self.mybifs.init_image()) 
            elif self.mybifs.imdim == 2:
                self.ax1.imshow(self.mybifs.init_image(),cmap = cm.Greys_r,norm=NoNorm())
            else: # assume for now that the only other possibility is 3D
                    # can change later
                slice_index = np.intp(np.round(self.mybifs.view3Dslice[1]*self.mybifs.init_image().shape[self.mybifs.view3Dslice[0]]))
                if self.mybifs.view3Dslice[0] == 0:
                    init_im_slice = self.mybifs.init_image()[slice_index,:,:]
                elif self.mybifs.view3Dslice[0] == 1:
                    init_im_slice = self.mybifs.init_image()[:,slice_index,:]
                elif self.mybifs.view3Dslice[0] == 2:
                    init_im_slice = self.mybifs.init_image()[:,:,slice_index]
                else:
                    raise BifsBadIndex("Sorry slice index needs to be one of 0,1,2")
                self.ax1.imshow(init_im_slice, cmap = cm.Greys_r)
            self.canvas.draw()
        return

        
    def show_post_proc_images(self):
        """
    
        function that displays the processed images.  

        """
        # Show initial and post BIFS k-spage images and final image
        self.ax1.set_title("Initial Image") # For some reason plt.cla()
                                            # clears plot 1 title
        self.ax2.clear()
        self.canvas.draw()
        self.ax2.set_title("Reconstructed Image")
        if self.mybifs.imdim == 1:
            self.ax2.plot(self.mybifs.final_image()) 
        elif self.mybifs.imdim == 2:
            self.ax2.imshow(self.mybifs.final_image(),cmap = cm.Greys_r)
        else: # assume for now that the only other possibility is 3D
                # can change later
            slice_index = np.intp(np.round(self.mybifs.view3Dslice[1]*self.mybifs.final_image().shape[self.mybifs.view3Dslice[0]]))
            if self.mybifs.view3Dslice[0] == 0:
                final_im_slice = self.mybifs.final_image()[slice_index,:,:]
            elif self.mybifs.view3Dslice[0] == 1:
                final_im_slice = self.mybifs.final_image()[:,slice_index,:]
            elif self.mybifs.view3Dslice[0] == 2:
                final_im_slice = self.mybifs.final_image()[:,:,slice_index]
            else:
                raise BifsBadIndex("Sorry slice index needs to be one of 0,1,2")
            self.ax2.imshow(final_im_slice, cmap = cm.Greys_r)
        self.canvas.draw()
                
        self.ax3.clear()
        self.canvas.draw()
        self.ax3.set_title("Initial K-Space Modulus Image")
        if self.mybifs.imdim == 1:
            showim1k = np.roll(np.roll(self.mybifs.mod_image(),self.mybifs.mod_image().shape[0]//2,0),1)
            self.ax3.plot(np.log(showim1k)) 
        elif self.mybifs.imdim == 2:
            showim1k = np.roll(np.roll(self.mybifs.mod_image(),self.mybifs.mod_image().shape[0]//2,0),self.mybifs.mod_image().shape[1]//2,1)
            self.ax3.imshow(np.log(showim1k),cmap = cm.Greys_r)
        else: # assume for now that the only other possibility is 3D
                # can change later
            slice_index = np.intp(np.round(self.mybifs.view3Dslice[1]*self.mybifs.mod_image().shape[self.mybifs.view3Dslice[0]]))
            if self.mybifs.view3Dslice[0] == 0:
                init_mod_im_slice = self.mybifs.mod_image()[slice_index,:,:]
            elif self.mybifs.view3Dslice[0] == 1:
                init_mod_im_slice = self.mybifs.mod_image()[:,slice_index,:]
            elif self.mybifs.view3Dslice[0] == 2:
                init_mod_im_slice = self.mybifs.mod_image()[:,:,slice_index]
            else:
                raise BifsBadIndex("Sorry slice index needs to be one of 0,1,2")

            showim1k = np.roll(np.roll(init_mod_im_slice,init_mod_im_slice.shape[0]//2,0),init_mod_im_slice.shape[1]//2,1)
            self.ax3.imshow(np.log(showim1k), cmap = cm.Greys_r)
        self.canvas.draw()

        self.ax4.clear()
        self.canvas.draw()
        self.ax4.set_title("BIFS K-Space Image")
        if self.mybifs.imdim == 1:
            showim2k = np.roll(np.roll(self.mybifs.bifsk_image(),self.mybifs.bifsk_image().shape[0]//2,0),1)
            self.ax4.plot(np.log(showim2k)) 
        elif self.mybifs.imdim == 2:
            showim2k = np.roll(np.roll(self.mybifs.bifsk_image(),self.mybifs.bifsk_image().shape[0]//2,0),self.mybifs.bifsk_image().shape[1]//2,1)
            self.ax4.imshow(np.log(showim2k),cmap = cm.Greys_r)
        else: # assume for now that the only other possibility is 3D
                # can change later
            slice_index = np.intp(np.round(self.mybifs.view3Dslice[1]*self.mybifs.bifsk_image().shape[self.mybifs.view3Dslice[0]]))
            if self.mybifs.view3Dslice[0] == 0:
                bifs_mod_im_slice = self.mybifs.bifsk_image()[slice_index,:,:]
            elif self.mybifs.view3Dslice[0] == 1:
                bifs_mod_im_slice = self.mybifs.bifsk_image()[:,slice_index,:]
            elif self.mybifs.view3Dslice[0] == 2:
                bifs_mod_im_slice = self.mybifs.bifsk_image()[:,:,slice_index]
            else:
                raise BifsBadIndex("Sorry slice index needs to be one of 0,1,2")

            showim2k = np.roll(np.roll(bifs_mod_im_slice,bifs_mod_im_slice.shape[0]//2,0),bifs_mod_im_slice.shape[1]//2,1)
            self.ax4.imshow(np.log(showim2k), cmap = cm.Greys_r)
        self.canvas.draw()
        return
    
    @catcher
    def saveCurrent(self):
        """
    
        function that calls the BIFS function save_results()
        to save the results of analysis.  

        """
        if not self.mybifs.final_image():
            # probably the test will throw an error rather than return
            QtWidgets.QMessageBox.information(self,"Save Current Results","No Results to Output Yet; Probably need to run - Get MAP Estimate Image - first")
        else:
            log.info("Saving Current Results")
            self.mybifs.save_results()

    @catcher
    def loadPrevious(self):
        """
    
        function that loads the results of a previous analysis
        saved via the BIFS function save_results().  

        """        
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Load Existing Paramter File",QtCore.QDir.currentPath())[0]
        # Check if it's a bifs parameter file
        if fileName.split('.')[1] == 'bifspout':
            bifs_handle = open(fileName,"r")
            bifsj = bifs_handle.read()
            bifs_handle.close()
            self.mybifs = jsonpickle.decode(bifsj)
            self._signal_setup()
            # Show intial image
            self.show_initial_image()
            # Show initial and post BIFS k-spage images and final image
            self.show_post_proc_images()                    
        else:
            QtWidgets.QMessageBox.information(self, "Parameter File Loader", "Cannot load {}. Doesn't look like a bifs parameter file".format(fileName))
            return
        return
    @catcher    
    def close(self):
        self.myapp.quit()
        
    @catcher
    def zoomIn(self):
        self.scaleImage(1.25)

    @catcher
    def zoomOut(self):
        self.scaleImage(0.8)

    @catcher
    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    @catcher
    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()

        self.updateActions()

    def createActions(self):

        self.setParamFuncAct = QtWidgets.QAction("&Parameter Space Function", self, triggered=self.setParamFunc)

        self.setPriorAct = QtWidgets.QAction("&Prior Distribution", self, triggered=self.setPrior)

        self.setLikelihoodAct = QtWidgets.QAction("&Likelihood Distribution", self, triggered=self.setLikelihood)

        self.setAddBumpAct =  QtWidgets.QAction("&Add K-Space Bump", self, triggered=self.setAddBump)

        self.setDeleteBumpAct =  QtWidgets.QAction("&Delete K-Space Bump", self, triggered=self.setDeleteBump)
        
        self.set3DSliceAct = QtWidgets.QAction("&3D Slice to View", self, triggered=self.set3DSlice)
        
        self.getImageAct = QtWidgets.QAction("&Load Initial Image...", self, triggered=self.getImage)

        self.getEmpiricalPriorAct = QtWidgets.QAction("&Empirical Prior...", self, triggered=self.getEmpiricalPrior)

        self.loadEmpiricalPriorAct = QtWidgets.QAction("&Load Empirical Prior (requires loaded image)", self, triggered=self.loadEmpiricalPrior)
        self.loadEmpiricalPriorAct.setEnabled(False)  # must have loaded image

        self.doMapAct = QtWidgets.QAction("&Get MAP Estimate Image...", self,triggered=self.doMAP)

        self.saveCurrentAct = QtWidgets.QAction("&Save Current Results...", self,triggered=self.saveCurrent)

        self.loadPreviousAct = QtWidgets.QAction("&Load Previous Results...", self,triggered=self.loadPrevious)
        
        self.exitAct = QtWidgets.QAction("&Exit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.zoomInAct = QtWidgets.QAction("Zoom &In (25%)", self,
                shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QtWidgets.QAction("Zoom &Out (25%)", self,
                shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)

        self.normalSizeAct = QtWidgets.QAction("&Normal Size", self,
                shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)

        self.fitToWindowAct = QtWidgets.QAction("&Fit to Window", self,
                enabled=False, checkable=True, shortcut="Ctrl+F",
                triggered=self.fitToWindow)

        # self.aboutAct = QtWidgets.QAction("&About", self, triggered=self.about)

        # self.aboutQtAct = QtWidgets.QAction("&About Qt", self,
        #        triggered=QtWidgets.qApp.aboutQt)

    def createMenus(self):
        self.bifsMenu = QtWidgets.QMenu("&BIFS Operations", self)
        self.bifsMenu.addAction(self.getImageAct)
        self.bifsMenu.addAction(self.getEmpiricalPriorAct)
        self.bifsMenu.addAction(self.doMapAct)
        self.bifsMenu.addAction(self.saveCurrentAct)
        self.bifsMenu.addAction(self.loadPreviousAct)
        self.bifsMenu.addSeparator()
        self.bifsMenu.addAction(self.exitAct)

        self.paramMenu = QtWidgets.QMenu("&Parameter Set", self)
        self.paramMenu.addAction(self.loadEmpiricalPriorAct)
        self.paramMenu.addAction(self.setParamFuncAct)
        self.paramMenu.addAction(self.setPriorAct)
        self.paramMenu.addAction(self.setLikelihoodAct)
        self.paramMenu.addAction(self.setAddBumpAct)
        self.paramMenu.addAction(self.setDeleteBumpAct)
        self.paramMenu.addAction(self.set3DSliceAct)
        self.paramMenu.addSeparator()
        self.paramMenu.addAction(self.exitAct)
        
        self.viewMenu = QtWidgets.QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        # self.helpMenu = QtWidgets.QMenu("&Help", self)
        # self.helpMenu.addAction(self.aboutAct)
        # self.helpMenu.addAction(self.aboutQtAct)
        
        self.menuBar().addMenu(self.bifsMenu)
        self.menuBar().addMenu(self.paramMenu)
        self.menuBar().addMenu(self.viewMenu)
        # self.menuBar().addMenu(self.helpMenu)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())
                    
    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))

    @catcher
    def setParamFunc(self):
        if self.mybifs.basis == "Fourier": # add else clauses as bases are added
            dialog = StartParam_Fourier_Space_Dialog(self)
            if dialog.exec_() == 1: # If OK button pressed
                self.mybifs.param_func_type = dialog.getFunc()
                self.mybifs.decay = dialog.getDecay()
        else:
            raise BifsBadInputs("Sorry, don't know how to handle {} basis yet.".format(self.mybifs.basis))

    @catcher
    def setPrior(self):
        dialog = StartPrior_Dialog(self)
        if dialog.exec_() == 1: # If OK button pressed
            self.mybifs.prior = dialog.getDist()
            self.mybifs.prior_scale = dialog.getScale()

    @catcher
    def setLikelihood(self):
        dialog = StartLikelihood_Dialog(self)
        if dialog.exec_() == 1: # If OK button pressed
            self.mybifs.likelihood = dialog.getDist()
            self.mybifs.likelihood_scale = dialog.getScale()

    @catcher
    def setAddBump(self):
        if not self.mybifs.image_file_loaded:
            QtWidgets.QMessageBox.information(self,"Add Bump", "Can't add bump without k-space structure, need to first load image using Load Initial Image... option from BIFS menu")
            return
        else:
            dialog = StartAddBump_Dialog(self)
            if dialog.exec_() == 1: # If OK button pressed
                get_key = dialog.getKey()
                get_position = dialog.getPosition()
                get_amplitude = dialog.getAmplitude()
                get_width = dialog.getWidth()
                self.mybifs.add_bump(get_key,get_position,get_amplitude,get_width)
                return

#                QtWidgets.QMessageBox.information(self, "Add Bump","Failed")
#                return

    @catcher
    def setDeleteBump(self):
        if self.mybifs.bumps:
            self.bumplist = []
            for keys in self.mybifs.bumps:
                self.bumplist.append(str(keys)+"  "+str(self.mybifs.bumps[keys][0]) + "  " + str(self.mybifs.bumps[keys][1]) + "  " + str(self.mybifs.bumps[keys][2]))
            dialog = StartDeleteBump_Dialog(self)
            if dialog.exec_() == 1: # If OK button pressed
                delstr = dialog.getDeleteString()
                delkey = str(delstr).split(" ")[0].strip("'[")
                del self.mybifs.bumps[delkey]
            return
        else:
            raise BifsBadInputs("No bumps to delete yet")
            return
    
    @catcher
    def set3DSlice(self):
        if self.mybifs.imdim != 3:
            raise BifsBadInputs("Sorry can only view slices for 3D data")
            return
        else:
            dialog = Start3DSlice_Dialog(self)
            if dialog.exec_() == 1: # If OK button pressed
                self.mybifs.view3Dslice[0] = dialog.getSliceIndex()
                self.mybifs.view3Dslice[1] = dialog.getSlicePercent()
                if self.didMAP:
                    self.show_initial_image()
                    self.show_post_proc_images()
                else:
                    if self.mybifs.image_file_loaded:
                        self.show_initial_image()
                return

            
class StartParam_Fourier_Space_Dialog(QtWidgets.QDialog, Param_Fourier_Space_Dialog):
    def __init__(self,parent=MainWindow):
        QtWidgets.QDialog.__init__(self,parent)
        self.setupUi(self)

    def getDecay(self):
        try:
            return float(QtWidgets.QLineEdit.text(self.decay))
        except:
            raise BifsBadParameter("Couldn't get decay value")
            
    def getFunc(self):
        try:
            return str(self.param_spaceBox.currentText())
        except:
            raise BifsBadParameter("Couldn't get parameter function")

class StartPrior_Dialog(QtWidgets.QDialog, Prior_Dialog):
    def __init__(self,parent=MainWindow):
        QtWidgets.QDialog.__init__(self,parent)
        self.setupUi(self)

    def getScale(self):
        try:
            return float(QtWidgets.QLineEdit.text(self.scale))
        except:
            raise BifsBadParameter("Couldn't get scale value")
            
    def getDist(self):
        try:
            return str(self.priorBox.currentText())
        except:
            raise BifsBadParameter("Couldn't get prior distribution")
            
class StartLikelihood_Dialog(QtWidgets.QDialog, Likelihood_Dialog):
    def __init__(self,parent=MainWindow):
        QtWidgets.QDialog.__init__(self,parent)
        self.setupUi(self)

    def getScale(self):
        try:
            return float(QtWidgets.QLineEdit.text(self.scale))
        except:
            raise BifsBadParameter("Couldn't get scale value")
            
    def getDist(self):
        try:
            return str(self.likelihoodBox.currentText())
        except:
            raise BifsBadParameter("Couldn't get likelihood distribution")

class Start3DSlice_Dialog(QtWidgets.QDialog, Slice3D_Dialog):
    def __init__(self,parent=MainWindow):
        QtWidgets.QDialog.__init__(self,parent)
        self.setupUi(self)

    def getSliceIndex(self):
        try:
            # currentIndex should yield same value as currentData, but the latter
            # seems more future-proof.  RB
            return np.int(self.slice_index.currentData())
        except:
            raise BifsBadParameter("Couldn't get slice index")
            
    def getSlicePercent(self):
        # the value is actually a fraction between 0 and 1
        try:
            return float(QtWidgets.QLineEdit.text(self.slice_percent))
        except:
            raise BifsBadParameter("Couldn't get slice percent")

class StartAddBump_Dialog(QtWidgets.QDialog, AddBump_Dialog):
    def __init__(self,parent=MainWindow):
        QtWidgets.QDialog.__init__(self,parent)
        self.setupUi(self)

    def getKey(self):
        try:
            return str(self.addBumpKeyBox.currentText())
        except:
            raise BifsBadParameter("Couldn't get bump key")
            
    def getPosition(self):
        try:
            return float(QtWidgets.QLineEdit.text(self.Position))
        except:
            raise BifsBadParameter("Couldn't get bump position")
            
    def getAmplitude(self):
        try:
            return float(QtWidgets.QLineEdit.text(self.Amplitude))
        except:
            raise BifsBadParameter("Couldn't get bump position")
            
    def getWidth(self):
        try:
            return float(QtWidgets.QLineEdit.text(self.Width))
        except:
            raise BifsBadParameter("Couldn't get bump width")
            
class StartDeleteBump_Dialog(QtWidgets.QDialog, DeleteBump_Dialog):
    def __init__(self,parent=MainWindow):
        QtWidgets.QDialog.__init__(self,parent)
        self.setupUi(self)

    def getDeleteString(self):
        try:
            return str(self.deleteBumpKeyBox.currentText())
        except:
            raise BifsBadParameter("Couldn't get bump function information")

def launch():
    "provided as a possible entry point"
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow(app)
    app.exec()  # for Python2 and Qt4 sys.exit(app.exec_())

if __name__ == '__main__':
    launch()
