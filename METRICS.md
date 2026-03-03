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

## Performer Demographics

Distribution metrics for performer attributes. Each metric has a single label with the attribute value; performers missing a value are counted as `Unknown`.

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

**Pro tip:** Exclude unknowns in Grafana with label matchers:
- `stash_performer_ethnicity_count{ethnicity!="Unknown"}`
- Top 10 countries: `topk(10, stash_performer_country_count{country!="Unknown"})`

## Performer Age at Scene Date

Distribution of performer ages at the time each scene was produced:
- `stash_scene_performer_age_count{age}` - Number of scene-performer pairs by performer age at scene date
  - Labels: integer ages as strings (`"18"`, `"25"`, `"35"`, etc.)
  - Only ages 18-80 are included
  - Requires both `date` on the scene and `birthdate` on the performer

**Pro tip:** Visualize as a histogram in Grafana to see the age distribution of performers across your library.

## Scene Production Timeline

Monthly breakdown of when your scenes were produced:
- `stash_scene_production_month_count{month}` - Number of scenes by production month
  - Labels: `YYYY-MM` format (`"2023-01"`, `"2024-06"`, etc.)
  - Only scenes with a valid `date` are included

**Pro tip:** Use a bar chart in Grafana sorted by month label to see your collection's production timeline.

## Exporter Health

Is the exporter working? These metrics tell you:
- `stash_up` - 1 if the last scrape succeeded, 0 otherwise
- `stash_scrape_duration_seconds` - Time spent on the last scrape
- `stash_scrapes_total{status="success|failure"}` - Total scrape attempts

