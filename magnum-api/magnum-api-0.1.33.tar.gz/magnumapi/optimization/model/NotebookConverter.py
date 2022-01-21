import magnumapi.commons.json_file as json_file
import magnumapi.commons.text_file as text_file


def convert_notebook_to_script(input_ipynb_file_path: str, notebook_name: str, output_script_file_path: str) -> None:
    """ Function converting a notebook into a script equivalent. The notebook is executed as a function.
    The function name is given by as run_<notebook_name>. The input arguments are taken from cells with `parameters`
    tags. The return value is taken from the sb.glue code.

    :param input_ipynb_file_path:
    :param notebook_name:
    :param output_script_file_path:
    """
    notebook = json_file.read(input_ipynb_file_path)

    parameters = []
    code_lines = []
    output_line = ''
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            if 'tags' in cell['metadata'] and ('parameters' in cell['metadata']['tags']):
                for line in cell['source']:
                    if '#' in line:
                        raise AttributeError('No commented lines are allowed in the Input Parameters cell!')
                    parameters.append(line)
            else:
                for line in cell['source']:
                    if 'sb.glue' in line:
                        output_line = line
                    else:
                        code_lines.append(line.replace('\n', ''))

    output_var = output_line.split(',')[1]
    if '=' in output_var:
        output_var = output_var.split('=')[-1]

    import_lines = []
    function_lines = []

    for code_line in code_lines:
        if code_line.strip().startswith('from') or code_line.strip().startswith('import'):
            import_lines.append(code_line)
        else:
            if not (code_line.startswith('%') or ('sys.path.append' in code_line)):
                function_lines.append(code_line)

    output_lines = list(import_lines)

    output_lines.append('\n')

    parameters = [parameter.replace('\n', '') for parameter in parameters]
    output_lines.append('def run_%s_script(%s):' % (notebook_name, ', '.join(parameters)))

    for function_line in function_lines:
        output_lines.append('\t' + function_line)

    output_lines.append('\t' + 'return ' + output_var)

    text_file.writelines(output_script_file_path, output_lines)
