#!/bin/bash
# Script to delete orgasm event history from Prometheus
# Usage: ./delete-prometheus-data.sh [container_name]

CONTAINER_NAME="${1:-prometheus}"

echo "Deleting orgasm event history (stash_scene_o_counter) from Prometheus container '${CONTAINER_NAME}'..."

# Delete only the orgasm counter metric
echo "Deleting stash_scene_o_counter metric..."
podman exec "${CONTAINER_NAME}" curl -X POST -g 'http://localhost:9090/api/v1/admin/tsdb/delete_series?match[]={__name__="stash_scene_o_counter"}'

# Clean up tombstones to free disk space
echo "Cleaning tombstones..."
podman exec "${CONTAINER_NAME}" curl -X POST 'http://localhost:9090/api/v1/admin/tsdb/clean_tombstones'

echo "Done! Orgasm event history has been deleted."
echo "Note: Data may still appear in Grafana until cache expires or you refresh."

