from libcst import CSTTransformer, ClassDef, FunctionDef, Module, SimpleStatementLine, Import, ImportFrom, Assign, Name, \
    AssignTarget, List, Expr


class MergingTransformer(CSTTransformer):
    def __init__(self, new_cst):
        super().__init__()
        self.new_cst = new_cst
        self.stack = []
        self._push(new_cst.body)

    def _push(self, new_members):
        self.stack.append((new_members, {}))

    def _pop(self):
        return self.stack.pop()

    def _set(self, key, value):
        self.stack[-1][1][key] = value

    def visit_ClassDef(self, node: ClassDef):
        self._set(node.name.value, node)
        for part in self.stack[-1][0]:
            if hasattr(part, 'name'):
                if part.name.value == node.name.value:
                    if hasattr(part, 'body'):
                        self._push(part.body.body)
                        break
        else:
            self._push([])

    def visit_FunctionDef(self, node: FunctionDef):
        # do not visit the children of the function as we do not modify
        # an already written function code
        self._set(node.name.value, node)
        return False

    def leave_ClassDef(
            self, original_node: ClassDef, updated_node: ClassDef
    ):
        parts_to_add = self.leave_class_module()
        self._pop()

        if parts_to_add:
            # and merge them with the original content
            return updated_node.with_changes(
                body=updated_node.body.with_changes(
                    body=[
                        *updated_node.body.body,
                        *parts_to_add
                    ]
                )
            )
        return updated_node

    def visit_Assign(self, node):
        assign_name = self._node_name(node)
        stack_top = self.stack[-1][0]
        for el in stack_top:
            el_name = self._node_name(el)
            if el_name == assign_name and isinstance(node.value, List):
                self._push(remove_simple_line(el))
                return node
        self._push(None)
        return False

    def leave_Assign(self, original_node, updated_node):
        self._pop()
        return updated_node

    def leave_List(self, original_node, updated_node):
        stack_top = self.stack[-1][0]
        if not isinstance(stack_top, Assign):
            return False
        # TODO: merge
        node_elements = list(updated_node.elements)
        for el in stack_top.value.elements:
            for ne in updated_node.elements:
                if ne.value.deep_equals(el.value):
                    break
            else:
                node_elements.append(el)
        return updated_node.with_changes(
            elements=node_elements
        )


    def _merge_assign_value(self, target_node, source_node):
        return target_node

    def leave_Module(self, original_node: Module, updated_node: Module):
        parts_to_add = self.leave_class_module()

        extra_imports = self._merge_imports(original_node)
        extra_assigns = self._merge_assigns(original_node)

        self._pop()

        # and merge
        return updated_node.with_changes(
            body=[
                *extra_imports,
                *updated_node.body,
                *parts_to_add,
                *extra_assigns
            ]
        )

    def _merge_imports(self, original_node):
        new_imports = self._extract_imports(self.stack[0][0])
        existing_imports = self._extract_imports(original_node.body)
        return self._merge_nodes(existing_imports, new_imports)

    def _merge_assigns(self, original_node):
        new_assigns = self._extract_assigns(self.stack[0][0])
        existing_assigns = self._extract_assigns(original_node.body)
        return self._merge_nodes(existing_assigns, new_assigns)

    def _merge_nodes(self, existing_nodes, new_nodes):
        # extract nodes that are not yet present
        extra_nodes = []
        for ni in new_nodes:
            for ei in existing_nodes:
                if self._node_name(ei) == self._node_name(ni):
                    break
            else:
                extra_nodes.append(ni)
        return extra_nodes

    def _node_name(self, node):
        if isinstance(node, SimpleStatementLine):
            body = node.body
            if not len(body):
                raise NotImplementedError(f'No body in SimpleStatementLine {node}')
            name_element = body[0]
        else:
            name_element = node

        if isinstance(name_element, Assign):
            lhs = name_element.children[0]
            if not isinstance(lhs, AssignTarget):
                raise NotImplementedError(f'Getting name of node type {type(lhs)} not implemented yet')
            return lhs.target.value
        elif isinstance(name_element, (Import, ImportFrom)):
            return 'Import:' + self.new_cst.code_for_node(name_element).strip()
        elif isinstance(name_element, (Expr, )):
            return 'Expr:' + self.new_cst.code_for_node(name_element).strip()
        elif isinstance(name_element, (FunctionDef, )):
            return 'Function:' + name_element.name.value
        else:
            raise NotImplementedError(f'Getting name of node type {type(name_element)} not implemented yet')

    def _extract_imports(self, lines):
        return self._extract_top_level(lines, (Import, ImportFrom))

    def _extract_assigns(self, lines):
        return self._extract_top_level(lines, Assign)

    def _extract_top_level(self, lines, classes=()):
        extracted = []
        for l in lines:
            if isinstance(l, SimpleStatementLine):
                for ml in l.children:
                    if isinstance(ml, classes):
                        extracted.append(l)
                        break
        return extracted

    def leave_class_module(self):
        new_parts = self.stack[-1][0]
        existing_parts = self.stack[-1][1]

        # look for the parts in the new parts that are not in the existing parts
        parts_to_add = []
        for part in new_parts:
            if hasattr(part, 'name'):
                if part.name.value not in existing_parts:
                    parts_to_add.append(part)
        return parts_to_add


def remove_simple_line(node):
    if isinstance(node, SimpleStatementLine):
        return node.body[0]
    return node
