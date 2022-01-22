#!/usr/bin/env python3

import wx,time,math,os
from . import SourceImages
import wx.grid
from cv2 import imread
class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "My Frame", size=(800, 450))
        self.createProxyWidget()
        self.setMenubar()
        self.SetToolBar()
    def SetToolBar(self):
        toolbar = self.CreateToolBar()
        tsize = (30,30)
        # help(toolbar.AddTool)
        t1 = toolbar.AddTool(toolId = 501,bitmap = SourceImages.origin.GetImage().Scale(20,20).ConvertToBitmap(),label = "origin", shortHelp="Set the origin")
        t2= toolbar.AddTool(toolId = 502,bitmap = SourceImages.point.GetImage().Scale(17,17).ConvertToBitmap(),label = 'getdata',shortHelp = "Get data from a point")
        t3 = toolbar.AddTool(toolId = 503,bitmap = SourceImages.point.GetImage().Scale(17,17).ConvertToBitmap(),label = 'getinfo',shortHelp = "Get info of a point")
        toolbar.Realize()
        self.Bind(wx.EVT_TOOL,dataWindow.OnClick,t1)
        self.Bind(wx.EVT_TOOL,self.GetDataSwitch,t2)
        self.Bind(wx.EVT_TOOL,self.GetInfo,t3)
    def GetInfo(self,evt):
        if mainWindow.GETINFO==True:mainWindow.GETINFO=False
        else:mainWindow.GETINFO=True
    def GetDataSwitch(self,evt):
        if mainWindow.shape==None:return
        if mainWindow.setOrigin<0:
            mainWindow.setOrigin=0
        elif mainWindow.setOrigin==0 and len(mainWindow.line)==2:
            mainWindow.setOrigin=-1
    def setMenubar(self):
        menubar=wx.MenuBar()  
        file0=wx.Menu()  
        edit=wx.Menu()  
        help=wx.Menu()  
        op_file = file0.Append(101,'&Open','Open a new document')  
        save_file = file0.Append(102,'&Export data','Save the data to a file')  
        file0.AppendSeparator()  
        quit_=wx.MenuItem(file0,105,'&Quit\tCtrl+Q','Quit the Application')  
        file0.Append(quit_)  
        edit.Append(201,'&Nothing')
        help.Append(301,'&About author')
        menubar.Append(file0,'&File')  
        menubar.Append(edit,'&Edit')  
        menubar.Append(help,'&Help')  
        self.SetMenuBar( menubar )  
        self.Bind(wx.EVT_TOOL,self.OnFileOpen,op_file )
        self.Bind(wx.EVT_TOOL, self.OnSaveFile,save_file)
        self.Bind(wx.EVT_TOOL,self.OnExit,quit_)
    def createProxyWidget(self):
        self.proxyFrame = ProxyFrame(self)
    def OnSaveFile(self,event):
        """
        Create and show the Save FileDialog
        """
        dlg = wx.FileDialog(self,message="select the Save file style",defaultFile="",wildcard="*.txt;*.csv",style=wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            filename=""
            paths = dlg.GetPaths()
            #split the paths
            for path in paths:
                filename=filename+path
            #write the contents of the TextCtrl[Contents] into the file
            file1=open(filename,'w')
            for i in dataWindow.data:
                file1.write('%f %f\n'%i)
            file1.close()
            #show the save file path
        dlg.Destroy()           
    def OnFileOpen(self,event):
        #创建标准文件对话框
        dialog = wx.FileDialog(self,"Open file...",os.getcwd(),style=wx.ID_OPEN,wildcard="*.jpg;*.png;*.jpeg,*.bmp")
        #这里有个概念：模态对话框和非模态对话框. 它们主要的差别在于模态对话框会阻塞其它事件的响应,
        #而非模态对话框显示时,还可以进行其它的操作. 此处是模态对话框显示. 其返回值有wx.ID_OK,wx.ID_CANEL;
        if dialog.ShowModal() == wx.ID_OK:
            self.filename = dialog.GetPath()
            mainWindow.SetImage(self.filename)
            #在TopWindow中更新标题为文件名.
            self.SetTitle(self.filename)
        #销毁对话框,释放资源.
        dialog.Destroy()
    def OnExit(self,evt):
        self.Close()
class ProxyFrame(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent)
        self.createWidget()

    def createWidget(self):
        self.proxy_split_mult = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE, size=(800, 450))
        self.proxy_split_mult.SetMinimumPaneSize(10) #最小面板大小

        self.proxy_split_left = wx.SplitterWindow(self.proxy_split_mult) #上结构
        self.proxy_split_right = wx.SplitterWindow(self.proxy_split_mult) #下结构
        self.proxy_split_mult.SplitVertically(self.proxy_split_left, self.proxy_split_right) #分割面板
        
        ########## 结构左右 ##########
        self.proxy_scrol_rightTop = wx.ScrolledWindow(self.proxy_split_right)
        self.proxy_scrol_rightBottom = wx.ScrolledWindow(self.proxy_split_right)
        self.proxy_scrol_rightBottom.SetBackgroundColour(wx.WHITE)
        self.proxy_split_right.SetMinimumPaneSize(10) #最小面板大小
        self.proxy_split_right.SplitHorizontally(self.proxy_scrol_rightTop, self.proxy_scrol_rightBottom) #分割面板
        self.proxy_split_right.SetSashGravity(0.99)
        ########## 结构下左右 end ##########

        self.proxy_split_mult.SetSashGravity(0.99)

        self.SetScrollbars(10, 10, 600, 400)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.proxy_split_mult, 1, flag=wx.EXPAND) #自动缩放
        self.SetSizer(sizer)
        # DragWindow(self.proxy_split_left)
        # DragWindow(self.proxy_scrol_rightTop)
        # DragWindow(self.proxy_scrol_rightBottom)
        mainWindow.__init__(sc=self.proxy_split_left)
        enlargeWindow.__init__(sc=self.proxy_scrol_rightBottom)
        dataWindow.__init__(sc=self.proxy_scrol_rightTop)



#**************************************************
class DragShape:
    def __init__(self, bmp,pos=(0,0)):
        self.bmp = bmp
        self.img = bmp.ConvertToImage()
        self.pos = pos
        self.pos0=pos
        self.shown = True
        self.subRect = 0,0,self.img.GetWidth(),self.img.GetHeight()
        self.fullscreen = False
        self.rate=1
    def Fit(self,x,y,w,h):
        imgW,imgH=self.img.GetWidth(),self.img.GetHeight()
        if x<0:
            w+=x
            x=0
        elif x>imgW:return 0,0,0,0
        if y<0:
            h+=y
            y=0
        elif y>imgH:return 0,0,0,0
        if w+x>imgW:w=imgW-x
        if h+y>imgH:h=imgH-y
        return x,y,w,h
    def SetRect(self):
        x,y,w,h=self.subRect
        x,y,w,h=self.Fit(x-w,y-h,w*3,h*3)
        dx=self.subRect[0]-x
        dy=self.subRect[1]-y
        self.pos=int(self.pos[0]-dx*self.rate),int(self.pos[1]-dy*self.rate)
        img=self.img.GetSubImage(wx.Rect(x,y,w,h))
        self.bmp=img.Scale(w*self.rate,h*self.rate).ConvertToBitmap()
        self.subRect=x,y,w,h
        return
    def GetRect(self,wsize):
        return
    def SetBmpScale(self,rate0,rate,mouse_pos,wsize):
        self.rate=rate
        mx,my=(mouse_pos[0]-self.pos0[0])/rate0,(mouse_pos[1]-self.pos0[1])/rate0
        wLeft,hTop=mouse_pos
        wLeft/=rate
        hTop/=rate
        x,y,w,h=int(mx-wLeft),int(my-hTop),int(wsize[0]/rate)+3,int(wsize[1]/rate)+3
        x,y,w,h=self.Fit(x,y,w,h)
        self.subRect=x,y,w,h
        self.pos0=int(mouse_pos[0]-mx*rate),int(mouse_pos[1]-my*rate)
        self.pos=int(mouse_pos[0]-(mx-x)*rate),int(mouse_pos[1]-(my-y)*rate)
        bmp=self.img.GetSubImage(wx.Rect(x,y,w,h))
        self.bmp=bmp.Scale(w*rate,h*rate).ConvertToBitmap()
    def Draw(self, dc, op = wx.COPY):
        if self.bmp.IsOk():
            memDC = wx.MemoryDC()
            memDC.SelectObject(self.bmp)
            dc.Blit(self.pos[0], self.pos[1],
                    self.bmp.GetWidth(), self.bmp.GetHeight(),
                    memDC, 0, 0, op, True)
            return True
        else:
            return False
#----------------------------------------------------------------------
class DragCanvas:
    def __init__(self, sc=None,background=None):
        if sc==None:return
        self.window=sc
        self.dragImage0 = None
        self.GETINFO=False
        self.dragShape = None
        self.hiliteShape = None
        self.shape=None
        self.setOrigin=0  #0:不进行设计原点，大于0正在设置原点，小于0原点设置完毕
        self.showMark=True
        self.pen = wx.Pen("green", 2)
        self.window.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        self.bg_img=SourceImages.bgc.GetImage()
        self.bgSize=0,0
        self.bg_bmp = self.bg_img.ConvertToBitmap()
        self.window.SetBackgroundStyle(wx.BG_STYLE_ERASE)
        self.window.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.mouseWhell=0

    
    # We're not doing anything here, but you might have reason to.
    # for example, if you were dragging something, you might elect to
    # 'drop it' when the cursor left the window.
    def Update(self,size=None,showBmp=True,showMark=True):
        if size==None:
            wsize=self.window.GetSize()
            size=0,0,wsize[0],wsize[1]
        self.shape.shown,self.showMark=showBmp,showMark
        self.window.RefreshRect(wx.Rect(*size))
        self.window.Update()
    def SetImage(self,img):
        self.cv2image=imread(img)
        img = wx.Image(img,wx.BITMAP_TYPE_ANY)
        enlargeWindow.SetImage(img=img)
        bmp=img.ConvertToBitmap()
        self.shape = DragShape(bmp,pos=(200,10))
        self.window.Bind(wx.EVT_PAINT, self.OnPaint)
        self.window.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.window.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.window.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.window.Bind(wx.EVT_MOTION, self.OnMotion)
        self.window.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        self.window.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWhell)
        self.window.Bind(wx.EVT_MIDDLE_DOWN, self.OnMiddleDown)
        self.InitSetOrigin()
        dataWindow.Oninit()
    def InitSetOrigin(self):
        mainWindow.line=[]
        mainWindow.circle=[]
        gridWindow.data=[]
        self.Update()
    def OnMiddleDown(self,evt):
        pass
    def SetOrigin(self,evt):
        shape=self.FindShape(evt)
        pos=evt.GetPosition()
        dataWindow.SetOrigin(pic_pos=shape.pos0, mouse_pos=(pos.x,pos.y), scale=(shape.img.GetWidth()*shape.rate,shape.img.GetHeight()*shape.rate))
    def GetPoint(self,*s):
        wsize,pos,size,rate=s
        fx=(pos[0]-wsize[0])/(size[0]*rate)
        fy=(pos[1]-wsize[1])/(size[1]*rate)
        intx=int(fx*size[0])
        inty=int(fy*size[1])
        print((fx,fy),(intx,inty),self.cv2image[inty,intx])
    def OnLeftDown(self,evt):
        shape=self.FindShape(evt)
        if not shape:return
        if self.GETINFO==True:
            pos=evt.GetPosition()
            self.GetPoint(self.shape.pos0,(pos.x,pos.y),(self.shape.img.GetWidth(),self.shape.img.GetHeight()),shape.rate)
        if self.setOrigin>0:
            self.SetOrigin(evt)
        elif self.setOrigin==0:return
        else:
            pos=evt.GetPosition()
            dataWindow.writedata(self.shape.pos0,(pos.x,pos.y),(self.shape.img.GetWidth()*shape.rate,self.shape.img.GetHeight()*shape.rate))
        self.Update()
    def OnLeaveWindow(self, evt):
        pass
    def OnMouseWhell(self,evt):
        angle=evt.GetWheelRotation()
        angle/=abs(angle)
        self.mouseWhell+=angle
        if self.mouseWhell==2:
            angle=2
            self.mouseWhell=0
        elif self.mouseWhell==-2:
            angle=-2
            self.mouseWhell=0
        else:return
        shape = self.shape
        pos=evt.GetPosition()
        rate0=shape.rate
        if angle>0:
            if rate0<1:rate=rate0+0.2
            else:rate=rate0+0.2*rate0
        else:
            if rate0<1:rate=rate0-0.2
            else:rate=rate0-0.2*rate0
        if rate<0.1 or rate>80:return
        wsize=self.window.GetSize()
        shape.SetBmpScale(rate0, rate, (pos.x,pos.y), wsize)
        self.Update()
        pos=evt.GetPosition()
        enlargeWindow.setPos(shape.pos0,(pos.x,pos.y),(shape.img.GetWidth()*shape.rate,shape.img.GetHeight()*shape.rate),wsize)
    def OnLeaveWindow(self, evt):
        pass
    # tile the background bitmap
    def TileBackground(self, dc):
        pass
    # Go through our list of shapes and draw them in whatever place they are.
    def DrawShapes(self, dc):
        shape=self.shape
        if shape.shown:
            shape.Draw(dc)
        wp,hp=shape.pos0
        w,h=shape.img.GetWidth()*shape.rate,shape.img.GetHeight()*shape.rate
        ww,hw=self.window.GetSize()
        if self.showMark==True:
            dc.SetPen(self.pen)
            for wr,hr in self.circle:
                wr=w*wr+wp
                hr=h*hr+hp
                if wr>0 and wr<ww and hr>0 and hr<hw:
                    dc.DrawCircle(wr,hr,3)
            for p1,p2,p3,p4 in self.line:
                p1=p1*w+wp
                p2=p2*h+hp
                p3=p3*w+wp
                p4=p4*h+hp
                x,y=p3-p1,p4-p2
                if abs(x)>abs(y):
                    t=(ww-p1)/float(x)
                    p3,p4=p1+t*x,p2+t*y
                    t=p1/float(x)
                    p1,p2=p1-t*x,p2-t*y
                else:
                    t=(hw-p2)/float(y)
                    p3,p4=p1+t*x,p2+t*y
                    t=p2/float(y)
                    p1,p2=p1-t*x,p2-t*y
                dc.DrawLine(p1,p2,p3,p4)
    # This is actually a sophisticated 'hit test', but in this
    # case we're also determining which shape, if any, was 'hit'.
    def FindShape(self, evt):
        pos=self.shape.pos
        mpos=evt.GetPosition()
        w,h=self.shape.bmp.GetWidth(),self.shape.bmp.GetHeight()
        pos=mpos.x-pos[0],mpos.y-pos[1]
        if pos[0]<=w and pos[0]>=0 and pos[1]>=0 and pos[1]<=h:
            return self.shape
        else:return None
    # Clears the background, then redraws it. If the DC is passed, then
    # we only do so in the area so designated. Otherwise, it's the whole thing.
    def OnEraseBackground(self, evt):
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self.window)
            rect = self.window.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        sz = self.window.GetClientSize()
        if sz!=self.bgSize:
            self.bgSize=sz
            w=min((sz[0],self.bg_img.GetWidth()))
            h=min((self.bg_img.GetHeight(),sz[1]))
            self.bg_bmp=self.bg_img.GetSubImage(wx.Rect(0,0,w,h)).ConvertToBitmap()
        dc.DrawBitmap(self.bg_bmp, 0, 0)

    # Fired whenever a paint event occurs
    def OnPaint(self, evt):
        dc = wx.PaintDC(self.window)
        self.DrawShapes(dc)

    # Left mouse button is down.
    def OnRightDown(self, evt):
        shape = self.FindShape(evt)
        if shape:
            shape.SetRect()
            #self.Update()
            self.ppos=shape.pos
            self.dragShape = shape
            self.dragStartPos = evt.GetPosition()
    # Left mouse button up.
    def OnRightUp(self, evt):
        if not self.dragImage0 or not self.dragShape:
            self.dragImage0 = None
            self.dragShape = None
            return
        # Hide the image, end dragging, and nuke out the drag image.
        #self.dragImage0.Hide()
        self.dragImage0.EndDrag()
        self.dragImage0 = None
        # if self.hiliteShape:
        #     self.window.RefreshRect(self.hiliteShape.GetRect())
        #     self.hiliteShape = None
        # reposition and draw the shape

        # Note by jmg 11/28/03 
        # Here's the original:
        #
        # self.dragShape.pos = self.dragShape.pos + evt.GetPosition() - self.dragStartPos
        #
        # So if there are any problems associated with this, use that as
        # a starting place in your investigation. I've tried to simulate the
        # wx.Point __add__ method here -- it won't work for tuples as we
        # have now from the various methods
        #
        # There must be a better way to do this :-)
        self.dragShape.pos = (
            self.dragShape.pos[0] + evt.GetPosition()[0] - self.dragStartPos[0],
            self.dragShape.pos[1] + evt.GetPosition()[1] - self.dragStartPos[1]
            )
        wsize=self.window.GetSize()
        self.dragShape = None
        dx,dy=self.shape.pos[0]-self.ppos[0],self.shape.pos[1]-self.ppos[1]
        self.shape.pos0=self.shape.pos0[0]+dx,self.shape.pos0[1]+dy
        pos=evt.GetPosition()
        self.shape.SetBmpScale(self.shape.rate, self.shape.rate,(pos.x,pos.y), wsize)
        self.Update()
    # The mouse is moving
    def OnMotion(self, evt):
        pos=evt.GetPosition()
        shape=self.shape
        enlargeWindow.setPos(shape.pos0,(pos.x,pos.y),(shape.img.GetWidth()*shape.rate,shape.img.GetHeight()*shape.rate),self.window.GetSize())
        # Ignore mouse movement if we're not dragging.
        if not self.dragShape  or not evt.RightIsDown():#or not evt.Dragging()
            return
        # if we have a shape, but haven't started dragging yet
        if self.dragShape and not self.dragImage0:
            # only start the drag after having moved a couple pixels
            # refresh the area of the window where the shape was so it
            # will get erased.
            wsize=self.window.GetSize()
            self.showMark=False
            self.dragShape.shown = False
            pw,ph=self.shape.pos
            x0=max((0,pw))
            y0=max((0,ph))
            x1=min((wsize[0],self.shape.bmp.GetWidth()+pw))
            y1=min((wsize[1],self.shape.bmp.GetHeight()+ph))
            self.window.RefreshRect(wx.Rect(x0,y0,x1-x0,y1-y0), True)
            self.window.Update()

            self.dragImage0 = wx.DragImage(self.dragShape.bmp,wx.Cursor(wx.CURSOR_HAND))
            hotspot = self.dragStartPos - self.dragShape.pos
            self.dragImage0.BeginDrag(hotspot, self.window, self.dragShape.fullscreen)
            self.dragImage0.Move(pos)
            self.dragImage0.Show()
        # if we have shape and image then move it, posibly highlighting another shape.
        if self.dragShape and self.dragImage0:
            self.dragImage0.Move(evt.GetPosition())
class LargePicture:
    def __init__(self,sc=None):
        if sc==None:return
        self.window=sc
        self.cross=SourceImages.cross.GetBitmap()
        self.cross_shape=self.cross.GetWidth(),self.cross.GetHeight()
    def SetImage(self,img):
        self.img=img
        self.shape=img.GetWidth(),img.GetHeight()
        self.pos=(0,0)
        self.scale=(0,0)
        self.rate=5
        self.bmp=None
        self.rect=None
        self.window.Bind(wx.EVT_PAINT,self.OnPaint)
    def setPos(self,pic_pos=None,mouse_pos=None,scale=None,windowSize=None):
        '''enlarge picture'''
        if self.img==None:return
        wsize=self.window.GetSize()
        x0,y0=-pic_pos[0],-pic_pos[1]
        x1,y1=x0+windowSize[0],y0+windowSize[1]
        rr=self.shape[0]/float(scale[0])
        xadd=wsize[0]/2.0/(self.rate/rr)
        yadd=wsize[1]/2.0/(self.rate/rr)
        x0,y0,x1,y1=int(x0*rr-xadd),int(y0*rr-yadd),int(x1*rr+xadd),int(y1*rr+yadd)
        m_pos=(mouse_pos[0]-pic_pos[0])*rr,(mouse_pos[1]-pic_pos[1])*rr
        if x0<0:x0=0
        if y0<0:y0=0
        if x1>self.shape[0]:x1=self.shape[0]
        if y1>self.shape[1]:y1=self.shape[1]
        rect=x0,y0,x1-x0,y1-y0
        if rect!=self.rect or scale!=self.scale:
            self.scale=scale
            self.rect=rect
            img=self.img.GetSubImage(wx.Rect(*rect))
            self.bmp=img.Scale(int(rect[2]*self.rate/rr),int(rect[3]*self.rate/rr)).ConvertToBitmap()
        x0=wsize[0]/2-(m_pos[0]-self.rect[0])*self.rate/rr
        y0=wsize[1]/2-(m_pos[1]-self.rect[1])*self.rate/rr
        self.pos=int(x0),int(y0)
        self.window.RefreshRect(wx.Rect(0,0,wsize[0],wsize[1]))
        self.window.Update()
    def OnPaint(self,evt):
        if self.bmp==None:return
        wsize=self.window.GetSize()
        dc=wx.PaintDC(self.window)
        dc.DrawBitmap(self.bmp,self.pos[0],self.pos[1],True)
        dc.DrawBitmap(self.cross,(wsize[0]-self.cross_shape[0])/2,(wsize[1]-self.cross_shape[1])/2)
class gridWindow:
    def __init__(self,sc=None):
        if sc==None:return
        self.window=sc
        self.setdistribution() 
        self.Oninit()
    def setdistribution(self):
        wsize=self.window.GetSize()
        wsize=wsize[0]-10,wsize[1]-50
        # self.area_text = wx.TextCtrl(self.window, -1,'', pos=(5,5),size=(wsize[0], wsize[1]),  
        #                              style=(wx.TE_MULTILINE | wx.TE_AUTO_SCROLL | wx.TE_DONTWRAP))  
        self.area_text = wx.TextCtrl(self.window, -1,'', pos=(5,5),size=(wsize[0], wsize[1]),  
                                     style=(wx.TE_MULTILINE | wx.TE_DONTWRAP))  
        self.posCtrl = wx.TextCtrl(self.window, -1, "Set origin", pos=(70, wsize[1]+10),size=(100,30))
    def Oninit(self):
        self.data=[]
        self.originIndex=0
        self.xmax,self.xmin,self.ymax,self.ymin=1,0,1,0
        self.xmax_pos,self.xmin_pos,self.ymax_pos,self.ymin_pos=(0,0),(0,0),(0,0),(0,0)
        self.area_text.SetValue('Result data\nX                         Y')
        self.setText('Set origin')
    def SetOrigin(self,pic_pos,mouse_pos,scale):
        setModel=['set xmax','set ymin','set ymax','successfully']
        self.setText(setModel[self.originIndex])
        pos=float(mouse_pos[0]-pic_pos[0])/scale[0],float(mouse_pos[1]-pic_pos[1])/scale[1]
        self.originIndex+=1
        if self.originIndex==1:
            self.xmin_pos=pos
            self.xmin=float(self.GetValue('Xmin value','0').strip())
        elif self.originIndex==2:
            self.xmax_pos=pos
            mainWindow.line.append((self.xmin_pos[0],self.xmin_pos[1],pos[0],pos[1]))
            self.xmax=float(self.GetValue('Xmax value','1').strip())
        elif self.originIndex==3:
            self.ymin_pos=pos
            self.ymin=float(self.GetValue('Ymin value','0').strip())
        elif self.originIndex==4:
            self.ymax_pos=pos
            self.ymax=float(self.GetValue('Ymax value','1').strip())
            mainWindow.line.append((self.ymin_pos[0],self.ymin_pos[1],pos[0],pos[1]))
            self.xVector=self.xmax_pos[0]-self.xmin_pos[0],self.xmax_pos[1]-self.xmin_pos[1]
            self.yVector=self.ymax_pos[0]-self.ymin_pos[0],self.ymax_pos[1]-self.ymin_pos[1]
            a=self.xVector[0]*self.yVector[0]+self.xVector[1]*self.yVector[1]
            self.sinAngle=math.sin(math.acos(a/(math.sqrt(self.xVector[0]**2+self.xVector[1]**2)*math.sqrt(self.yVector[0]**2+self.yVector[1]**2))))
            self.xCoefficient=(self.xmax-self.xmin)/math.sqrt(self.xVector[0]**2+self.xVector[1]**2)
            self.yCoefficient=(self.ymax-self.ymin)/math.sqrt(self.yVector[0]**2+self.yVector[1]**2)
            x0=self.Distance(self.xmin_pos, self.ymin_pos, self.ymax_pos, self.sinAngle)
            y0=self.Distance(self.ymin_pos, self.xmax_pos, self.xmin_pos, self.sinAngle)
            self.origin=self.xmin-x0*self.xCoefficient,self.ymin-y0*self.yCoefficient
            mainWindow.setOrigin=0
            print(self.xmin,self.xmax,self.ymin,self.ymax)
        else:pass
    def Distance(self,pos,posStart,posStop,sinAngle):
        vector0=posStop[0]-posStart[0],posStop[1]-posStart[1]
        vector=pos[0]-posStart[0],pos[1]-posStart[1]
        area=vector[1]*vector0[0]-vector[0]*vector0[1]
        d=area/(math.sqrt(vector0[0]*vector0[0]+vector0[1]*vector0[1])*sinAngle)
        return d
    def writedata(self,pic_pos=None,mouse_pos=None,scale=None):
        pos=float(mouse_pos[0]-pic_pos[0])/scale[0],float(mouse_pos[1]-pic_pos[1])/scale[1]
        mainWindow.circle.append(pos)
        dy=self.Distance(pos, self.xmax_pos, self.xmin_pos, self.sinAngle)
        dx=self.Distance(pos, self.ymin_pos, self.ymax_pos, self.sinAngle)
        t=dx*self.xCoefficient+self.origin[0],dy*self.yCoefficient+self.origin[1]
        self.data.append(t)
        self.area_text.AppendText('\n%e  ,  %e' % t)
    def OnClick(self,evt):
        self.originIndex=0
        mainWindow.InitSetOrigin()
        mainWindow.setOrigin=1
        self.setText('set xmin')
    def setText(self,text):
        self.posCtrl.SetValue(text)
    def GetValue(self,title='Value',default='0'):
        dlg = wx.TextEntryDialog(self.window, title,'Value Entry Dialog',default)    
        if dlg.ShowModal() == wx.ID_OK: 
            d=dlg.GetValue()
        else:d=default
        dlg.Destroy()
        return d
#*******************************************************
class MyDialog(wx.Dialog): 
   def __init__(self, parent, title): 
      super(MyDialog, self).__init__(parent, title = title, size = (250,150)) 
      panel = wx.Panel(self) 
      self.posCtrl = wx.TextCtrl(panel, -1, "Set origin", pos=(10, 10),size=(100,30))
      self.btn = wx.Button(panel, wx.ID_OK, label = "ok", size = (50,20), pos = (75,50))
#end*********************************************************************************************
mainWindow=DragCanvas()
enlargeWindow=LargePicture()
dataWindow=gridWindow()
#********************************************************************************************
def area(polygon):
    '''
    Calculate the area of a polygon
    polygon:a set of points
    '''
    Direction=lambda a,b,c:(b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0])
    d=([polygon[0],polygon[1]],[])
    i,n,ed=2,len(polygon),0
    isBreak=False
    while i<n:
        a,b,c=d[0][-2],d[0][-1],polygon[i]
        if Direction(a,b,c)<0:
            d[0][-1]=c
            d[1].append((a,b,c))
        else:d[0].append(c)
        i+=1
    def check(ma,mb,mc):
        while True:
            a,b,c=d[0][ma],d[0][mb],d[0][mc]
            if Direction(a,b,c)<0:
                d[0].pop(mb)
                d[1].append((a,b,c))
            else :break
    check(-2,-1,0)
    check(-1,0,1)
    s,st=0,0
    a=d[0][0]
    for i in range(1,len(d[0])-1):
        b,c=d[0][i],d[0][i+1]
        sp=Direction(a,b,c)/2.0
        s+=sp
    for a,b,c in d[1]:
        sp=Direction(a,b,c)/2.0
        st+=sp
    return d,abs(st+s)
#***********************************************************************************************
def main():
    #设置了主窗口的初始大小960x540 800x450 640x360
    root = wx.App()
    frame = MainFrame()
    frame.Show(True)
    root.MainLoop()
#****************end sdf********************
if __name__ == "__main__":
    main()
