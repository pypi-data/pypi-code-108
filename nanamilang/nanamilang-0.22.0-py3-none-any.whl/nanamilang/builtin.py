"""NanamiLang Builtin- Macros/Functions classes"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

import functools
from typing import List
from functools import reduce

from nanamilang.token import Token
from nanamilang import fn, datatypes, loader
from nanamilang.shortcuts import get
from nanamilang.shortcuts import (
    NML_M_FORM_IS_A_VECTOR, NML_M_FORM_IS_A_HASHMAP,
    NML_M_ASSERT_FORM_IS_A_VALID_HASHMAP,
    NML_M_ASSERT_COLL_FORM_ITEMS_COUNT_IS,
    NML_M_ASSERT_COLL_FORM_ITEMS_COUNT_IS_EVEN,
    NML_M_ASSERT_FORM_IS_A_HASHMAP, NML_M_ITERATE_AS_PAIRS,
    NML_M_ASSERT_FORM_IS_A_VECTOR, ASSERT_DICT_CONTAINS_KEY
)
from nanamilang.spec import Spec
from nanamilang.shortcuts import randstr, plain2partitioned


def meta(data: dict):
    """
    NanamiLang, apply metadata to the handler function
    'name': function or macro LISP name (to access as)
    'forms': possible function or macro possible forms
    'docstring': what function or macro actually does?
    May contain 'spec' attribute, but could be omitted

    :param data: a function metadata Python dictionary
    """

    def wrapped(_fn):
        @functools.wraps(_fn)
        def function(*args, **kwargs):

            spec = data.get('spec')
            if spec:
                Spec.validate(data.get('name'), args[0], spec)

            return _fn(*args, **kwargs)

        # TODO: maybe also implement spec linting like in defn

        ASSERT_DICT_CONTAINS_KEY('name', data, 'function meta data must contain a name')
        ASSERT_DICT_CONTAINS_KEY('forms', data, 'function meta data must contain a forms')
        ASSERT_DICT_CONTAINS_KEY('docstring', data, 'function meta data must contain a docstring')

        if 'BuiltinMacro' in function.__qualname__:
            data.update({'kind': 'macro'})
        elif 'BuiltinFunctions' in function.__qualname__:
            data.update({'kind': 'function'})  # <- do not require a meta data to contain kind key

        function.meta = data

        return function

    return wrapped  # <- register builtin function/macro handle to access it inside the NanamiLang


class BuiltinMacros:
    """NanamiLang Builtin Macros"""

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne]],
           'name': '->',
           'forms': ['(-> form1 form2 ... formN)'],
           'docstring': 'Allows to write code as a pipeline'})
    def first_threading_macro(tree: list, *_: tuple) -> list or Token:
        """
        Builtin '->' macro implementation

        :param tree: a form given to this macro
        :param _: unused argument, but I need to mention it here
        :return: the modified or new source tree as it would be expected
        """

        if not len(tree) > 1:
            return tree[-1]  # <- if tree contains only one item, return it

        for idx, tof in enumerate(tree):
            if len(tree) - 1 != idx:
                next_tof = tree[idx + 1]
                if isinstance(next_tof, list):
                    tree[idx + 1].insert(1, tof)
                else:
                    tree[idx + 1] = [next_tof, tof]

        return tree[-1]  # <- will return the last form of the modified tree

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne]],
           'name': '->>',
           'forms': ['(->> form1 form2 ... formN)'],
           'docstring': 'Allows to write code as a pipeline'})
    def last_threading_macro(tree: list, *_: tuple) -> list or Token:
        """
        Builtin '->>' macro implementation

        :param tree: a form given to this macro
        :param _: unused argument, but I need to mention it here
        :return: the modified or new source tree as it would be expected
        """

        if not len(tree) > 1:
            return tree[-1]  # <- if tree contains only one item, return it

        for idx, tof in enumerate(tree):
            if len(tree) - 1 != idx:
                next_tof = tree[idx + 1]
                if isinstance(next_tof, list):
                    tree[idx + 1].append(tof)
                else:
                    tree[idx + 1] = [next_tof, tof]

        return tree[-1]  # <- will return the last form of the modified tree

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 3]],
           'name': 'if',
           'forms': ['(if cond then-branch else-branch)'],
           'docstring': 'Returns then/else depending on cond'})
    def if_macro(tree: list, local_env: dict, _, eval_function) -> list or Token:
        """
        Builtin 'if' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param _: unused argument, but I need to mention it here
        :param eval_function: reference to recursive eval function
        :return: the modified or new source tree as it would be expected
        """

        cond, then_branch, else_branch = tree

        evaluated = eval_function(local_env, cond)
        if isinstance(evaluated, datatypes.NException):
            return Token(Token.Proxy, evaluated)  # <- propagate possible exception

        return then_branch if evaluated.truthy() is True else else_branch  # return corresponding branch

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityEven]],
           'name': 'cond',
           'forms': ['(cond cond1 expr1 ... condN exprN)'],
           'docstring': 'Allows you to describe your cond-expr pairs'})
    def cond_macro(tree: list, local_env: dict, _, eval_function) -> list or Token:
        """
        Builtin 'cond' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param _: unused argument, but I need to mention it here
        :param eval_function: reference to recursive eval function
        :return: the modified or new source tree as it would be expected
        """

        for [cond, expr] in plain2partitioned(tree):

            evaluated = eval_function(local_env, cond)
            if isinstance(evaluated, datatypes.NException):
                return Token(Token.Proxy, evaluated)  # <- propagate possible exception

            if evaluated.truthy():
                return expr  # <- return expression if corresponding condition evaluated is truthy

        return Token(Token.Nil, 'nil')  # <- if nothing has been supplied to cond -> return nil data type

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne]],
           'name': 'comment',
           'forms': ['(comment ...)'],
           'docstring': 'Allows you to replace entire form with a Nil'})
    def comment_macro(*_: tuple) -> list or Token:
        """
        Builtin 'comment' macro implementation

        :param _: unused argument, but I need to mention it here
        :return: the modified or new source tree as it would be expected
        """

        return Token(Token.Nil, 'nil')  # <- our comment macro implementation just returns a nil data type

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [2, 3]]],
           'name': 'fn',
           'forms': ['(fn [p1 p2 ...] body)',
                     '(fn name [p1 p2 ...] body)'],
           'docstring': 'Allows to define anonymous function, maybe named'})
    def fn_macro(tree: list, local_env: dict, _, eval_function) -> list or Token:
        """
        Builtin 'fn' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param _: unused argument, but I need to mention it here
        :param eval_function: reference to recursive eval function
        :return: the modified or new source tree as it would be expected
        """

        name_token, parameters_form, body_token_or_form = [None] * 3

        if len(tree) == 2:
            parameters_form, body_token_or_form = tree
        elif len(tree) == 3:
            name_token, parameters_form, body_token_or_form = tree
            assert not isinstance(name_token, list), 'fn: name needs to be a token, not a form'
            assert name_token.type() == Token.Identifier, 'fn: fn name needs to be an Identifier'

        NML_M_ASSERT_FORM_IS_A_VECTOR(parameters_form, 'fn: parameters form needs to be a Vector')

        parameters = []
        for parameter_tof in NML_M_ITERATE_AS_PAIRS(parameters_form):
            if isinstance(parameter_tof, list):
                NML_M_ASSERT_FORM_IS_A_VECTOR(parameters_form, 'fn: the form needs to be a Vector')
                right = []
                for x in NML_M_ITERATE_AS_PAIRS(parameter_tof):
                    assert x.type() == Token.Identifier, 'fn: param name needs to be an Identifier'
                    right.append(x.dt().origin())
                parameters.append((f'{randstr()}', right))
            else:
                assert parameter_tof.type() == Token.Identifier, 'fn: param name is not Identifier'
                parameters.append((parameter_tof.dt().origin(), None))

        name = name_token.dt().origin() if name_token else randstr()

        fni = fn.Fn(body_token_or_form, local_env, eval_function, name, parameters)
        handle = lambda args: fni.handle(tuple(args))  # <- we can not use fni.handle in direct way

        handle.meta = {
            'name': name, 'docstring': '',
            'kind': 'function', 'forms': fni.generate_meta__forms()
        }

        payload = {name: datatypes.Function({'function_name': name,  'function_reference': handle})}

        local_env.update(payload)  # <- update local environment, thus AST will be aware of our function
        fni.env().update(payload)  # <- and also we need to update function closure for the same purpose

        return Token(Token.Identifier, name)  # <- should return a locally defined NanamiLang function name

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne]],
           'name': 'and',
           'forms': ['(and cond1 cond2 ... condN)'],
           'docstring': 'Returns true if nothing, first/last depending on cond'})
    def and_macro(tree: list, local_env: dict, _, eval_function) -> list or Token:
        """
        Builtin 'and' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param _: unused argument, but I need to mention it here
        :param eval_function: reference to recursive eval function
        :return: the modified or new source tree as it would be expected
        """

        if not tree:
            return Token(Token.Boolean, True)  # <- by default -> return true

        for cond in tree:

            evaluated = eval_function(local_env, cond)
            if isinstance(evaluated, datatypes.NException):
                return Token(Token.Proxy, evaluated)  # <- propagate possible exception

            if not evaluated.truthy():
                return cond  # <- return condition if it has not been evaluated into truthy one

        return tree[-1]  # <- like in Clojure and other LISP engines, if nothing is falsie, return the latest element

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne]],
           'name': 'or',
           'forms': ['(or cond1 cond2 ... condN)'],
           'docstring': 'Returns nil if nothing, first/last depending on cond'})
    def or_macro(tree: list, local_env: dict, _, eval_function) -> list or Token:
        """
        Builtin 'or' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param _: unused argument, but I need to mention it here
        :param eval_function: reference to recursive eval function
        :return: the modified or new source tree as it would be expected
        """

        if not tree:
            return Token(Token.Nil, 'nil')  # <- by default -> return nil

        for condition in tree:

            evaluated = eval_function(local_env, condition)
            if isinstance(evaluated, datatypes.NException):
                return Token(Token.Proxy, evaluated)  # <- propagate possible exception

            if evaluated.truthy():
                return condition  # <- return condition if it has been evaluated into truthy one

        return tree[-1]  # <- like in Clojure and other LISP engines, if nothing is truthy, return the latest element

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 2]],
           'name': 'def',
           'forms': ['(def binding dtype)'],
           'docstring': 'Allows to define global binding and access it later'})
    def def_macro(tree: list, local_env: dict, module_env, eval_function) -> list or Token:
        """
        Builtin 'def' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param module_env: module environment we are free to modify
        :param eval_function: reference to recursive eval function
        :return: modified or new source tree as it would be expected
        """

        binding_token, dtype_token_or_form = tree

        assert not isinstance(binding_token, list), 'def: binding could not be a form'
        assert binding_token.type() == Token.Identifier, 'def: binding needs to be an Identifier'

        evaluated = eval_function(local_env, dtype_token_or_form)
        if isinstance(evaluated, datatypes.NException):
            return Token(Token.Proxy, evaluated)  # <- propagate possible exception

        name = binding_token.dt().origin()

        module_env.set(name, evaluated)

        return Token(Token.Identifier, name)  # <- our def macro implementation will just return defined binding name

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [3, 4, 5]]],
           'name': 'defn',
           'forms': ['(defn name [p1 p2 ...] body)',
                     '(defn name docstring [p1 p2 ...] body)',
                     '(defn name docstring spec [p1 p2 ...] body)'],
           'docstring': 'Allows to define named (maybe documented) function'})
    def defn_macro(tree: list, local_env: dict, module_env, eval_function) -> list or Token:
        """
        Builtin 'defn' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param module_env: module environment we are free to modify
        :param eval_function: reference to recursive eval function
        :return: modified or new source tree as it would be expected
        """

        name_token, docstring_token, spec_form, parameters_form, body_token_or_form = [None] * 5

        if len(tree) == 3:
            name_token, parameters_form, body_token_or_form = tree
        elif len(tree) == 4:
            name_token, docstring_token, parameters_form, body_token_or_form = tree
        elif len(tree) == 5:
            name_token, docstring_token, spec_form, parameters_form, body_token_or_form = tree

        assert not isinstance(name_token, list), 'defn: name needs to be a token, not a form'
        assert name_token.type() == Token.Identifier, 'defn: function name needs to be Identifier'

        if docstring_token:
            assert not isinstance(docstring_token, list), 'defn: docstring needs to be a token, not a form'
            assert docstring_token.type() == Token.String, 'defn: docstring needs to be a type of a String'

        ####################################################################################################

        spec_list = None  # <- even if there is no spec form has passed, I need to define local variable :))

        if spec_form:
            NML_M_ASSERT_FORM_IS_A_HASHMAP(spec_form, 'defn: spec form needs to be a Hashmap')
            NML_M_ASSERT_FORM_IS_A_VALID_HASHMAP(spec_form, 'defn: spec form needs to be a _valid_ HashMap')

            spec_list = []

            evaluated = eval_function(local_env, spec_form)
            if isinstance(evaluated, datatypes.NException):
                return Token(Token.Proxy, evaluated)  # <- propagate possible exception

            spec_key_mapping = {'each-argument-type-is': Spec.EachArgumentTypeIs,
                                'each-argument-type-variants': Spec.EachArgumentTypeVariants,
                                'arguments-type-chain-variants': Spec.ArgumentsTypeChainVariants}

            # We could do this much simpler, but at least we support 99% of current NanamiLang Spec linting

            spec_vector = evaluated.get(datatypes.Keyword('nanamilang-spec'))
            assert isinstance(spec_vector, datatypes.Vector), 'defn::nanamilang-spec key\'s missing/invalid'
            assert not spec_vector.empty().truthy(),  'defn: could not work with the empty spec Vector coll'
            for concrete_spec_vector in spec_vector.items():
                assert isinstance(concrete_spec_vector, datatypes.Vector),   'defn: spec needs to be Vector'
                assert not concrete_spec_vector.empty().truthy(), 'defn: could not work with empty spec Vec'
                spec_key, spec_value = concrete_spec_vector.items()
                assert isinstance(spec_key, datatypes.Keyword),  'defn: each spec key needs to be a Keyword'
                assert isinstance(spec_value, (datatypes.String,
                                               datatypes.Vector)),  'defn: needs to be a String or a Vector'
                spec_key_str = spec_key.reference()
                assert spec_key_str in spec_key_mapping,   'defn: that spec does not exist or not available'
                actual_spec_key_str = spec_key_mapping.get(spec_key_str)
                if isinstance(spec_value, datatypes.String):
                    actual_spec_value_str_or_tuple = datatypes.DataType.resolve(spec_value.reference())
                elif isinstance(spec_value, datatypes.Vector):
                    assert not spec_value.empty().truthy(), 'defn: could now work with an empty Vector coll'
                    actual_spec_value_str_or_tuple = []
                    for maybe_vector_or_string in spec_value.items():
                        if isinstance(maybe_vector_or_string, datatypes.String):
                            actual_spec_value_str_or_tuple.append(datatypes.DataType.resolve(
                                maybe_vector_or_string.reference()
                            ))
                        elif isinstance(maybe_vector_or_string, datatypes.Vector):
                            datatype_classes = []
                            for should_be_string in maybe_vector_or_string.items():
                                assert isinstance(should_be_string, datatypes.String), 'defn: not a String!'
                                datatype_classes.append(datatypes.DataType.resolve(
                                    should_be_string.reference()
                                ))
                            datatype_classes = tuple(datatype_classes)  # <- cast list into tuple, need it!
                            actual_spec_value_str_or_tuple.append(datatype_classes)
                        else:
                            raise AssertionError('defn: something went wrong while applying a spec form.')
                    actual_spec_value_str_or_tuple = tuple(actual_spec_value_str_or_tuple)  # <- cast it !!
                else:
                    actual_spec_value_str_or_tuple = ()  # <- just because I want to ensure this is defined
                spec_list.append([actual_spec_key_str, actual_spec_value_str_or_tuple])  # <- how we handle.

        ####################################################################################################

        NML_M_ASSERT_FORM_IS_A_VECTOR(parameters_form, 'defn: function parameters form needs to be a Vector')

        parameters = []
        for parameter_tof in NML_M_ITERATE_AS_PAIRS(parameters_form):
            if isinstance(parameter_tof, list):
                NML_M_ASSERT_FORM_IS_A_VECTOR(parameters_form, message='defn: the form needs to be a Vector')
                right = []
                for x in NML_M_ITERATE_AS_PAIRS(parameter_tof):
                    assert x.type() == Token.Identifier, 'defn: function param name needs to be an Identifier'
                    right.append(x.dt().origin())
                parameters.append((f'{randstr()}', right))
            else:
                assert parameter_tof.type() == Token.Identifier, 'defn: function param name is not Identifier'
                parameters.append((parameter_tof.dt().origin(), None))

        name = name_token.dt().origin()

        fni = fn.Fn(body_token_or_form, local_env, eval_function, name, parameters, spec_list)
        handle = lambda args: fni.handle(tuple(args))  # <- we are not able to use fni.handle in direct way :(

        handle.meta = {
            'name': name, 'docstring': docstring_token.dt().reference() if docstring_token else '',
            'kind': 'function', 'forms': fni.generate_meta__forms()
        }

        module_env.set(name, datatypes.Function({'function_name': name,  'function_reference': handle}))

        return Token(Token.Identifier, name)  # <- our defn implementation will just return the defined function name

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 1]],
           'name': 'require',
           'forms': ['(require \'module-name)'],
           'docstring': 'Allows to require *.nml module'})
    def require_macro(tree: list, local_env: dict, module_env, eval_function) -> list or Token:
        """
        Builtin 'require' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param module_env: module environment we are free to modify
        :param eval_function: reference to recursive eval function
        :return: modified or new source tree as it would be expected
        """

        # We make it a macro because functions has no access to global environment

        module_name_token_or_form = tree[0]

        evaluated = eval_function(local_env, module_name_token_or_form)
        if isinstance(evaluated, datatypes.NException):
            return Token(Token.Proxy, evaluated)  # <- propagate possible exception

        assert isinstance(evaluated, datatypes.Symbol), 'require: module name needs to be Symbol'

        loader.Loader.load(evaluated.reference(), module_env)  # <- this should take care of module environment

        return Token(Token.Nil, 'nil')  # <- our require macro implementation just returns nil dtype (like in Clojure)

    ##################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 2]],
           'name': 'for',
           'forms': ['(for [identifier coll] body-token-or-form)'],
           'docstring': 'Iterates through an evaluated Vector collection'})
    def for_macro(tree: list, local_env: dict, _, eval_function) -> list or Token:
        """
        Builtin 'for' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param _: unused argument, but i need to mention it here
        :param eval_function: reference to recursive eval function
        :return: modified or new source tree as it would be expected
        """

        identifier_coll_vector_form, body_token_or_form = tree

        NML_M_ASSERT_FORM_IS_A_VECTOR(identifier_coll_vector_form, 'for: first argument needs to be a Vector')

        NML_M_ASSERT_COLL_FORM_ITEMS_COUNT_IS(identifier_coll_vector_form, 2,
                                              'for: first arguments should contain identifier and collection')

        identifier_token, coll_token_or_form = tuple(NML_M_ITERATE_AS_PAIRS(identifier_coll_vector_form))

        assert identifier_token.type() == Token.Identifier, 'for: for-cycle identifier needs to be an Identifier'

        evaluated = eval_function(local_env, coll_token_or_form)
        if isinstance(evaluated, datatypes.NException):
            return Token(Token.Proxy, evaluated)  # <- propagate possible exception

        assert isinstance(evaluated, datatypes.Vector), 'for: collection to iterate through needs to be a Vector'

        _ = []

        for an_item in evaluated.items():
            local_env[identifier_token.dt().origin()] = an_item
            _evaluated = eval_function(local_env, body_token_or_form)
            if isinstance(_evaluated, datatypes.NException):
                return Token(Token.Proxy, _evaluated)  # <- propagate possible exception
            _.append(_evaluated)

        _resulting_vector_data_type = datatypes.Vector(tuple(_))

        return Token(Token.Proxy, _resulting_vector_data_type)  # <- for-cycle will return resulted vector collection

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 2]],
           'name': 'let',
           'forms': ['(let [b1 v1 ...] b1)'],
           'docstring': 'Allows to define local bindings and access them later'})
    def let_macro(tree: list, local_env: dict, _, eval_function) -> list or Token:
        """
        Builtin 'let' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param _: unused argument, but i need to mention it here
        :param eval_function: reference to recursive eval function
        :return: modified or new source tree as it would be expected
        """

        bindings_form, body_token_or_form = tree

        NML_M_ASSERT_FORM_IS_A_VECTOR(bindings_form, 'let: bindings form needs to be a Vector')
        NML_M_ASSERT_COLL_FORM_ITEMS_COUNT_IS_EVEN(bindings_form, 'let: bindings form needs to be even')

        for [idn_token_or_form, dtype_token_or_form] in NML_M_ITERATE_AS_PAIRS(bindings_form, 2):
            evaluated = eval_function(local_env, dtype_token_or_form)
            if isinstance(evaluated, datatypes.NException):
                return Token(Token.Proxy, evaluated)  # <- propagate possible exception
            if isinstance(idn_token_or_form, list):
                if NML_M_FORM_IS_A_VECTOR(idn_token_or_form):
                    assert isinstance(evaluated, datatypes.Vector),  'let: right-side needs to be Vector collection'
                    NML_M_ASSERT_COLL_FORM_ITEMS_COUNT_IS(
                        idn_token_or_form,
                        evaluated.count().reference(), 'let: lengths of both left, right-side vectors do not match')
                    for from_left, from_right in zip(NML_M_ITERATE_AS_PAIRS(idn_token_or_form),
                                                     evaluated.reference()):
                        assert from_left.type() == Token.Identifier,      'let: left-side needs to be an Identifier'
                        local_env[from_left.dt().origin()] = from_right
                elif NML_M_FORM_IS_A_HASHMAP(idn_token_or_form):
                    NML_M_ASSERT_FORM_IS_A_VALID_HASHMAP(idn_token_or_form, 'let: can not destruct invalid HashMap')
                    assert isinstance(evaluated, datatypes.HashMap), 'let: right-side needs to be HashMap data type'
                    _ = tuple(NML_M_ITERATE_AS_PAIRS(idn_token_or_form, 0))
                    assert len(_) == 2,  'let: expected exactly two things: the key and a vector of the identifiers'
                    NML_M_ASSERT_FORM_IS_A_VECTOR(_[1], message='let: the vector we were expected is not a Vector!')
                    assert isinstance(_[0].dt(), datatypes.Keyword),  'let: the key we were expected is not Keyword'
                    if _[0].dt().reference() == 'strs':
                        for left in NML_M_ITERATE_AS_PAIRS(_[1]):
                            assert left.type() == Token.Identifier,   'let: the left-side needs to be an Identifier'
                            local_env[left.dt().origin()] = evaluated.get(datatypes.String(left.dt().origin()))
                    elif _[0].dt().reference() == 'keys':
                        for left in NML_M_ITERATE_AS_PAIRS(_[1]):
                            assert left.type() == Token.Identifier,   'let: the left-side needs to be an Identifier'
                            local_env[left.dt().origin()] = evaluated.get(datatypes.Keyword(left.dt().origin()))
                    else:
                        raise AssertionError('let: invalid key was specified: currently supported: :keys and :strs')
                else:
                    raise AssertionError('let: given form is invalid, or we can not destructure this form for now.')
            else:
                assert idn_token_or_form.type() == Token.Identifier,  'let: the left-side needs to be an Identifier'
                local_env[idn_token_or_form.dt().origin()] = evaluated

        return body_token_or_form  # <- we just return body or token form there as is, without any modifications made

    #################################################################################################################


class BuiltinFunctions:
    """NanamiLang Builtin Functions"""

    #################################################################################################################

    @staticmethod
    def install(fn_meta: dict, fn_callback) -> bool:
        """
        Allow others to install own functions.
        For example: let the REPL install (exit) function

        :param fn_meta: required function meta information
        :param fn_callback: installed function callback reference
        """

        fn_meta.update({'kind': 'function'})
        reference_key = f'{fn_meta.get("name")}_func'
        maybe_existing = getattr(BuiltinFunctions, reference_key, None)
        if maybe_existing:
            delattr(BuiltinFunctions, reference_key)

        setattr(BuiltinFunctions, reference_key, fn_callback)
        getattr(BuiltinFunctions, reference_key, None).meta = fn_meta
        return bool(getattr(BuiltinFunctions, reference_key, None).meta == fn_meta)

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 1]],
           'name': 'identity',
           'forms': ['(identity something)'],
           'docstring': 'Returns something as it is'})
    def identity_func(args: List[datatypes.Base]) -> datatypes.Base:
        """
        Builtin 'identity' function implementation

        :param args: incoming 'identity' function arguments
        :return: datatypes.Base

        """

        return args[0]
        # Function is required for internal purposes && can be used elsewhere

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 2],
                    [Spec.ArgumentsTypeChainVariants, [[datatypes.Collection, datatypes.Base]]]],
           'name': 'contains?',
           'forms': ['(contains? collection element)'],
           'docstring': 'Check whether collection contains element or not'})
    def contains_func(args: List[datatypes.Base]) -> datatypes.Base:
        """
        Builtin 'contains?' function implementation

        :param args: incoming 'contains?' function arguments
        :return: datatypes.Base
        """

        collection: datatypes.Collection
        element: datatypes.Base

        collection, element = args

        return collection.contains(element)
        # Since complex data structures use Boolean to represent boolean value, there is no need to cast it manually

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 2],
                    [Spec.ArgumentsTypeChainVariants, [[datatypes.HashSet, datatypes.Base],
                                                       [datatypes.Vector, datatypes.IntegerNumber],
                                                       [datatypes.HashMap, datatypes.Base],
                                                       [datatypes.NException, datatypes.Keyword]]]],
           'name': 'get',
           'forms': ['(get collection by)'],
           'docstring': 'Returns collection element by key, index or element'})
    def get_func(args: List[datatypes.Base]) -> datatypes.Base:
        """
        Builtin 'get' function implementation

        :param args: incoming 'get' function arguments
        :return: datatypes.Base
        """

        collection: datatypes.Collection
        by: datatypes.Base

        collection, by = args

        return collection.get(by)
        # Let the concrete Collection.get() handle 'get' operation depending on what collection is and 'by' argument

    #################################################################################################################

    @staticmethod
    @meta({'spec': None,
           'name': 'make-vector',
           'forms': ['(make-vector e1 e2 ... eX)'],
           'docstring': 'Creates a Vector data structure'})
    def make_vector_func(args: List[datatypes.Base]) -> datatypes.Vector:
        """
        Builtin 'make-vector' function implementation

        :param args: incoming 'make-vector' function arguments
        :return: datatypes.Vector
        """

        return datatypes.Vector(tuple(args))
        # Let the Collection.__init__() handle vector structure construction

    #################################################################################################################

    @staticmethod
    @meta({'spec': None,
           'name': 'make-hashset',
           'forms': ['(make-hashset e1 e2 ... eX)'],
           'docstring': 'Creates a HashSet data structure'})
    def make_set_func(args: List[datatypes.Base]) -> datatypes.HashSet:
        """
        Builtin 'make-hashset' function implementation

        :param args: incoming 'make-hashset' function arguments
        :return: datatypes.HashSet
        """

        return datatypes.HashSet(tuple(args))
        # Let the Collection.__init__() handle hashset structure construction

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityEven]],
           'name': 'make-hashmap',
           'forms': ['(make-hashmap k1 v2 ... kX vX)'],
           'docstring': 'Creates a HashMap data structure'})
    def make_hashmap_func(args: List[datatypes.Base]) -> datatypes.HashMap:
        """
        Builtin 'make-hashmap' function implementation

        :param args: incoming 'make-hashmap' function arguments
        :return: datatypes.HashMap
        """

        return datatypes.HashMap(tuple(args))
        # Let the Collection.__init__() handle hashmap structure construction

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 1]],
           'name': 'not',
           'forms': ['(not something)'],
           'docstring': 'Returns something truth inverted'})
    def not_func(args: List[datatypes.Base]) -> datatypes.Boolean:
        """
        Builtin 'not' function implementation

        :param args: incoming 'not' function arguments
        :return: datatypes.String
        """

        return datatypes.Boolean(args[0].truthy()).nope()
        # We need to cast truthy() return value manually to Boolean

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne]],
           'name': '=',
           'forms': ['(= s1 s2 ... sX)'],
           'docstring': 'Returns false once current != next'})
    def eq_func(args: List[datatypes.Base]) -> datatypes.Boolean:
        """
        Builtin '=' function implementation

        :param args: incoming '=' function arguments
        :return: datatypes.Boolean
        """

        _ne = False
        for idx, curr in enumerate(args):
            _next = get(args, idx + 1, None)
            if not _next:
                break
            _ne = curr.hashed() == _next.hashed()
            if not _ne:
                break

        return datatypes.Boolean(_ne)  # once _ne == False, exit the function

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne],
                    [Spec.EachArgumentTypeIs, datatypes.Numeric]],
           'name': '<',
           'forms': ['(< n1 n2 ... nX)'],
           'docstring': 'Returns false once current > than next'})
    def less_than_func(
            args: List[datatypes.Numeric]) -> datatypes.Boolean:
        """
        Builtin '<' function implementation

        :param args: incoming '<' function arguments
        :return: datatypes.Boolean
        """

        _lt = False
        for idx, curr in enumerate(args):
            _next = get(args, idx + 1, None)
            if not _next:
                break
            _lt = curr.reference() < _next.reference()
            if not _lt:
                break

        return datatypes.Boolean(_lt)  # once _lt == False, exit the function

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne],
                    [Spec.EachArgumentTypeIs, datatypes.Numeric]],
           'name': '>',
           'forms': ['(> n1 n2 ... nX)'],
           'docstring': 'Returns false once current < than next'})
    def greater_than_func(
            args: List[datatypes.Numeric]) -> datatypes.Boolean:
        """
        Builtin '>' function implementation

        :param args: incoming '>' function arguments
        :return: datatypes.Boolean
        """

        _gt = False
        for idx, curr in enumerate(args):
            _next = get(args, idx + 1, None)
            if not _next:
                break
            _gt = curr.reference() > _next.reference()
            if not _gt:
                break

        return datatypes.Boolean(_gt)  # once _gt == False, exit the function

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne],
                    [Spec.EachArgumentTypeIs, datatypes.Numeric]],
           'name': '<=',
           'forms': ['(<= n1 n2 ... nX)'],
           'docstring': 'Returns false once current >= than next'})
    def less_than_eq_func(
            args: List[datatypes.Numeric]) -> datatypes.Boolean:
        """
        Builtin '<=' function implementation

        :param args: incoming '>=' function arguments
        :return: datatypes.Boolean
        """

        _lte = False
        for idx, curr in enumerate(args):
            _next = get(args, idx + 1, None)
            if not _next:
                break
            _lte = curr.reference() <= _next.reference()
            if not _lte:
                break

        return datatypes.Boolean(_lte)  # once _lte == False, exit the function

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 2],
                    [Spec.EachArgumentTypeIs, datatypes.Numeric]],
           'name': '>=',
           'forms': ['(>= n1 n2 ... nX)'],
           'docstring': 'Returns false once current <= than next'})
    def greater_than_eq_func(
            args: List[datatypes.Numeric]) -> datatypes.Boolean:
        """
        Builtin '>=' function implementation

        :param args: incoming '>=' function arguments
        :return: datatypes.Boolean
        """

        _gte = False
        for idx, curr in enumerate(args):
            _next = get(args, idx + 1, None)
            if not _next:
                break
            _gte = curr.reference() >= _next.reference()
            if not _gte:
                break

        return datatypes.Boolean(_gte)  # once _gte == False, exit the function

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne],
                    [Spec.EachArgumentTypeIs, datatypes.Numeric]],
           'name': '+',
           'forms': ['(+ n1 n2 ... nX)'],
           'docstring': 'Applies "+" operation to passed numbers'})
    def add_func(args: List[datatypes.Numeric]) -> datatypes.Numeric:
        """
        Builtin '+' function implementation

        :param args: incoming '+' function arguments
        :return: datatypes.IntegerNumber or datatypes.FloatNumber
        """

        result = reduce(lambda _, x: _ + x, map(lambda n: n.reference(), args))

        return datatypes.IntegerNumber(result) if isinstance(result, int) else datatypes.FloatNumber(result)

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne],
                    [Spec.EachArgumentTypeIs, datatypes.Numeric]],
           'name': '-',
           'forms': ['(- n1 n2 ... nX)'],
           'docstring': 'Applies "-" operation to passed numbers'})
    def sub_func(args: List[datatypes.Numeric]) -> datatypes.Numeric:
        """
        Builtin '-' function implementation

        :param args: incoming '-' function arguments
        :return: datatypes.IntegerNumber or datatypes.FloatNumber
        """

        result = reduce(lambda _, x: _ - x, map(lambda n: n.reference(), args))

        return datatypes.IntegerNumber(result) if isinstance(result, int) else datatypes.FloatNumber(result)

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne],
                    [Spec.EachArgumentTypeIs, datatypes.Numeric]],
           'name': '*',
           'forms': ['(* n1 n2 ... nX)'],
           'docstring': 'Applies "*" operation to passed numbers'})
    def mul_func(args: List[datatypes.Numeric]) -> datatypes.Numeric:
        """
        Builtin '*' function implementation

        :param args: incoming '*' function arguments
        :return: datatypes.IntegerNumber or datatypes.FloatNumber
        """

        result = reduce(lambda _, x: _ * x, map(lambda n: n.reference(), args))

        return datatypes.IntegerNumber(result) if isinstance(result, int) else datatypes.FloatNumber(result)

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne],
                    [Spec.EachArgumentTypeIs, datatypes.Numeric]],
           'name': '/',
           'forms': ['(/ n1 n2 ... nX)'],
           'docstring': 'Applies "/" operation to passed numbers'})
    def divide_func(args: List[datatypes.Numeric]) -> datatypes.Numeric:
        """
        Builtin '/' function implementation

        :param args: incoming '/' function arguments
        :return: datatypes.IntegerNumber or datatypes.FloatNumber
        """

        result = reduce(lambda _, x: _ / x, map(lambda n: n.reference(), args))

        return datatypes.IntegerNumber(result) if isinstance(result, int) else datatypes.FloatNumber(result)

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne],
                    [Spec.EachArgumentTypeIs, datatypes.Numeric]],
           'name': 'mod',
           'forms': ['(mod n1 n2 ... nX)'],
           'docstring': 'Applies "mod" operation to passed numbers'})
    def modulo_func(args: List[datatypes.Numeric]) -> datatypes.Numeric:
        """
        Builtin 'mod' function implementation

        :param args: incoming 'mod' function arguments
        :return: datatypes.IntegerNumber or datatypes.FloatNumber
        """

        result = reduce(lambda _, x: _ % x, map(lambda n: n.reference(), args))

        return datatypes.IntegerNumber(result) if isinstance(result, int) else datatypes.FloatNumber(result)

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 2],
                    [Spec.ArgumentsTypeChainVariants, [[datatypes.Function, datatypes.Collection],
                                                       [datatypes.Keyword, datatypes.Collection]]]],
           'name': 'map',
           'forms': ['(map function collection)'],
           'docstring': 'Allows to map collection elements with the passed function'})
    def map_func(args: List[datatypes.Base]) -> datatypes.Vector or datatypes.NException:
        """
        Builtin 'map' function implementation

        :param args: incoming 'map' function arguments
        :return: datatypes.Vector
        """

        function: datatypes.Function or datatypes.Keyword
        collection: datatypes.Collection

        function, collection = args

        if isinstance(function, datatypes.Keyword):
            k = function
            function = datatypes.Function(
                {'function_name': randstr(),
                 'function_reference': lambda _a_: BuiltinFunctions.get_func(_a_ + [k])})

        _ = []
        for element in collection.items():
            res = function.reference()([element])
            if isinstance(res, datatypes.NException):
                return res  # <- if we encountered an NException data type, we need to propagate it
            _.append(res)

        return datatypes.Vector(tuple(_))  # <- return a resulting vector of the mapped collection elements

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 2],
                    [Spec.ArgumentsTypeChainVariants, [[datatypes.Function, datatypes.Collection],
                                                       [datatypes.Keyword, datatypes.Collection]]]],
           'name': 'filter',
           'forms': ['(filter function collection)'],
           'docstring': 'Allows to filter collection elements with the passed function'})
    def filter_func(args: List[datatypes.Base]) -> datatypes.Vector or datatypes.NException:
        """
        Builtin 'filter' function implementation

        :param args: incoming 'filter' function arguments
        :return: datatypes.Vector
        """

        function: datatypes.Function or datatypes.Keyword
        collection: datatypes.Collection

        function, collection = args

        if isinstance(function, datatypes.Keyword):
            k = function
            function = datatypes.Function(
                {'function_name': randstr(),
                 'function_reference': lambda _a_: BuiltinFunctions.get_func(_a_ + [k])})

        _ = []
        for element in collection.items():
            res = function.reference()([element])
            if isinstance(res, datatypes.NException):
                return res  # <- if we encountered an NException data type, we need to propagate it
            if res.truthy():
                _.append(element)

        return datatypes.Vector(tuple(_))  # <- return a resulting vector of the filtered collection elements
