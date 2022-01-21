from pathlib import Path
from .common import ProcessedMessageArgs, ExceptionArgs
from .util import get_line_number


def exception_formatter(processed_message_args: ProcessedMessageArgs, exception_args: ExceptionArgs) -> str:
    """
    The exception formatter creates consistent clean exception output.
    No logging will take place within this function.\\
    The exception output will have an origination location based on the exception section.\\
    Any formatted raised exceptions will originate from the calling function.\\
    All local function or Attribute errors will originate from this function.

    The user can override the exception type from the general custom exception module classes above.

    Args:
        processed_message_args (ProcessedMessageArgs):\\
        \t\\- Message args to populate the formatted exception message.
        exception_args (ExceptionArgs):
        \t\\- Exception args to populate the formatted exception message.
    """
    try:
        caller_module = exception_args.caller_module
        caller_name = exception_args.caller_name
        if str(caller_name) == '<module>':
            caller_name = '__main__'
        caller_line = exception_args.caller_line

        # #################################################
        # ###########Formats Lists or Str Output###########
        # #################################################
        if processed_message_args.expected_result:
            if isinstance(processed_message_args.expected_result, list):
                formatted_expected_result = str('  - ' + '\n  - '.join(map(str, processed_message_args.expected_result)))
            else:
                formatted_expected_result = f'  - {processed_message_args.expected_result}'
        if processed_message_args.returned_result:
            if isinstance(processed_message_args.returned_result, list):
                formatted_returned_result = str('  - ' + '\n  - '.join(map(str, processed_message_args.returned_result)))
            else:
                formatted_returned_result = f'  - {processed_message_args.returned_result}'
        if processed_message_args.suggested_resolution:
            if isinstance(processed_message_args.suggested_resolution, list):
                formatted_suggested_resolution = str('  - ' + '\n  - '.join(map(str, processed_message_args.suggested_resolution)))
            else:
                formatted_suggested_resolution = f'  - {processed_message_args.suggested_resolution}'
        if processed_message_args.original_exception:
            formatted_original_exception = str('\n            ' + '\n            '.join(map(str, str(processed_message_args.original_exception).splitlines())))

        # #################################################
        # #######Constructs Message Based On Input#########
        # #################################################
        if processed_message_args.main_message:
            formatted_main_message = f'{processed_message_args.main_message}\n'
        else:
            formatted_main_message = ' None: No Message Provided\n'

        if processed_message_args.expected_result:
            formatted_expected_result = ('Expected Result:\n'
                                         + f'{formatted_expected_result}\n\n')
        else:
            formatted_expected_result = ''

        if processed_message_args.returned_result:
            formatted_returned_result = ('Returned Result:\n'
                                         + f'{formatted_returned_result}\n\n')
        else:
            formatted_returned_result = ''

        if processed_message_args.original_exception:
            nested_module = Path(processed_message_args.original_exception.__traceback__.tb_frame.f_code.co_filename).stem
            nested_name = processed_message_args.original_exception.__traceback__.tb_frame.f_code.co_name
            if str(nested_name) == '<module>':
                nested_name = '__main__'
            nested_line = processed_message_args.original_exception.__traceback__.tb_lineno

            formatted_original_exception = ('Nested Exception:\n\n'
                                            + '            '
                                            + (('~' * 150) + '\n            ')
                                            + (('~' * 63) + 'Start Original Exception' + ('~' * 63) + '\n            ')
                                            + (('~' * 150) + '\n            \n')
                                            + f'{formatted_original_exception}\n\n'
                                            + f'            Nested Trace Details:\n'
                                            + f'              - Exception: {type(processed_message_args.original_exception).__name__}\n'
                                            + f'              - Module: {nested_module}\n'
                                            + f'              - Name: {nested_name}\n'
                                            + f'              - Line: {nested_line}\n'
                                            + '            ' + (('~' * 150) + '\n            ')
                                            + (('~' * 65) + 'End Original Exception' + ('~' * 63) + '\n            ')
                                            + (('~' * 150) + '\n            \n'))
        else:
            formatted_original_exception = ''

        if processed_message_args.suggested_resolution:
            formatted_suggested_resolution = ('Suggested Resolution:\n'
                                              f'{formatted_suggested_resolution}\n\n')
        else:
            formatted_suggested_resolution = ''

        exception_message = (
            formatted_main_message
            + (('-' * 150) + '\n')
            + (('-' * 65) + 'Additional Information' + ('-' * 63) + '\n')
            + (('-' * 150) + '\n')
            + formatted_expected_result
            + formatted_returned_result
            + formatted_original_exception
            + formatted_suggested_resolution
            + f'Trace Details:\n'
            f'  - Exception: {exception_args.exception_type.__name__}\n'
            f'  - Module: {caller_module}\n'
            f'  - Name: {caller_name}\n'
            f'  - Line: {caller_line}\n'
            + (('-' * 150) + '\n') * 2
        )
        return exception_message
    except Exception as exec:
        # Converts the error into a formatted string with tab spacing.
        original_exception = str('\n            ' + '\n            '.join(map(str, str(exec).splitlines())))
        exception_message = (
            f'A general error has occurred while formatting the exception message.\n'
            + (('-' * 150) + '\n') + (('-' * 65) + 'Additional Information' + ('-' * 63) + '\n') + (('-' * 150) + '\n')
            + 'Returned Result:\n'
            '  - Original Exception listed below:\n\n'
            + '            ' + (('~' * 150) + '\n            ') + (('~' * 63) + 'Start Original Exception' + ('~' * 63) + '\n            ') + (('~' * 150) + '\n            \n')
            + f'{original_exception}\n\n'
            + f'            Nested Trace Details:\n'
            + f'              - Exception: {type(exec).__name__}\n'
            + f'              - Module: {Path(exec.__traceback__.tb_frame.f_code.co_filename).stem}\n'
            + f'              - Name: {exec.__traceback__.tb_frame.f_code.co_name}\n'
            + f'              - Line: {exec.__traceback__.tb_lineno}\n'
            + '            ' + (('~' * 150) + '\n            ') + (('~' * 65) + 'End Original Exception' + ('~' * 63) + '\n            ') + (('~' * 150) + '\n            \n\n')
            + f'Trace Details:\n'
            f'  - Exception: Exception\n'
            f'  - Module: formatter\n'
            f'  - Name: exception_formatter\n'
            f'  - Line: {get_line_number() + 3}\n'
            + (('-' * 150) + '\n') * 2
        )
        raise Exception(exception_message)
