from __future__ import annotations
import numpy as np
from typing import Union, TypeVar, NamedTuple, Sequence, Deque, Optional, List, Type, Dict, Any, Type
from types import ModuleType
from collections import namedtuple
import copy
import inspect
import xml.etree.ElementTree as ET
from xml.dom.minidom import Document
from xml.dom import minidom
import importlib
from collections import deque

from .datatype import data_type
from .instanceattrs import InstanceAttrs
from .strcast import strcast
from .serializerutils import SerializerUtils
from .userinputnode import UserInputNode
from .serialize import Serialize


#Generic class type alias
CLASS = TypeVar('CLASS')

#Generic class inst type alias
INSTANCE = TypeVar('INSTANCE')

#Add documentation...otherwise good



class DeserializeUserInput(SerializerUtils):

	def init_args(
			self, 
			inst: INSTANCE,
		) -> None:
		class_ = type(inst)
		signature = inspect.signature(class_)
		init_arg_names = [
			arg_name for arg_name in list(signature.parameters)
		]
		inst_attr_names = self.get_inst_dict(keys=True) 
		

	def instance_attr(
			self, 
			node: UserInputNode, 
			xml_node: ET.Element, 
			inst_attrs: InstanceAttrs,
		) -> None:
		module = importlib.import_module('__main__')
		inst = self.class_instance(xml_node)
		new_inst_attrs = InstanceAttrs(inst)
		empty_str_attrs = []
		for attr in new_inst_attrs.default_instance_attrs():
			if new_inst_attrs.is_empty_str(attr):
				empty_str_attrs.append(attr)
		inst_attrs.call_init()
		setattr(self, node.name, inst)
		inst.__deserialize_user_input(
			node, 
			xml_node, 
			empty_str_attrs, 
			new_inst_attrs
		)

	def instance_list_attr(
			self, 
			node: UserInputNode, 
			xml_node: ET.Element, 
			inst_attrs: InstanceAttrs,
		) -> None:
		num_children = len(xml_node)
		null_list = self.null_adt(num_children)
		inst_list = []
		children = []
		inst_list_empty_str_attrs = []
		inst_list_attrs = []
		for index in range(len(null_list)):
			inst = self.class_instance(xml_node[index])
			new_inst_attrs = InstanceAttrs(inst)
			empty_str_attrs = []
			for attr in new_inst_attrs.default_instance_attrs():
				if new_inst_attrs.is_empty_str(attr):
					empty_str_attrs.append(attr)
			inst_list.append(inst)
			inst_list_attrs.append(new_inst_attrs)
			inst_list_empty_str_attrs.append(empty_str_attrs)
			children.append(node.add_child(xml_node[index]))
		inst_attrs.call_init()
		setattr(self, node.name, inst_list) 
		for index in range(len(children)):
			inst_list[index].__deserialize_user_input(
				children[index], 
				xml_node[index], 
				inst_list_empty_str_attrs[index], 
				inst_list_attrs[index]
			)

	def numpy_dtype_dict(
			self,
			) -> Dict[str, Union[
				Type[np.ndarray],
				Type[np.float32], 
				Type[np.float64], 
				Type[np.int32],
				Type[np.int64], 
				Type[np.complex64],
				Type[np.complex128]
			]]:
		return {
			"array" : np.array,
			"float32" : np.float32,
			"float64" : np.float64,
			"int32" : np.int32,
			"int64" : np.int64,
			"complex64" : np.complex64,
			"complex128" : np.complex128
		}

	def ndarray_dtype(
			self,
			array_dtype: str,
			) -> Union[
				np.float32, 
				np.float64, 
				np.int32,
				np.int64, 
				np.complex64,
				np.complex128
			]:
		dtype_name = array_dtype.replace(" array", "")
		if dtype_name == "array":
			return self.numpy_dtype_dict()["float32"]
		return self.numpy_dtype_dict()[dtype_name]
			

	def cast_to_numpy_dtype(
			self,
			val: Union[List, int, float],
			dtype: str,
			) -> Union[
				np.ndarray,
				np.float32, 
				np.float64, 
				np.int32,
				np.int64, 
				np.complex64,
				np.complex128
			]:
		if "array" in dtype:
			array_dtype = self.ndarray_dtype(dtype)
			return self.numpy_dtype_dict()['array'](
				val, 
				dtype=array_dtype
			)
		return self.numpy_dtype_dict()[dtype](
			val 
		)
		

	def non_instance_attr(
			self, 
			node: UserInputNode, 
			xml_node: ET.Element, 
			empty_str_attrs: List, 
			inst_attrs: InstanceAttrs,
		) -> None:
		if (type(xml_node.text) == type(None)
				and xml_node.tag in empty_str_attrs):
			setattr(self, node.name, '')
			inst_attrs.call_init()
		else:
			if "numpy" in xml_node.attrib:
				setattr(
					self, 
					node.name, 
					self.cast_to_numpy_dtype(
						strcast(xml_node.text),
						xml_node.attrib["numpy"]
					)
				)
			else:
				setattr(
					self, 
					node.name, 
					strcast(xml_node.text)
				)
			inst_attrs.call_init()

	def __deserialize_user_input(
			self, 
			node: UserInputNode, 
			xml_node: ET.Element, 
			empty_str_attrs: List, 
			inst_attrs: InstanceAttrs,
			) -> UserInputNode:
		for xml_child in node.xml_node:
			child = node.add_child(xml_child)
			#Added "or child.type == 'class'" for legacy support
			if child.type_ == 'instance' or child.type_ == 'class': 
				self.instance_attr(child, xml_child, inst_attrs)
			elif child.type_ == 'instance_list':
				self.instance_list_attr(child, xml_child, inst_attrs)
			elif child.type_ == 'non_instance':
				self.non_instance_attr(
					child, 
					xml_child, 
					empty_str_attrs, 
					inst_attrs,
				)
		return node
			

	def deserialize_user_input(
			self, 
			node: UserInputNode, 
			xml_root: ET.Element, 
			empty_str_attrs: List, 
			inst_attrs: InstanceAttrs,
		) -> str:
		name = xml_root.tag
		root = UserInputNode(xml_root, name, 'instance')
		self.__deserialize_user_input(
			root, 
			xml_root, 
			empty_str_attrs, 
			inst_attrs, 
		)
		return root
'''
-----------------------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------------------
'''
