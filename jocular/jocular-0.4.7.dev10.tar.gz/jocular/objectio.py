''' Handles new and previous object logic, and associated confirmation
    dialogues.
'''

import os
import shutil
from functools import partial
from datetime import date, datetime
from loguru import logger

from kivy.app import App
from kivy.metrics import dp
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.label import Label
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

from jocular.component import Component
from jocular.utils import add_if_not_exists, generate_observation_name, move_to_dir, toast
from jocular.image import save_image, Image
from jocular.formwidgets import configurable_to_widget

Builder.load_string('''

<SaveDialogContent>:
    orientation: 'vertical'
    adaptive_height: True
    # height: '340dp'

    MDLabel:
        id: text
        text: root.text
        font_style: "Body1"
        theme_text_color: "Custom"
        text_color: app.theme_cls.disabled_hint_text_color
        size_hint_y: None
        height: self.texture_size[1]
        markup: True

''')

class SaveDialogContent(MDBoxLayout):
    ''' Save dialog options to allow user to change exposure, temperature, 
        or sub_type
    '''
    configurables = [
        ('exposure', {'name': 'exposure', 
            'double_slider_float': (0, 60), 
            'fmt': '{:.2f} s',
            'help': 'change if exposure is incorrect'}),
        ('sub_type', {'name': 'sub type', 'options': ['light', 'dark', 'flat', 'bias'], 
            'help': 'change if sub type is incorrect'}),
        ('save_master', {'name': 'save master?', 'switch': True, 
            'help': 'save subs and create new calibration master?'}),
        ('temperature', {'name': 'temperature', 'float': (-40, 40, 1), 
            'fmt': '{:.0f} C',
            'help': 'change if temperature is incorrect'}),
        ('change_fits_headers', {'name': 'change FITs?', 'switch': True, 
            'help': 'permanently write new properties into FITs headers'})
        ]

    exposure = NumericProperty(0)
    sub_type = StringProperty('light')
    temperature = NumericProperty(0, allownone=True)
    save_master = BooleanProperty(False)
    change_fits_headers = BooleanProperty(False)

    def __init__(self, text=None, sub_type=None, temperature=None, exposure=None, **kwargs):
        self.text = text
        self.sub_type = 'light' if sub_type is None else sub_type
        self.temperature = -40 if temperature is None else temperature
        self.exposure = 0 if exposure is None else exposure
        self.save_master = self.sub_type in {'flat', 'dark', 'bias'}
        super().__init__(**kwargs)

        self.widgets = {}
        for name, spec in self.configurables:
            self.widgets[name] = configurable_to_widget(
                text=spec.get('name', name),
                name=name,
                spec=spec,
                helptext=spec.get('help', ''),
                initval=getattr(self, name), 
                changed=self.setting_changed,
                textwidth=dp(150),
                widgetwidth=dp(100))

        self.add_widget(Label(size_hint=(1, None), height='50dp'))  # spacer
        for widget in self.widgets.values():
            self.add_widget(widget)
        self.add_widget(Label(size_hint=(1, None), height='50dp'))  # spacer
        self.widgets['save_master'].disabled = sub_type == 'light'

    def setting_changed(self, name, value, spec, *args):
        ''' Called by widget when a setting changes
        '''
        if name == 'sub_type':
            self.widgets['save_master'].disabled = value == 'light'
        setattr(self, name, value)        


class ObjectIO(Component):

    existing_object = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.current_object_dir = None
        self.closing = False
        dformat = '%y_%m_%d'
        self.session_dir = os.path.join(self.app.get_path('captures'), date.today().strftime(dformat))
        add_if_not_exists(self.session_dir)

    def on_close(self):
        self.closing = True

    @logger.catch()
    def confirm_new_object(self, *args):
        ''' Called when user clicks 'new' on interface. 
            Here we give user a chance to change certain settings such as
            sub type and exposure, decide whether to pull out, add
            temperature if dark, create master and potentially others
        '''

        stacker = Component.get('Stacker')
        if stacker.is_empty():
            self.new_object()
            return

        self.change_fits_headers = False   # force user to set this to True

        # find name, sub_type, exposure and temperature
        name = Component.get('DSO').Name
        if name.lower()[:4] in {'dark', 'flat', 'bias'}:
            sub_type = name.lower()[:4]
        else:
            sub_type = stacker.get_prop('sub_type')

        exposure = stacker.get_prop('exposure')
        temperature = Component.get('Session').temperature

        # nothing to save
        if self.current_object_dir is None:
            self.new_object()
            return

        # previous object but unchanged
        if self.existing_object and not self.app.gui.something_has_changed():
            self.new_object()
            return

        # we have something to confirm so set up dialog
        color = self.app.theme_cls.primary_color
        text = 'Please confirm that you wish to save. You may also change the following properties if required.'
        if self.existing_object:
            text = 'Your previous object has changed. ' + text

        content = SaveDialogContent(
            text=text,
            exposure=exposure,
            sub_type=sub_type,
            temperature=temperature)

        buttons = [MDFlatButton(text='CANCEL', on_press=self.cancel_save, text_color=color)]

        # allow user to save or discard changes
        if self.existing_object:
            buttons += [
                MDFlatButton(
                    text='SAVE CHANGES', 
                    on_press=partial(self.do_save, content),
                    text_color=color),
                MDFlatButton(
                    text='DISCARD CHANGES', 
                    on_press=self.dont_save,
                    text_color=color)
            ]
        else:
            buttons += [
                MDFlatButton(
                    text='SAVE', 
                    on_press=partial(self.do_save, content),
                    text_color=color)
                ]

        self.dialog = MDDialog(
            auto_dismiss=False,
            type='custom',
            content_cls=content,
            buttons=buttons
            )
        self.dialog.open()


    def cancel_save(self, *args):
        ''' just dismiss dialog
        '''
        self.dialog.dismiss()

    def dont_save(self, *args):
        ''' User doesn't want to save the changes made to previous object
        '''
        self.dialog.dismiss()
        self.new_object()

    def do_save(self, content, *args):

        self.dialog.dismiss()

        metadata = Component.get('Metadata')
        stacker = Component.get('Stacker')
        # subs = Component.get('Stacker').subs

        # save master if requested
        if content.save_master:
            # form capture properties: might streamline this
            if content.temperature == -40:
                content.temperature = None
            capture_props = {
                'exposure': content.exposure, 
                'temperature': content.temperature,
                'filter': stacker.get_prop('filter'),
                'gain': stacker.get_prop('gain'),
                'offset': stacker.get_prop('offset'),
                'binning': stacker.get_prop('binning'),
                'ROI': stacker.get_prop('ROI'),
                'camera': stacker.get_prop('camera'),
                'sub_type': content.sub_type
            }

            Component.get('Calibrator').create_master(capture_props=capture_props)

        # save info.json, handle rejects, and update observations table

        # not clear this is useful?
        metadata.set(
            {'exposure': content.exposure, 
            'sub_type': content.sub_type,
            'temperature': content.temperature})

        oldpath = self.current_object_dir
        Component.save_object()

        # check if name has been changed
        name = metadata.get('Name', default='')
        if name:
            session_dir, object_dir = os.path.split(self.current_object_dir)
            if name != object_dir:
                # user has changed name, so generate a (unique) new folder name
                new_name = generate_observation_name(session_dir, prefix=name)
                # change directory name; any problem, don't bother
                try:
                    os.rename(self.current_object_dir, 
                        os.path.join(session_dir, new_name)) 
                    self.current_object_dir = os.path.join(session_dir, new_name)
                except Exception as e:
                    logger.exception('cannot change name ({:})'.format(e))

        # save metadata, and if successful update observations
        newpath = self.current_object_dir
        try:
            ''' kludge for now: temperature at least may have been changed by session 
                during save_object so ensure metadata is reset with these new values
            '''
            metadata.set(
                {'exposure': content.exposure, 
                'sub_type': content.sub_type,
                'temperature': content.temperature})
            metadata.save(newpath, change_fits_headers=content.change_fits_headers)
            Component.get('Observations').update(oldpath, newpath)
            Component.get('ObservingList').new_observation()
            toast('Saved to {:}'.format(newpath))
        except Exception as e:
            logger.exception('OSError saving info3.json to {:} ({:})'.format(newpath, e))

        self.new_object()

    def new_object(self, *args):
        if self.closing:
            return
        self.current_object_dir = None
        self.existing_object = False
        self.sub_type = None
        Component.initialise_new_object()
        self.app.gui.set('frame_script', True, update_property=True)

    def load_previous(self, path):
        # previous will have been saved by this point
        self.existing_object = True
        gui = self.app.gui
        gui.enable()
        gui.set('show_reticle', False, update_property=True)
        self.current_object_dir = path
        Component.initialise_previous_object()

    def new_sub(self, data=None, name=None, capture_props=None):
        ''' Called by Capture or WatchedCamera
            capture_props is a dictionary that contains additional key/values
            that we want to save in the FITs header (eg gain) 
        '''

        if data is None or name is None:
            return

        logger.debug('New sub | {:}'.format(capture_props))
        sub_type = capture_props['sub_type']
        stacker = Component.get('Stacker')
 
        if self.current_object_dir is None:
            # new object, so check if calibration or light
            if sub_type in {'dark', 'flat', 'bias'}:
                self.current_object_dir = os.path.join(self.session_dir, 
                    generate_observation_name(self.session_dir, prefix=sub_type))
                stacker.sub_type = sub_type  # is this needed any more?
                Component.get('DSO').Name = sub_type
            else:
                self.current_object_dir = os.path.join(self.session_dir, 
                    generate_observation_name(self.session_dir, prefix=Component.get('DSO').Name))
                self.app.gui.disable(['load_previous'])
            add_if_not_exists(self.current_object_dir)

        path = os.path.join(self.current_object_dir, name)

        try:
            save_image(data=data, path=path, capture_props=capture_props)
            stacker.add_sub(Image(path))
        except Exception as e:
            logger.exception('cannot add sub to stack ({:})'.format(e))
           

    def save_original(self, path):
        ''' Move non-Jocular sub from path (in Watched) to current object subdirectory
        '''
        if self.current_object_dir is None:
            self.current_object_dir = os.path.join(self.session_dir, 
                generate_observation_name(self.session_dir, prefix=Component.get('DSO').Name))
            add_if_not_exists(self.current_object_dir)
        move_to_dir(path, os.path.join(self.current_object_dir, 'originals'))


    def delete_file(self, path):
        ''' Move file to delete directory under today's date for convenience
        '''
        try:
            delete_dir = self.app.get_path('deleted')
            today = datetime.now().strftime('%d_%b_%y')
            delete_path = os.path.join(delete_dir, today)
            if not os.path.exists(delete_path):
                os.mkdir(delete_path)
            dname = os.path.join(delete_path,
                '{:}_{:}'.format(os.path.basename(path),
                datetime.now().strftime('%H_%M_%S.%f')))
            shutil.move(path, dname)
        except Exception as e:
            logger.exception('Problem deleting {:} ({:})'.format(path, e))

