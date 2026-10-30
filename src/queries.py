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
      title
      date
      organized
      stash_ids { endpoint stash_id }
      tags { name }
      performers { id birthdate }
      studio { id }
      scene_markers { id }
      rating100
      interactive
      created_at
      last_played_at
      captions { language_code }
      galleries { id }
      groups { group { id } }
      files {
        width
        height
        duration
        video_codec
        audio_codec
        fingerprints { type }
      }

      play_count
      play_duration
      play_history
      o_counter

    }
  }
}
"""


PERFORMER_ATTRIBUTES_QUERY: str = """
query PerformerAttributes {
  findPerformers(filter: { per_page: -1 }) {
    performers {
      id
      name
      favorite
      rating100
      scene_count
      o_counter
      ethnicity
      hair_color
      eye_color
      height_cm
      measurements
      fake_tits
      country
      gender
    }
  }
}
"""


# Galleries, studios, tags and operational state. Fetched separately so
# a failure here never takes down the core metrics.
LIBRARY_EXTRAS_QUERY: str = """
query LibraryExtras {
  findGalleries(filter: { per_page: -1 }) {
    galleries { organized image_count }
  }
  findStudios(filter: { per_page: -1 }) {
    studios { name organized scene_count o_counter }
  }
  findTags(filter: { per_page: -1 }) {
    tags { scene_count image_count performer_count }
  }
  jobQueue { status progress }
  systemStatus { status databaseSchema }
  version { version }
  latestversion { version }
}
"""

# Stash doesn't index images, so listing them all is slow. The collector
# fetches this in the background and caches it, never inline in a scrape.
LIBRARY_IMAGES_QUERY: str = """
query LibraryImages {
  findImages(filter: { per_page: -1 }) {
    images {
      organized
      rating100
      o_counter
      tags { id }
      performers { id }
      visual_files {
        ... on ImageFile { width height format size }
        ... on VideoFile { width height size }
      }
    }
  }
}
"""


__all__ = [
    "LIBRARY_EXTRAS_QUERY",
    "LIBRARY_IMAGES_QUERY",
    "LIBRARY_STATS_QUERY",
    "PERFORMER_ATTRIBUTES_QUERY",
    "SCENE_PLAY_HISTORY_QUERY",
]

