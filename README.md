# Arrsync

Arrsync syncs takes a source Sonarr/Radarr/Lidarr server and syncs the items that
are missing on a destination Sonarr/Radarr/Lidarr server using the API.

## ⚠️ WARNING ⚠️

Please take care to ensure you have backups of your instances before using this script. This software is provided "as is" with out warranty. Use at your own risk.

This project is currently under active development, and the config structure and API is subject to change with out warning. There will not be any releases tagged until this has solidified.

## Requirements

- Only supports Sonarr/Radarr v3 and Lidarr v1
- Python 3.8 or newer

## Features

- Allows any number of sync jobs to run
- Filtering source by profile include or exclude rules
- Filtering source by tag include or exclude rules
- Set destination quality profile
- (Sonarr Only) Set destination language profile
- (Radarr Only) Include items that do not have files in sync
- Fully unit tested
- Written with modern Python with strict type checking


## Documentation

- `type` One of: `sonarr | radarr | lidarr`
- `source_url` **Required** The instance you wish to sync _from_
- `source_key` **Required**  The API key of the source instance
- `source_headers` Extra headers you may wish to send to the source instance.
- `dest_url` **Required**  The instance you wish to sync _to_
- `dest_key` **Required**  The API key of the destination instance
- `dest_headers` Extra headers you may wish to send to the destination instance.
- `dest_path` **Required** The root path of the destination instance. e.g. `/data` or `/home/USER/media`
- `dest_search_missing` Immediately start searching after syncing to destination
- `dest_monitor` Monitor the item after it is synced to the destination
- `source_tag_exclude` A comma separated list of tags on the source instance to exclude. This may be the `id` of the tag, or the label of the tag. e.g. `42` or `My Tag`. Items on the source that match will not be synced to the destination.
- `source_tag_include` A comma separated list of tags on the source instance to include. This may be the `id` of the tag, or the label of the tag. e.g. `42` or `My Tag`. Items on the source that do not match will not be synced to the destination.
- `source_profile_include` A comma separated list of profiles on the source instance to exclude. This may be the `id` of the profile, or the label of the profile. e.g. `42` or `My Tag`. Items on the source that match will not be synced to the destination.
- `source_profile_exclude` A comma separated list of profiles on the source instance to include. This may be the `id` of the profile, or the label of the profile. e.g. `42` or `My Tag`. Items on the source that do not match will not be synced to the destination.
- `source_include_missing` **Radarr Only** include "missing" files in Radarr during the sync (defaults to off)
- `dest_language_profile` **Sonarr Only** the language profile you wish to set the items synced to the destination. May be either the language profile `id` or the `name`. e.g. `42` or `English`
- `dest_metadata_profile` **Lidarr Only** the metadata profile you wish to set the items synced to the destination. May be  either the metadata profile `id` or the `name`. e.g. `42` or `Standard`


#### Example config

Each section name is a label for the job. You may specify any number of jobs you wish. You could specify `radarr-remote-to-local` then after `radarr-local-to-remote` with different settings to achieve bidirectional sync. The section headers are just labels, but if you name sections identically the last one in the config will override any that come before it.

The `[common]` section will apply to _all_ sections. This is useful if there is shared configuration between them


```
[radarr-remote-to-local]
type=radarr
source_url = http://localhost:7878/
source_key = aaa
dest_url = http://localhost:7879/radarr
dest_key = bbb
dest_path = /movies
source_include_missing = 1

[sonarr-remote-to-local]
type=sonarr
source_url = http://localhost:8989
source_key = aaa
dest_url = http://localhost:8980/sonarr
dest_key = bbb
dest_path = /tv

[lidarr-remote-to-local]
type=lidarr
source_url = http://localhost:8686/
source_key = aaa
dest_url = http://localhost:8687/lidarr
dest_key = bbb
dest_path = /music


# Shared settings between all sync jobs
[common]
dest_search_missing = 0
dest_monitor = 1
source_headers =
  X-My-Header=Custom Header Value
source_tag_exclude = no-sync
dest_profile = Any
```

## Usage

```
usage: arrsync [-h] -c CONFIG [--debug] [--dry-run]

Sync missing content between Sonarr, Radarr, and Lidarr instances

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Configuration file to use
  --debug               Print debug messages to stdout
  --dry-run             Do not sync anything
```


```
arrsync -c /etc/arrsync.conf

```
