# -*- coding: utf-8 -*-
# Copyright (c) 2026 Lenny Shirley
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Sort version strings by dotted numeric components (e.g. 2.6 before 2.10; RHEL 8, 9, 10)."""

from __future__ import annotations


def _version_key(item: object) -> tuple:
    s = str(item).strip()
    if not s:
        return (0,)
    parts: list = []
    for p in s.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(p)
    return tuple(parts)


def sort_version_strings(items):
    """Return a new list sorted by version order (not lexicographic)."""
    if items is None:
        return []
    return sorted(list(items), key=_version_key)
