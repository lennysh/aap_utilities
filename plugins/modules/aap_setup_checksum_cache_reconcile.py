#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 Lenny Shirley
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Prune checksum cache entries for missing files; optionally touch mtimes from date_published."""

from __future__ import annotations

import os
import subprocess

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r"""
---
module: aap_setup_checksum_cache_reconcile
short_description: Prune AAP setup checksum cache for missing files and optionally set timestamps
version_added: "1.1.0"
description:
  - Removes cache keys whose files no longer exist under O(dest_dir) so a later sync will redownload them.
  - Optionally runs C(touch -d) using each entry's C(date_published) when present (GNU coreutils).
options:
  dest_dir:
    description: Directory containing downloaded archive files (basenames match cache keys).
    type: path
    required: true
  cache:
    description: In-memory checksum cache mapping filename to metadata (C(sha256), C(size), C(date_published), etc.).
    type: dict
    required: true
  touch_from_date_published:
    description: If C(true), run C(touch -d '<date_published>') for each remaining file when C(date_published) is set.
    type: bool
    default: false
author:
  - Lenny Shirley (@lennysh)
notes:
  - Touch behavior requires GNU C(touch); typical on RHEL-like targets.
"""

EXAMPLES = r"""
- name: Reconcile checksum cache after loading from disk
  lennysh.aap_utilities.aap_setup_checksum_cache_reconcile:
    dest_dir: "{{ aap_setup_down_dest_dir }}"
    cache: "{{ __aap_checksum_cache }}"
    touch_from_date_published: "{{ aap_setup_down_set_file_times_from_api | bool }}"
  register: __reconcile
"""

RETURN = r"""
cache:
  description: Pruned cache dictionary (missing files removed).
  type: dict
pruned_keys:
  description: Basenames removed because the file was not on disk.
  type: list
  elements: str
"""


def main() -> None:
    module = AnsibleModule(
        argument_spec=dict(
            dest_dir=dict(type="path", required=True),
            cache=dict(type="dict", required=True),
            touch_from_date_published=dict(type="bool", default=False),
        ),
        supports_check_mode=True,
    )

    dest = module.params["dest_dir"]
    cache = module.params["cache"]
    touch = module.params["touch_from_date_published"]
    check_mode = module.check_mode

    if not isinstance(cache, dict):
        module.fail_json(msg="cache must be a dictionary")

    pruned: dict = {}
    pruned_keys: list[str] = []
    for fn, meta in cache.items():
        path = os.path.join(dest, fn)
        if os.path.isfile(path):
            pruned[fn] = meta
        else:
            pruned_keys.append(fn)

    # Report changed only when cache keys were removed; touch may adjust mtimes without key changes.
    changed = bool(pruned_keys)

    if touch and not check_mode:
        for fn, meta in pruned.items():
            path = os.path.join(dest, fn)
            dp = (meta or {}).get("date_published") or ""
            if dp and os.path.isfile(path):
                subprocess.run(
                    ["touch", "-d", dp, path],
                    check=False,
                )

    module.exit_json(
        changed=changed,
        cache=pruned,
        pruned_keys=pruned_keys,
    )


if __name__ == "__main__":
    main()
