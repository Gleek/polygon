from shapely.geometry import shape, Polygon
from rdp import rdp
import json
import sys

def simplify_line_to_polygon(line_geojson, buffer_distance, simplification_epsilon):
    # Convert GeoJSON to Shapely LineString
    try:
        line = shape(line_geojson['geometry'])
    except Exception:
        print("failed for "+ line_geojson, file=sys.stderr)
        return {}

    # Convert LineString to Polygon with padding
    buffered_polygon = line.buffer(buffer_distance)

    # Simplify the Polygon using RDP
    simplified_polygon_coords = rdp(list(buffered_polygon.exterior.coords), epsilon=simplification_epsilon)

    # Create a simplified Polygon
    simplified_polygon = Polygon(simplified_polygon_coords)

    # Convert Shapely Polygon to valid GeoJSON Feature
    polygon_feature = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [list(simplified_polygon.exterior.coords)]
        },
        "properties": line_geojson['properties']
    }

    return polygon_feature

def simplify_feature_collection(file_path, buffer_distance, simplification_epsilon):
    with open(file_path, 'r') as file:
        feature_collection = json.load(file)

    # Process each LineString feature in the FeatureCollection
    polygon_features = [
        simplify_line_to_polygon(feature, buffer_distance, simplification_epsilon)
        for feature in feature_collection['features']
    ]

    # Create a FeatureCollection with the resulting polygons
    polygon_feature_collection = {
        "type": "FeatureCollection",
        "features": polygon_features
    }

    return polygon_feature_collection

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python linetopoly.py input_file.geojson")
        sys.exit(1)

    input_file_path = sys.argv[1]

    # Set parameters
    buffer_distance = 0.0002  # Assuming approximately 20 meters for padding in degrees
    simplification_epsilon = 0.0001  # Adjust according to your requirements

    # Generate simplified Polygon FeatureCollection
    result_feature_collection = simplify_feature_collection(
        input_file_path, buffer_distance, simplification_epsilon
    )

    # Print the resulting GeoJSON FeatureCollection
    print(json.dumps(result_feature_collection, indent=2))
