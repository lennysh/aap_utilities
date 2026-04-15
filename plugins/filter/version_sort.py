# -*- coding: utf-8 -*-
# Copyright (c) 2026 Lenny Shirley
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Jinja filters: numeric-ish version list sort for AAP/RHEL columns."""

from __future__ import annotations

from ansible_collections.lennysh.aap_utilities.plugins.module_utils.version_sort import sort_version_strings


class FilterModule:
    def filters(self):
        return {"aap_version_sort": self.aap_version_sort}

    def aap_version_sort(self, value):
        if value is None:
            return []
        if not isinstance(value, (list, tuple, set)):
            return sort_version_strings([value])
        return sort_version_strings(list(value))
