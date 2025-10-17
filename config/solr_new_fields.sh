#!/bin/bash
set -e

echo "Adding closed_tags field..."
curl -s -X POST -H 'Content-type:application/json' \
  http://localhost:8983/solr/ckan/schema \
  -d '{
    "add-field": {
      "name": "closed_tags",
      "type": "string",
      "multiValued": true,
      "stored": true,
      "indexed": true
    }
  }'

echo
echo "Adding dataset_categories field..."
curl -s -X POST -H 'Content-type:application/json' \
  http://localhost:8983/solr/ckan/schema \
  -d '{
    "add-field": {
      "name": "dataset_categories",
      "type": "string",
      "multiValued": false,
      "stored": true,
      "indexed": true
    }
  }'
