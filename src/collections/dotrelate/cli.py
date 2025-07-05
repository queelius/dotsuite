import click
import json
import sys
from .core import left_join, project, union, set_difference

def load_collection(source):
    if source == "-":
        for line in sys.stdin:
            yield json.loads(line)
    else:
        with open(source) as f:
            for line in f:
                yield json.loads(line)

@click.group()
def cli():
    pass

@cli.command()
@click.option("--left-on", required=True)
@click.option("--right-on", required=True)
@click.argument("left_source")
@click.argument("right_source")
def join(left_on, right_on, left_source, right_source):
    left = load_collection(left_source)
    right = load_collection(right_source)
    for item in left_join(left, right, left_on, right_on):
        print(json.dumps(item))

@cli.command("project")
@click.argument("fields")
@click.argument("source")
def project_command(fields, source):
    collection = load_collection(source)
    field_list = fields.split(",")
    for item in project(collection, field_list):
        print(json.dumps(item))

@cli.command()
@click.argument("left_source")
@click.argument("right_source")
def union_command(left_source, right_source):
    left = load_collection(left_source)
    right = load_collection(right_source)
    for item in union(left, right):
        print(json.dumps(item))

@cli.command()
@click.argument("left_source")
@click.argument("right_source")
def diff(left_source, right_source):
    left = load_collection(left_source)
    right = load_collection(right_source)
    for item in set_difference(left, right):
        print(json.dumps(item))

if __name__ == "__main__":
    cli()
