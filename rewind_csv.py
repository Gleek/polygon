import csv
import json
from shapely.geometry import shape
from geojson_rewind import rewind
import sys


def correct_winding_order(feature_collection):
    corrected_features = []

    for feature in feature_collection['features']:
        geometry = feature['geometry']
        properties = feature['properties']

        # Correct the winding order of the polygon using geojson_rewind
        corrected_geometry = shape(rewind(geometry))

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


def process_csv(input_csv_path):
    output_rows = []

    with open(input_csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for idx, row in enumerate(reader):
            # print(f"Processing row {idx + 1}...", file=sys.stderr)

            # Parse the "polygon" column as a feature collection
            try:
                feature_collection = json.loads(row['polygon'])
            except json.JSONDecodeError as e:
                print(f"Failed to parse 'polygon' in row {idx + 1}: {e}", file=sys.stderr)
                continue

            # Correct the winding order of the feature collection
            corrected_features = correct_winding_order(feature_collection)

            # Update the "polygon" column with the corrected feature collection
            row['polygon'] = json.dumps({
                "type": "FeatureCollection",
                "features": corrected_features
            })

            output_rows.append(row)

    return output_rows


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python correct_winding_order_csv.py input_csv_file.csv", file=sys.stderr)
        sys.exit(1)

    input_csv_path = sys.argv[1]

    # Process the CSV and get the resulting rows with corrected winding order
    corrected_rows = process_csv(input_csv_path)

    # Write the corrected rows to a new CSV file
    output_csv_path = "output_corrected.csv"
    with open(output_csv_path, 'w', newline='') as csvfile:
        fieldnames = corrected_rows[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header
        writer.writeheader()

        # Write rows
        writer.writerows(corrected_rows)

    print(f"Updated CSV written to: {output_csv_path}", file=sys.stderr)
