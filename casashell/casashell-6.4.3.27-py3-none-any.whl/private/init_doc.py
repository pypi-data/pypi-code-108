import urllib.request
import ssl
import re
import webbrowser
from casatools import ctsys

from casashell import extra_task_modules as __extra_mods

def toolhelp( ):
    import casatools
    from casashell.private.stack_manip import find_frame
    glbl = find_frame( )
    groups = { }     
    for tname in sorted(dir(casatools)):
        if not tname.startswith('_') and tname != 'ctsys' and all( x in dir(getattr(casatools,tname)) for x in ['_info_group_','_info_desc_'] ):
            group = getattr(getattr(casatools,tname),'_info_group_')
            if group in groups:
                groups[group].append((tname,getattr(getattr(casatools,tname),'_info_group_'),getattr(getattr(casatools,tname),'_info_desc_'),getattr(casatools,tname)))
            else:
                groups[group] = [(tname,getattr(getattr(casatools,tname),'_info_group_'),getattr(getattr(casatools,tname),'_info_desc_'),getattr(casatools,tname))]

    toolnames = sorted(groups.keys())
    label_width = max(map(lambda x: len(x),toolnames)) + 1
    print("=" * (label_width + 52))
    print("CASA tools")
    for i in [t for t in toolnames]:
        last_group = ''
        for t in groups[i]:
            if t[1] != last_group:
                last_group = t[1]
                print('-' * (label_width + 52))
                print("> %s" % t[1])
                print('-' * (label_width) + '-' * 52)
            print(("%%%ds : %%s" % label_width) % (t[0].replace('\n',''),t[2].replace('\n','')))
            glbl = find_frame( )
            ctor = [x for x in glbl.keys( ) if x != 'ctsys' and glbl[x] == t[3]]
            if len(ctor) > 0:
                print(("%%%ds |    create: %%s" % label_width) % ('',", ".join(ctor)))
            inst = [x for x in glbl.keys( ) if x != 'ctsys' and isinstance(glbl[x],t[3])]
            if len(inst) > 0:
                print(("%%%ds | instances: %%s" % label_width) % ('',", ".join(inst)))
    print("-" * (label_width + 52))
    print("> singleton objects (used directly)")
    print("-" * (label_width + 52))
    print(("%%%ds : %%s" % label_width) % ('ctsys','set/get casa state (utils tool)'))
    print(("%%%ds : %%s" % label_width) % ('casalog','add messages to the CASA log (logsync tool)'))
    print("=" * (label_width + 52))

def taskhelp( ):

    def collect(groups,module):
        for tname in sorted(dir(module)):
            if not tname.startswith('_') and tname != 'ctsys' and all( x in dir(getattr(module,tname)) for x in ['_info_group_','_info_desc_'] ):
                # split group up by group name separated by misc space and a comma
                for group in ''.join(getattr(getattr(module,tname),'_info_group_').split( )).split(','):
                    if group in groups:
                        groups[group].append((tname,group,getattr(getattr(module,tname),'_info_desc_'),getattr(module,tname)))
                    else:
                        groups[group] = [(tname,group,getattr(getattr(module,tname),'_info_desc_'),getattr(module,tname))]

    import casatasks
    groups = { }
    collect( groups, casatasks )

    try:
        import casaviewer
        collect( groups, casaviewer )
    except: pass

    try:
        import casaplotms
        collect( groups, casaplotms )
    except: pass

    try:
        import casalith
        collect( groups, casalith )
    except: pass

    try:
        import almatasks
        collect( groups, almatasks )
    except: pass

    extra_groups = { }
    for m in __extra_mods:
        try:
            collect( extra_groups, m )
        except: pass

    tasknames = sorted(groups.keys())
    label_width = max(map(lambda x: len(x),tasknames)) + 1
    print("=" * (label_width + 52))
    print("CASA tasks")
    for i in tasknames:
        last_group = ''
        for t in groups[i]:
            if t[1] != last_group:
                last_group = t[1]
                print('-' * (label_width + 52))
                print("> %s" % t[1])
                print('-' * (label_width) + '-' * 52)
            print(("%%%ds : %%s" % label_width) % (t[0].replace('\n',''),t[2].replace('\n','')))
    print("-" * (label_width + 52))
    print("=" * (label_width + 52))
    if len(extra_groups) > 0:
        tasknames = sorted(extra_groups.keys())
        label_width = max(map(lambda x: len(x),tasknames)) + 1
        print("Extra tasks")
        for i in tasknames:
            last_group = ''
            for t in extra_groups[i]:
                if t[1] != last_group:
                    last_group = t[1]
                    print('-' * (label_width + 52))
                    print("> %s" % t[1])
                    print('-' * (label_width) + '-' * 52)
                print(("%%%ds : %%s" % label_width) % (t[0].replace('\n',''),t[2].replace('\n','')))
        print("=" * (label_width + 52))


class __doc(object):
    "command-line Plone help"

    def __init__( self ):

        # set the default version
        try:
            import casalith as _casalith
            self.__version = "v%d.%d.%d" % tuple(_casalith.version( )[:3])
        except:
            from casashell import version as _version
            self.__version = "v%d.%d.%d" % tuple(_version( )[:3])

        self.__root_url = "https://casadocs.readthedocs.io/en/"

        # dictionary for each version, to contain a top_url, toc_url, task_dict, and tool_dict
        self.__version_dict = {}

    def __call__( self, topic=None, version=None ):
        "open browser with documentation, try \"doc('toc')\""

        # optional version is "v" + version number, e.g. "v6.3.0"

        use_version = version
        if use_version is None:
            use_version = self.__version

        if use_version not in self.__version_dict:
            # try and get the index for this version
            index_text = None

            index_url = self.__root_url + use_version + "/genindex.html"
            req = urllib.request.Request(index_url,headers={'User-Agent': 'Mozilla/5.0'})
            try:
                with urllib.request.urlopen(req,context=ssl._create_unverified_context()) as url:
                    index_text = url.read().decode('ISO-8859-1')
                if index_text.find('casa') < 0:
                    # not the actual casa index - try again
                    index_text = None
            # except urllib.error.HTTPError as e:
            #    print(e.read())
            #    print(e.code)
            except:
                pass
                
            # remember if this has defaulted to "latest"
            use_latest = False
            if index_text is None:
                # it's still None
                # if this is a requested version, stop there
                if version is not None: 
                    print("WARN: online documentation not found corresponding to requested version: %s." % version)
                else:
                    # otherwise, try to get "latest"
                    print("WARN: online documentation not found corresponding to this version: %s "% self.__version)

                    use_latest = True
                    # if latest was already known, self.__version would already be set to it and not here

                    try:
                        index_url = self.__root_url + "latest/genindex.html"
                        req = urllib.request.Request(index_url,headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req,context=ssl._create_unverified_context()) as url:
                            index_text = url.read().decode('ISO-8859-1')
                        if index_text.find('casa') < 0:
                            # still not found, give up
                            index_text = None
                        else:
                            print("WARN: using the latest documentation, which may not be appropriate for this version.")
                    #except urllib.error.HTTPError as e:
                    #    print(e.read())
                    #    print(e.code)
                    #    index_text = None
                    except:
                        index_text = None

            top_url = None
            toc_url = None
            tool_dict = {}
            task_dict = {}

            if index_text is not None:
                # there must be something there, 'casa' was found to get here
                # the urls for this version
                if use_latest:
                    top_url = self.__root_url + "latest/"
                else:
                    top_url = self.__root_url + use_version + "/"
                toc_url = top_url + "api/casatasks.html"

                # tools
                try:
                    tools_hrefs = re.findall('<a href="(.*)">.*\(class in casatools\).*</a>',index_text)
                    toolname_re = re.compile('casatools\.(.*)\.html')
                    for href in tools_hrefs:
                        try:
                            this_tool = toolname_re.findall(href)[0]
                            tool_dict[this_tool] = href
                        except:
                            pass

                    # singletons : ctsys and casalog
                    for this_singleton in ["ctsys","casalog"]:
                        try:
                            hrefs = re.findall('<a href="(.*%s)">%s.*\(in module casatools\).*</a>' % (this_singleton,this_singleton), index_text)
                            # that should find exactly 1 match, otherwise ignore whatever it found and this singleton will remain unknown to doc
                            if len(hrefs)==1:
                                tool_dict[this_singleton] = hrefs[0]
                        except:
                            pass
                except:
                    pass
                    

                # tasks
                try:
                    tasks_hrefs = re.findall('<a href="(.*)">.*\(in module casatasks\..*\).*</a>',index_text)
                    taskname_re = re.compile('casatasks\..*\.(.*)\.html')
                    for href in tasks_hrefs:
                        try:
                            this_task = taskname_re.findall(href)[0]
                            task_dict[this_task] = href
                        except:
                            pass

                    # tasks found outside of casatasks (v6.4.0 an on)
                    other_tasks = ["browsetable","imview","msuvbin","msview","plotms","wvrgcal"]
                    for this_task in other_tasks:
                        # skip this if already known, must be before v6.4.0
                        if this_task not in task_dict:
                            try:
                                hrefs = re.findall(('<a href="(.*\.%s.html.*)">%s\(\).*\(in module.*\).*</a>' % (this_task,this_task)), index_text)
                                # that should find exactly 1 match, otherwise ignore whatever it found and this task will remain unknown to doc
                                if len(hrefs)==1:
                                    task_dict[this_task] = hrefs[0]
                            except:
                                pass
                except:
                    pass

            if index_text is None:
                # nothing found, ultimate fallback is the main casa documentation page
                print("No online documentation appears to be available at the expected locations")
                toc_url = "https://casa.nrao.edu/index_docs.shtml"
                top_url = toc_url

            this_version_dict = {'top_url':top_url,'toc_url':toc_url,'tool_dict':tool_dict,'task_dict':task_dict}
            self.__version_dict[use_version] = this_version_dict

            # if this resulted in "latest", remember that
            if use_latest:
                self.__version_dict["latest"] = this_version_dict

        this_dict = self.__version_dict[use_version]

        if type(topic) != str or topic == "toc":
            webbrowser.open_new_tab(this_dict['toc_url'])
        elif topic == "start":
            webbrowser.open_new_tab(this_dict['top_url'])
        elif topic in this_dict['task_dict']:
            webbrowser.open_new_tab(this_dict['top_url']+this_dict['task_dict'][topic])
        elif topic in this_dict['tool_dict']:
            webbrowser.open_new_tab(this_dict['top_url']+this_dict['tool_dict'][topic])
        else:
            webbrowser.open_new_tab(this_dict['top_url'] if len(this_dict['task_dict']) == 0 else this_dict['toc_url'])

doc = __doc( )
del __doc
