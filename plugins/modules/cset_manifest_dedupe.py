#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 Lenny Shirley
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: merge duplicate cset API rows; disambiguate filename clashes."""

from __future__ import annotations

from collections import defaultdict

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r"""
---
module: cset_manifest_dedupe
short_description: Deduplicate Red Hat cset API image rows by filename and checksum
version_added: "1.1.0"
description:
  - Merges duplicate rows that share the same API filename and SHA-256 (e.g. overlapping AAP/RHEL cset listings).
  - When the same filename appears with different checksums, assigns C(effective_filename) values by appending
    C(-aap<ver>-rhel<maj>) before the bundle extension (C(.tar.gz) handled as a unit).
options:
  cset_rows:
    description: List of image objects from the cset API (each must include C(filename) and C(checksum)).
    type: list
    elements: dict
    required: true
author:
  - Lenny Shirley (@lennysh)
"""

EXAMPLES = r"""
- name: Deduplicate aggregated cset rows
  lennysh.aap_utilities.cset_manifest_dedupe:
    cset_rows: "{{ __aap_cset_raw_list }}"
  register: __cset_dedupe
"""

RETURN = r"""
deduped:
  description: Deduplicated manifest rows (C(filename) set to the effective basename on disk).
  type: list
  elements: dict
dedupe_warnings:
  description: Messages when filename/checksum collisions required disambiguation (also emitted via C(AnsibleModule.warn)).
  type: list
  elements: str
"""


def disambiguate(filename: str, aap: str, rhel: str) -> str:
    suf = f"-aap{aap}-rhel{rhel}"
    if filename.endswith(".tar.gz"):
        return filename[:-7] + suf + ".tar.gz"
    i = filename.rfind(".")
    if i > 0:
        return filename[:i] + suf + filename[i:]
    return filename + suf


def dedupe(rows: list) -> tuple[list, list]:
    by_fn: dict[str, list] = defaultdict(list)
    for r in rows:
        by_fn[r["filename"]].append(r)

    out: list = []
    warnings: list[str] = []

    for fn, group in by_fn.items():
        by_ck: dict[str, dict] = {}
        for x in group:
            ck = x["checksum"].lower()
            if ck not in by_ck:
                by_ck[ck] = x
        uniq = list(by_ck.values())
        cks = {x["checksum"].lower() for x in uniq}
        if len(cks) == 1:
            x = uniq[0]
            entry = dict(x)
            eff = fn
            entry["effective_filename"] = eff
            entry["filename"] = eff
            entry["_sources"] = [[g.get("_aap_src_version"), g.get("_aap_src_rhel")] for g in group]
            out.append(entry)
        else:
            warnings.append(
                f"Cset filename {fn!r} has {len(cks)} different checksums across "
                "AAP/RHEL pairs; using disambiguated filenames."
            )
            for x in uniq:
                aap = str(x.get("_aap_src_version") or "")
                rhel = str(x.get("_aap_src_rhel") or "")
                eff = disambiguate(fn, aap, rhel)
                entry = dict(x)
                entry["effective_filename"] = eff
                entry["filename"] = eff
                entry["_sources"] = [[aap, rhel]]
                out.append(entry)

    seen: set[tuple[str, str]] = set()
    deduped: list = []
    for e in out:
        key = (e["effective_filename"], e["checksum"].lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(e)

    return deduped, warnings


def main() -> None:
    module = AnsibleModule(
        argument_spec=dict(
            cset_rows=dict(type="list", elements="dict", required=True),
        ),
        supports_check_mode=True,
    )
    rows = module.params["cset_rows"]
    if not isinstance(rows, list):
        module.fail_json(msg="cset_rows must be a list")

    deduped, warn_msgs = dedupe(rows)
    for w in warn_msgs:
        module.warn(w)
    module.exit_json(changed=False, deduped=deduped, dedupe_warnings=warn_msgs)


if __name__ == "__main__":
    main()
