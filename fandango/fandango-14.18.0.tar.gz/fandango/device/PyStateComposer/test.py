import sys,time
import taurus,fandango

class ComposerWatcher():
    def __init__(self,composer):
        self.state = taurus.Attribute(composer+'/state')
        self.status = taurus.Attribute(composer+'/status')
        #self.pressure = taurus.Attribute(composer+'/averagepressure')
        self.last_state,self.last_status = None,None
        self.state.addListener(self.state_received)
        self.status.addListener(self.status_received)
        #self.pressure.addListener(self.event_received)

    def close(self):
        self.state.removeListener(self.state_received)
        self.status.removeListener(self.status_received)
        
    def event_received(self,source,type_,value):
        type_ = taurus.core.TaurusEventType.reverseLookup[type_]
        value = getattr(value,'value',value if type_!='Config' else 'Config')
        if type_ == 'Error': print '%s = %s.Error: %s'%(time.ctime(),source,value) 
        return type_,value

    def state_received(self,source,type_,value):
        type_,value = self.event_received(source,type_,value)
        self.last_state = None if type_ in ('Error','Config') else value
        if type_!='Error':
            print '%s - state.%s = %s'%(time.ctime(),type_,self.last_state or value)

    def status_received(self,source,type_,value):
        type_,value = self.event_received(source,type_,value)
        if self.last_state is not None and type_!='Error':
            match = [s for s in str(value).split('\n') if str(self.last_state) in s and '=' not in s][:2]
            print '%s - status(%s) = %s'%(time.ctime(),str(self.last_state),'\n'.join(match))
            
if __name__ == '__main__':
    import threading
    assert sys.argv[1:], 'Usage: python test.py a/dev/name NSeconds'
    d = sys.argv[1]
    t = int(sys.argv[2])
    cw = ComposerWatcher(d)
    threading.Event().wait(t)