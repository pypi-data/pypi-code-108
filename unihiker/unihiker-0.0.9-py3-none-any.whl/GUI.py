from threading import Thread
import tkinter as tk
from tkinter import ttk, font
from time import sleep
from PIL import Image, ImageTk
from pathlib import Path
import math
import qrcode

class GUI():

    global_master = None
    master = None
    font_name = None

    def __init__(self):
        def mainloopThread():
            GUI.global_master = tk.Tk()
            families = {'HYQiHei', '汉仪旗黑 50S', '汉仪旗黑', 'HYQiHei 50S'}
            for family in families:
                if family in font.families():
                    self.font_name = family
                    print("found font:" + family)
                    break
            else:
                self.font_name = self.load_font(Path(__file__).parent/"HYQiHei_50S.ttf")
                print("loaded font:" + family)
            
            style = ttk.Style(GUI.global_master)
            style.configure('.', font=(self.font_name, 11))
            GUI.global_master.geometry('240x320')
            GUI.global_master.resizable(0, 0)
            GUI.global_master.mainloop()
        
        if GUI.thd is not None:
            raise Exception("Can only create single GUI instance!")
            return
        GUI.thd = Thread(target=mainloopThread)   # gui thread
        GUI.thd.daemon = True  # background thread will exit if main thread exits
        GUI.thd.start()  # start tk loop
        while GUI.global_master is None:
            sleep(0.01)
        self.master = GUI.global_master
        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill='both', expand=1)

        self.canvas = tk.Canvas(self.frame, bd=0, highlightthickness=0)
        self.canvas.pack(fill='both', expand=1)
        

        def check_alive():
            self.master.after(500, check_alive)
        check_alive()

    def load_font(self, path):
        import os
        import sys
        from contextlib import redirect_stderr
        from fontTools import ttLib


        def font_name(font_path):
            font = ttLib.TTFont(font_path, ignoreDecompileErrors=True)
            with redirect_stderr(None):
                names = font['name'].names
            families = set()
            for x in names:
                if x.nameID == 1 or x.nameID == 16:
                    try:
                        families.add(x.toUnicode())
                    except UnicodeDecodeError:
                        families.add(x.string.decode(errors='ignore'))
            print("font_name:" + str(families))
            return families

        families = font_name(path)
        tk_font_families = font.families()
        for family in families:
            if family in tk_font_families:
                return family
        import platform
        import shutil
        if platform.system() == "Linux":
            Path.mkdir(Path.home()/".fonts", exist_ok=True)
            shutil.copy(path, Path.home()/".fonts")
            os.execl(sys.executable, sys.executable, *sys.argv)
        elif platform.system() == "Windows":
            import ctypes
            import os
            import shutil
            import sys

            from ctypes import wintypes

            try:
                import winreg
            except ImportError:
                import _winreg as winreg

            user32 = ctypes.WinDLL('user32', use_last_error=True)
            gdi32 = ctypes.WinDLL('gdi32', use_last_error=True)

            FONTS_REG_PATH = r'Software\Microsoft\Windows NT\CurrentVersion\Fonts'

            HWND_BROADCAST = 0xFFFF
            SMTO_ABORTIFHUNG = 0x0002
            WM_FONTCHANGE = 0x001D
            GFRI_DESCRIPTION = 1
            GFRI_ISTRUETYPE = 3

            if not hasattr(wintypes, 'LPDWORD'):
                wintypes.LPDWORD = ctypes.POINTER(wintypes.DWORD)

            user32.SendMessageTimeoutW.restype = wintypes.LPVOID
            user32.SendMessageTimeoutW.argtypes = (
                wintypes.HWND,   # hWnd
                wintypes.UINT,   # Msg
                wintypes.LPVOID, # wParam
                wintypes.LPVOID, # lParam
                wintypes.UINT,   # fuFlags
                wintypes.UINT,   # uTimeout
                wintypes.LPVOID  # lpdwResult
            )

            gdi32.AddFontResourceW.argtypes = (
                wintypes.LPCWSTR,) # lpszFilename

            # http://www.undocprint.org/winspool/getfontresourceinfo
            gdi32.GetFontResourceInfoW.argtypes = (
                wintypes.LPCWSTR, # lpszFilename
                wintypes.LPDWORD, # cbBuffer
                wintypes.LPVOID,  # lpBuffer
                wintypes.DWORD)   # dwQueryType


            def install_font(src_path):
                # copy the font to the Windows Fonts folder
                dst_path = os.path.join(
                    os.environ['USERPROFILE'], 'AppData\Local\Microsoft\Windows\Fonts', os.path.basename(src_path)
                )
                shutil.copy(src_path, dst_path)

                # load the font in the current session
                if not gdi32.AddFontResourceW(dst_path):
                    os.remove(dst_path)
                    raise WindowsError('AddFontResource failed to load "%s"' % src_path)

                # notify running programs
                user32.SendMessageTimeoutW(HWND_BROADCAST, WM_FONTCHANGE, 0, 0, SMTO_ABORTIFHUNG, 1000, None)

                # store the fontname/filename in the registry
                filename = dst_path
                fontname = os.path.splitext(filename)[0]

                # try to get the font's real name
                cb = wintypes.DWORD()
                if gdi32.GetFontResourceInfoW(filename, ctypes.byref(cb), None, GFRI_DESCRIPTION):
                    buf = (ctypes.c_wchar * cb.value)()
                    if gdi32.GetFontResourceInfoW(filename, ctypes.byref(cb), buf, GFRI_DESCRIPTION):
                        fontname = buf.value

                is_truetype = wintypes.BOOL()
                cb.value = ctypes.sizeof(is_truetype)
                gdi32.GetFontResourceInfoW(filename, ctypes.byref(cb), ctypes.byref(is_truetype), GFRI_ISTRUETYPE)

                if is_truetype:
                    fontname += ' (TrueType)'

                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, FONTS_REG_PATH, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, fontname, 0, winreg.REG_SZ, filename)
            
            install_font(path)
            os.execl(sys.executable, sys.executable, *sys.argv)
        elif platform.system() == "Darwin":
            Path.mkdir(Path.home() / "Library" / "Fonts", exist_ok=True)
            shutil.copy(path, Path.home() / "Library" / "Fonts")
            os.execl(sys.executable, sys.executable, *sys.argv)


    cache_images = {}

    class CanvasBase(object):
        ids = None
        parent = None

        def __init__(self, parent):
            self.ids = []
            self.parent = parent

        def remove(self):
            for id in self.ids:
                self.parent.cache_images.pop(id, None)
                self.parent.canvas.delete(id)
        
        def rgb2hex(self, color):
            if isinstance(color, tuple):
                return "#%02x%02x%02x" % color
            return color


    class CanvasText(CanvasBase):

        def preprocess(self, kw):
            self.font = kw.pop('font', (self.font[0], kw.pop('font_size', self.font[1])))
            self.anchor = kw.pop('anchor', kw.pop('origin', self.anchor))
            self.fill = kw.pop('fill', kw.pop('color', self.fill))
            self.onclick = kw.pop('onclick', None)

            kw['font']=self.font
            kw['anchor']=self.anchor
            kw['fill']=self.rgb2hex(self.fill)

        def postprocess(self):
            if self.onclick is not None:
                self.command = self.onclick
                for id in self.ids:
                    self.parent.canvas.tag_bind(id, '<Button-1>', lambda event: self.command())

        def __init__(self, parent, x, y, **kw):
            super().__init__(parent)
            self.x = x
            self.y = y

            self.font = (self.parent.font_name, 14)
            self.anchor = 'nw'
            self.fill = 'black'

            self.preprocess(kw)
            self.ids.append(self.parent.canvas.create_text(x, y, **kw))
            self.postprocess()      
        
        def config(self, **kw):
            self.preprocess(kw)
            self.parent.canvas.itemconfigure(self.ids[0], **kw)
            self.postprocess() 
  
    def draw_text(self, x, y, **kw):
        return GUI.CanvasText(self, x, y, **kw)

    class CanvasImage(CanvasBase):
        def preprocess(self, kw):
            self.image = kw.pop('image', self.image)
            self.anchor = kw.pop('anchor', kw.pop('origin', self.anchor))
            self.onclick = kw.pop('onclick', None)

            if self.image is None:
                self.imageTK = None
            elif "PIL" in str(type(self.image)):
                self.imageTK = ImageTk.PhotoImage(self.image)
            else:
                self.imageTK = ImageTk.PhotoImage(Image.open(str(self.image)))
            
            kw['image'] = self.imageTK
            kw['anchor'] = self.anchor

        def postprocess(self):
            if self.onclick is not None:
                self.command = self.onclick
                for id in self.ids:
                    self.parent.canvas.tag_bind(id, '<Button-1>', lambda event: self.command())

        def __init__(self, parent, x, y, **kw):
            super().__init__(parent)
            self.x = x
            self.y = y

            self.image = None
            self.anchor = 'nw'

            self.preprocess(kw)
            self.ids.append(self.parent.canvas.create_image(x, y, **kw))
            self.parent.cache_images[self.ids[0]] = self.imageTK
            self.postprocess()

        def config(self, **kw):
            self.preprocess(kw)
            self.parent.canvas.itemconfigure(self.ids[0], **kw)
            self.parent.cache_images[self.ids[0]] = self.imageTK
            self.postprocess()

    def draw_image(self, x, y, **kw):
        return GUI.CanvasImage(self, x, y, **kw)
    
    class CanvasLine(CanvasBase):

        def preprocess(self, kw):
            self.fill = kw.pop('fill', kw.pop('color', self.fill))
            self.onclick = kw.pop('onclick', None)
            
            kw['fill'] = self.rgb2hex(self.fill)

        def postprocess(self):
            if self.onclick is not None:
                self.command = self.onclick
                for id in self.ids:
                    self.parent.canvas.tag_bind(id, '<Button-1>', lambda event: self.command())

        def __init__(self, parent, x0, y0, x1, y1, **kw):
            super().__init__(parent)
            self.x = x0
            self.y = y0
            self.x1 = x1
            self.y1 = y1

            self.fill = 'black'

            self.preprocess(kw)
            self.ids.append(self.parent.canvas.create_line(x0, y0, x1, y1, **kw))
            self.postprocess()

        def config(self, **kw):
            self.preprocess(kw)
            self.parent.canvas.itemconfigure(self.ids[0], **kw)
            self.postprocess()

    def draw_line(self, x0, y0, x1, y1, **kw):
        return GUI.CanvasLine(self, x0, y0, x1, y1, **kw)

    class CanvasCircle(CanvasBase):
        def preprocess(self, kw):
            self.color = kw.pop('color', self.color)
            self.outline = kw.pop('outline', self.color)
            if self.fill != '':
                self.fill = kw.pop('fill', self.color)
            self.onclick = kw.pop('onclick', None)

            kw['outline'] = self.rgb2hex(self.outline)
            kw['fill'] = self.rgb2hex(self.fill)

        def postprocess(self):
            if self.onclick is not None:
                self.command = self.onclick
                for id in self.ids:
                    self.parent.canvas.tag_bind(id, '<Button-1>', lambda event: self.command())

        def __init__(self, parent, x, y, r, **kw):
            super().__init__(parent)
            self.x = x
            self.y = y
            self.r = r

            self.color = 'black'
            self.fill = kw.get('fill', '')

            self.preprocess(kw)
            self.ids.append(self.parent.canvas.create_oval(x-r, y-r, x+r, y+r, **kw))
            self.postprocess()
        
        def config(self, **kw):
            self.preprocess(kw)
            self.parent.canvas.itemconfigure(self.ids[0], **kw)
            self.postprocess()

    def draw_circle(self, x, y, r, **kw):
        return GUI.CanvasCircle(self, x, y, r, **kw)

    def fill_circle(self, x, y, r, **kw):
        kw['fill'] = kw.get('fill', kw.get('color', 'black'))
        return GUI.CanvasCircle(self, x, y, r, **kw)

    class CanvasPoint(CanvasCircle):
        def __init__(self, parent, x, y, **kw):
            kw['fill'] = kw.get('fill', kw.get('color', 'black'))
            super().__init__(parent, x, y, 2, **kw)

    def draw_point(self, x, y, **kw):
        return GUI.CanvasPoint(self, x, y, **kw)


    class CanvasRect(CanvasBase):
        def preprocess(self, kw):
            self.color = kw.pop('color', self.color)
            self.outline = kw.pop('outline', self.color)
            if self.fill != '':
                self.fill = kw.pop('fill', self.color)
            self.onclick = kw.pop('onclick', None)

            kw['outline'] = self.rgb2hex(self.outline)
            kw['fill'] = self.rgb2hex(self.fill)

        def postprocess(self):
            if self.onclick is not None:
                self.command = self.onclick
                for id in self.ids:
                    self.parent.canvas.tag_bind(id, '<Button-1>', lambda event: self.command())

        def __init__(self, parent, x, y, w, h, **kw):
            super().__init__(parent)
            self.x = x
            self.y = y
            self.w = w
            self.h = h

            self.color = 'black'
            self.fill = kw.get('fill', '')

            self.preprocess(kw)
            self.ids.append(self.parent.canvas.create_rectangle(x, y, x+w, y+h, **kw))
            self.postprocess()
        
        def config(self, **kw):
            self.preprocess(kw)
            self.parent.canvas.itemconfigure(self.ids[0], **kw)
            self.postprocess()

    def draw_rect(self, x, y, w, h, **kw):
        return GUI.CanvasRect(self, x, y, w, h, **kw)

    def fill_rect(self, x, y, w, h, **kw):
        kw['fill'] = kw.get('fill', kw.get('color', 'black'))
        return GUI.CanvasRect(self, x, y, w, h, **kw)

    
    class CanvasClock(CanvasBase):
        def preprocess(self, kw):
            self.backup = (self.outline, self.fill)

            self.style = kw.pop('style', self.style)
            if self.style == 'customize':
                self.color = kw.pop('color', self.color)
                self.outline = kw.pop('outline', self.color)
                self.fill = kw.pop('fill', self.fill)
            else:
                self.outline = "black"
                self.fill = "white"
            self.onclick = kw.pop('onclick', None)

            kw['outline'] = self.rgb2hex(self.outline)
            kw['fill'] = self.rgb2hex(self.fill)

            return self.backup != (self.outline, self.fill)

        def postprocess(self):
            if self.onclick is not None:
                self.command = self.onclick
                for id in self.ids:
                    self.parent.canvas.tag_bind(id, '<Button-1>', lambda event: self.command())

        def __init__(self, parent, x, y, r, h, m, s, **kw):
            super().__init__(parent)
            self.x = x
            self.y = y
            self.r = r

            self.color = 'black'
            self.outline = 'black'
            self.fill = kw.get('fill', '')
            self.style = 'customize'

            self.preprocess(kw)
            self.ids.append(self.parent.canvas.create_oval(x-r, y-r, x+r, y+r, width=r//12, outline=kw['outline'], fill=kw['fill']))
            self.ids.append(self.parent.canvas.create_oval(x-r//24,y-r//24,x+r//24,y+r//24, outline=kw['outline'], fill=kw['outline']))
            r1=r # dial lines for one minute 
            r2=r//1.42 # for hour numbers  after the lines 
            rs=r//1.2 # length of second needle 
            rm=r//1.3 # length of minute needle
            rh=r//1.8 # lenght of hour needle

            in_degree = 0
            in_degree_s=int(s)*6 # local second 
            in_degree_m=int(m)*6 # local minutes  
            in_degree_h=int(h) * 30 # 12 hour format 

            if(in_degree_h==360):
                in_degree_h=0 # adjusting 12 O'clock to 0 
            h=iter(['12','1','2','3','4','5','6','7','8','9','10','11'])

            for i in range(0,60):
                in_radian = math.radians(in_degree)
                if(i%5==0): 
                    ratio=0.85 # Long marks ( lines )
                    t1=x+r2*math.sin(in_radian) # coordinate to add text ( hour numbers )
                    t2=y-r2*math.cos(in_radian) # coordinate to add text ( hour numbers )
                    self.ids.append(self.parent.canvas.create_text(t1,t2,fill=kw['outline'],font=(self.parent.font_name, int(r//6)),text=next(h))) # number added
                    marksWidth = 2
                else:
                    ratio=0.9 # small marks ( lines )
                    marksWidth = 1
                
                x1=x+ratio*r1*math.sin(in_radian)
                y1=y-ratio*r1*math.cos(in_radian)
                x2=x+r1*math.sin(in_radian)
                y2=y-r1*math.cos(in_radian)
                self.ids.append(self.parent.canvas.create_line(x1,y1,x2,y2,fill=kw['outline'],width=marksWidth)) # draw the line for segment
                in_degree=in_degree+6 # increment for next segment
                # End of Marking on the dial with hour numbers 
                # Initialize the second needle based on local seconds value  
            
            in_radian = math.radians(in_degree_s) 
            x2=x+rs*math.sin(in_radian)
            y2=y-rs*math.cos(in_radian)
            self.ids.append(self.parent.canvas.create_line(x,y,x2,y2,fill=kw['outline'],width=r/40)) # draw the second needle

            in_radian = math.radians(in_degree_m)
            x2=x+rm*math.sin(in_radian)
            y2=y-rm*math.cos(in_radian) 
            self.ids.append(self.parent.canvas.create_line(x,y,x2,y2,width=r/40,fill=kw['outline']))

            in_degree_h=in_degree_h+(in_degree_m*0.0833333)          
            in_radian = math.radians(in_degree_h)
            x2=x+rh*math.sin(in_radian)
            y2=y-rh*math.cos(in_radian)
            self.ids.append(self.parent.canvas.create_line(x,y,x2,y2,width=r/40+r/40,fill=kw['outline']))
            self.postprocess()
        
        def config(self, h, m, s, **kw):
            if self.preprocess(kw):
                for i, id in enumerate(self.ids):
                    if i == 0:
                        self.parent.canvas.itemconfigure(id, outline=kw['outline'], fill=kw['fill'])
                    elif i == 1:
                        self.parent.canvas.itemconfigure(id, outline=kw['outline'], fill=kw['outline'])
                    else:
                        self.parent.canvas.itemconfigure(id, fill=kw['outline'])

            in_degree_s=int(s)*6 # local second 
            in_degree_m=int(m)*6 # local minutes  
            in_degree_h=int(h)*30 # 12 hour format 


            xa, ya, xb, yb  = self.parent.canvas.coords(self.ids[0])
            r = (xb-xa)/2

            r1=r # dial lines for one minute 
            r2=r//1.42 # for hour numbers  after the lines 
            rs=r//1.2 # length of second needle 
            rm=r//1.3 # length of minute needle
            rh=r//1.8 # lenght of hour needle

            in_degree_h=in_degree_h+(in_degree_m*0.0833333)          
            in_radian = math.radians(in_degree_h)
            x, y, _, _  = self.parent.canvas.coords(self.ids[-1])
            x2=x+rh*math.sin(in_radian)
            y2=y-rh*math.cos(in_radian)
            
            self.parent.canvas.coords(self.ids[-1], x, y, x2, y2)
            
            in_radian = math.radians(in_degree_m)
            x, y, _, _  = self.parent.canvas.coords(self.ids[-2])
            x2=x+rm*math.sin(in_radian)
            y2=y-rm*math.cos(in_radian) 
            self.parent.canvas.coords(self.ids[-2], x, y, x2, y2)

            in_radian = math.radians(in_degree_s) 
            x, y, _, _  = self.parent.canvas.coords(self.ids[-3])
            x2=x+rs*math.sin(in_radian)
            y2=y-rs*math.cos(in_radian)
            self.parent.canvas.coords(self.ids[-3], x, y, x2, y2)
            
            self.postprocess()

    def draw_clock(self, x, y, r, h, m, s, **kw):
        return GUI.CanvasClock(self, x, y, r, h, m, s, **kw)

    def fill_clock(self, x, y, r, h, m, s, **kw):
        kw['fill'] = kw.get('fill', 'white')
        return GUI.CanvasClock(self, x, y, r, h, m, s, **kw)



    class CanvasRoundRect(CanvasBase):
        def preprocess(self, kw):
            self.color = kw.pop('color', self.color)
            self.outline = kw.pop('outline', self.color)
            if self.fill != '':
                self.fill = kw.pop('fill', self.color)
            self.onclick = kw.pop('onclick', None)

            kw['outline'] = self.rgb2hex(self.outline)
            kw['fill'] = self.rgb2hex(self.fill)

        def postprocess(self):
            if self.onclick is not None:
                self.command = self.onclick
                for id in self.ids:
                    self.parent.canvas.tag_bind(id, '<Button-1>', lambda event: self.command())

        def __init__(self, parent, x, y, w, h, r, **kw):
            super().__init__(parent)
            self.x = x
            self.y = y
            self.w = w
            self.h = h
            self.r = r

            self.color = 'black'
            self.fill = kw.get('fill', '')

            self.preprocess(kw)

            if self.fill != '':
                points=[
                    x+r, y+r, x+r, y, x+w-r, y, x+w-r, y+r, x+w, y+r, x+w, y+h-r,
                    x+w-r, y+h-r, x+w-r, y+h ,x+r, y+h, x+r, y+h-r, x, y+h-r, x, y+r, 
                ]
                kw["outline"] = self.rgb2hex(self.fill)
                self.ids.append(self.parent.canvas.create_polygon(points, **kw))
                self.ids.append(self.parent.canvas.create_arc(x,   y,   x+2*r,   y+2*r,   **kw, start= 90, extent=90, style="pieslice"))
                self.ids.append(self.parent.canvas.create_arc(x+w-2*r, y+h-2*r, x+w, y+h, **kw, start=270, extent=90, style="pieslice"))
                self.ids.append(self.parent.canvas.create_arc(x+w-2*r, y,   x+w, y+2*r,   **kw, start=  0, extent=90, style="pieslice"))
                self.ids.append(self.parent.canvas.create_arc(x,   y+h-2*r, x+2*r,   y+h, **kw, start=180, extent=90, style="pieslice"))
                kw["outline"] = self.rgb2hex(self.outline)

            self.ids.append(self.parent.canvas.create_arc(x,   y,   x+2*r,   y+2*r,   start= 90, extent=90, style="arc", **kw))
            self.ids.append(self.parent.canvas.create_arc(x+w-2*r, y+h-2*r, x+w, y+h, start=270, extent=90, style="arc", **kw))
            self.ids.append(self.parent.canvas.create_arc(x+w-2*r, y,   x+w, y+2*r,   start=  0, extent=90, style="arc", **kw))
            self.ids.append(self.parent.canvas.create_arc(x,   y+h-2*r, x+2*r,   y+h, start=180, extent=90, style="arc", **kw))
            kw["fill"] = kw.pop('outline')
            self.ids.append(self.parent.canvas.create_line(x+r, y,   x+w-r, y    , **kw))
            self.ids.append(self.parent.canvas.create_line(x+r, y+h, x+w-r, y+h  , **kw))
            self.ids.append(self.parent.canvas.create_line(x,   y+r, x,     y+h-r, **kw))
            self.ids.append(self.parent.canvas.create_line(x+w, y+r, x+w,   y+h-r, **kw))

            self.postprocess()
        
        def config(self, **kw):
            self.preprocess(kw)
            if len(self.ids) == 13:
                kw["outline"] = self.rgb2hex(self.fill)
                for i in range(5):
                    self.parent.canvas.itemconfigure(self.ids[i], **kw)
                kw["outline"] = self.rgb2hex(self.outline)
            for i in range(-8, -4):
                self.parent.canvas.itemconfigure(self.ids[i], **kw)
            kw["fill"] = kw.pop('outline')
            for i in range(-4, 0):
                self.parent.canvas.itemconfigure(self.ids[i], **kw)
                
            self.postprocess()

    def draw_round_rect(self, x, y, w, h, r, **kw):
        return GUI.CanvasRoundRect(self, x, y, w, h, r, **kw)

    def fill_round_rect(self, x, y, w, h, r, **kw):
        kw['fill'] = kw.get('fill', kw.get('color', 'black'))
        return GUI.CanvasRoundRect(self, x, y, w, h, r, **kw)


    class CanvasQRCode(CanvasImage):
        def __init__(self, parent, x, y, w, h, **kw):
            self.text = kw.pop('text', '')
            self.w = w
            self.h = h
            img = qrcode.make(self.text)
            img = img.resize((w, h))
            super().__init__(parent, x, y, image=img, **kw)
        
        def config(self, **kw):
            self.text = kw.pop('text', '')
            img = qrcode.make(self.text)
            img = img.resize((self.w, self.h))
            super().config(image=img, **kw)


    def draw_qr_code(self, x, y, w, h, **kw):
        return GUI.CanvasQRCode(self, x, y, w, h, **kw)




    def add_button(self, x, y, w, h, **kw):
        kw['command'] = kw.pop('command', kw.pop('onclick', None)) 
        kw['style'] = kw.pop('style', 'TButton')
        object = ttk.Button(self.canvas, **kw)
        object.place(x=x, y=y, width=w, height=h)

        def remove():
            object.place_forget()
            object.destroy()
        setattr(object, "remove", remove)

        return object
    
    def startLoop(self, callback):
        def loop():
            while True:
                callback()
        loopThread = Thread(target=loop)
        loopThread.daemon = True
        loopThread.start()
        return loopThread

GUI.thd = None