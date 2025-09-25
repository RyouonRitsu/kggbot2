def is_blank(s: str | None) -> bool:
    return all(c.isspace() for c in s) if s else True
