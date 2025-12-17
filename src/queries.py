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


SCENE_PLAY_HISTORY_QUERY: str = """
query ScenePlayHistory {
  findScenes(filter: { per_page: -1 }) {
    scenes {
      play_count
      play_duration
      play_history
    }
  }
}
"""


__all__ = ["LIBRARY_STATS_QUERY", "SCENE_PLAY_HISTORY_QUERY"]


