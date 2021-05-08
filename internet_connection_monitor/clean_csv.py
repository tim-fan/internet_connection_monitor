"""
clean_csv.py

Remove null bytes and corrupt .csv lines from the given file
"""
import click

def is_float_str(s:str) -> bool:
    try:
        x = float(s)
        return True
    except ValueError:
        return False

def is_junk_line(line_index: int, line:str) -> bool:
    """
    Check that the first .csv item is a float, or the line is
    the header
    """
    if line_index == 0:
        return False
    else:
        first_entry = line[:line.find(',')]
        return not is_float_str(first_entry)

def remove_null_bytes(line:str) -> str:
    return line.replace('\x00', '')

@click.command()
@click.argument("input_csv")
def main(input_csv):
    """
    Clean given .csv file to remove corrupt lines.
    
    Result is sent to std out.
    
    Example to update the input file in place:
    clean_csv log.csv | sponge log.csv
    """

    with open(input_csv, 'r') as f:
        lines = f.readlines()

    lines = [remove_null_bytes(line) for line in lines]
    lines = [line for i, line in enumerate(lines) if not is_junk_line(i, line)]

    for line in lines:
        print(line, end='')