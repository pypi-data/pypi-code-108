import subprocess
from pygears import PluginBase, reg, find
from pygears.core.graph import get_consumer_tree
from pygears.core.port import OutPort
from pygears.sim import log, timestep, SimPlugin
from pygears.sim.sim_gear import SimGear
from pygears.typing import typeof, TLM, Float, Uint
from pygears.typing.visitor import TypingVisitorBase
from vcd import VCDWriter
from pygears.core.hier_node import HierVisitorBase
from .sim_extend import SimExtend
import os
import fnmatch
import itertools
import atexit
from pygears.conf import inject, Inject


def match(val, include_pattern):
    def check(pattern):
        if isinstance(pattern, str):
            return fnmatch.fnmatch(val.name, pattern)
        else:
            return pattern(val)

    return any(check(p) for p in include_pattern)


def is_trace_included(port, include):
    return True
    # # if not match(f'{port.gear.name}.{port.basename}', include):
    # if not match(port, include):
    #     return False

    # if (port.dtype is None) or (typeof(port.dtype, TLM) and not vcd_tlm):
    #     return False

    # return True


class VCDHierVisitor(HierVisitorBase):
    @inject
    def __init__(self, include, sim_map=Inject('sim/map')):
        self.include = include
        self.sim_map = sim_map
        self.vcd_vars = set()
        self.end_consumers = {}

    def trace_if_included(self, p):
        if not is_trace_included(p, self.include):
            return

        self.vcd_vars.add(p)

    def Gear(self, module):
        if module.parent is None:
            return super().HierNode(module)

        for p in module.in_ports:
            self.trace_if_included(p)

        if module in self.sim_map or module.hierarchical:
            for p in module.out_ports:
                self.trace_if_included(p)

        if module in self.sim_map:
            for p in module.in_ports:
                # TODO Hack to make end_consumer unique with id(intf) so that
                # it can be looked upon in the list. Make it in a better way
                self.end_consumers[p.consumer] = {'prods': [], 'intf': id(p.consumer)}

        if (module in self.sim_map or module.hierarchical) and module.params['sim_cls'] is None:
            super().HierNode(module)

        return True


from enum import IntEnum


class ChannelState(IntEnum):
    Invalid = 0
    NotReady = 1
    Ready = 2
    Done = 3


class WebSim(SimExtend):
    @inject
    def __init__(self,
                 trace_fn='pygears.json',
                 include=Inject('debug/trace'),
                 sim=Inject('sim/simulator'),
                 outdir=Inject('results-dir')):

        super().__init__()
        self.sim = sim
        self.finished = False
        self.outdir = outdir
        self.trace_fn = None
        self.shmid_proc = None
        self.include = include

        self.trace_fn = os.path.abspath(os.path.join(self.outdir, trace_fn))
        atexit.register(self.finish)

        try:
            subprocess.call(f"rm -f {self.trace_fn}", shell=True)
        except OSError:
            pass

        log.info(f'Main VCD dump to "{self.trace_fn}"')
        # self.json_vcd = open(self.trace_fn, 'w')

        self.json_vcd = {}

        self.handhake = set()
        self.valid = set()
        self.value_change = {}
        self.prev_cycle_handshake = set()

    def before_run(self, sim):
        vcd_visitor = VCDHierVisitor(self.include)
        vcd_visitor.visit(find('/'))
        self.vcd_vars = {
            p: {
                'srcs': [],
                'srcs_active': [],
                'dtype': p.dtype,
                'val': None,
            }
            for p in vcd_visitor.vcd_vars
        }

        for p in self.vcd_vars:
            self.json_vcd[p.name] = []

        if not vcd_visitor.vcd_vars:
            self.deactivate('before_run')
            return True

        self.end_consumers = vcd_visitor.end_consumers

        for intf in self.end_consumers:
            intf.events['put'].append(self.intf_put)
            intf.events['ack'].append(self.intf_ack)

        self.extend_intfs()

    def extend_intfs(self):
        for p, v in self.vcd_vars.items():
            v['srcs'] = [self.end_consumers[pp.consumer] for pp in get_consumer_tree(p.consumer)]
            v['srcs_active'] = [False] * len(v['srcs'])
            v['p'] = p
            for vs in v['srcs']:
                vs['prods'].append(v)

        reg['graph/consumer_tree'] = {}
        reg['graph/end_producer'] = {}

    def var_put(self, v, val):
        self.valid.add(v['p'])
        self.value_change[v['p']] = val

        # print(f'{v["p"].name}: {val}')
        # breakpoint()
        # if typeof(v['dtype'], TLM):
        #     self.writer.change(v['data'], timestep() * 10, str(val))
        # else:
        #     try:
        #         visitor = VCDValVisitor(v, self.writer, timestep() * 10, max_level=10)
        #         visitor.visit(v['dtype'], 'data', val=val)
        #     except AttributeError:
        #         pass

        # self.writer.change(v['valid'], timestep() * 10, 1)

    def intf_put(self, intf, val):
        p = intf.producer
        if p in self.vcd_vars:
            v = self.vcd_vars[p]
            self.var_put(v, val)

        if intf in self.end_consumers:
            v = self.end_consumers[intf]
            for vp in v['prods']:
                if not any(vp['srcs_active']):
                    # TODO: Optimization possibility, don't write the data, only ready/valid signals
                    self.var_put(vp, val)

                for i, vv in enumerate(vp['srcs']):
                    if vv is v:
                        vp['srcs_active'][i] = True
                        break

        return True

    def intf_ack(self, intf):
        p = intf.producer
        if p in self.vcd_vars:
            v = self.vcd_vars[p]
            # print(f'{v["p"].name}: HSHK')
            # self.writer.change(v['ready'], timestep() * 10, 1)
            self.handhake.add(p)

        if intf in self.end_consumers:
            v = self.end_consumers[intf]
            for vp in v['prods']:

                for i, vv in enumerate(vp['srcs']):
                    if vv is v:
                        vp['srcs_active'][i] = False
                        break

                if not any(vp['srcs_active']):
                    # print(f'{vp["p"].name}: HSHK')
                    # self.writer.change(vp['ready'], timestep() * 10, 1)
                    self.handhake.add(vp['p'])

        return True

    def create_data_change(self, val, prev_val):
        from pygears.typing import Queue, Array, Tuple
        is_changed = prev_val is None and not val is None or val != prev_val

        if isinstance(val, (Queue, Array, Tuple)):
            if prev_val is None:
                prev_val = [None] * len(val)

            change = [self.create_data_change(v, prev_v) for v, prev_v in zip(val, prev_val)]
            return {'isValueComplex': True, 'isDataChanged': is_changed, 'value': change}
        else:
            if isinstance(val, (int, float)):
                val = int(val)
            else:
                val = val.code()

            return {'isValueComplex': False, 'isDataChanged': is_changed, 'value': val}

    def create_change(self, timestep, state, state_change, val, prev_val):
        elem = {
            'cycle': timestep,
            'state': int(state),
            'isStateChanged': state_change,
        }

        if val is not None:
            elem['data'] = self.create_data_change(val, prev_val)

        return elem

    def after_timestep(self, sim, timestep):
        for p, v in self.vcd_vars.items():
            changes = self.json_vcd[p.name]
            ack = p in self.handhake and not any(v['srcs_active'])
            if ack:
                state = ChannelState.Ready
            elif p in self.valid:
                state = ChannelState.NotReady
            else:
                state = ChannelState.Invalid

            became_not_ready = p in self.prev_cycle_handshake and state != ChannelState.Ready
            became_valid = p in self.valid and v['val'] is None

            state_change = ((timestep == 0 and state != ChannelState.Invalid)
                            or (ack and p not in self.prev_cycle_handshake) or became_valid
                            or became_not_ready)
            data_change = False
            if p in self.value_change:
                data_change = v['val'] is None or (p in self.prev_cycle_handshake
                                                   and self.value_change[p] != v['val'])

            if state_change or data_change or timestep == 0:
                cycle_change = self.create_change(timestep, state, state_change,
                                                  self.value_change.get(p, v['val']), v['val'])
                if cycle_change is not None:
                    changes.append(cycle_change)

            if state == ChannelState.Ready:
                v['val'] = self.value_change[p]
                del self.value_change[p]
                self.valid.remove(p)
            elif state == ChannelState.NotReady:
                v['val'] = self.value_change[p]
            elif state == ChannelState.Invalid:
                v['val'] = None

            if p in self.handhake and any(v['srcs_active']):
                self.handhake.remove(p)

            # cycle_change = None
            # if p in self.valid:
            #     ack = p in self.handhake and not any(v['srcs_active'])
            #     state = ChannelState.Ready if ack else ChannelState.NotReady
            #     state_change = ack and p not in self.prev_cycle_handshake
            #     data_change = v['val'] is None or self.value_change[p] != v['val']
            #     if state_change or data_change:
            #         cycle_change = self.create_change(timestep, state, state_change,
            #                                           self.value_change[p], v['val'])
            # elif p in self.handhake:
            #     cycle_change = self.create_change(timestep, ChannelState.Ready,
            #                                       self.value_change[p], v['val'])

            # elif p in self.prev_cycle_handhake:
            #     cycle_change = self.create_change(timestep, ChannelState.Invalid, None, None)
            # else:
            #     v['val'] = None

        self.prev_cycle_handshake = self.handhake.copy()
        self.handhake = set()

        return True

    def finish(self):
        if not self.finished:
            json_out = {'startCycle': 0, 'endCycle': timestep(), 'channelChanges': []}

            for p in self.vcd_vars:
                json_out['channelChanges'].append({
                    'channelName': p.producer.name,
                    'changes': self.json_vcd[p.name]
                })

            import json
            # json.dump(json_out, open(self.trace_fn, 'w'), indent=4)
            json.dump(json_out, open(self.trace_fn, 'w'))
            self.finished = True

    def after_cleanup(self, sim):
        self.finish()
