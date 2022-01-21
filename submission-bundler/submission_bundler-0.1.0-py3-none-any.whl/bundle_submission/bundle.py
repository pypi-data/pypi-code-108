import ast
import typing 


# # with open('fenwick_tree.py') as f:
# with open('a.py') as f:
    
#     data = f.read()
# b = typing.cast(dict, 1)
# import pprint 
# data = ast.parse(data)
# for node in ast.iter_child_nodes(data):
#     print(node)
#     for n in ast.iter_child_nodes(node):
#         print(n)
#         print(1)
#         for m in ast.iter_child_nodes(n):
#             print(m)
#             print(2)
# # print(data.body[0].lineno)

# def iter_child_nodes(
#         node: ast.AST,
#         import_info: Optional[ImportInfo] = None) -> List[ImportInfo]:
#     result = []

#     if isinstance(node, ast.alias):
#         if import_info:
#             result.append(ImportInfo(
#                 import_info.lineno, import_info.end_lineno,
#                 import_info.import_from, node.name, node.asname))
#         return result

#     if isinstance(node, ast.Import):
#         for name in node.names:
#             if re.match(r'^atcoder\.?', name.name):
#                 if hasattr(node, 'end_lineno'):
#                     end_lineno = cast(int, node.end_lineno)  # type: ignore
#                 else:
#                     end_lineno = node.lineno
#                 import_info = ImportInfo(node.lineno, end_lineno)
#     elif isinstance(node, ast.ImportFrom):
#         if re.match(r'^atcoder\.?', cast(str, node.module)):
#             if hasattr(node, 'end_lineno'):
#                 end_lineno = cast(int, node.end_lineno)  # type: ignore
#             else:
#                 end_lineno = node.lineno
#             import_info = ImportInfo(node.lineno, end_lineno, node.module)

#     for child in ast.iter_child_nodes(node):
#         result += iter_child_nodes(child, import_info)
#     return result

# print(iter_child_nodes(