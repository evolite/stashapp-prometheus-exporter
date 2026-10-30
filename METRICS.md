# Metrics Documentation

## Library Stats

- `stash_scenes_total` - Total scenes
- `stash_images_total` - Total images  
- `stash_galleries_total` - Total galleries
- `stash_performers_total` - Total performers
- `stash_studios_total` - Total studios
- `stash_tags_total` - Total tags
- `stash_groups_total` - Total groups
- `stash_files_total` - Total files (scenes + images)
- `stash_files_size_bytes` - Total file size in bytes
- `stash_scenes_duration_seconds` - Total scene duration in seconds

## Curation & Coverage

- `stash_scenes_organized_total` - Scenes marked as organized
- `stash_scenes_with_stashid_total` - Scenes with at least one StashID
- `stash_scenes_tagged_total` - Scenes with at least one tag
- `stash_scenes_with_performers_total` - Scenes with at least one performer
- `stash_scenes_with_studio_total` - Scenes with a studio
- `stash_scenes_watched_total` - Scenes with at least one play
- `stash_scenes_with_markers_total` - Scenes with at least one marker
- `stash_scene_markers_total` - Total number of scene markers

## Play Statistics

- `stash_total_play_count` - Total number of scene plays
- `stash_total_play_duration_seconds` - Total play duration across all scenes
- `stash_scenes_played_total` - Scenes that have at least one recorded play
- `stash_total_o_count` - Total o-count counter across all scenes

## Playtime Patterns

- `stash_play_duration_seconds_by_dow{day_of_week}` - Play duration by day of week
  - Labels: `Mon`, `Tue`, `Wed`, `Thu`, `Fri`, `Sat`, `Sun`
- `stash_play_duration_seconds_by_hour{hour_of_day}` - Play duration by hour of day
  - Labels: `0` through `23` (24-hour format)

## Tag Usage

- `stash_tag_usage_count{tag_name}` - Number of played scenes using each tag
  - Only the top 100 tags by usage are exported to limit cardinality
- `stash_tag_top_rated{tag_name}` - Number of top-rated scenes using each tag
  - Computed from the top 100 scenes by `rating100`
  - Only the top 100 tags by usage are exported to limit cardinality

## O-Count Events

- `stash_scene_o_counter{scene_id, scene_name}` - Current o-count counter value per scene
  - Only scenes with `o_counter > 0` are exported

## Performer Demographics

Missing values are exported as `Unknown`.

- `stash_performer_ethnicity_count{ethnicity}` - Number of performers by ethnicity
  - Labels: `Caucasian`, `Black`, `Asian`, `Latin`, `Unknown`, etc.
- `stash_performer_hair_color_count{hair_color}` - Number of performers by hair color
  - Labels: `Blonde`, `Brunette`, `Black`, `Red`, `Unknown`, etc.
- `stash_performer_eye_color_count{eye_color}` - Number of performers by eye color
  - Labels: `Blue`, `Brown`, `Green`, `Hazel`, `Unknown`, etc.
- `stash_performer_height_range_count{height_range}` - Number of performers by height range (5cm buckets)
  - Labels: `Under 140cm`, `140-144cm`, ... `200cm+`, `Unknown`
- `stash_performer_cup_size_count{cup_size}` - Number of performers by cup size (parsed from measurements)
  - Labels: `A`, `B`, `C`, `D`, `DD`, `Unknown`, etc.
- `stash_performer_fake_tits_count{fake_tits}` - Number of performers by fake tits status
  - Labels: `Yes`, `No`, `Unknown`, etc.
- `stash_performer_country_count{country}` - Number of performers by country (top 50 + "Other")
  - Labels: country names; countries outside the top 50 are grouped as `Other`
- `stash_performer_gender_count{gender}` - Number of performers by gender
  - Labels: `FEMALE`, `MALE`, `TRANSGENDER_MALE`, `TRANSGENDER_FEMALE`, `INTERSEX`, `NON_BINARY`, `Unknown`

## Performer Age at Scene Date

- `stash_scene_performer_age_count{age}` - Number of scene-performer pairs by performer age at scene date
  - Labels: integer ages as strings (`"18"`, `"25"`, `"35"`, etc.)
  - Only ages 18-80 are included
  - Requires both `date` on the scene and `birthdate` on the performer

## Scene Production Timeline

- `stash_scene_production_month_count{month}` - Number of scenes by production month
  - Labels: `YYYY-MM` format (`"2023-01"`, `"2024-06"`, etc.)
  - Only scenes with a valid `date` are included

## Scene Files & Quality

- `stash_scene_resolution_count{resolution}` - `4K`, `1080p`, `720p`, `480p`, `SD`, `Unknown` (by short edge)
- `stash_scene_video_codec_count{codec}` / `stash_scene_audio_codec_count{codec}` - audio `none` means no audio track
- `stash_scene_duration_bucket_count{bucket}` - `<5m`, `5-20m`, `20-60m`, `1h+`
- `stash_scenes_without_phash_total` - scenes missing a phash

## Ratings, Freshness & Flags

- `stash_scene_rating_count{rating}` / `stash_performer_rating_count{rating}` - `1`-`5` stars or `unrated`
- `stash_scene_added_month_count{month}` - scenes added to Stash per `YYYY-MM`
- `stash_scene_last_played_timestamp_seconds` - unix time of the latest play
- `stash_scenes_unplayed_total`, `stash_scenes_interactive_total`, `stash_scenes_with_captions_total`, `stash_scenes_in_gallery_total`, `stash_scenes_in_group_total`

## Performers, Studios, Tags

Named series are limited to the top 20; zero values are omitted.

- `stash_performer_scene_count{performer}`, `stash_performer_o_count{performer}`
- `stash_studio_scene_count{studio}`, `stash_studio_o_count{studio}`
- `stash_performers_favorite_total`, `stash_performers_without_scenes_total`
- `stash_studios_organized_total`
- `stash_tags_unused_total` - tags not applied to any scene, image or performer

## Images & Galleries

Image metrics come from a full image listing (slow: Stash doesn't index images). It runs in the background, refreshes hourly, and the metrics are absent until the first fetch completes.

- `stash_extras_up` - 1 if the extras query (everything below, plus studios/tags/server info) succeeded; 0 means those metrics are being dropped

- `stash_images_organized_total`, `stash_images_rated_total`, `stash_images_tagged_total`, `stash_images_with_performers_total`, `stash_images_o_count`
- `stash_image_resolution_count{resolution}`, `stash_image_format_count{format}`
- `stash_galleries_organized_total`, `stash_galleries_empty_total`

## Stash Server State

- `stash_job_queue_length{status}` - jobs by status (`running`, `ready`, ...)
- `stash_job_running_progress` - 0-1 progress of the running job, `-1` when idle
- `stash_system_status_ok`, `stash_database_schema_version`
- `stash_info{version}` - always 1; `stash_update_available` - 1 when a newer release exists (checked every 6 h; absent while the GitHub lookup fails)

## Exporter Health

- `stash_up` - 1 if the last scrape succeeded, 0 otherwise
- `stash_scrape_duration_seconds` - Time spent on the last scrape
- `stash_scrapes_total{status="success|failure"}` - Total scrape attempts
