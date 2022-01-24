def replace_string_in_file(filepath, searched, replaced):
    with open(filepath) as f:
        file_source = f.read()
        # replace all occurences
        replace_string = file_source.replace(searched, replaced)

    with open(filepath, "w") as f:
        f.write(replace_string)
