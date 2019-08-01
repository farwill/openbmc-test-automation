#!/usr/bin/env python

r"""
This module provides validation functions like valid_value(), valid_integer(),
etc.
"""

import os
import gen_print as gp
import func_args as fa

exit_on_error = False


def set_exit_on_error(value):
    r"""
    Set the exit_on_error value to either True or False.

    If exit_on_error is set, validation functions like valid_value() will exit
    the program on error instead of returning False.

    Description of argument(s):
    value                           Value to set global exit_on_error to.
    """

    global exit_on_error
    exit_on_error = value


def get_var_name(*args, **kwargs):
    r"""
    If args/kwargs contain a var_name, simply return its value.  Otherwise,
    get the variable name of the first argument used to call the validation
    function (e.g. valid, valid_integer, etc.) and return it.

    This function is designed solely for use by other functions in this file.

    Example:

    A programmer codes this:

    valid_value(last_name)

    Which results in the following call stack:

    valid_value(last_name)
      -> get_var_name(var_name)

    In this example, this function will return "last_name".

    Example:

    err_msg = valid_value(last_name, var_name="some_other_name")

    Which results in the following call stack:

    valid_value(var_value, var_name="some_other_name")
      -> get_var_name(var_name)

    In this example, this function will return "some_other_name".

    Description of argument(s):
    var_name                        The name of the variable.
    """

    var_name, args, kwargs = fa.pop_arg(*args, **kwargs)
    if var_name:
        return var_name
    return gp.get_arg_name(0, 1, stack_frame_ix=3)


def process_error_message(error_message):
    r"""
    Process the error_message in the manner described below.

    This function is designed solely for use by other functions in this file.

    NOTE: A blank error_message means that there is no error.

    For the following explanations, assume the caller of this function is a
    function with the following definition:
    valid_value(var_value, valid_values=[], invalid_values=[], *args,
    **kwargs):

    If the user of valid_value() is assigning the valid_value() return value
    to a variable, process_error_message() will simply return the
    error_message.  This mode of usage is illustrated by the following example:

    error_message = valid_value(var1)

    This mode is useful for callers who wish to validate a variable and then
    decide for themselves what to do with the error_message (e.g.
    raise(error_message), BuiltIn().fail(error_message), etc.).

    If the user of valid_value() is NOT assigning the valid_value() return
    value to a variable, process_error_message() will behave as follows.

    First, if error_message is non-blank, it will be printed to stderr via a
    call to gp.print_error_report(error_message).

    If exit_on_error is set:
    - If the error_message is blank, simply return.
    - If the error_message is non-blank, exit the program with a return code
      of 1.

    If exit_on_error is NOT set:
    - If the error_message is blank, return True.
    - If the error_message is non-blank, return False.

    Description of argument(s):
    error_message                   An error message.
    """

    # Determine whether the caller's caller is assigning the result to a
    # variable.
    l_value = gp.get_arg_name(None, -1, stack_frame_ix=3)
    if l_value:
        return error_message

    if error_message == "":
        if exit_on_error:
            return
        return True

    gp.print_error_report(error_message, stack_frame_ix=4)
    if exit_on_error:
        exit(1)
    return False


# Note to programmers:  All of the validation functions in this module should
# follow the same basic template:
# def valid_value(var_value, var1, var2, varn, *args, **kwargs):
#
#     error_message = ""
#     if not valid:
#         var_name = get_var_name(*args, **kwargs)
#         error_message += "The following variable is invalid because...:\n"
#         error_message += gp.sprint_varx(var_name, var_value, gp.blank())
#
#     return process_error_message(error_message)


# The docstring header and footer will be added to each validation function's
# existing docstring.
docstring_header = \
    r"""
    Determine whether var_value is valid, construct an error_message and call
    process_error_message(error_message).

    See the process_error_message() function defined in this module for a
    description of how error messages are processed.
    """

additional_args_docstring_footer = \
    r"""
    args                            Additional positional arguments (described
                                    below).
    kwargs                          Additional keyword arguments (described
                                    below).

    Additional argument(s):
    var_name                        The name of the variable whose value is
                                    passed in var_value.  For the general
                                    case, this argument is unnecessary as this
                                    function can figure out the var_name.
                                    This is provided for Robot callers in
                                    which case, this function lacks the
                                    ability to determine the variable name.
    """


def valid_type(var_value, required_type, *args, **kwargs):
    r"""
    The variable value is valid if it is of the required type.

    Examples:

    valid_type(var1, int)

    valid_type(var1, (list, dict))

    Description of argument(s):
    var_value                       The value being validated.
    required_type                   A type or a tuple of types (e.g. str, int,
                                    etc.).
    """

    error_message = ""
    if type(required_type) is tuple:
        if type(var_value) in required_type:
            return process_error_message(error_message)
    else:
        if type(var_value) is required_type:
            return process_error_message(error_message)

    # If we get to this point, the validation has failed.
    var_name = get_var_name(*args, **kwargs)
    error_message += "Invalid variable type:\n"
    error_message += gp.sprint_varx(var_name, var_value,
                                    gp.blank() | gp.show_type())
    error_message += "\n"
    error_message += gp.sprint_var(required_type)

    return process_error_message(error_message)


def valid_value(var_value, valid_values=[], invalid_values=[], *args,
                **kwargs):

    r"""
    The variable value is valid if it is either contained in the valid_values
    list or if it is NOT contained in the invalid_values list.  If the caller
    specifies nothing for either of these 2 arguments, invalid_values will be
    initialized to ['', None].  This is a good way to fail on variables which
    contain blank values.

    It is illegal to specify both valid_values and invalid values.

    Example:

    var1 = ''
    valid_value(var1)

    This code would fail because var1 is blank and the default value for
    invalid_values is ['', None].

    Example:
    var1 = 'yes'
    valid_value(var1, valid_values=['yes', 'true'])

    This code would pass.

    Description of argument(s):
    var_value                       The value being validated.
    valid_values                    A list of valid values.  The variable
                                    value must be equal to one of these values
                                    to be considered valid.
    invalid_values                  A list of invalid values.  If the variable
                                    value is equal to any of these, it is
                                    considered invalid.
    """

    error_message = ""

    # Validate this function's arguments.
    len_valid_values = len(valid_values)
    len_invalid_values = len(invalid_values)
    if len_valid_values > 0 and len_invalid_values > 0:
        error_message += "Programmer error - You must provide either an"
        error_message += " invalid_values list or a valid_values"
        error_message += " list but NOT both:\n"
        error_message += gp.sprint_var(invalid_values)
        error_message += gp.sprint_var(valid_values)
        return process_error_message(error_message)

    if len_valid_values > 0:
        # Processing the valid_values list.
        if var_value in valid_values:
            return process_error_message(error_message)
        var_name = get_var_name(*args, **kwargs)
        error_message += "Invalid variable value:\n"
        error_message += gp.sprint_varx(var_name, var_value,
                                        gp.blank() | gp.verbose()
                                        | gp.show_type())
        error_message += "\n"
        error_message += "It must be one of the following values:\n"
        error_message += "\n"
        error_message += gp.sprint_var(valid_values,
                                       gp.blank() | gp.show_type())
        return process_error_message(error_message)

    if len_invalid_values == 0:
        # Assign default value.
        invalid_values = ["", None]

    # Assertion: We have an invalid_values list.  Processing it now.
    if var_value not in invalid_values:
        return process_error_message(error_message)

    var_name = get_var_name(*args, **kwargs)
    error_message += "Invalid variable value:\n"
    error_message += gp.sprint_varx(var_name, var_value,
                                    gp.blank() | gp.verbose()
                                    | gp.show_type())
    error_message += "\n"
    error_message += "It must NOT be one of the following values:\n"
    error_message += "\n"
    error_message += gp.sprint_var(invalid_values,
                                   gp.blank() | gp.show_type())
    return process_error_message(error_message)


def valid_range(var_value, lower=None, upper=None, *args, **kwargs):
    r"""
    The variable value is valid if it is within the specified range.

    This function can be used with any type of operands where they can have a
    greater than/less than relationship to each other (e.g. int, float, str).

    Description of argument(s):
    var_value                       The value being validated.
    lower                           The lower end of the range.  If not None,
                                    the var_value must be greater than or
                                    equal to lower.
    upper                           The upper end of the range.  If not None,
                                    the var_value must be less than or equal
                                    to upper.
    """

    error_message = ""
    if not lower and not upper:
        return process_error_message(error_message)
    if not lower and var_value <= upper:
        return process_error_message(error_message)
    if not upper and var_value >= lower:
        return process_error_message(error_message)
    if lower and upper:
        if lower > upper:
            var_name = get_var_name(*args, **kwargs)
            error_message += "Programmer error - the lower value is greater"
            error_message += " than the upper value:\n"
            error_message += gp.sprint_vars(lower, upper, fmt=gp.show_type())
            return process_error_message(error_message)
        if lower <= var_value <= upper:
            return process_error_message(error_message)

    var_name = get_var_name(*args, **kwargs)
    error_message += "The following variable is not within the expected"
    error_message += " range:\n"
    error_message += gp.sprint_varx(var_name, var_value, gp.show_type())
    error_message += "\n"
    error_message += "range:\n"
    error_message += gp.sprint_vars(lower, upper, fmt=gp.show_type(), indent=2)
    return process_error_message(error_message)


def valid_integer(var_value, lower=None, upper=None, *args, **kwargs):
    r"""
    The variable value is valid if it is an integer or can be interpreted as
    an integer (e.g. 7, "7", etc.).

    This function also calls valid_range to make sure the integer value is
    within the specified range (if any).

    Description of argument(s):
    var_value                       The value being validated.
    lower                           The lower end of the range.  If not None,
                                    the var_value must be greater than or
                                    equal to lower.
    upper                           The upper end of the range.  If not None,
                                    the var_value must be less than or equal
                                    to upper.
    """

    error_message = ""
    var_name = get_var_name(*args, **kwargs)
    try:
        var_value = int(str(var_value), 0)
    except ValueError:
        error_message += "Invalid integer value:\n"
        error_message += gp.sprint_varx(var_name, var_value,
                                        gp.blank() | gp.show_type())
        return process_error_message(error_message)

    # Check the range (if any).
    if lower:
        lower = int(str(lower), 0)
    if upper:
        upper = int(str(upper), 0)
    error_message = valid_range(var_value, lower, upper, var_name=var_name)

    return process_error_message(error_message)


def valid_dir_path(var_value, *args, **kwargs):
    r"""
    The variable value is valid if it contains the path of an existing
    directory.

    Description of argument(s):
    var_value                       The value being validated.
    """

    error_message = ""
    if not os.path.isdir(str(var_value)):
        var_name = get_var_name(*args, **kwargs)
        error_message += "The following directory does not exist:\n"
        error_message += gp.sprint_varx(var_name, var_value)

    return process_error_message(error_message)


def valid_file_path(var_value, *args, **kwargs):
    r"""
    The variable value is valid if it contains the path of an existing file.

    Description of argument(s):
    var_value                       The value being validated.
    """

    error_message = ""
    if not os.path.isfile(str(var_value)):
        var_name = get_var_name(*args, **kwargs)
        error_message += "The following file does not exist:\n"
        error_message += gp.sprint_varx(var_name, var_value)

    return process_error_message(error_message)


def valid_path(var_value, *args, **kwargs):
    r"""
    The variable value is valid if it contains the path of an existing file or
    directory.

    Description of argument(s):
    var_value                       The value being validated.
    """

    error_message = ""
    if not (os.path.isfile(str(var_value)) or os.path.isdir(str(var_value))):
        var_name = get_var_name(*args, **kwargs)
        error_message += "Invalid path (file or directory does not exist):\n"
        error_message += gp.sprint_varx(var_name, var_value)

    return process_error_message(error_message)


def valid_list(var_value, valid_values=[], fail_on_empty=False, *args,
               **kwargs):
    r"""
    The variable value is valid if it is a list where each entry can be found
    in the valid_values list.

    Description of argument(s):
    var_value                       The value being validated.
    valid_values                    A list of valid values.  Each element in
                                    the var_value list must be equal to one of
                                    these values to be considered valid.
    fail_on_empty                   Indicates that an empty list for the
                                    variable value should be considered an
                                    error.
    """

    error_message = ""

    if type(var_value) is not list:
        var_name = get_var_name(*args, **kwargs)
        error_message = valid_type(var_value, list, var_name=var_name)
        if error_message:
            return process_error_message(error_message)

    if fail_on_empty and len(var_value) == 0:
        var_name = get_var_name(*args, **kwargs)
        error_message += "Invalid empty list:\n"
        error_message += gp.sprint_varx(var_name, var_value, gp.show_type())
        return process_error_message(error_message)

    found_error = 0
    display_var_value = list(var_value)
    for ix in range(0, len(var_value)):
        if var_value[ix] not in valid_values:
            found_error = 1
            display_var_value[ix] = var_value[ix] + "*"

    if found_error:
        var_name = get_var_name(*args, **kwargs)
        error_message += "The following list is invalid (see entries marked"
        error_message += " with \"*\"):\n"
        error_message += gp.sprint_varx(var_name, display_var_value,
                                        gp.blank() | gp.show_type())
        error_message += "\n"
        error_message += gp.sprint_var(valid_values | gp.show_type())
        return process_error_message(error_message)

    return process_error_message(error_message)


def valid_dict(var_value, required_keys=[], *args, **kwargs):
    r"""
    The variable value is valid if it is a dictionary containing all of the
    required keys.

    Description of argument(s):
    var_value                       The value being validated.
    required_keys                   A list of keys which must be found in the
                                    dictionary for it to be considered valid.
    """

    error_message = ""
    missing_keys = list(set(required_keys) - set(var_value.keys()))
    if len(missing_keys) > 0:
        var_name = get_var_name(*args, **kwargs)
        error_message += "The following dictionary is invalid because it is"
        error_message += " missing required keys:\n"
        error_message += gp.sprint_varx(var_name, var_value,
                                        gp.blank() | gp.show_type())
        error_message += "\n"
        error_message += gp.sprint_var(missing_keys | gp.show_type())
    return process_error_message(error_message)


# Modify selected function docstrings by adding headers/footers.

func_names = [
    "valid_type", "valid_value", "valid_range", "valid_integer",
    "valid_dir_path", "valid_file_path", "valid_path", "valid_list",
    "valid_dict"
]

raw_doc_strings = {}

for func_name in func_names:
    cmd_buf = "raw_doc_strings['" + func_name + "'] = " + func_name
    cmd_buf += ".__doc__"
    exec(cmd_buf)
    cmd_buf = func_name + ".__doc__ = docstring_header + " + func_name
    cmd_buf += ".__doc__.rstrip(\" \\n\") + additional_args_docstring_footer"
    exec(cmd_buf)
