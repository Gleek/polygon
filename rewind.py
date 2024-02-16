import json
from shapely.geometry import shape
from geojson_rewind import rewind
import sys


def correct_winding_order(polygon):
    return shape(rewind(polygon))


def process_feature_collection(input_file_path):
    with open(input_file_path, 'r') as file:
        feature_collection = json.load(file)

    corrected_features = []

    for idx, feature in enumerate(feature_collection['features']):
        geometry = feature['geometry']
        properties = feature['properties']

        # Correct the winding order of the polygon using geojson_rewind
        corrected_geometry = correct_winding_order(geometry)

        # Create a GeoJSON feature with corrected winding order and preserved properties
        corrected_feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [list(corrected_geometry.exterior.coords)]
            },
            "properties": properties
        }

        corrected_features.append(corrected_feature)

    return corrected_features


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python correct_winding_order_script.py input_polygon_file.geojson", file=sys.stderr)
        sys.exit(1)

    input_polygon_file_path = sys.argv[1]

    # Process the FeatureCollection and get the resulting features with corrected winding order
    corrected_features = process_feature_collection(input_polygon_file_path)

    # Create a FeatureCollection with the resulting features
    corrected_feature_collection = {
        "type": "FeatureCollection",
        "features": corrected_features
    }

    # Print the resulting GeoJSON FeatureCollection with corrected winding order and preserved properties
    print(json.dumps(corrected_feature_collection))
