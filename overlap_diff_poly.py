from shapely.geometry import shape, Polygon, MultiPolygon
import json
import sys

def subtract_intersecting_parts(polygons_with_properties):
    modified_polygons = []

    for i, (polygon1, properties1) in enumerate(polygons_with_properties):
        remaining_polygon = polygon1

        for j in range(len(polygons_with_properties)):
            if i != j and polygon1.intersects(polygons_with_properties[j][0]):
                remaining_polygon = remaining_polygon.difference(polygons_with_properties[j][0])
                polygons_with_properties[i] = (remaining_polygon, properties1)

        modified_polygons.append((remaining_polygon, properties1))

    return modified_polygons

def filter_non_empty_polygons(polygons_with_properties):
    return [(polygon, properties) for polygon, properties in polygons_with_properties if not polygon.is_empty]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python intersection_polygon_script.py input_polygon_file.geojson", file=sys.stderr)
        sys.exit(1)

    input_polygon_file_path = sys.argv[1]

    # Read the existing GeoJSON FeatureCollection of polygons
    with open(input_polygon_file_path, 'r') as file:
        existing_polygon_feature_collection = json.load(file)

    # Extract polygons and properties from the FeatureCollection
    polygons_with_properties = [(shape(feature['geometry']), feature['properties']) for feature in existing_polygon_feature_collection['features']]

    # Subtract intersecting parts and filter non-empty polygons
    modified_polygons = subtract_intersecting_parts(polygons_with_properties)
    filtered_polygons = filter_non_empty_polygons(modified_polygons)

    # Convert Shapely Polygons to valid GeoJSON Features with preserved properties
    processed_polygon_features = []

    for polygon, properties in filtered_polygons:
        if isinstance(polygon, Polygon):
            processed_polygon_features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [list(polygon.exterior.coords)]
                },
                "properties": properties
            })
        elif isinstance(polygon, MultiPolygon):
            for part in polygon.geoms:
                processed_polygon_features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [list(part.exterior.coords)]
                    },
                    "properties": properties
                })

    # Create a FeatureCollection with the resulting polygons
    processed_feature_collection = {
        "type": "FeatureCollection",
        "features": processed_polygon_features
    }

    # Print the resulting GeoJSON FeatureCollection
    print(json.dumps(processed_feature_collection, indent=2))
