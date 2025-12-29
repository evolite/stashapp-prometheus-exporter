"""
GraphQL queries used by the StashApp Prometheus exporter.

These queries are based on the public Stash GraphQL API documentation
(`https://docs.stashapp.cc/api/?utm_source=openai`) and are intended to
return cheap, aggregated statistics suitable for exporter usage.

If you run a different Stash version or customised schema, validate these
queries in the Stash GraphQL playground (Settings > Tools > GraphQL playground)
and adjust them as needed.
"""

LIBRARY_STATS_QUERY: str = """
query LibraryStats {
  stats {
    scene_count
    scenes_size
    scenes_duration

    image_count
    images_size

    gallery_count
    performer_count
    studio_count
    group_count
    tag_count

    total_o_count
    total_play_duration
    total_play_count
    scenes_played
  }
}
"""


# This query powers both the playtime buckets and the metadata/coverage
# metrics. It intentionally fetches only the fields needed for aggregate
# calculations inside the exporter.
SCENE_PLAY_HISTORY_QUERY: str = """
query ScenePlayHistory {
  findScenes(filter: { per_page: -1 }) {
    scenes {
      id
      organized
      stash_ids { endpoint stash_id }
      tags { name }
      performers { id }
      studio { id }
      scene_markers { id }

      play_count
      play_duration
      play_history
      o_counter
    }
  }
}
"""


__all__ = ["LIBRARY_STATS_QUERY", "SCENE_PLAY_HISTORY_QUERY"]

