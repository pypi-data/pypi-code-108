from google.protobuf.json_format import MessageToDict
import json

from deepomatic.oef.utils.class_helpers import load_class, load_proto_class_from_protobuf_descriptor
from deepomatic.oef.protos.hyperparameter_pb2 import field_option, oneof_option


def fill_hyperparameters(proto, hp_dict):
    for oo in proto.DESCRIPTOR.oneofs:
        if oo.has_options:
            oneof_value = hp_dict.setdefault(proto.DESCRIPTOR.full_name, {})
            oneof_value.setdefault(oo.name, MessageToDict(oo.GetOptions().Extensions[oneof_option]))

    for f in proto.DESCRIPTOR.fields:
        if f.message_type is not None:
            proto_class = load_proto_class_from_protobuf_descriptor(f.message_type)
            fill_hyperparameters(proto_class, hp_dict)
        if f.has_options:
            message_value = hp_dict.setdefault(proto.DESCRIPTOR.full_name, {})
            message_value[f.name] = MessageToDict(f.GetOptions().Extensions[field_option])


def dump_hyperparameters():
    protobuf_class = load_class('deepomatic.oef.protos.experiment_pb2', ['Experiment'])
    hyperparameters = {}
    fill_hyperparameters(protobuf_class, hyperparameters)
    with open('hyperparameter_list.json', 'w') as fp:
        json.dump(hyperparameters, fp, indent=4)


if __name__ == '__main__':
    dump_hyperparameters()
