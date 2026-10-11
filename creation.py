from arrows import arrows
from arrows.arrows import ArrowType, Direction
import networkx as nx
import matplotlib.pyplot as plt

COLOR_MAP = {
    ArrowType.Arrow: "red",
    ArrowType.SplitterUpDown: "red",
    ArrowType.SplitterUpRight: "red",
    ArrowType.SplitterUpRightLeft: "red",
    ArrowType.Source: "red",
    ArrowType.Blocker: "red",
    ArrowType.Delay: "red",
    ArrowType.Detector: "red",
    ArrowType.Not: "yellow",
    ArrowType.And: "yellow",
    ArrowType.Xor: "yellow",
    ArrowType.Latch: "yellow",
    ArrowType.Flipflop: "yellow",
    ArrowType.BlueArrow: "lightblue",
    ArrowType.Diagonal: "lightblue",
    ArrowType.BlueSplitterUpUp: "lightblue",
    ArrowType.BlueSplitterRightUp: "lightblue",
    ArrowType.BlueSplitterUpDiagonal: "lightblue",
    ArrowType.Button: "orange",
    ArrowType.Random: "orange",
    ArrowType.DirectoinalButton: "orange",
}
LABEL_MAP = {
    ArrowType.Arrow: "→",
    ArrowType.SplitterUpDown: "Splitter ↕",
    ArrowType.SplitterUpRight: "Splitter ↑→",
    ArrowType.SplitterUpRightLeft: "Splitter ←↑→",
    ArrowType.Source: "Source",
    ArrowType.Blocker: "Blocker",
    ArrowType.Delay: "Delay",
    ArrowType.Detector: "Detector",
    ArrowType.Not: "NOT",
    ArrowType.And: "AND",
    ArrowType.Xor: "XOR",
    ArrowType.Latch: "Latch",
    ArrowType.Flipflop: "Flip-Flop",
    ArrowType.BlueArrow: "→",
    ArrowType.Diagonal: "↗",
    ArrowType.BlueSplitterUpUp: "Splitter ↑↑",
    ArrowType.BlueSplitterRightUp: "Splitter →↑",
    ArrowType.BlueSplitterUpDiagonal: "Splitter ↑↗",
    ArrowType.Button: "Button",
    ArrowType.Random: "Random",
    ArrowType.DirectoinalButton: "Dir. Button",
    ArrowType.Pulse: "Pulse"
}
SCALE = 80
CREATE_INV = False


def get_color(arrow_type: ArrowType) -> str:
    return COLOR_MAP.get(arrow_type, "gray")


# Перебор стрелок
def create_nodes(ar_map: arrows.Map, graph: nx.DiGraph):
    for (chunk_x, chunk_y), chunk in ar_map.chunks.items():
        for x in range(16):
            for y in range(16):
                arrow = chunk.get(x, y)
                if arrow.type in (ArrowType.Empty, ArrowType.Wall):
                    continue
                gx, gy = chunk_x * 16 + x, chunk_y * 16 + y
                graph.add_node(
                    (gx, gy),
                    type=arrow.type,
                    direction=arrow.direction,
                    flipped=getattr(arrow, "flipped", False),
                    color=get_color(arrow.type),
                    x=gx * SCALE,
                    y=gy * SCALE,
                    level=gx+gy,
                    label=LABEL_MAP.get(arrow.type, "?"),
                    # fixed=True,
                    physics=False,
                )


def new_cords_with_dir(old_cords: tuple[int, int], direction: Direction, step=1) -> tuple[int, int] | None:
    """Получает координаты из направлений"""
    match direction:
        case Direction.North:
            return old_cords[0], old_cords[1] - step
        case Direction.South:
            return old_cords[0], old_cords[1] + step
        case Direction.East:
            return old_cords[0] + step, old_cords[1]
        case Direction.West:
            return old_cords[0] - step, old_cords[1]
    return None


def new_cords_with_dir_diagonal(old_cords: tuple[int, int], direction: Direction, flip=1, step=1) -> tuple[
                                                                                                         int, int] | None:
    """Получает координаты из направлений"""
    match direction:
        case Direction.North:
            return old_cords[0] + step * flip, old_cords[1] - step
        case Direction.South:
            return old_cords[0] - step * flip, old_cords[1] + step
        case Direction.East:
            return old_cords[0] + step, old_cords[1] + step * flip
        case Direction.West:
            return old_cords[0] - step, old_cords[1] - step * flip
    return None


def add_edge_if_target_exists(G, u, v, perm=True, **attrs):
    if (v in G and u in G) or CREATE_INV:
        if (G.nodes()[v]["type"] in (ArrowType.Detector, ArrowType.Button) and perm) or \
                (G.nodes()[u]["type"] != ArrowType.Blocker and G.nodes()[v]["type"] in (ArrowType.Pulse, ArrowType.Source)):
            return False
        G.add_edge(u, v, **attrs)
        return True
    return False


# Создание рёбер
def create_edges(graph: nx.DiGraph):
    for node, data in list(graph.nodes(data=True)):
        match data["type"]:
            case ArrowType.Arrow | ArrowType.Not | ArrowType.And | ArrowType.Xor \
                 | ArrowType.DirectoinalButton | ArrowType.Latch | ArrowType.Flipflop | ArrowType.Random \
                 | ArrowType.Delay | ArrowType.Blocker:
                if (new_cords := new_cords_with_dir(node, data["direction"])) is not None:
                    add_edge_if_target_exists(graph, node, new_cords)
            case ArrowType.BlueArrow:
                if (new_cords := new_cords_with_dir(node, data["direction"], step=2)) is not None:
                    add_edge_if_target_exists(graph, node, new_cords)
            case ArrowType.Diagonal:
                if (new_cords := new_cords_with_dir_diagonal(node, data["direction"],
                                                             flip=(-1 if data['flipped'] else 1), step=1)) is not None:
                    add_edge_if_target_exists(graph, node, new_cords)
            case ArrowType.SplitterUpDown:
                if data["direction"] in (Direction.East, Direction.West):
                    add_edge_if_target_exists(graph, node, new_cords_with_dir(node, Direction.East))
                    add_edge_if_target_exists(graph, node, new_cords_with_dir(node, Direction.West))
                else:
                    add_edge_if_target_exists(graph, node, new_cords_with_dir(node, Direction.South))
                    add_edge_if_target_exists(graph, node, new_cords_with_dir(node, Direction.North))
            case ArrowType.SplitterUpRight:
                if not data['flipped']:
                    if data["direction"] in (Direction.East, Direction.North):
                        add_edge_if_target_exists(graph, node, new_cords_with_dir(node, Direction.East))
                        add_edge_if_target_exists(graph, node, new_cords_with_dir(node, Direction.North,
                                                                                  step=(-1 if data[
                                                                                                  'direction'] == Direction.East else 1)))
                    else:
                        add_edge_if_target_exists(graph, node, new_cords_with_dir(node, Direction.West))
                        add_edge_if_target_exists(graph, node, new_cords_with_dir(node, Direction.North,
                                                                                  step=(-1 if data[
                                                                                                  'direction'] == Direction.South else 1)))
                else:
                    if data["direction"] in (Direction.East, Direction.North):
                        add_edge_if_target_exists(graph, node, new_cords_with_dir(node, Direction.East,
                                                                                  step=(-1 if data[
                                                                                                  'direction'] == Direction.North else 1)))
                        add_edge_if_target_exists(graph, node, new_cords_with_dir(node, Direction.North, ))
                    else:
                        add_edge_if_target_exists(graph, node, new_cords_with_dir(node, Direction.West,
                                                                                  step=(-1 if data[
                                                                                                  'direction'] == Direction.South else 1)))
                        add_edge_if_target_exists(graph, node, new_cords_with_dir(node, Direction.North, -1))
            case ArrowType.BlueSplitterUpUp:
                if (new_cords := new_cords_with_dir(node, data["direction"])) is not None:
                    add_edge_if_target_exists(graph, node, new_cords)
                    add_edge_if_target_exists(graph, node, new_cords_with_dir(node, data["direction"], step=2))
            case ArrowType.BlueSplitterRightUp:
                if (new_cords := new_cords_with_dir(node, data["direction"], step=2)) is not None:
                    add_edge_if_target_exists(graph, node, new_cords)
                    add_edge_if_target_exists(graph, node, new_cords_with_dir(node, (data["direction"] + 1) % 4,
                                                                              step=(-1 if data['flipped'] else 1)))
            case ArrowType.BlueSplitterUpDiagonal:
                if (new_cords := new_cords_with_dir(node, data["direction"])) is not None:
                    add_edge_if_target_exists(graph, node, new_cords)
                    add_edge_if_target_exists(graph, node, new_cords_with_dir_diagonal(node, data["direction"],
                                                                                       flip=(-1 if data[
                                                                                           'flipped'] else 1), step=1))
            case ArrowType.Button:
                for i in range(4):
                    add_edge_if_target_exists(graph, node, new_cords_with_dir(node, Direction(i)))
            case ArrowType.Source | ArrowType.Pulse:
                for i in range(4):
                    add_edge_if_target_exists(graph, node, new_cords_with_dir(node, Direction(i)))
            case ArrowType.Detector:
                add_edge_if_target_exists(graph, new_cords_with_dir(node, data["direction"], step=-1), node, perm=False)
                add_edge_if_target_exists(graph, node, new_cords_with_dir(node, data["direction"]))
            case ArrowType.SplitterUpRightLeft:
                # print(node, data)
                add_edge_if_target_exists(graph, node, new_cords_with_dir(node, data["direction"]))
                add_edge_if_target_exists(graph, node, new_cords_with_dir(node, data["direction"] + 1, step=-1))
                add_edge_if_target_exists(graph, node, new_cords_with_dir(node, (data["direction"] + 1) % 4))
