from attune_project_api import StorageTuple
from attune_project_api.Exceptions import InvalidReferenceError
from attune_project_api.Exceptions import NonUniqueScriptRefError
from attune_project_api.ObjectStorageContext import ObjectStorageContext
from attune_project_api.ObjectStorageContext import TupleValidatorABC
from attune_project_api.items.parameter_tuple import ParameterTuple
from attune_project_api.items.step_tuples.step_tuple import StepTuple


@ObjectStorageContext.registerValidator
class ParameterScriptRefValidator(TupleValidatorABC):
    """ParameterTuple Name Validator

    ParameterTuple names are checked for uniqueness by UniqueNameValidator.
    They should also result in unique script references

    """

    def validate(
        self,
        context: "ObjectStorageContext",
        item: ParameterTuple,
    ) -> None:
        if not isinstance(item, ParameterTuple):
            return

        scriptRef = item.textName
        paramsWithScriptRef = filter(
            lambda p: p.textName == scriptRef and p.name != item.name,
            context.getItems(ParameterTuple.storageGroup),
        )

        if len(list(paramsWithScriptRef)) != 0:
            raise NonUniqueScriptRefError(
                f"ParameterTuple with script reference {scriptRef} "
                f"already exists"
            )


@ObjectStorageContext.registerValidator
class StepDeployConfigParamValidator(TupleValidatorABC):
    def validate(
        self, context: ObjectStorageContext, item: StorageTuple
    ) -> None:
        from attune_project_api.items.step_tuples.step_push_design_file_compiled_tuple import (
            StepPushDesignFileCompiledParamTuple,
            StepPushDesignFileCompiledTuple,
        )

        if item is None or not isinstance(
            item, StepPushDesignFileCompiledParamTuple
        ):
            return

        placeholder = context.getItem(
            ParameterTuple.storageGroup, item.placeholderName
        )
        configStep = context.getItem(StepTuple.storageGroup, item.configstepKey)

        if (
            configStep is None
            or not isinstance(configStep, StepPushDesignFileCompiledTuple)
        ) and placeholder is None:
            raise InvalidReferenceError(
                f"A ParameterTuple with {item.placeholderName} and StepTuple"
                f" with {item.configstepKey} does not exist"
            )
        elif configStep is None or not isinstance(
            configStep, StepPushDesignFileCompiledTuple
        ):
            raise InvalidReferenceError(
                f"A StepTuple with {item.configstepKey} does not exist"
            )
        elif placeholder is None:
            raise InvalidReferenceError(
                f"A ParameterTuple with {item.placeholderName} does not exist"
            )
