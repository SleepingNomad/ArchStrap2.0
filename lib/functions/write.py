

def write_string_to_line(file_path, line_number, string_to_write):
    # Read the contents of the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Modify the specific line with the new string
    lines[line_number - 1] = string_to_write + '\n'

    # Write the modified contents back to the file
    with open(file_path, 'w') as file:
        file.writelines(lines)