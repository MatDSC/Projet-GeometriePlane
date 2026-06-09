import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.lines import Line2D

try:
    import mplcursors
    HAS_MPLCURSORS = True
except Exception:
    HAS_MPLCURSORS = False

# --- Data ------------------------------------------------------------------
nodes = {
    "RT-1": (0, 4),
    "FW-1": (0, 2.9),
    "SW-1": (0, 2),
    "SW-2": (-2, 1),
    "SW-3": (2, 1),
    "PC-1": (-3, 0),
    "PC-2": (-1, 0),
    "PC-3": (1, 0),
    "PC-4": (0, -0.5),
    "SRV-1": (3, 0),
}

edges = [
    ("RT-1", "FW-1"),
    ("FW-1", "SW-1"),
    ("SW-1", "SW-2"),
    ("SW-1", "SW-3"),
    ("SW-2", "PC-1"),
    ("SW-2", "PC-2"),
    ("SW-3", "PC-3"),
    ("SW-3", "SRV-1"),
    ("SW-2", "SRV-1"),
    ("SW-3", "PC-1",),
]


PALETTE = {
    "RT": "#9be7a3",
    "FW": "#ffb86b",
    "SW": "#ffd166",
    "PC": "#9ad0f5",
    "SRV": "#caa0ff",
}

MARKER_BY_TYPE = {
    # o = circle, v = triangle, s = square, D = rhombus, h = hexagon
    "RT": ("o", 3800),
    "FW": ("v", 3000),
    "SW": ("s", 2600),
    "PC": ("D", 2000),
    "SRV": ("h", 2800),
}

IMG_PATH = {
    "RT": "./images/router.png",
    "FW": "./images/firewall.png",
    "SW": "./images/switch.png",
    "PC": "./images/computer.png",
    "SRV": "./images/server.png",
}


def node_type(name: str) -> str:
    return name.split("-")[0]


def segment_intersection(p1, p2, p3, p4):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None

    det1 = x1 * y2 - y1 * x2
    det2 = x3 * y4 - y3 * x4
    px = (det1 * (x3 - x4) - (x1 - x2) * det2) / denom
    py = (det1 * (y3 - y4) - (y1 - y2) * det2) / denom

    def within(a, b, c):
        return min(a, b) - 1e-9 <= c <= max(a, b) + 1e-9

    if (
        within(x1, x2, px)
        and within(y1, y2, py)
        and within(x3, x4, px)
        and within(y3, y4, py)
    ):
        return px, py
    return None


def build_plot(save_path: str | None = None):
    connected_nodes = {a for a, b in edges} | {b for a, b in edges}
    unconnected_nodes = [n for n in nodes if n not in connected_nodes]

    # automatic detection for cross network edges
    crossing_indices = set()
    for i, (a1, b1 ) in enumerate(edges):
        for j, (a2, b2 ) in enumerate(edges[i + 1:], start=i + 1):
            if len({a1, b1, a2, b2}) < 4:
                continue
            if segment_intersection(nodes[a1], nodes[b1], nodes[a2], nodes[b2]):
                crossing_indices.add(i)
                crossing_indices.add(j)

    nb_anomalies_edges = len(crossing_indices)
    nb_anomalies_nodes = len(unconnected_nodes)
    nb_anomalies = nb_anomalies_edges + nb_anomalies_nodes

    fig, ax = plt.subplots(figsize=(10, 8))

    # draw edges between nodes
    for i, (a, b) in enumerate(edges):
        x1, y1 = nodes[a]
        x2, y2 = nodes[b]
        if i in crossing_indices:
            ax.plot([x1, x2], [y1, y2], "r--", linewidth=2, zorder=1)
        else:
            ax.plot([x1, x2], [y1, y2], color="#333333", linewidth=2, zorder=1)

    # mark line intersections with crosses
    intersections = []
    for i, (a1, b1) in enumerate(edges):
        for a2, b2 in edges[i + 1:]:
            if len({a1, b1, a2, b2}) < 4:
                continue
            point = segment_intersection(nodes[a1], nodes[b1], nodes[a2], nodes[b2])
            if point is not None:
                intersections.append(point)

    unique_intersections = []
    for point in intersections:
        if not any(abs(point[0] - p[0]) < 1e-6 and abs(point[1] - p[1]) < 1e-6 for p in unique_intersections):
            unique_intersections.append(point)

    for x, y in unique_intersections:
        ax.scatter(x, y, s=110, marker="x", color="red", linewidths=2.2, zorder=4)

    # draw nodes (scatter + optional image)
    scatters = {}
    for name, (x, y) in nodes.items():
        t = node_type(name)
        marker, size = MARKER_BY_TYPE.get(t, ("o", 500))
        color = PALETTE.get(t, "lightgray")

        sct = ax.scatter(x, y, s=size, color=color, edgecolors="black", marker=marker, zorder=3)
        scatters[name] = sct

        # try to overlay an icon if available
        img_file = IMG_PATH.get(t)
        if img_file:
            try:
                img = mpimg.imread(img_file)
                img_box = OffsetImage(img, zoom=0.16)
                ab = AnnotationBbox(img_box, (x, y - 0.03), frameon=False, zorder=5)
                ax.add_artist(ab)
            except Exception:
                pass

        ax.text(x, y + 0.15, name, ha="center", va="center", fontsize=9, weight="bold", zorder=6)

    # highlight unconnected nodes
    for node in unconnected_nodes:
        x, y = nodes[node]
        circle = plt.Circle((x, y), 0.45, color="red", fill=False, linestyle="dashed", linewidth=2, zorder=2)
        ax.add_patch(circle)

    # legend
    legend_elements = [
        Line2D([0], [0], marker=MARKER_BY_TYPE[t][0], color="w", label=t,
               markerfacecolor=col, markeredgecolor="black", markersize=10)
        for t, col in PALETTE.items()
    ]
    legend_elements.append(Line2D([0], [0], color="#333333", lw=2, label="Lien OK"))
    legend_elements.append(Line2D([0], [0], color="red", lw=2, linestyle="--", label="Anomalie lien"))
    legend_elements.append(Line2D([0], [0], color="red", marker="x", linestyle="None", markersize=8, label="Intersection"))
    ax.legend(handles=legend_elements, loc="upper left", bbox_to_anchor=(1.02, 1), frameon=True)

    # annotation summary
    ax.text(0.02, 0.95,
            f"Anomalies détectées : {nb_anomalies}\n(Liaisons : {nb_anomalies_edges}, Matériel : {nb_anomalies_nodes})",
            transform=ax.transAxes,
            color="red", weight="bold", fontsize=11,
            bbox=dict(facecolor='white', alpha=0.9, edgecolor='red', boxstyle='round,pad=0.5'))

    ax.set_title("Visualisation du réseau avec anomalies")
    ax.axis("equal")
    ax.axis("off")

    # interactive tooltips if mplcursors is available
    if HAS_MPLCURSORS:
        cursor = mplcursors.cursor(list(scatters.values()), hover=True)

        @cursor.connect("add")
        def on_add(sel):
            for name, artist in scatters.items():
                if artist is sel.artist:
                    x, y = nodes[name]
                    sel.annotation.set(text=f"{name}\n({x}, {y})")
                    break

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Figure saved to {save_path}")

    plt.show()


if __name__ == "__main__":
    dirpath = os.path.dirname(__file__)
    save_file = os.path.join(dirpath, "network_visualization.png")
    build_plot(save_path=save_file)
