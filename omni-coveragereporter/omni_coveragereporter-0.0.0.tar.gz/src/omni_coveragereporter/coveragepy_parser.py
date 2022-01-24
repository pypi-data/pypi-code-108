def total_lines(file_object):
    executed_lines = max(file_object['executed_lines']) if file_object['executed_lines'] else 0
    missing_lines = max(file_object['missing_lines']) if file_object['missing_lines'] else 0
    return max(executed_lines, missing_lines)
