# Ansible Collection — `lennysh.aap_utilities`

Utilities for Ansible Automation Platform workflows (tokens, gateway API helpers, AAP setup download/archive sync, etc.).

## Roles

| Role | Purpose |
|------|---------|
| `aap_setup_download_archive` | Download all files from the Red Hat AAP content-set (cset) API for configured AAP/RHEL/arch pairs, with checksum cache and minimal per-file sync. |

See each role’s `README.md` under `roles/<name>/`.

## Plugins / modules

| Module | Purpose |
|--------|---------|
| `lennysh.aap_utilities.cset_manifest_dedupe` | Merge duplicate cset API image rows (same filename + checksum); disambiguate when the same basename has different checksums. |
| `lennysh.aap_utilities.aap_setup_checksum_cache_reconcile` | Prune checksum-cache keys whose files are missing under a destination directory; optionally `touch -d` using each entry’s `date_published`. |
| `lennysh.aap_utilities.cset_download_work_queue` | Given a deduplicated manifest and checksum cache, return only rows that still need download or verification. |

Use `ansible-doc lennysh.aap_utilities.<module_name>` for full documentation and examples.

## Installation

Build or install from source (see `galaxy.yml` and your Ansible Galaxy / private index workflow).

## License

See `galaxy.yml` (MIT-0 for the collection metadata; individual roles may specify GPL or other licenses in their `meta/main.yml`).
