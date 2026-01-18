# Metrics Documentation

All metrics are prefixed with `stash_` and follow Prometheus naming conventions.

## Library Stats

Basic counts of everything in your library:
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

How well-organized is your library? These metrics help you track that:
- `stash_scenes_organized_total` - Scenes marked as organized
- `stash_scenes_with_stashid_total` - Scenes with at least one StashID
- `stash_scenes_tagged_total` - Scenes with at least one tag
- `stash_scenes_with_performers_total` - Scenes with at least one performer
- `stash_scenes_with_studio_total` - Scenes with a studio
- `stash_scenes_watched_total` - Scenes with at least one play
- `stash_scenes_with_markers_total` - Scenes with at least one marker
- `stash_scene_markers_total` - Total number of scene markers

**Pro tip:** Calculate coverage ratios with PromQL:
- StashID coverage: `stash_scenes_with_stashid_total / stash_scenes_total`
- Organization rate: `stash_scenes_organized_total / stash_scenes_total`

## Play Statistics

Track your viewing habits:
- `stash_total_play_count` - Total number of scene plays
- `stash_total_play_duration_seconds` - Total play duration across all scenes
- `stash_scenes_played_total` - Scenes that have at least one recorded play
- `stash_total_o_count` - Total o-count counter across all scenes

## Playtime Patterns

When do you watch? These metrics break it down:
- `stash_play_duration_seconds_by_dow{day_of_week}` - Play duration by day of week
  - Labels: `Mon`, `Tue`, `Wed`, `Thu`, `Fri`, `Sat`, `Sun`
- `stash_play_duration_seconds_by_hour{hour_of_day}` - Play duration by hour of day
  - Labels: `0` through `23` (24-hour format)

## Tag Usage

See which tags are most popular among your played scenes:
- `stash_tag_usage_count{tag_name}` - Number of played scenes using each tag
  - Only the top 100 tags by usage are exported to limit cardinality
- `stash_tag_top_rated{tag_name}` - Number of top-rated scenes using each tag
  - Computed from the top 100 scenes by `rating100`
  - Only the top 100 tags by usage are exported to limit cardinality

## O-Count Events

Track o-count events per scene:
- `stash_scene_o_counter{scene_id, scene_name}` - Current o-count counter value per scene
  - Only scenes with `o_counter > 0` are exported
  - Use `increase(stash_scene_o_counter[5m])` in PromQL to see new events over time
  - Use `topk(5, stash_scene_o_counter)` to see your top 5 scenes

## Exporter Health

Is the exporter working? These metrics tell you:
- `stash_up` - 1 if the last scrape succeeded, 0 otherwise
- `stash_scrape_duration_seconds` - Time spent on the last scrape
- `stash_scrapes_total{status="success|failure"}` - Total scrape attempts

