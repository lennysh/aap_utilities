# infra.aap_utilities.aap\_setup\_download\_archive

Download **every** image file returned by the Red Hat content-set (cset) API for each requested Ansible Automation Platform minor version, RHEL major, and architecture. The role **aggregates** all cset API responses first, **deduplicates** rows that share the same filename and SHA-256 (overlaps across AAP/RHEL pairs), and **disambiguates** when the same filename appears with different checksums by appending `-aap<version>-rhel<major>` before the file extension (with a `debug` summary). Collection modules **cset_manifest_dedupe**, **aap_setup_checksum_cache_reconcile**, **aap_setup_checksum_cache_merge_manifest**, and **cset_download_work_queue** (in `lennysh.aap_utilities`) perform deduplication, checksum-cache reconciliation against disk (dropping missing files; optionally `touch` by `datePublished`), merging per-file **AAP/RHEL source lists** into the cache from the deduped manifest, and building a minimal **work queue** so Ansible only runs the per-file sync tasks for artifacts that still need a download or verification.

Files already present under the destination directory are **skipped** when their SHA-256 matches the `checksum` field from the API—so re-runs only fetch new tarballs or replace files that are missing, incomplete, or corrupted.

Each cset listing uses a single API request with the `limit` query parameter (capped at 100).

## Requirements

Same as `aap_setup_download`: a valid Red Hat offline API token from [Red Hat API access](https://access.redhat.com/management/api/) (see [Getting started with Red Hat APIs](https://access.redhat.com/articles/3626371)).

## Role Variables

Required:

* `aap_setup_down_offline_token` — offline refresh token (no default).

Common options (see `defaults/main.yml`):

* `aap_setup_down_versions` — list of AAP minor lines to download (default `["2.6"]`). You may pass a single string; it is normalized to a one-element list.
* `aap_setup_down_version` — (optional) single AAP minor line as a string; if set, it overrides `aap_setup_down_versions` for backward compatibility.
* `aap_setup_rhel_versions` — list of RHEL majors for the cset name (`8`, `9`, and/or `10`). Defaults from facts when available (same idea as `aap_setup_download`); set explicitly when the control host OS does not match the install target (e.g. Fedora). You may pass a single string; it is normalized to a one-element list. Combinations with no published content return HTTP **404** from the API; those pairs are skipped (optional `debug` at verbosity 1).
* `aap_setup_rhel_version` — (optional) single RHEL major as a string; if set, it overrides `aap_setup_rhel_versions` for backward compatibility.
* `aap_setup_arch` — e.g. `x86_64`.
* `aap_setup_down_dest_dir` — directory on the target host to store all files (default `/var/tmp` or `aap_setup_working_dir` when set).
* `aap_setup_down_checksum_cache_enabled` — when `true` (default), store each file’s SHA-256, size, API `datePublished`, `imageName` (as `image_name`), and which **AAP minor** / **RHEL major** lines included that artifact (`aap_versions` and `rhel_versions`, sorted lists derived from cset `_sources`) in a JSON file so later runs skip the expensive checksum `stat` when the on-disk size still matches the cache (metadata-only `stat` still runs per file). Set `false` to always compute SHA-256 on disk.
* `aap_setup_down_checksum_cache_file` — path to that JSON file (default `{{ aap_setup_down_dest_dir }}/.aap_setup_download_archive_checksum_cache.json`). Delete the file to force a full re-checksum pass.
* `aap_setup_down_inventory_markdown_enabled` — when `true` (default), write `aap_setup_down_inventory_markdown_file` after the run: a Markdown report grouped by API **image name**, with one table per image; rows are files sorted by `datePublished`, with columns for **AAP versions**, **RHEL versions** (sorted numerically, not as plain strings), and **Size** (bytes from the cache, shown as human-readable binary units, e.g. GiB).
* `aap_setup_down_inventory_markdown_file` — destination path for that Markdown file (default `{{ aap_setup_down_dest_dir }}/aap_setup_download_inventory.md`).
* `aap_setup_down_set_file_times_from_api` — when `true` (default), run `touch -d '<datePublished>'` on each file that exists after sync so atime and mtime match the API (GNU coreutils `touch`; typical on RHEL-like targets). Set `false` to leave timestamps as set by the downloader.
* `aap_setup_down_all_page_limit` — API `limit` parameter (default `100`, maximum `100`).
* `aap_setup_down_token_refresh_skew_seconds` — obtain a new access token this many seconds before the SSO ``expires_in`` window ends (default `120`), so long runs do not hit HTTP 401 on downloads.

## Facts set by the role

* `aap_setup_down_archive_files` — list of absolute paths to each file name under `aap_setup_down_dest_dir` after the play.

## Example Playbook

```yaml
- hosts: installationserver
  gather_facts: true
  roles:
    - role: infra.aap_utilities.aap_setup_download_archive
      vars:
        aap_setup_down_offline_token: "{{ vault_rh_offline_token }}"
        aap_setup_down_dest_dir: /var/lib/aap-installers
```

## License

GPLv3+ (see collection README).
