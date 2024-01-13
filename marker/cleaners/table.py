from marker.bbox import merge_boxes
from marker.schema import Line, Span, Block, Page
from copy import deepcopy
from tabulate import tabulate
from typing import List
import re
import textwrap
import os

def merge_table_blocks(blocks: List[Page]):
    current_lines = []
    current_bbox = None
    for page in blocks:
        new_page_blocks = []
        pnum = page.pnum
        for block in page.blocks:
            if block.most_common_block_type() != "Table":
                if len(current_lines) > 0:
                    new_block = Block(
                        lines=deepcopy(current_lines),
                        pnum=pnum,
                        bbox=current_bbox
                    )
                    new_page_blocks.append(new_block)
                    current_lines = []
                    current_bbox = None

                new_page_blocks.append(block)
                continue

            current_lines.extend(block.lines)
            if current_bbox is None:
                current_bbox = block.bbox
            else:
                current_bbox = merge_boxes(current_bbox, block.bbox)

        if len(current_lines) > 0:
            new_block = Block(
                lines=deepcopy(current_lines),
                pnum=pnum,
                bbox=current_bbox
            )
            new_page_blocks.append(new_block)
            current_lines = []
            current_bbox = None

        page.blocks = new_page_blocks


def create_new_tables(blocks: List[Page]):
    table_idx = 0
    dot_pattern = re.compile(r'(\s*\.\s*){4,}')
    dot_multiline_pattern = re.compile(r'.*(\s*\.\s*){4,}.*', re.DOTALL)

    BANK = os.environ.get('BANK', "UNKNOWN-BANK")
    YYYYMM = os.environ.get('YYYYMM', "UNKNOWN-DATE")

    for page in blocks:
        for block in page.blocks:
            if block.most_common_block_type() != "Table" or len(block.lines) < 3:
                continue

            table_rows = []
            y_coord = None
            row = []
            for line in block.lines:
                for span in line.spans:
                    if y_coord != span.y_start:
                        if len(row) > 0:
                            table_rows.append(row)
                            row = []
                        y_coord = span.y_start

                    text = span.text
                    if dot_multiline_pattern.match(text):
                        text = dot_pattern.sub(' ', text)
                    row.append(text)
            if len(row) > 0:
                table_rows.append(row)

            # Don't render tables if they will be too large
            # (d2efire) commented block
            # if max([len("".join(r)) for r in table_rows]) > 300 or len(table_rows[0]) > 8 or len(table_rows[0]) < 2:
            #    continue

            new_text = tabulate(table_rows, headers="firstrow", tablefmt="github")

            # d2efire start
            if BANK == 'OCBC':
                check_first_char = False
            else:
                check_first_char = True
            for iter_row in table_rows:
                # is first char of first element a number?
                # if not, likely not a cc transaction
                # applies to DBS and Citibank
                if check_first_char:
                    check_char = iter_row[0][0]
                    try:
                        int(check_char)
                    except:
                        continue
                if not check_first_char:
                    # OCBC-specific
                    if len(iter_row) < 3:
                        continue
                    # check that 2nd column is supposedly an "amount"
                    check_char = iter_row[1][0]
                    try:
                        int(check_char)
                    except:
                        continue

                new_row = [BANK, YYYYMM] + process_lst(iter_row)
                my_output = ','.join(new_row)
                print(my_output)
            # d2efire end

            new_span = Span(
                bbox=block.bbox,
                span_id=f"{table_idx}_fix_table",
                font="Table",
                color=0,
                block_type="Table",
                text=new_text
            )
            new_line = Line(
                bbox=block.bbox,
                spans=[new_span]
            )
            block.lines = [new_line]
            table_idx += 1
    return table_idx

def process_lst(input: List[str]) -> List[str]:
    """
    Accepts an arbitrary-sized list (length >= 3), and merges the contents of
    the second element till the second-last element into a single string,
    separated by whitespace, thus returning a list of length 3. Also strips ","
    character which affects csv output.
    process_lst(["a", "b", "c", "d", "e"]) => ["a", "b c d", "e"]
    process_lst([" a ", "b,", "c1", "d,2", "e,f"]) => ["a", "b c1 d2", "ef"]
    """
    center = input[1:-1]
    center_str = " ".join(center)
    return [input[0].strip()] + [center_str.replace(',', '')] + [input[-1].replace(',', '')]
