import argparse
import json
from numpy import deprecate
import plotly.graph_objects as go
import os

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True, help="Path to interval's data")
    parser.add_argument("-o", "--output", type=str, required=True, help="Output image path")
    parser.add_argument("-k", type=int, required=True, help="Color count")
    return parser


class IntervalGraphsColoring:
    def __init__(self, input, output):
        pass
        with open(input) as f:
            data = json.load(f)
        self.data = self.parse_data(data)
        self.output = output
        self.color = 0
        self.result = {}


    def get_next_color(self):
        """Increments `color` on each call."""
        self.color += 1
        return self.color


    def validate_data(self, data):
        """Check if `data` is valid and intervals are correct."""
        if not isinstance(data, dict):
            raise TypeError("Data must be dictionary")
        for value in data.values():
            if not isinstance(value, list):
                raise TypeError("Values must be list")
            if not len(value) == 2:
                raise ValueError("Length of values must be 2")
            if value[0] == value[1]:
                raise ValueError(f"Invalid interval {value}")


    def parse_data(self, data):
        """Parses data and returns formatted dictionary of intervals to work with."""
        if isinstance(data, dict):
            self.validate_data(data)
        elif isinstance(data, list):
            parsed_data = {}
            for i, value in enumerate(data, 1):
                parsed_data[f'f{i}'] = value
            self.validate_data(parsed_data)
            data = parsed_data
        else:
            raise TypeError(f'Unsupported data type {type(data)}, must be object or array')

        for key, value in data.items():
            data[key] = sorted(value)
        return data


    def show_interval_graph(self):
        """Saves created intervals image in given path."""
        delta = 360 // self.color
        traces = []
        for key, value in self.result.items():
            traces.append(go.Scatter(
                x=value['x'],
                y=[value['color'], value['color']],
                name=f'{key}{value["x"]}',
                line_color=f'hsl({delta * value["color"]}, 100, 50)',
                mode='lines+markers',
                ))
        plt = go.Figure(data=traces, layout={"xaxis":{"dtick":1},"yaxis":{"dtick":1}})
        plt.write_image(self.output)


    def sort_graph_corresponding_second_value(self, data):
        """Sorts intervals with their second value."""
        return dict(sorted(data.items(), key=lambda l: l[1][1]))


    def left_edge_algorithm(self, data):
        """Creates row form intervals that are not intersecting using left edge algorthm."""
        data_copy = self.sort_graph_corresponding_second_value(data.copy())

        first_key = list(data_copy.keys())[0]
        first = data_copy.pop(first_key)

        intersect = []
        for key, value in data_copy.items():
            if first[1] >= value[0]:
                intersect.append(key)

        for key in intersect:
            data_copy.pop(key)

        row=[{first_key:first}]

        if data_copy:
            row += self.left_edge_algorithm(data_copy)
        return row


    def generate(self, k):
        """Sorts intervals that can be placed in `k` lines."""
        data = self.data.copy()
        found = {}
        while data:
            row = self.left_edge_algorithm(data)
            color = self.get_next_color()
            for item in row:
                key = list(item.keys())[0]
                found[key] = {
                    "x": item[key],
                    "color": color
                }
            if color == k:
                break
            for key in found.keys():
                data.pop(key, None)
        return found


    def build_minimal_color_graph(self, k):
        """Returns all intervals that can be colored with `k` colors, and maximum color that needs to color all intervals."""
        data_backup = self.data

        self.result = self.generate(k)

        self.data = data_backup
        less_than_k = self.color < k
        return less_than_k, self.result


def main(args):
    if not os.path.isfile(args.input):
        print(f"{args.input} doesn't exist")
        return

    graph = IntervalGraphsColoring(args.input, args.output)

    if args.k < 1:
        print(f"Invalid color count {args.k}")
        return

    less_than_k, result = graph.build_minimal_color_graph(k=args.k)
    if less_than_k:
        print(
            f" No need {args.k} colors, it is possible to color all {len(result)} intervals with {list(result.values())[-1]['color']} colors.")
    else:
        print(f" {len(result)} intervals can be colored with {args.k} colors")

    for k, v in result.items():
        print(f" {k} = {v['x']}\twith color {v['color']}")

    graph.show_interval_graph()


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(args)