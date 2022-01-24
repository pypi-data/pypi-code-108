from collections import defaultdict, namedtuple

from libcst import CSTTransformer, ClassDef, FunctionDef, SimpleStatementLine, Import, ImportFrom, Assign, List, Expr, \
    IndentedBlock, Element, Pass


def merge(existing_cst, new_cst, top_cst=None, mergers=None, **kwargs):
    return existing_cst.visit(MergingTransformer(top_cst or new_cst, new_cst, mergers or general_mergers, **kwargs))


node_with_type = namedtuple('node_with_type', 'node, type')


class MergingTransformer(CSTTransformer):
    def __init__(self, top_cst, new_cst, mergers, finalizer=None):
        super().__init__()
        self.top_cst = top_cst
        self.new_cst = new_cst
        self.mergers = mergers
        self.finalizer = finalizer
        self.node_type_category = {
            Import: 'import',
            ImportFrom: 'import',
            ClassDef: 'classdef',
            Assign: 'assign'
        }

    def on_visit(self, node):  # do not process children
        return False

    def on_leave(self, original_node, updated_node):
        existing_list = self.extract_body(updated_node)
        new_list = self.extract_body(self.new_cst)

        ret = []
        existing_list = [node_with_type(e, self.get_node_type(e)) for e in existing_list]
        new_list = [node_with_type(e, self.get_node_type(e)) for e in new_list]

        last_type = None
        for existing in existing_list:
            if last_type is not None and last_type != existing.type:
                while new_list and new_list[0].type == last_type:
                    ret.append(new_list.pop().node)
            last_type = existing.type
            found = False
            for idx, new in enumerate(new_list):
                if new.type != existing.type:
                    break
                if type(self.real_node(new.node)) is type(self.real_node(existing.node)):
                    merger = self.mergers.get(type(self.real_node(existing.node)), IdentityMerger())
                    if merger.should_merge(self.top_cst, existing.node, new.node):
                        ret.append(merger.merge(self.top_cst, existing.node, new.node))
                        del new_list[idx]
                        found = True
                        break
            if not found:
                ret.append(existing.node)

        for node in new_list:
            ret.append(node.node)

        if self.finalizer:
            return self.finalizer(updated_node, ret)
        else:
            return updated_node.with_changes(
                body=ret
            )

    def real_node(self, node):
        if isinstance(node, SimpleStatementLine):
            return node.body[0]
        return node

    def get_node_type(self, node):
        t = type(self.real_node(node))
        return self.node_type_category.get(t, 'unknown')

    def extract_body(self, node):
        ret = defaultdict(list)
        if hasattr(node, 'body'):
            body = node.body
        elif isinstance(node, List):
            body = node.elements
        else:
            raise Exception(f'Do not know how to get body from {node}')
        if isinstance(body, IndentedBlock):
            body = body.body
        return body


class MergerBase:
    def merge(self, cst, existing_node, new_node):
        raise NotImplementedError()

    def should_merge(self, cst, existing_node, new_node):
        return False

    def real_node(self, node):
        if isinstance(node, SimpleStatementLine):
            return node.body[0]
        return node

    def real_with_changes(self, node, **kwargs):
        if isinstance(node, SimpleStatementLine):
            return node.with_changes(
                body=[
                    node.body[0].with_changes(**kwargs)
                ]
            )
        else:
            return node.with_changes(**kwargs)


class IdentityBaseMerger(MergerBase):
    def merge(self, cst, existing_node, new_node):
        return existing_node

    def should_merge(self, cst, existing_node, new_node):
        return cst.code_for_node(existing_node).strip() == cst.code_for_node(new_node).strip()


class IdentityMerger(IdentityBaseMerger):
    def merge(self, cst, existing_node, new_node):
        return existing_node

    def should_merge(self, cst, existing_node, new_node):
        print(
            f'Warning: using naive merger for {type(self.real_node(existing_node))}'
            f'>>>\n{cst.code_for_node(existing_node).strip()}\n<<<')
        return super().should_merge(cst, existing_node, new_node)


class ClassMerger(MergerBase):
    def merge(self, cst, existing_node, new_node):
        return merge(existing_node, new_node, cst, general_mergers, finalizer=self.finalize)

    def finalize(self, node, new_content):
        return node.with_changes(
            body=node.body.with_changes(body=new_content)
        )

    def should_merge(self, cst, existing_node, new_node):
        return existing_node.name.value == new_node.name.value


class AssignMerger(MergerBase):
    def merge(self, cst, existing_node, new_node):
        # TODO: merge dictionaries
        real_existing = self.real_node(existing_node)
        real_new = self.real_node(new_node)
        if isinstance(real_existing.value, List) or isinstance(real_new.value, List):
            return self.real_with_changes(existing_node, value=self.merge_lists(
                cst, real_existing.value, real_new.value
            ))
        return existing_node

    def merge_lists(self, cst, existing_list, new_list):
        return merge(existing_list, new_list, cst, list_mergers, finalizer=self.finalize_list)

    def finalize_list(self, node, new_content):
        return node.with_changes(elements=new_content)

    def node_to_name(self, node):
        return tuple(sorted([x.target.value for x in self.real_node(node).targets]))

    def should_merge(self, cst, existing_node, new_node):
        return self.node_to_name(existing_node) == self.node_to_name(new_node)


class ImportMerger(IdentityBaseMerger):
    pass


class ImportFromMerger(IdentityBaseMerger):
    pass


class ExprMerger(IdentityBaseMerger):
    pass


class PassMerger(IdentityBaseMerger):
    pass


class FunctionMerger(MergerBase):
    def merge(self, cst, existing_node, new_node):
        return existing_node

    def should_merge(self, cst, existing_node, new_node):
        return existing_node.name.value == new_node.name.value


class ElementMerger(MergerBase):
    def merge(self, cst, existing_node, new_node):
        return existing_node

    def should_merge(self, cst, existing_node, new_node):
        return cst.code_for_node(existing_node.value).strip() == cst.code_for_node(new_node.value).strip()


general_mergers = {
    ClassDef: ClassMerger(),
    Assign: AssignMerger(),
    Import: ImportMerger(),
    ImportFrom: ImportFromMerger(),
    Expr: ExprMerger(),
    FunctionDef: FunctionMerger(),
    Pass: PassMerger()
}

list_mergers = {
    Element: ElementMerger()
}
