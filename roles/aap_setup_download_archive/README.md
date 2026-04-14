# infra.aap_utilities.aap\_setup\_download\_archive

Download **every** image file returned by the Red Hat content-set (cset) API for a given Ansible Automation Platform minor version, RHEL major, and architecture. Files already present under the destination directory are **skipped** when their SHA-256 matches the `checksum` field from the API—so re-runs only fetch new tarballs or replace files that are missing, incomplete, or corrupted.

The cset listing uses a single API request with the `limit` query parameter (capped at 100).

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
