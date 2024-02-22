import csv
import json
from shapely.geometry import shape, Polygon, mapping
import sys
from rdp import rdp

def simplify_geometry(geometry, simplification_epsilon):
    simplified_geometry = rdp(geometry, epsilon=simplification_epsilon)
    if len(simplified_geometry) < 4:
        # Try with a smaller epsilon
        simplified_geometry = rdp(geometry, epsilon=simplification_epsilon / 10)
        if len(simplified_geometry) < 4:
            # Return the original geometry if it still fails
            return geometry
    return simplified_geometry

def simplify_feature(feature, simplification_epsilon):
    # Convert the feature's geometry to a Shapely Polygon
    polygon = shape(feature['geometry'])
    simplified_exterior_coords = simplify_geometry(list(polygon.exterior.coords), simplification_epsilon)

    # Rebuild the simplified geometry, ensuring it's valid
    if len(simplified_exterior_coords) >= 4:
        simplified_geometry = Polygon(simplified_exterior_coords)
    else:
        simplified_geometry = polygon  # Use original polygon if simplification failed

    return {
        "type": "Feature",
        "geometry": mapping(simplified_geometry),
        "properties": feature['properties']
    }

def process_csv(input_csv_path, output_csv_path, simplification_epsilon):
    with open(input_csv_path, mode='r', encoding='utf-8') as infile, open(output_csv_path, mode='w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                feature_collection = json.loads(row['polygon'])
                simplified_features = []

                for feature in feature_collection['features']:
                    original_geometry = json.dumps(feature['geometry'])  # Serialize original geometry for comparison
                    simplified_feature = simplify_feature(feature, simplification_epsilon)
                    simplified_geometry = json.dumps(simplified_feature['geometry'])  # Serialize simplified geometry for comparison

                    if original_geometry == simplified_geometry:
                        print(row['uuid'], file=sys.stderr)  # Log unchanged UUIDs to stderr

                    simplified_features.append(simplified_feature)

                simplified_feature_collection = {
                    "type": "FeatureCollection",
                    "features": simplified_features
                }

                # Update the row with the simplified FeatureCollection
                row['polygon'] = json.dumps(simplified_feature_collection)
            except Exception as e:
                print(f"Error processing row: {e}", file=sys.stderr)

            writer.writerow(row)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py input_csv_file.csv output_csv_file.csv simplification_epsilon", file=sys.stderr)
        sys.exit(1)

    input_csv_path = sys.argv[1]
    output_csv_path = sys.argv[2]
    simplification_epsilon = float(sys.argv[3])

    process_csv(input_csv_path, output_csv_path, simplification_epsilon)
