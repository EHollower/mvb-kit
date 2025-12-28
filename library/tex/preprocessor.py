#!/usr/bin/env python3

"""
Source code preprocessor for the MVB-KIT build process.

This script is inspired by the KACTL preprocessor.py. It reads source files,
extracts specially formatted comment blocks for metadata, and generates
LaTeX code for typesetting the code into a printable document.

Attributes:
    LICENSE: This work is released under the CC0-1.0 Universal Public
        Domain Dedication. For the full legal text, see:
        https://creativecommons.org/publicdomain/zero/1.0/

    REFERENCE: https://github.com/kth-competitive-programming/kactl
"""

import re
import sys
import argparse
import subprocess

from pathlib import Path
from typing import List, Dict, Tuple, Optional


# --- Regex ---
_INCLUDE_RE = re.compile(r'#include\s*[<"](.+)[>"]')
_ORDO_PATTERN = re.compile(r'O\(([^()]*(?:\([^()]*\)[^()]*)*)\)')

# -- Paths ---
_HASH_SCRIPT = Path('library/contest/hash.sh')


# --- LaTeX Utilities ---


def tex_escape(text: str) -> str:
    """Escapes characters that have special meaning in LaTeX"""
    return (text.replace('<', r'\ensuremath{<}')
                .replace('>', r'\ensuremath{>}')
            )


def path_escape(text: str) -> str:
    """Escapes characters for file paths in LaTeX."""
    return tex_escape(text.replace('\\', r'\\')
                          .replace('_', r'\_'))


def code_escape(text: str) -> str:
    """Escapes characters for code environments."""
    return tex_escape(text.replace('_', r'\_')
                          .replace('{', r'\{')
                          .replace('}', r'\}')
                          .replace('\n', '\\\\\n')
                          .replace('^', r'\textasciicircum{}'))


def ordo_escape(text: str, esc: bool = True) -> str:
    """
    Identifies O(...) blocks, preserves their math syntax.
    It goes just one level deep.
    Note: "Time:" and "Memory:" section should be wrapped in $$
    """
    if esc:
        text = tex_escape(text)

    def _replacer(match: re.Match) -> str:
        inner = match.group(1)
        processed_inner = ordo_escape(inner, esc=False)
        return rf"\bigo{{{processed_inner}}}"

    return _ORDO_PATTERN.sub(_replacer, text)


# --- Core Processing Logic ---


class CodeProcessor:
    """Processes a source file to extract code, metadata, and includes."""

    """
    These types of comments:
        - include metadata
        - are long descriptions
    They WILL NOT be included in the pdf unless, raw or rawcpp is specified!
    """

    COMMENT_TYPES = [
        ('/**', '*/'),   # C, CPP, JAVA, KOTLIN, RUST
        ("'''", "'''"),  # PYTHON
        ('"""', '"""')   # PYTHON
    ]

    """Commands used in metadata comment (always first line)"""
    KNOWN_COMMANDS = [
        'Author',
        'Date',
        'Description',
        'Source',
        'Time',
        'Memory',
        'License',
        'Status',
        'Usage',
        'Details',
        'Warning'
    ]

    REQUIRED_COMMANDS = [
        'Author',
        'Description'
    ]

    def __init__(self, file_path: Path, language: str):
        # -- Input State --
        self.file_path = file_path
        self.language = language
        self.source_lines: List[str] = []

        # -- Output State --
        self.includes: List[str] = []
        self.commands: Dict[str, str] = {}
        self.code: str = ""

        # -- Processing Issues --
        self.errors: List[str] = []
        self.warnings: List[str] = []

    @staticmethod
    def _parse_include(line: str) -> Optional[str]:
        """Parses an #include line and returns the filename."""
        m = _INCLUDE_RE.match(line)
        if not m:
            return None
        path = m.group(1)
        parts = path.split("/")
        while parts and parts[0] == "..":
            parts.pop(0)
        return "/".join(parts) if parts else None

    def _find_start_comment(
        self, source: str, start: int
    ) -> Tuple[int, int, Optional[str]]:
        """Finds the earliest start-comment delimiter."""
        candidates = [
            (i, i + len(s), e)
            for s, e in self.COMMENT_TYPES
            if (i := source.find(s, start)) != -1
        ]
        return min(candidates, default=[-1, -1, None], key=lambda x: x[0])

    def _store_command(self, command: str, value: str):
        """Stores a parsed command and warns if it's unknown."""
        if command not in self.KNOWN_COMMANDS:
            self.warnings.append(f"Unknown command: {command}.")
        self.commands[command] = value.lstrip()

    def _parse_comment_block(self, comment: str):
        """Extracts key-value command pairs from a comment block."""
        current_command = None
        current_value = ""

        for line in comment.split('\n'):
            line = line.strip()
            if line.startswith('*'):
                line = line[1:].strip()

            head, *rest = line.split(":", 1)
            is_command = (
                rest                     # has a colon
                and " " not in head      # no spaces
                and head.isalpha()       # letters only
                and head[0].isupper()    # starts with capital
            )

            if is_command:
                if current_command:
                    self._store_command(current_command, current_value)
                current_command = head
                current_value = rest[0].strip()
            else:
                current_value += "\n" + line

        if current_command:
            self._store_command(current_command, current_value)

    def _read_and_filter_lines(self):
        """Reads a source file, filtering out excluded lines and includes."""
        try:
            lines = self.file_path.read_text(encoding='utf-8').splitlines()
        except OSError as e:
            self.errors.append(f"Could not read source file: {e}.")
            return

        toggle = False
        has_HPP = False
        for raw in lines:
            if "_HPP" in raw:
                has_HPP = True

            if any(x in raw for x in ("#pragma once", "_HPP", "exclude-line")):
                continue

            if "exclude-function" in raw:
                toggle = not toggle
                continue

            if toggle is True:
                continue

            if 'include-line' in raw:
                raw = raw.replace('// ', '', 1)

            # Strip trailing /// comments
            line, sep, _ = raw.partition("///")
            line = line.rstrip()
            had_comment = bool(sep)

            # Skip lines that are only ///
            if had_comment and not line:
                continue

            keep_include = "keep-include" in raw
            include = self._parse_include(line)
            if include is not None and not keep_include:
                self.includes.append(include)
                continue

            if has_HPP:
                leading = len(line) - len(line.lstrip(' '))
                line = ' ' * (leading // 2) + line.lstrip(' ')

            self.source_lines.append(line)

    def _extract_metadata_and_code(self):
        """
        Parses multiline comment blocks,
        there should be one at the start of the file containing the metadata,
        before the header guards / #pragma once, otherwise
        if there are more comments then they will not be included in the pdf
        """
        source = "\n".join(self.source_lines)
        parts: list[str] = []
        cursor = 0

        while True:
            (
                start,
                start_inner,
                end_delim
            ) = self._find_start_comment(source, cursor)

            if start == -1:
                break

            parts.append(source[cursor:start])
            cursor_end = source.find(end_delim, start_inner)

            if cursor_end == -1:
                error_delim = source[start:start_inner]
                self.errors.append(
                    f"Invalid comment block starting with '{error_delim}'."
                )
                return

            comment_text = source[start_inner:cursor_end].strip()
            self._parse_comment_block(comment_text)
            cursor = cursor_end + len(end_delim)

        self.code = ("" .join(parts) + source[cursor:]).strip()

    def _validate_commands(self):
        """Checks if all required metadata commands are present."""
        missing = set(self.REQUIRED_COMMANDS) - set(self.commands)
        for cmd in sorted(missing):
            self.errors.append(f"Missing command: {cmd}.")

    def run(self):
        """Main processing workflow."""
        self._read_and_filter_lines()
        self._extract_metadata_and_code()
        self._validate_commands()
        return self


def get_code_hash(source_code: str) -> str:
    """Calculates a hash of the source code via an external shell script."""
    try:
        proc = subprocess.run(
            ['sh', str(_HASH_SCRIPT)],
            input=source_code,
            capture_output=True,
            text=True,
            check=True
        )
        return proc.stdout.strip().split(None, 1)[0]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "hash_error"


def add_ref(caption: str, outstream) -> None:
    """Add a reference to the ToC and the header temp file."""
    stripped = caption.strip()
    escaped = path_escape(stripped)

    outstream.write(f"\\mvbkitref{{{escaped}}}\n")

    with open("header.tmp", "a", encoding="utf-8") as f:
        f.write(stripped + "\n")


def generate_raw_latex(
    caption: str,
    instream,
    outstream,
    language: str
) -> None:
    """Generates LaTeX for a raw, unprocessed code listing."""
    try:
        source = instream.read().strip()
    except IOError:
        outstream.write(r"\mvbkiterror{Could not read source.}\n")
        return

    add_ref(caption, outstream)

    line_count = source.count("\n") + 1
    outstream.write(f"\\rightcaption{{{line_count} lines}}\n")

    caption_part = f"caption={{{path_escape(caption)}}}"
    outstream.write(
        f"\\begin{{lstlisting}}[language={language},"
        f"{caption_part}]\n"
    )

    outstream.write(source.rstrip() + "\n")
    outstream.write("\\end{lstlisting}\n")


def generate_latex_output(
    processor: CodeProcessor,
    caption: str,
    outstream
) -> None:
    """Generates the final LaTeX string from the processed data."""
    if processor.errors:
        for err in processor.errors:
            outstream.write(f"\\mvbkiterror{{{caption}: {err}}}\n")
        return

    add_ref(caption, outstream)

    for warn in processor.warnings:
        outstream.write(f"\\mvbkitwarning{{{caption}: {warn}}}\n")

    def _maybe_print(cmd_name: str, macro: str, esc=tex_escape) -> None:
        val = processor.commands.get(cmd_name)
        if val:
            outstream.write(f"\\{macro}{{{esc(val)}}}\n")

    _maybe_print("Description", "defdescription", tex_escape)
    _maybe_print("Usage", "defusage", code_escape)
    _maybe_print("Time", "deftime", ordo_escape)
    _maybe_print("Memory", "defmemory", ordo_escape)
    _maybe_print("Warning", "defwarning", ordo_escape)

    if processor.includes:
        joined = ", ".join(processor.includes)
        outstream.write(f"\\leftcaption{{{path_escape(joined)}}}\n")

    if processor.code:
        hsh = (
            get_code_hash(processor.code)
            if processor.language in ['C++', 'Java']
            else ""
        )
        line_count = processor.code.count('\n') + 1
        right_caption = f"{hsh + ', ' if hsh else ''}{line_count} lines"
        outstream.write(f"\\rightcaption{{{right_caption}}}\n")

    lang_str = f", language={processor.language}"
    outstream.write(
        f"\\begin{{lstlisting}}[caption={{{path_escape(caption)}}}"
        f"{lang_str}]\n"
    )
    outstream.write(processor.code.rstrip() + "\n")
    outstream.write("\\end{lstlisting}\n")


def print_header(data: str, outstream) -> None:
    """Processes header.tmp to generate the running page header."""
    parts = data.split('|')
    until = parts[0].strip() or parts[1].strip()
    if not until:
        return

    header_file = Path('header.tmp')
    if not header_file.exists():
        return

    lines = [
        line.strip()
        for line in header_file.read_text(encoding='utf-8').splitlines()
    ]

    if until not in lines:
        return

    print("here")

    split_index = lines.index(until) + 1
    header_lines, remaining_lines = lines[:split_index], lines[split_index:]

    adjust = (
        lambda name:
        name if name.startswith('.') else name.split('.')[0]
    )

    output = r"\enspace{}".join(map(adjust, header_lines))
    font_size = 8 if sum(len(line) for line in header_lines) > 150 else 10

    outstream.write(
        rf"\fontsize{{{font_size}}}{{{font_size}}}\hspace{{3mm}}"
        rf"\textbf{{{output}}}"
    )

    header_file.write_text('\n'.join(remaining_lines) + '\n', encoding='utf-8')


def main():
    """Main function to parse arguments and dispatch tasks."""

    parser = argparse.ArgumentParser(
        description=(
            "mvbkit source code preprocessor for LaTeX. "
            "Processes headers, formats code, and manages output."
        )
    )
    parser.add_argument("-i", "--input", type=Path, help="Input source file.")
    parser.add_argument("-o", "--output", type=Path, help="Output LaTeX file.")
    parser.add_argument("-l", "--language", help="The programming language.")
    parser.add_argument("-c", "--caption", help="The caption for the listing.")
    parser.add_argument("--print-header", help="Generate dynamic page header.")

    args = parser.parse_args()

    # Determine language and caption from input file if not provided
    lang = args.language
    caption = args.caption

    if args.input:
        if not lang:
            lang = args.input.suffix[1:] if args.input.suffix else 'raw'

        if not caption:
            caption = args.input.name

    try:
        outstream = (
            open(args.output, 'w', encoding='utf-8')
            if args.output else sys.stdout
        )

        with outstream:
            if args.print_header:
                print_header(args.print_header, outstream)
                return

            if not args.input:
                raise ValueError("Input file must be specified.")

            print(f" * \x1b[1m{caption}\x1b[0m", file=sys.stderr)

            language_map = {
                "ps": ("raw", "raw"),
                "sh": ("raw", "bash"),
                "raw": ("raw", "raw"),
                "h": ("comment", "C++"),
                "c": ("comment", "C++"),
                "cc": ("comment", "C++"),
                "rawcpp": ("raw", "C++"),
                "hpp": ("comment", "C++"),
                "cpp": ("comment", "C++"),
                "kt": ("comment", "Java"),
                "rawpy": ("raw", "Python"),
                "java": ("comment", "Java"),
                "py": ("comment", "Python"),
            }

            proc_type, listings_lang = language_map.get(lang, (None, None))

            if proc_type == "comment":
                processor = CodeProcessor(args.input, listings_lang).run()
                generate_latex_output(processor, caption, outstream)
            elif proc_type == "raw":
                with open(args.input, 'r', encoding='utf-8') as instream:
                    generate_raw_latex(
                        caption, instream, outstream, listings_lang
                    )
            else:
                raise ValueError(f"Unknown language: {lang}")
    except (ValueError, IOError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
