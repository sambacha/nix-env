#!/usr/bin/env python
import argparse
import json
import sys


argparser = argparse.ArgumentParser()
argparser.add_argument(
    '--graph', type=argparse.FileType('r', encoding='UTF-8'),
    required=True)
argparser.add_argument(
    '--cuts', type=argparse.FileType('r', encoding='UTF-8'),
    required=True)


def get_layer(graph, key, cut_points, _layer=None):
    if _layer is None:
        _layer = set()
    node = graph[key]
    _layer.add(key)

    for ref in node.get('references', []):
        if ref == key or ref in cut_points:
            continue
        get_layer(graph, ref, cut_points, _layer=_layer)
    return _layer


def process_layers(graph_data, cut_points):
    leaf_path = graph_data['exportReferencesGraph']['graph']
    graph = {
        node['path']: node
        for node in graph_data['graph']
    }

    layer_keys = cut_points.intersection(set(graph.keys()))
    layer_keys.add(leaf_path)

    return {
        layer_key: get_layer(graph, layer_key, cut_points)
        for layer_key in layer_keys
    }


def find_duplicate_refs(layers):
    dups = set()
    for layer_key, layer in layers.items():
        for l_k, l in layers.items():
            if layer_key == l_k:
                continue
            dups.update(l.intersection(layer))
    return dups


class SetJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return sorted(obj)
        return json.JSONEncoder.default(self, obj)


if __name__ == '__main__':
    args = argparser.parse_args()
    graph_data = json.load(args.graph)
    cut_points = set(json.load(args.cuts))

    layers = process_layers(graph_data, cut_points)
    for dup in find_duplicate_refs(layers):
        sys.stderr.write(
            'Found path in multiple layers, consider adding cut: %s\n' % dup)

    print(json.dumps(layers, cls=SetJSONEncoder, indent=2))
