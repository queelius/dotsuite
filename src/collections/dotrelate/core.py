import json

def left_join(left_collection, right_collection, left_on, right_on):
    right_map = {item.get(right_on): item for item in right_collection}
    for left_item in left_collection:
        right_item = right_map.get(left_item.get(left_on), {})
        yield {**left_item, **right_item}

def project(collection, fields):
    for item in collection:
        yield {field: item.get(field) for field in fields}

def union(left_collection, right_collection):
    yield from left_collection
    yield from right_collection

def set_difference(left_collection, right_collection):
    right_set = {json.dumps(item, sort_keys=True) for item in right_collection}
    for item in left_collection:
        if json.dumps(item, sort_keys=True) not in right_set:
            yield item
