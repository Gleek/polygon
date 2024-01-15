from shapely.geometry import shape, Polygon
import json
import sys

def split_large_polygon(polygon, max_coordinates):
    coordinates = list(polygon.exterior.coords)
    num_coordinates = len(coordinates)

    if num_coordinates <= max_coordinates:
        return [polygon]

    # Split the coordinates into chunks of max_coordinates
    chunks = [coordinates[i:i+max_coordinates] for i in range(0, num_coordinates, max_coordinates)]

    # Create a list of Polygons from the chunks
    polygons = [Polygon(chunk) for chunk in chunks]

    return polygons

def process_feature_collection(input_file_path, max_coordinates=100):
    with open(input_file_path, 'r') as file:
        feature_collection = json.load(file)

    processed_polygons = []

    for feature in feature_collection['features']:
        polygon = shape(feature['geometry'])

        # Split the polygon if it exceeds the maximum number of coordinates
        polygons = split_large_polygon(polygon, max_coordinates)

        # Add the resulting polygons to the processed list
        processed_polygons.extend(polygons)

    return processed_polygons

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python split_large_polygons_script.py input_polygon_file.geojson max_coordinates", file=sys.stderr)
        sys.exit(1)

    input_polygon_file_path = sys.argv[1]
    max_coordinates = int(sys.argv[2])

    # Process the FeatureCollection and get the resulting polygons
    processed_polygons = process_feature_collection(input_polygon_file_path, max_coordinates)

    # Convert Shapely Polygons to valid GeoJSON Features
    processed_feature_collection = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [list(polygon.exterior.coords)]
                },
                "properties": {}
            }
            for polygon in processed_polygons
        ]
    }

    # Print the resulting GeoJSON FeatureCollection
    print(json.dumps(processed_feature_collection, indent=2))
