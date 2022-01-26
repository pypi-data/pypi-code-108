#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_interpreter.py                                                          #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 3.0 Interpreter class                                                                     #
#                                                                                                 #
###################################################################################################

"""macal Language Interpreter class implementation"""

from .macal_parsernodetypes import (BLOCK, ASSIGN, CALL, FOREACH, HALT, BREAK, 
                                    RETURN, SELECT, IF)
from .macal_lextokentypes import NEW_ARRAY_INDEX
from .macal_variable_types import ANY, ARRAY, BOOL, FLOAT, INT, PARAMS, RECORD, FUNCTION
from .macal_parsernodetypes import VARIABLE
from .macal_keywords import NIL
from .macal_exprtypes import LITERAL, BINARY, UNARY, GROUPING
from .macal_interpreterconsts import EXIT_VAR_NAME, SelectFieldFilter
from .macal_variable import MacalVariable
from .macal_function import MacalFunction
from .macal_parsernodes import ast_list_Index
from .macal_astvariablenode import ast_Variable
from .macal_astifnode import ast_If
from .macal_expritem import ExpressionItem
from .macal_astselectnode import ast_Select
from .macal_astfunctionnode import ast_Function_definition
from .macal_expr import Expr
from .macal_scope import MacalScope
from .macal_exceptions import RuntimeError

class MacalInterpreter:
    def __init__(self):
        self.ast_tree = None
        self.scope = MacalScope("root", None)
        self.version = "3.0.1"
        self.select_subst_fields = True

    @staticmethod
    def raise_error(message: str, instruction, scope: MacalScope):
        if not isinstance(instruction, ExpressionItem):
            raise Exception(f"Runtime error: {message} @({instruction.token.token_line}, {instruction.token.token_offset})\nScope: {scope.name}")
        else:
            raise Exception(f"Runtime error: {message} \nScope: {scope.name}\n")
            
    def interpret(self, ast_tree):
        var = self.scope.find_variable(EXIT_VAR_NAME)
        if var is None:
            var = self.scope.add_new_variable(EXIT_VAR_NAME)
        var.set_value(0)
        var.set_type(INT)
        self.ast_tree = ast_tree
        self.interpret_block(self.ast_tree, self.scope)
        return var.get_value()

    def interpret_instruction(self, instruction, scope: MacalScope):
        if instruction.type == ASSIGN:
            self.interpret_assign(instruction, scope)
        elif instruction.type == BLOCK:
            self.interpret_block(instruction, scope)
        elif instruction.type == BREAK:
            self.interpret_break_loop(instruction, scope)
        elif instruction.type == CALL:
            self.interpret_function_call(instruction, scope)
        elif instruction.type == FOREACH:
            self.interpret_foreach_loop(instruction, scope)
        elif instruction.type == FUNCTION:
            self.interpret_function_definition(instruction, scope)
        elif instruction.type == HALT:
            self.interpret_halt(instruction, scope)
        elif instruction.type == RETURN:
            self.interpret_return(instruction, scope)
        elif instruction.type == IF:
            self.interpret_if(instruction, scope)
        elif instruction.type == SELECT:
            self.interpret_select(instruction, scope)
        else:
            self.raise_error("Unknown instruction", instruction, scope)

    def evaluate_expression(self, expr, scope: MacalScope):
        if isinstance(expr, ast_Variable):
            value = self._eval_var(expr, scope)
            return value
        elif isinstance(expr, MacalVariable):
            return self._eval_variable(expr, scope)
        elif isinstance(expr, ast_list_Index):
            return self._eval_index(expr, scope)
        elif expr.expr_type == LITERAL:
            item = ExpressionItem(expr.left.value, expr.left.item_type)
            item.ref    = expr.left.ref
            item.format = expr.left.format
            return item
        elif expr.expr_type == BINARY:
            return self._eval_binary_expr(expr, scope)
        elif expr.expr_type == UNARY:
            return self._eval_unary_expr(expr, scope)
        elif expr.expr_type == GROUPING:
            return self._eval_grouping_expr(expr, scope)
        elif expr.expr_type == FUNCTION:
            return self._eval_function_expr(expr, scope)
        self.raise_error("Unknown expression type ({})".format(expr.expr_type), expr, scope)

    def _eval(self, expr: ExpressionItem, scope: MacalScope):
        if isinstance(expr.value, ast_Variable):
            return self._eval_var(expr.value, scope)
        elif isinstance(expr.value, Expr):
            result = self.evaluate_expression(expr.value, scope)
            return result
        self.raise_error("Unknown instance ({})".format(type(expr.value)), expr, scope)

    def _eval_var(self, expr: ast_Variable, scope: MacalScope):
        var = scope.find_variable(expr.name())
        if var is None:
            var = scope.find_function(expr.name())
            if var is None:
                self.raise_error("Variable not found {}".format(expr.name()), expr, scope)
            else:
                return ExpressionItem(var, FUNCTION)
        if expr.has_index():
            index = []
            for index_expr in expr.index:
                iev = self.evaluate_expression(index_expr, scope)
                index.append(iev)
            return self._eval_indexed_var(var, index, scope)
        return ExpressionItem(var.get_value(), var.get_type())

    def listToStr(self, lst: list) -> str:
        s = "[";
        for x in lst:
            s = f"{s}{x},"
        return f"{s}]"

    def _eval_indexed_var(self, var: MacalVariable, index: list, scope: MacalScope):
        value = var.get_value()
        if value is None:
            raise RuntimeError(f"Invalid index, nil has no index. {var.name} ({self.listToStr(index)})")
        for idx in index:
            if idx is None:
                raise RuntimeError(f"Invalid index, index is nil: ({var.name}, {var.get_type()})")
            if idx.value is None:
                raise RuntimeError(f"Invalid index, index value is nil: ({var.name}, {var.get_type()}) {idx}")
            if value is None:
                raise RuntimeError(f"Invalid index, nil has no index. {var.name} ({self.listToStr(index)})")
            if isinstance(value, dict) and not idx.value in value:
                raise RuntimeError(f"Index not found: {idx.value} ({var.name})")
            elif isinstance(value, list):
                if not isinstance(idx.value, int):
                    raise RuntimeError(f"Invalid index type. Expected int, got:{idx.value} ({var.name}, {var.get_type()})")
                if not 0 <= idx.value < len(value):
                    raise RuntimeError(f"Index not found: {idx.value} ({var.name})")
            elif not (isinstance(value, dict) or isinstance(value, list)):
                raise RuntimeError(f"Index not valid, value is neither an array nor a record. Value: {value} {type(value)} var:({var.name} index: {idx.value})")
            value = value[idx.value]
        return ExpressionItem(value, scope.get_value_type(value))
    
    def _eval_index(self, index: ast_list_Index, scope: MacalScope):
        result = self.evaluate_expression(index.expr, scope)
        return result

    def _eval_variable(self, var: MacalVariable, scope: MacalScope):
        return ExpressionItem(var.get_value(), var.get_type())

    def _eval_nil(self, left, right, operand):
        lv = left.value
        rv = right.value
        if lv is None:
            lv = NIL
        if rv is None:
            rv = NIL
        if operand == "==":
            return ExpressionItem(lv == rv, BOOL)
        elif operand == "!=":
            return ExpressionItem(lv != rv, BOOL)
        raise RuntimeError(f"Incompatible operand types {left.item_type} ({left.value}) {operand} {right.item_type} ({right.value}).")

    def _eval_binary_expr(self, expr: Expr, scope: MacalScope):
        left  = self._eval(expr.left, scope)
        # Stop evaluating right hand of an and if the left is already false. Just in case it is a "gate keeper" value
        # that stops syntactic and logic problems evaluating the rest of the equasion.
        if expr.operator == 'and' and left.value is False:
            return ExpressionItem(False, BOOL)
        if expr.operator == 'or' and left.value is True:
            return ExpressionItem(True, BOOL)
        right = self._eval(expr.right, scope)

        if left.value is None or right.value is None or left.item_type == NIL or right.item_type == NIL:
            return self._eval_nil(left, right, expr.operator)
        result_type = left.item_type
        if (left.item_type == INT and right.item_type == FLOAT) or (left.item_type == FLOAT and right.item_type == INT):
            result_type = FLOAT
        elif left.item_type != right.item_type:
            if expr.operator == "==" or expr.operator == "!=":
                return ExpressionItem(expr.operator == "!=", BOOL)
            self.raise_error(f"Incompatible operand types {left.item_type} ({left.value}) {expr.operator} {right.item_type} ({right.value}).", expr, scope)
        if expr.operator == '>':
            return ExpressionItem(left.value > right.value, BOOL)
        if expr.operator == '<':
            return ExpressionItem(left.value < right.value, BOOL)
        if expr.operator == '>=':
            return ExpressionItem(left.value >= right.value, BOOL)
        if expr.operator == '<=':
            return ExpressionItem(left.value >= right.value, BOOL)
        if expr.operator == '==':
            return ExpressionItem(left.value == right.value, BOOL)
        if expr.operator == '!=':
            return ExpressionItem(left.value != right.value, BOOL)
        if expr.operator == '*':
            value = self.get_copy_of(left.value) * self.get_copy_of(right.value)
            return ExpressionItem(value, result_type)
        if expr.operator == '/':
            if right.value == 0 or right.value == 0.0:
                self.raise_error("Division by zero.", expr, scope)
            value = self.get_copy_of(left.value) / self.get_copy_of(right.value)
            return ExpressionItem(value, result_type)
        if expr.operator == '+':
            value = self.get_copy_of(left.value) + self.get_copy_of(right.value)
            return ExpressionItem(value, result_type)
        if expr.operator == '-':
            value = self.get_copy_of(left.value) - self.get_copy_of(right.value)
            return ExpressionItem(value, result_type)
        if expr.operator == 'and':
            return ExpressionItem(left.value and right.value, result_type)
        if expr.operator == 'or':
            return ExpressionItem(left.value or right.value, result_type)

        self.raise_error("Unknown op in expression ({})".format(expr.operator), expr, scope)

    def _eval_unary_expr(self, expr: Expr, scope: MacalScope):
        right = self._eval(expr.right, scope)
        # neg
        if expr.operator == '-' and (right.item_type == INT or right.item_type == FLOAT):
            return ExpressionItem(right.value * -1, right.item_type)
        # not
        elif expr.operator == '!' and right.item_type == BOOL:
            return ExpressionItem(not right.value, BOOL)
        elif expr.operator == '&':
            right.ref = True
            return right
        elif expr.operator == '$':
            right.format = True
            return right
        self.raise_error("Incompatible type: ({})".format(right.item_type), expr, scope)
    
    def _eval_grouping_expr(self, expr: Expr, scope: MacalScope):
        return self._eval(expr.left, scope)
    
    def _eval_function_expr(self, expr: Expr, scope:MacalScope):
        fval = self.interpret_function_call(expr.left.value, scope)
        while not isinstance(fval, ExpressionItem):
            fval = self.evaluate_expression(fval, scope)
        return fval

    def interpret_assign(self, instruction, scope: MacalScope):
        if instruction.expr is None:
            self.raise_error("Expression is None", instruction, scope)
        if instruction.ident.has_index():
            self._interpret_indexed_assign(instruction, scope)
            return
        var_name = instruction.ident.name()
        var = scope.find_variable(var_name)
        
        if var is None:
            var = scope.add_new_variable(var_name)
        item = self.evaluate_expression(instruction.expr, scope)
        var.set_type(item.item_type)
        var.set_value(self.get_copy_of(item.value))

    def get_copy_of(self, value):
        if isinstance(value, bool):
            return bool(value)
        if isinstance(value, list):
            return list(value)
        if isinstance(value, dict):
            return dict(value)
        if isinstance(value, str):
            return str(value)
        if isinstance(value, int):
            return int(value)
        if isinstance(value, tuple):
            return tuple(value)
        if isinstance(value, set):
            return set(value)
        if isinstance(value, float):
            return float(value)
        return value

    def _get_full_index(self, instruction, scope: MacalScope):
        """Returns an array with all the values that make up the index"""
        index = []
        for idx in instruction.ident.index:
            idv = self.evaluate_expression(idx.expr, scope)
            index.append(idv.value)
        return index

    def _interpret_indexed_assign(self, instruction, scope: MacalScope):
        """Assignes a value to an indexed variable"""
        var_name = instruction.ident.name()
        var = scope.find_variable(var_name)
        if var is None:
            self.raise_error("Variable not found: {}".format(var_name), instruction, scope)
        var_type = var.get_type()
        var_value = var.get_value()
        if not (var_type == ARRAY or var_type == RECORD or var_type == ANY):
            self.raise_error("Incompatible variable type: {}".format(var_type), instruction, scope)
        indexed_value = var_value
        index = self._get_full_index(instruction, scope)
        if len(index) > 1:
            for i, v in enumerate(index):
                indexed_value = indexed_value[index[i]]
                if i == len(index) - 2:
                    break;
        i = len(index) - 1
        item = self.evaluate_expression(instruction.expr, scope)
        if index[i] == NEW_ARRAY_INDEX:
            if isinstance(indexed_value, list):
                indexed_value.append(self.get_copy_of(item.value))
            else:
                raise self.raise_error(f"Invalid new array index on record.", instruction, scope)
        elif isinstance(index[i], str):
            if isinstance(indexed_value, dict):
                indexed_value[index[i]] = self.get_copy_of(item.value)
            else:
                raise self.raise_error(f"String is not a valid index for an array.", instruction, scope)
        elif isinstance(index[i], int):
            if isinstance(indexed_value, list):
                indexed_value[index[i]] = self.get_copy_of(item.value)
            else:
                raise self.raise_error(f"Int is not a valid index for a record.", instruction, scope)
        else:
            raise self.raise_error(f"Invalid index type. (need int or string) ({type(index[i])}).", instruction, scope)

    def interpret_block(self, block, scope: MacalScope):
        if scope.get_halt():
            return
        for instruction in block.instruction_list:
            self.interpret_instruction(instruction, scope)
            if scope.break_flag or scope.get_halt():
                return

    def interpret_break_loop(self, instruction, scope: MacalScope):
        if scope.is_loop:
            scope.break_flag = True
        else:
            self.raise_error("not in loop", scope, instruction)
        if scope.parent is not None:
            s = scope.parent
            while s is not None and s.is_loop:
                s.break_flag = True
                s = s.parent

    def interpret_function_call(self, instruction, scope: MacalScope):
        func = scope.find_function(instruction.name())
        if func is None:
            var = scope.find_variable(instruction.name())
            if var is not None:
                value = var.get_value()
                if (isinstance(value, MacalFunction)):
                    func = value
                else:
                    self.raise_error("function not found: {}".format(instruction.name()), instruction, scope)
            else:
                self.raise_error("function not found: {}".format(instruction.name()), instruction, scope)
        call_scope = scope.create_child('call {}'.format(instruction.name()), False)
        call_scope.can_search = False
        call_scope.is_function = True
        return_var = call_scope.add_new_variable('?return_var{}'.format(call_scope.name))
        return_var.set_type(NIL)
        return_var.set_value(NIL)
        param_list = []
        if func.args.count() == 1 and func.args.params[0].token.token_type == PARAMS:
            index = 0
            for expr in instruction.params.params:
                pn = f"{func.args.params[0].name()}{index}"
                index += 1
                var = call_scope.add_new_variable(pn)
                param_list.append(var)
                value = self.evaluate_expression(expr, scope)
                if (isinstance(value, ExpressionItem)):
                    var.set_value(self.get_copy_of(value.value))
                    var.set_type(value.item_type)
                    var.ref = value.ref
                    var.format = value.format
                else:
                    self.raise_error("Unknown return type", value, scope)
        else:
            for param, instr in zip(func.args.params, instruction.params.params):
                var = call_scope.add_new_variable(param.name())
                param_list.append(var)
                value = None
                if param.token.token_type == VARIABLE:
                    pv = MacalVariable(instr.token.value)
                    index = []
                    for ind in instr.index:
                        index.append(self.evaluate_expression(ind.expr, scope))
                    pv.index = index
                    value = ExpressionItem(pv, VARIABLE)
                else:
                    value = self.evaluate_expression(instr, scope)
                if (isinstance(value, ExpressionItem)):
                    var.set_value(self.get_copy_of(value.value))
                    var.set_type(value.item_type)
                    var.ref = value.ref
                    var.format = value.format
                else:
                    self.raise_error("Unknown return type", value, scope)

        if func.is_extern:
            func.call_extern(func, instruction.name(), param_list, call_scope)
        else:
            self.interpret_block(func.block, call_scope)
        vc = return_var
        scope.remove_child(call_scope) #for testing purposes we don't remove the child scope.
        return vc

    def walk_var_index(self, var: MacalVariable, index: list, scope: MacalScope):
        value = var.get_value()
        for idx in index:
            index = self.evaluate_expression(idx.expr, scope)
            if isinstance(value, dict) and not index.value in value:
                raise RuntimeError(f"Index not found {index.value} ({var.name}, {scope.name})")
            elif isinstance(value, list):
                if not isinstance(index.value, int):
                    raise RuntimeError(f"Invalid index type. Expected int, got:{index.value} ({var.name}, {var.get_type()})")
                if not 0 <= index.value < len(value):
                    raise RuntimeError(f"Index not found {index.value} ({var.name}, {scope.name})")
            elif not (isinstance(value, dict) or isinstance(value, list)):
                raise RuntimeError(f"Index not valid, not an array or record: {value} ({var.name}, {scope.name})")
            value = value[index.value]
        return ExpressionItem(value, scope.get_value_type(value))        

    def interpret_foreach_loop(self, instruction, scope: MacalScope):
        loop_var   = scope.find_variable(instruction.expr.name())
        if loop_var is None:
            raise RuntimeError(f"Foreach variable not found {instruction.expr.name()} ({scope.name}) @{instruction.token.token_line},{instruction.token.token_offset}.")
        walker = None
        if len(instruction.expr.index) > 0:
            walker = self.get_copy_of(self.walk_var_index(loop_var, instruction.expr.index, scope).value)
        else:
            walker = self.get_copy_of(loop_var.get_value())
        loop_scope = scope.create_child("foreach")
        loop_scope.is_loop = True
        foreach_var = loop_scope.add_new_variable('it')
        foreach_var.set_type(ANY)
        foreach_var.set_value(None)
        for value in walker:
            foreach_var.set_value(value)
            self.interpret_block(instruction.block, loop_scope)
            if loop_scope.break_flag or loop_scope.get_halt():
                break;
        scope.remove_child(loop_scope)

    def interpret_function_definition(self, instruction: ast_Function_definition, scope: MacalScope):
        func = scope.find_function(instruction.name())
        if func is not None:
            self.raise_error("function already exists", instruction, scope)
        scope.add_new_function(instruction.name(), instruction.params, instruction.block)

    def interpret_halt(self, instruction, scope: MacalScope):
        exit_var = self.scope.find_variable(EXIT_VAR_NAME)
        if exit_var is None:
            exit_var = self.scope.add_new_variable(EXIT_VAR_NAME)
        value = self.evaluate_expression(instruction.expr, scope);
        exit_var.set_type(value.item_type)
        exit_var.set_value(value.value)
        scope.set_halt()
        s = scope
        while s.parent is not None:
            s = s.parent
            s.set_halt()

    def interpret_return(self, instruction, scope: MacalScope):
        if scope.is_function is False:
            raise RuntimeError(f"Return can't be used outside a function. @{instruction.token.token_line},{instruction.token.token_offset}");
        exit_var = scope.find_variable("?return_var{}".format(scope.name))
        if exit_var is None:
            self.raise_error("Not in a function?", instruction, scope)
        value = self.evaluate_expression(instruction.expr, scope);
        exit_var.set_type(value.item_type)
        exit_var.set_value(value.value)
        scope.break_flag = True

    def interpret_if(self, instruction: ast_If, scope: MacalScope):
        flag = False
        if self.evaluate_expression(instruction.condition, scope).value:
            if_scope = scope.create_child("if")
            self.interpret_block(instruction.block,if_scope)
            scope.remove_child(if_scope)
            flag = True
        if not flag and instruction.has_elif():
            branch_index = 0
            for branch in instruction.elif_branch:
                if self.evaluate_expression(branch.condition, scope).value:
                    branch_scope = scope.create_child("elif{}".format(branch_index))
                    self.interpret_block(branch.block, branch_scope)
                    scope.remove_child(branch_scope)
                    flag = True
                    break
                branch_index += 1
        if not flag and instruction.has_else():
            else_scope = scope.create_child("else")
            self.interpret_block(instruction.else_branch.block, else_scope)
            scope.remove_child(else_scope)
   
    def SelectWhere(self, where, items, distinct, scope: MacalScope):
        if where is None or items is None:
            return items
        result = []
        for record in items:
            userecord = self.evaluate_df(where, record, scope).value
            if userecord:
                result.append(record)
        if distinct is True:
            if len(result) > 0:
                return result[0]
            else:
                return None
        return result

    def SelectGetFields(self, params):
        fields = []
        for param in params:
            name   = param.token.token_value
            asname = name
            if param.asvalue is not None:
                asname = param.asvalue.token_value
            field = SelectFieldFilter(name,asname)
            fields.append(field)
        return fields

    def SelectDistinctList(self, items, fields):
        if items is None or len(items) == 0:
            items = {}
            if fields[0].field_name != "*":
                for field in fields:
                    items[field] = None
            return items
        return items[0]

    def SelectNoResult(self, distinct, fields):
        if not distinct:
            return []
        record = {}
        for field in fields:
            record[field.field_name] = None
        return record

    def SelectMapFields(self, fields, items):
        if isinstance(items, list):
            result = []
            for record in items:
                result.append(self.SelectMapRecord(fields, record))
            return result;
        else:
            return self.SelectMapRecord(fields, items)

    def SelectMapRecord(self, fields, record):
        # return single value if the value was already a single value!
        if not(record is not None and isinstance(record, dict)):
            return record
        if len(fields) == 1 and fields[0].field_name == '*':
            return record
        result = {}
        for field in fields:
            if field.field_name in record:
                result[field.as_name] = record[field.field_name]
            else:
                result[field.as_name] = None
        return result

    def GetIndexedValue(self, var, index, scope: MacalScope):
        value = var.get_value()
        if len(index) == 0:
            return value
        if value is None:
            return NIL
        i = 0
        while i < len(index) - 1:
            f = self.evaluate_expression(index[i].expr, scope).value
            if value is None:
                return NIL
            value = value[f]
            i += 1
        f = self.evaluate_expression(index[i].expr, scope).value
        if value is None:
            return NIL
        value = value[f]
        return value

    def SetIndexedValue(self, var, index, value, scope: MacalScope):
        rv = var.get_value()
        if len(index) == 0:
            return rv
        i = 0
        while i < (len(index) - 1):
            f = self.evaluate_expression(index[i].expr, scope).value
            if rv is None:
                if isinstance(f, str):
                    rv = {}
                elif isinstance(f, int):
                    rv = [None] * f
                else:
                    raise RuntimeError(f"Invalid index type ({type(f)}).")
            rv = rv[f]
            i += 1
        f = self.evaluate_expression(index[i].expr, scope).value
        if rv is None:
            if isinstance(f, str):
                rv = {}
            elif isinstance(f, int):
                rv = [None] * f
            else:
                raise RuntimeError(f"Invalid index type ({type(f)}).")
        rv[f] = value

    def SelectMergeInto(self, var, varindex, value, merge, scope: MacalScope):
        data = None
        if varindex is None or len(varindex) == 0:
            data = var.get_value()
        else:
            data = self.GetIndexedValue(var, varindex, scope)
        if data is None or data == NIL:
            if varindex is None or len(varindex) == 0:
                var.set_value(value)
                var.set_type(MacalScope.get_value_type(value))
            else:
                self.SetIndexedValue(var, varindex, value, scope)
            return
        if isinstance(data, dict) and isinstance(value, dict):
            if set(data.keys()) == set(value.keys()):
                # both 2 records have the same set of keys. Then we must make a list out of it!
                lst = []
                lst.append(data)
                lst.append(value)
                data = lst
            else: # just combine the two records into one.
                for key, val in value.items():
                    if not key in data or (val is not None and val != NIL):
                        data[key] = val
        elif isinstance(data, list) and isinstance(value, dict):
            data.append(value)
        elif isinstance(data, list) and isinstance(value, list) and len(value) > 0:
            for record in value:
                data.append(record)
        elif isinstance(data, dict) and isinstance(value, list):
            value.append(data)
            data = value
        else:
            data = value
        if varindex is None or len(varindex) == 0:
            var.set_value(data)
            var.set_type(MacalScope.get_value_type(data))
        else:
            self.SetIndexedValue(var, varindex, data, scope)
    
    def SelectInto(self, varname, varindex, items, merge, scope: MacalScope):
        var = scope.find_variable(varname)
        if var is None:
            var = scope.add_new_variable(varname)
        if merge:
            self.SelectMergeInto(var, varindex, items, merge, scope)
            return
        #need to reset value first, just to make sure.
        var.set_value(None)
        if varindex is not None and len(varindex) > 0:
            self.SetIndexedValue(var, varindex, items, scope)
        else:
            var.set_value(items)
            var.set_type(MacalScope.get_value_type(items))
    
    def NoneToNIL(self, varname, varindex, scope):
        var = scope.find_variable(varname)
        if varindex is None or len(varindex) == 0:
            ds = var.get_value()
        else:
            ds = self.GetIndexedValue(var, varindex, scope)
        if isinstance(ds, dict):
            for key in ds:
                if ds[key] is None:
                    ds[key] = NIL
        elif isinstance(ds, list):
            for rec in ds:
                if (rec is not None):
                    for key in rec:
                        if rec[key] is None:
                            rec[key] = NIL

    def interpret_select(self, instruction: ast_Select, scope: MacalScope):
        fields = self.SelectGetFields(instruction.params)
        items = self.evaluate_expression(instruction.sfrom, scope).value

        if instruction.where and items is not None:
            items = self.SelectWhere(instruction.where, items, instruction.distinct, scope)

        if items is not None and instruction.distinct is True and isinstance(items,list):
            items = self.SelectDistinctList(items, fields)

        if items is None and fields[0].field_name != "*":
            items = self.SelectNoResult(instruction.distinct, fields)

        if items is not None:
            items = self.SelectMapFields(fields, items)

        into_expr = instruction.into
        if isinstance(into_expr, Expr):
            if into_expr.expr_type == UNARY:
                into_expr = into_expr.right.value
        if not isinstance(into_expr, ast_Variable):
            self.raise_error("Select Into must be a variable.", 
                f"{instruction.token.location.line} {type(into_expr)}", scope)

        varname  = into_expr.name()
        varindex = into_expr.index

        self.SelectInto(varname, varindex, items, instruction.merge, scope)

        self.NoneToNIL(varname, varindex, scope)
    
    @staticmethod
    def raise_df_error(message: str):
        raise Exception(message)
    
    def evaluate_df(self, expr, record: dict, scope: MacalScope):
        if isinstance(expr, ast_Variable):
            return self._eval_var_df(expr, record, scope)
        elif isinstance(expr, MacalVariable):
            return self._eval_variable_df(expr, record, scope)
        elif isinstance(expr, ast_list_Index):
            return self._eval_index_df(expr, record, scope)
        elif expr.expr_type == LITERAL:
            return ExpressionItem(expr.left.value, expr.left.item_type)
        elif expr.expr_type == BINARY:
            return self._eval_binary_df(expr, record, scope)
        elif expr.expr_type == UNARY:
            return self._eval_unary_df(expr, record, scope)
        elif expr.expr_type == GROUPING:
            return self._eval_grouping_df(expr, record, scope)
        elif expr.expr_type == FUNCTION:
            return self._eval_function_df(expr, record, scope)
        self.raise_df_error(f"Unknown expression type ({expr.expr_type})")

    def _eval_df(self, expr: ExpressionItem, record: dict, scope: MacalScope):
        if isinstance(expr.value, ast_Variable):
            return self._eval_var_df(expr.value, record, scope)
        elif isinstance(expr.value, Expr):
            result = self.evaluate_df(expr.value, record, scope)
            return result
        self.raise_df_error(f"Unknown instance ({type(expr.value)})")

    def _get_var_df(self, expr: ast_Variable, record: dict, scope: MacalScope):
        var = scope.find_variable(expr.name())
        if var is None:
            self.raise_error(f"Variable not found {expr.name()}", expr, scope)
        if expr.has_index():
            index = []
            for index_expr in expr.index:
                iev = self.evaluate_expression(index_expr, scope)
                index.append(iev)
            return self._eval_indexed_var(var, index, scope)
        return ExpressionItem(var.get_value(), var.get_type())

    def _eval_var_df(self, expr: ast_Variable, record: dict, scope: MacalScope):
        if not expr.name() in record:
            var = scope.find_variable(expr.name())
            if var is None:
                self.raise_df_error("Field not found: {} {}".format(expr.name(), record))
            return self._get_var_df(expr, record, scope)

        var = record[expr.name()]
        return ExpressionItem(var, scope.get_value_type(var))
    
    def _eval_indexed_var_df(self, var: MacalVariable, index: list, record: dict, scope: MacalScope):
        value = var.get_value()
        for idx in index:
            if isinstance(value, dict) and not idx.value in value:
                self.raise_error("Index not found: {} ({})".format(idx.value, var.name), idx, scope)
            elif isinstance(value, list)  and not 0 <= idx.value < len(value):
                self.raise_error("Index not found: {} ({})".format(idx.value, var.name), idx, scope)
            elif not (isinstance(value, dict) or isinstance(value, list)):
                self.raise_error("Index not valid?: {} ({})".format(value, var.name), idx, scope)
            value = value[idx.value]
                    
        return ExpressionItem(value, scope.get_value_type(value))
    
    def _eval_index_df(self, index: ast_list_Index, record: dict, scope: MacalScope):
        result = self.evaluate_df(index.expr, record, scope)
        return result

    def _eval_variable_df(self, var: MacalVariable, record: dict, scope: MacalScope):
        return ExpressionItem(var.get_value(), var.get_type())

    def _eval_binary_df(self, expr: Expr, record: dict, scope: MacalScope):
        left  = self._eval_df(expr.left, record, scope)
        # Stop evaluating right hand of an and if the left is already false. Just in case it is a "gate keeper" value
        # that stops syntactic and logic problems evaluating the rest of the equasion.
        if expr.operator == 'and' and left.value is False:
            return ExpressionItem(False, BOOL)
        if expr.operator == 'or' and left.value is True:
            return ExpressionItem(True, BOOL)
        right = self._eval_df(expr.right, record, scope)
        result_type = left.item_type
        if left.item_type == INT and right.item_type == FLOAT or left.item_type == FLOAT and right.item_type == INT:
            result_type = FLOAT
        elif left.item_type == NIL or right.item_type == NIL:
            if not(expr.operator == "==" or expr.operator == "!="):
                self.raise_error(f"Incompatible operand types {left.item_type} ({left.value}) {expr.operator} {right.item_type} ({right.value}).", expr, scope)        
            if left.item_type == NIL and right.item_type == NIL:
                return ExpressionItem(expr.operator == "==", BOOL)
            else:
                return ExpressionItem(expr.operator == "!=", BOOL)
        elif left.item_type != right.item_type:
            if expr.operator == "==" or expr.operator == "!=":
                return ExpressionItem(expr.operator == "!=", BOOL)
            self.raise_error(f"Incompatible operand types {left.item_type} ({left.value}) {expr.operator} {right.item_type} ({right.value}).", expr, scope)
        if left.value is None or right.value is None:
            if left.value is None and right.value is None and expr.operator == '==':
                return ExpressionItem(True, BOOL)
            elif expr.operator == '!=':
                return ExpressionItem(True, BOOL)
            return ExpressionItem(False, BOOL)
        if expr.operator == '>':
            return ExpressionItem(left.value > right.value, BOOL)
        if expr.operator == '<':
            return ExpressionItem(left.value < right.value, BOOL)
        if expr.operator == '>=':
            return ExpressionItem(left.value >= right.value, BOOL)
        if expr.operator == '<=':
            return ExpressionItem(left.value >= right.value, BOOL)
        if expr.operator == '==':
            return ExpressionItem(left.value == right.value, BOOL)
        if expr.operator == '!=':
            return ExpressionItem(left.value != right.value, BOOL)
        if expr.operator == '*':
            value = self.get_copy_of(left.value) * self.get_copy_of(right.value)
            return ExpressionItem(value, result_type)
        if expr.operator == '/':
            if right.value == 0 or right.value == 0.0:
                self.raise_error("Division by zero.", expr, scope)
            value = self.get_copy_of(left.value) / self.get_copy_of(right.value)
            return ExpressionItem(value, result_type)
        if expr.operator == '+':
            value = self.get_copy_of(left.value) + self.get_copy_of(right.value)
            return ExpressionItem(value, result_type)
        if expr.operator == '-':
            value = self.get_copy_of(left.value) - self.get_copy_of(right.value)
            return ExpressionItem(value, result_type)
        if expr.operator == 'and':
            return ExpressionItem(left.value and right.value, result_type)
        if expr.operator == 'or':
            return ExpressionItem(left.value or right.value, result_type)

        self.raise_error("Unknown op in expression ({})".format(expr.operator), expr, scope)

    def _eval_unary_df(self, expr: Expr, record: dict, scope: MacalScope):
        right = self._eval(expr.right, scope)
        # neg
        if expr.operator == '-' and (right.item_type == INT or right.item_type == FLOAT):
            return ExpressionItem(right.value * -1, right.item_type)
        # not
        elif expr.operator == '!' and right.item_type == BOOL:
            return ExpressionItem(not right.value, BOOL)
        elif expr.operator == '&':
            right.ref = True
            return right
        elif expr.operator == '$':
            right.format = True
            return right
        self.raise_error("Incompatible type: ({})".format(right.item_type), expr, scope)
    
    def _eval_grouping_df(self, expr: Expr, record: dict, scope: MacalScope):
        return self._eval_df(expr.left, record, scope)
    
    def _eval_function_df(self, expr: Expr, record: dict, scope:MacalScope):
        fval = self.interpret_function_call(expr.left.value, scope)
        while not isinstance(fval, ExpressionItem):
            fval = self.evaluate_expression(fval, scope)
        return fval
