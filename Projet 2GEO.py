import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib import patches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

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
    "SRV-1": (3, 0)
}

edges = [
    ("RT-1", "FW-1", False),
    ("FW-1", "SW-1", False),
    ("SW-1", "SW-2", False),
    ("SW-1", "SW-3", False),
    ("SW-2", "PC-1", False),
    ("SW-2", "PC-2", True),
    ("SW-3", "PC-3", True),
    ("SW-3", "SRV-1", False),
    ("SW-2", "SRV-1", True),
    ("SW-3", "PC-1", True),
]

colors = {
    "RT": "lightgreen",
    "FW": "orange",
    "SW": "gold",
    "PC": "skyblue",
    "SRV": "violet"
}

img_path = {
    "RT": "./images/router.png",
    "FW": "./images/firewall.png",
    "SW": "./images/switch.png",
    "PC": "./images/computer.png",
    "SRV": "./images/server.png"
}

connected_nodes = set()
for a, b, _ in edges:
    connected_nodes.add(a)
    connected_nodes.add(b)
unconnected_nodes = [node for node in nodes if node not in connected_nodes]

nb_anomalies_edges = sum(1 for edge in edges if edge[2])
nb_anomalies_nodes = len(unconnected_nodes)
nb_anomalies = nb_anomalies_edges + nb_anomalies_nodes

fig, ax = plt.subplots(figsize=(10, 8))

for a, b, anomalie in edges:
    x1, y1 = nodes[a]
    x2, y2 = nodes[b]
    if anomalie:
        plt.plot([x1, x2], [y1, y2], "r--", linewidth=2)
    else:
        plt.plot([x1, x2], [y1, y2], color="black", linewidth=2)

for name, (x, y) in nodes.items():
    if name.startswith("RT"):
        c = colors["RT"]
        img = mpimg.imread(img_path["RT"])
        img_box = OffsetImage(img, zoom=0.23)
        ab = AnnotationBbox(img_box, (x, y - 0.13), zorder=4, frameon=False)
        ax.add_artist(ab)
    elif name.startswith("FW"):
        c = colors["FW"]
        img = mpimg.imread(img_path["FW"])
        img_box = OffsetImage(img, zoom=0.23)
        ab = AnnotationBbox(img_box, (x, y - 0.13), zorder=4, frameon=False)
        ax.add_artist(ab)
    elif name.startswith("SW"):
        c = colors["SW"]
        img = mpimg.imread(img_path["SW"])
        img_box = OffsetImage(img, zoom=0.23)
        ab = AnnotationBbox(img_box, (x, y - 0.13), zorder=4, frameon=False)
        ax.add_artist(ab)
    elif name.startswith("SRV"):
        c = colors["SRV"]
        img = mpimg.imread(img_path["SRV"])
        img_box = OffsetImage(img, zoom=0.23)
        ab = AnnotationBbox(img_box, (x, y - 0.13), zorder=4, frameon=False)
        ax.add_artist(ab)
    else:
        c = colors["PC"]
        img = mpimg.imread(img_path["PC"])
        img_box = OffsetImage(img, zoom=0.23)
        ab = AnnotationBbox(img_box, (x, y - 0.13), zorder=4, frameon=False)
        ax.add_artist(ab)

    ax.scatter(x, y, s=2300, color=c, edgecolors="black", zorder=3)
    ax.text(x, y + 0.1, name, ha="center", va="center", fontsize=9, weight="bold")

for node in unconnected_nodes:
    x, y = nodes[node]
    circle = plt.Circle((x, y), 0.5, color="red", fill=False, linestyle="dashed", linewidth=2)
    ax.add_patch(circle)

ax.text(0, 0.90,
        f"Anomalies détectées : {nb_anomalies}\n(Liaisons : {nb_anomalies_edges}, Matériel : {nb_anomalies_nodes})",
        transform=ax.transAxes,
        color="red", weight="bold", fontsize=11,
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='red', boxstyle='round,pad=0.5'))

ax.set_title("Visualisation du réseau avec anomalies")
ax.axis("equal")
ax.axis("off")
plt.show()
