import argparse
import json
import sys

try:
    import yaml
except ImportError:
    yaml = None

from .core import from_dsl

def main():
    """The main entry point for the dotpipe command-line tool."""
    
    parser = argparse.ArgumentParser(
        prog="dotpipe",
        description="Apply a declarative transformation pipeline to a JSON or YAML document.",
        epilog="Use '-' for a filename to read from stdin. The transformed document is written to stdout."
    )
    
    parser.add_argument(
        'pipeline_file',
        help="Path to the JSON or YAML file containing the pipeline DSL, or '-' for stdin."
    )
    
    parser.add_argument(
        'data_file',
        nargs='?', # Make data_file optional
        default='-', # Default to stdin if not provided
        help="Path to the source JSON or YAML data file, or '-' for stdin (default)."
    )

    parser.add_argument(
        '--in', '--input-format', dest='input_format',
        choices=['json', 'yaml'],
        help="Format of the input data and pipeline files. If not provided, it's inferred from file extensions. Defaults to 'json' for stdin or unknown file types."
    )
    
    args = parser.parse_args()

    def infer_format(filename, default='json'):
        if args.input_format:
            return args.input_format
        if filename != '-' and filename.lower().endswith((".yml", ".yaml")):
            return 'yaml'
        return default

    pipeline_format = infer_format(args.pipeline_file)
    data_format = infer_format(args.data_file)

    if (pipeline_format == 'yaml' or data_format == 'yaml') and not yaml:
        print("Error: PyYAML is not installed. Please install it with 'pip install PyYAML' to process YAML files.", file=sys.stderr)
        sys.exit(1)

    def load_data(filename, format):
        if filename == '-':
            content = sys.stdin.read()
        else:
            with open(filename, 'r') as f:
                content = f.read()
        
        if format == 'yaml':
            return yaml.safe_load(content)
        else:
            return json.loads(content)

    try:
        # --- Read Pipeline DSL ---
        if args.pipeline_file == '-' and args.data_file == '-':
            print("Error: Cannot read both pipeline and data from stdin.", file=sys.stderr)
            sys.exit(1)

        pipeline_dsl = load_data(args.pipeline_file, pipeline_format)

        # --- Read Source Data ---
        data = load_data(args.data_file, data_format)

        # --- Execute Transformation ---
        result = from_dsl(data, pipeline_dsl)

        # --- Print Result ---
        if data_format == 'yaml':
            yaml.dump(result, sys.stdout)
        else:
            json.dump(result, sys.stdout)
            print() # Add a trailing newline for shell niceness

    except FileNotFoundError as e:
        print(f"Error: File not found - {e.filename}", file=sys.stderr)
        sys.exit(1)
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        print(f"Error: Invalid format in input file - {e}", file=sys.stderr)
        sys.exit(1)
    except (TypeError, ValueError) as e:
        print(f"Error: Pipeline execution failed - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()