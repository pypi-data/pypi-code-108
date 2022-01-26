class NotFoundException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)


def get_project_by_name(all_projects, name):
    matching = [proj for proj in all_projects if proj.name.lower() == name.lower()]
    if len(matching) == 0:
        raise NotFoundException(f"Unknown project '{name}'.")
    if len(matching) > 1:
        raise ValueError(f"Unexpectedly found {len(matching)} projects with the name '{name}'")
    return matching[0]
