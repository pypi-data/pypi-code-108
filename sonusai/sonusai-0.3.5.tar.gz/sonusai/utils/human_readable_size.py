def human_readable_size(size: float, decimal_places: int = 3) -> str:
    for unit in ['B', 'kB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f'{size:.{decimal_places}f} {unit}'
