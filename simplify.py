import json
from shapely.geometry import shape
from rdp import rdp
import sys


def simplify_feature_collection(input_file_path, simplification_epsilon):
    with open(input_file_path, 'r') as file:
        feature_collection = json.load(file)

    simplified_features = []

    for idx, feature in enumerate(feature_collection['features']):
        print(f"Simplifying polygon {idx + 1}...", file=sys.stderr)

        geometry = feature['geometry']
        properties = feature['properties']

        # Convert the geometry to a Shapely object
        polygon = shape(geometry)

        # Simplify the polygon using RDP
        simplified_coords = rdp(list(polygon.exterior.coords), epsilon=simplification_epsilon)
        simplified_polygon = {
            "type": "Polygon",
            "coordinates": [simplified_coords]
        }

        # Create a simplified GeoJSON feature with preserved properties
        simplified_feature = {
            "type": "Feature",
            "geometry": simplified_polygon,
            "properties": properties
        }

        simplified_features.append(simplified_feature)

    return simplified_features


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python simplify_feature_collection.py input_geojson_file.geojson simplification_epsilon", file=sys.stderr)
        sys.exit(1)

    input_file_path = sys.argv[1]
    simplification_epsilon = float(sys.argv[2])

    # Process the GeoJSON FeatureCollection and get the resulting simplified features
    simplified_features = simplify_feature_collection(input_file_path, simplification_epsilon)

    # Create a simplified FeatureCollection
    simplified_feature_collection = {
        "type": "FeatureCollection",
        "features": simplified_features
    }

    # Print the resulting simplified GeoJSON FeatureCollection
    print(json.dumps(simplified_feature_collection, indent=2))
