# Window popup for an ongoing process
# Derek Fujimoto
# Nov 2020

from tkinter import *
from tkinter import ttk
from multiprocessing import Process
from queue import Empty

import bfit.backend.colors as colors

class popup_ongoing_process(object):
    """
        bfit:       pointer to bfit object
        do_disable: function to run to disable GUI elements on process start
        do_enable:  function to run to enable GUI elements on process end
        kill_status:BooleanVar, if true, the process was terminated
        message:    string, summary of process which is ongoing
        process:    multiprocessing.Process
        root:       TopLevels
        target:     function handle, run this with no arguments
        queue:      multiprocessing.Queue: put output in here, gets returned
    """
    
    
    def __init__(self, bfit, target, message, queue, do_disable=None, do_enable=None):
        """
            bfit:       pointer to bfit object
            do_disable: function to run to disable GUI elements on process start
            do_enable:  function to run to enable GUI elements on process end
            message:    string, summary of process which is ongoing
            root:       TopLevels
            target:     function handle, run this with no arguments
            queue:      multiprocessing.Queue: put output in here, gets returned
        """
        
        # variables
        self.bfit = bfit
        self.message = message
        self.logger = bfit.logger
        self.target = target
        self.do_disable = do_disable
        self.do_enable = do_enable
        self.queue = queue
        self.kill_status = BooleanVar()
        self.kill_status.set(False)
        
        # make window
        root = Toplevel(bfit.root)
        root.lift()
        root.resizable(FALSE, FALSE)
        
        # set icon
        self.bfit.set_icon(root)
        
        # set label
        label = ttk.Label(root, 
                      text=message, 
                      justify='center', 
                      pad=0)
        
        # make progress bar
        pbar = ttk.Progressbar(root, orient=HORIZONTAL, 
                               mode='indeterminate', length=200, maximum=20)
        pbar.start()
        
        # make button to cancel the fit
        cancel = ttk.Button(root, 
                      text="Cancel", 
                      command=self._kill,
                      pad=0)

        # grid 
        label.grid(column=0, row=0, padx=15, pady=5)
        pbar.grid(column=0, row=1, padx=15, pady=5)
        cancel.grid(column=0, row=2, padx=15, pady=5)
        
        # set up close window behaviour 
        root.protocol("WM_DELETE_WINDOW", self._kill)
        
        # update
        bfit.root.update_idletasks()
        
        # set window size
        width = root.winfo_reqwidth()
        height = root.winfo_reqheight()
        
        rt_x = bfit.root.winfo_x()
        rt_y = bfit.root.winfo_y()
        rt_w = bfit.root.winfo_width()
        rt_h = bfit.root.winfo_height()
        
        x = rt_x + rt_w/2 - (width/2)
        y = rt_y + rt_h/3 - (width/2)
        
        root.geometry('{}x{}+{}+{}'.format(width, height, int(x), int(y)))
        self.root = root
        
    def _kill(self):
        """Terminate the processs"""
        
        self.process.terminate()
        self.kill_status.set(True)
        self.logger.info('%s canceled', self.message)    
    
    def run(self):
        
        # start fit
        self.process = Process(target = self.target)
        self.process.start()
        
        # disable GUI
        if self.do_disable is not None:  
            self.do_disable()
        
        # get the output, checking for kill signal
        try:
            while True:  
                try: 
                    output = self.queue.get(timeout = 0.001)
                    
                except Empty:
                    
                    # iterate the gui
                    try:
                        self.root.update()
                    
                    # applicated destroyed
                    except TclError:    
                        return
                    
                    # check if fit cancelled
                    if self.kill_status.get():
                        if self.do_enable is not None:  
                            self.do_enable()
                        return 
                        
                # got someting in the queue
                else:
                    self.process.join()
                    if self.do_enable is not None:  
                        self.do_enable()
                    
                    # fit success
                    return output
                    
        finally:
            try:
                # kill process, destroy fit window
                self.process.terminate()
                self.root.destroy()
                del self.root
                
            # window already destroyed case (main window closed)
            except TclError:    
                pass
    
    
        
        
