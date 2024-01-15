from shapely.geometry import shape, Point, LineString
from pyproj import Geod

import json
import sys

def filter_polygons_by_radius(feature_collection, center_lat, center_lng, radius_km):
    center_point = Point(center_lng, center_lat)
    filtered_features = []

    for feature in feature_collection['features']:
        polygon = shape(feature['geometry'])
        # Check if the centroid of the polygon is within the specified radius
        if Geod(ellps="WGS84").geometry_length(LineString([polygon.centroid, center_point])) / 1000 <= radius_km:
            # if center_point.distance(polygon.centroid) <= radius_km:
            filtered_features.append(feature)

    # Create a FeatureCollection with the filtered polygons
    filtered_feature_collection = {
        "type": "FeatureCollection",
        "features": filtered_features
    }

    return filtered_feature_collection

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python filter_polygons_by_radius.py input_polygon_file.geojson center_lat center_lng radius_km")
        sys.exit(1)

    input_polygon_file_path = sys.argv[1]
    center_lat = float(sys.argv[2])
    center_lng = float(sys.argv[3])
    radius_km = float(sys.argv[4])

    # Read the existing GeoJSON FeatureCollection of polygons
    with open(input_polygon_file_path, 'r') as file:
        existing_polygon_feature_collection = json.load(file)

    # Filter polygons by radius
    filtered_feature_collection = filter_polygons_by_radius(existing_polygon_feature_collection, center_lat, center_lng, radius_km)

    # Print the resulting GeoJSON FeatureCollection
    print(json.dumps(filtered_feature_collection, indent=2))
