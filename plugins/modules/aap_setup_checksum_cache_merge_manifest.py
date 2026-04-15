#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 Lenny Shirley
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Union AAP/RHEL version lists from deduped cset rows into existing checksum cache entries."""

from __future__ import annotations

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.lennysh.aap_utilities.plugins.module_utils.version_sort import sort_version_strings

DOCUMENTATION = r"""
---
module: aap_setup_checksum_cache_merge_manifest
short_description: Merge AAP/RHEL source lists from cset manifest into checksum cache
version_added: "1.1.0"
description:
  - For each manifest row, updates the matching cache entry (by effective basename) with
    C(aap_versions) and C(rhel_versions) derived from C(_sources), unioned with any values already present.
  - Skips filenames not present in the cache (e.g. not yet downloaded).
options:
  cache:
    description: In-memory checksum cache (basename to metadata dict).
    type: dict
    required: true
  manifest:
    description: Deduped cset rows (each may include C(_sources) as list of C([aap_minor, rhel_major]) pairs).
    type: list
    elements: dict
    required: true
author:
  - Lenny Shirley (@lennysh)
"""

EXAMPLES = r"""
- name: Merge manifest AAP/RHEL lists into cache
  lennysh.aap_utilities.aap_setup_checksum_cache_merge_manifest:
    cache: "{{ __aap_checksum_cache }}"
    manifest: "{{ __deduped_cset_list }}"
  register: __merged
"""

RETURN = r"""
cache:
  description: Cache with C(aap_versions) and C(rhel_versions) merged where keys existed.
  type: dict
"""


def _merge_sources_into_cache(cache: dict, manifest: list) -> dict:
    out: dict = {k: dict(v) for k, v in cache.items()}
    for row in manifest:
        if not isinstance(row, dict):
            continue
        fn = row.get("effective_filename") or row.get("filename")
        if not fn or fn not in out:
            continue
        sources = row.get("_sources") or []
        aaps: set[str] = set()
        rhels: set[str] = set()
        for pair in sources:
            if isinstance(pair, (list, tuple)) and len(pair) >= 2:
                a, r = pair[0], pair[1]
                if a is not None and str(a).strip():
                    aaps.add(str(a).strip())
                if r is not None and str(r).strip():
                    rhels.add(str(r).strip())
        meta = dict(out[fn])
        old_a = {str(x).strip() for x in (meta.get("aap_versions") or []) if x is not None and str(x).strip()}
        old_r = {str(x).strip() for x in (meta.get("rhel_versions") or []) if x is not None and str(x).strip()}
        meta["aap_versions"] = sort_version_strings(old_a | aaps)
        meta["rhel_versions"] = sort_version_strings(old_r | rhels)
        out[fn] = meta
    return out


def main() -> None:
    module = AnsibleModule(
        argument_spec=dict(
            cache=dict(type="dict", required=True),
            manifest=dict(type="list", elements="dict", required=True),
        ),
        supports_check_mode=True,
    )
    cache = module.params["cache"]
    manifest = module.params["manifest"]
    if not isinstance(cache, dict):
        module.fail_json(msg="cache must be a dictionary")
    if not isinstance(manifest, list):
        module.fail_json(msg="manifest must be a list")

    merged = _merge_sources_into_cache(cache, manifest)
    module.exit_json(changed=False, cache=merged)


if __name__ == "__main__":
    main()
