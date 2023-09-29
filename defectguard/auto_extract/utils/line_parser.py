FILE_DIFF_HEADER = [
    re.compile(r"^diff --git a/(?P<from_file>.*?)\s* b/(?P<to_file>.*?)\s*$"),
    re.compile(
        r'^diff --git "a/(?P<from_file>.*?)"\s* "b/(?P<to_file>.*?)"\s*$'),
    re.compile(
        r'^diff --git a/(?P<from_file>.*?)\s* "b/(?P<to_file>.*?)"\s*$'),
    re.compile(
        r'^diff --git "a/(?P<from_file>.*?)"\s* b/(?P<to_file>.*?)\s*$'),
]
    r"^index (?P<from_blob>.*?)\.\.(?P<to_blob>.*?)(?: (?P<mode>\d+))?$")
BINARY_DIFF = re.compile(
    r"Binary files (?P<from_file>.*) and (?P<to_file>.*) differ$")
A_FILE_CHANGE_HEADER = [
    re.compile(r"^--- (?:/dev/null|a/(?P<file>.*?)\s*)$"),
    re.compile(r'^--- (?:/dev/null|"a/(?P<file>.*?)"\s*)$'),
]
B_FILE_CHANGE_HEADER = [
    re.compile(r"^\+\+\+ (?:/dev/null|b/(?P<file>.*?)\s*)$"),
    re.compile(r'^\+\+\+ (?:/dev/null|"b/(?P<file>.*?)"\s*)$'),
]

        return "Line {}: {}".format(self.line,
                                    super(LineParseError, self).__str__())
            raise LineParseError("{} ({!r})".format(parse_exc, line),
                                 line_index + 1)
            "start_of_file",
            "new_mode_header",
            "line_diff",
            "no_newline",
            "index_diff_header",
            "binary_diff",
            "rename_b_file",
        matches = [pattern.search(line) for pattern in FILE_DIFF_HEADER]
        for match in matches:
            if match:
                return "file_diff_header", match.groupdict()
        if prev_state == "start_of_file":
            "rename_b_file",
            "file_diff_header",
            "new_mode_header",
            "new_file_mode_header",
            "deleted_file_mode_header",
        matches = [pattern.search(line) for pattern in A_FILE_CHANGE_HEADER]
        for match in matches:
            if match:
                return "a_file_change_header", match.groupdict()
        raise ParseError("Expected a_file_change_header")
        matches = [pattern.search(line) for pattern in B_FILE_CHANGE_HEADER]
        for match in matches:
            if match:
                return "b_file_change_header", match.groupdict()
        raise ParseError("Expected b_file_change_header")
    raise ParseError(
        "Can't parse line with prev_state {!r}".format(prev_state))