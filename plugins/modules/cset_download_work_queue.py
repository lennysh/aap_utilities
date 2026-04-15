#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 Lenny Shirley
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Build the list of cset manifest rows that still need a download or verification pass."""

from __future__ import annotations

import os

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r"""
---
module: cset_download_work_queue
short_description: Compute which cset manifest rows still need download or verification
version_added: "1.1.0"
description:
  - Compares a deduplicated cset manifest to the checksum cache and files on disk under O(dest_dir).
  - When O(checksum_cache_enabled) is false, every manifest row is returned (full work queue).
options:
  dest_dir:
    description: Directory containing downloaded archive files.
    type: path
    required: true
  cache:
    description: Checksum cache mapping basename to metadata (C(sha256), C(size)).
    type: dict
    required: true
  manifest:
    description: Deduplicated cset rows (C(filename) or C(effective_filename) as the on-disk basename).
    type: list
    elements: dict
    required: true
  checksum_cache_enabled:
    description: If false, returns the full manifest as the work queue.
    type: bool
    default: true
author:
  - Lenny Shirley (@lennysh)
"""

EXAMPLES = r"""
- name: Build minimal work queue
  lennysh.aap_utilities.cset_download_work_queue:
    dest_dir: "{{ aap_setup_down_dest_dir }}"
    cache: "{{ __aap_checksum_cache }}"
    manifest: "{{ __deduped_cset_list }}"
    checksum_cache_enabled: true
  register: __wq
"""

RETURN = r"""
work_queue:
  description: Manifest rows that still require sync (download or checksum verification).
  type: list
  elements: dict
"""


def main() -> None:
    module = AnsibleModule(
        argument_spec=dict(
            dest_dir=dict(type="path", required=True),
            cache=dict(type="dict", required=True),
            manifest=dict(type="list", elements="dict", required=True),
            checksum_cache_enabled=dict(type="bool", default=True),
        ),
        supports_check_mode=True,
    )

    dest = module.params["dest_dir"]
    cache = module.params["cache"]
    manifest = module.params["manifest"]
    cache_enabled = module.params["checksum_cache_enabled"]

    work_queue: list = []
    for row in manifest:
        fn = row.get("effective_filename") or row.get("filename")
        api_sha = (row.get("checksum") or "").lower()
        path = os.path.join(dest, fn)

        if not cache_enabled:
            work_queue.append(row)
            continue

        if not os.path.isfile(path):
            work_queue.append(row)
            continue

        c = cache.get(fn)
        if not c:
            work_queue.append(row)
            continue

        if (c.get("sha256") or "").lower() != api_sha:
            work_queue.append(row)
            continue

        try:
            st_size = os.path.getsize(path)
        except OSError:
            work_queue.append(row)
            continue

        if int(c.get("size", -1)) != st_size:
            work_queue.append(row)
            continue

    module.exit_json(changed=False, work_queue=work_queue)


if __name__ == "__main__":
    main()
