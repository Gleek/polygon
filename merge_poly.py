from shapely.geometry import shape, Polygon
from shapely.ops import unary_union
import json
import sys

def merge_overlapping_polygons(feature_collection, threshold=0.3):
    polygons = [(shape(feature['geometry']), feature['properties'].copy()) for feature in feature_collection['features']]

    iteration_count = 0

    while True:
        iteration_count += 1
        num_merges = 0

        new_polygons = []

        for i, (polygon1, properties1) in enumerate(polygons):
            if polygon1 is None:
                continue

            for j, (polygon2, properties2) in enumerate(polygons):
                if i != j and polygon2 is not None and polygon1.intersects(polygon2):
                    # Calculate the minimum of the areas of the two polygons
                    min_area = min(polygon1.area, polygon2.area)

                    # Check if the area of intersection is more than 10% of the minimum area
                    intersection_area = polygon1.intersection(polygon2).area
                    if intersection_area > threshold * min_area:
                        # Merge polygons using unary_union
                        polygon1 = unary_union([polygon1, polygon2])
                        polygons[j] = (None, None)  # Mark polygon2 as merged
                        num_merges += 1

            new_polygons.append((polygon1, properties1))

        # Filter out merged polygons (marked as (None, None))
        new_polygons = [(polygon, properties) for polygon, properties in new_polygons if polygon is not None]

        # Check if any new polygons were created during the current iteration
        if len(new_polygons) == len(polygons):
            break  # No new polygons were created, exit the loop
        else:
            polygons = new_polygons

        print(f"Iteration {iteration_count}: {num_merges} merges", file=sys.stderr)

    # Convert Shapely Polygons to valid GeoJSON Features with preserved properties
    merged_polygon_features = [{
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [list(polygon.exterior.coords)]
        },
        "properties": properties
    } for polygon, properties in polygons]

    return merged_polygon_features

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python merge_poly.py input_polygon_file.geojson", file=sys.stderr)
        sys.exit(1)

    input_polygon_file_path = sys.argv[1]

    # Read the existing GeoJSON FeatureCollection of polygons
    with open(input_polygon_file_path, 'r') as file:
        existing_polygon_feature_collection = json.load(file)

    # Merge overlapping polygons using unary_union and preserve properties
    merged_features = merge_overlapping_polygons(existing_polygon_feature_collection)

    # Create a FeatureCollection with the resulting polygons
    merged_feature_collection = {
        "type": "FeatureCollection",
        "features": merged_features
    }

    # Print the resulting GeoJSON FeatureCollection
    print(json.dumps(merged_feature_collection, indent=2))
