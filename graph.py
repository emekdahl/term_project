import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()

nodes = {
    'Customer Arrival': {'pos': (0, 10)},
    'Assign Request Type': {'pos': (0, 9)},
    'Attempt AI Resolution': {'pos': (0, 8)},
    'Resolved by AI': {'pos': (2, 8)},
    'AI Fails to Resolve': {'pos': (-2, 8)},
    'Check for Balking': {'pos': (-2, 7)},
    'Customer Balks': {'pos': (-4, 7)},
    'Customer Joins Queue': {'pos': (-2, 6)},
    'Wait for Level 1 Support': {'pos': (-2, 5)},
    'Customer Reneges': {'pos': (-4, 5)},
    'Level 1 Support Starts': {'pos': (-2, 4)},
    'Level 1 Resolution': {'pos': (-2, 3)},
    'Resolved by Level 1': {'pos': (0, 3)},
    'Escalated to Level 2': {'pos': (-4, 3)},
    'Level 2 Support Starts': {'pos': (-4, 2)},
    'Level 2 Resolution': {'pos': (-4, 1)},
    'Resolved by Level 2': {'pos': (-2, 1)},
    'End': {'pos': (0, 0)}
}

for node, data in nodes.items():
    G.add_node(node, pos=data['pos'])

edges = [
    ('Customer Arrival', 'Assign Request Type'),
    ('Assign Request Type', 'Attempt AI Resolution'),
    ('Attempt AI Resolution', 'Resolved by AI'),
    ('Attempt AI Resolution', 'AI Fails to Resolve'),
    ('AI Fails to Resolve', 'Check for Balking'),
    ('Check for Balking', 'Customer Balks', {'label': 'Balks'}),
    ('Check for Balking', 'Customer Joins Queue', {'label': 'Joins Queue'}),
    ('Customer Joins Queue', 'Wait for Level 1 Support'),
    ('Wait for Level 1 Support', 'Customer Reneges', {'label': 'Reneges'}),
    ('Wait for Level 1 Support', 'Level 1 Support Starts', {'label': 'Support Available'}),
    ('Level 1 Support Starts', 'Level 1 Resolution'),
    ('Level 1 Resolution', 'Resolved by Level 1', {'label': 'Resolved'}),
    ('Level 1 Resolution', 'Escalated to Level 2', {'label': 'Escalate'}),
    ('Escalated to Level 2', 'Level 2 Support Starts'),
    ('Level 2 Support Starts', 'Level 2 Resolution'),
    ('Level 2 Resolution', 'Resolved by Level 2'),
    ('Resolved by Level 2', 'End'),
    ('Resolved by Level 1', 'End'),
    ('Resolved by AI', 'End'),
    ('Customer Balks', 'End'),
    ('Customer Reneges', 'End')
]

for edge in edges:
    if len(edge) == 2:
        G.add_edge(edge[0], edge[1])
    else:
        G.add_edge(edge[0], edge[1], **edge[2])

pos = nx.get_node_attributes(G, 'pos')

node_colors = []
for node in G.nodes():
    if node in ['Customer Arrival', 'End']:
        node_colors.append('lightblue')
    elif 'Resolution' in node or 'Resolved' in node:
        node_colors.append('lightgreen')
    elif 'Balks' in node or 'Reneges' in node:
        node_colors.append('lightcoral')
    elif 'Check for Balking' in node or 'Escalated to Level 2' in node:
        node_colors.append('lightyellow')
    else:
        node_colors.append('white')


plt.figure(figsize=(12, 12))
nx.draw_networkx_nodes(G, pos, node_size=3000, node_color=node_colors, edgecolors='black')

nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20)

labels = {node: '\n'.join(node.split(' ')) if len(node) > 15 else node for node in G.nodes()}

nx.draw_networkx_labels(G, pos, labels=labels, font_size=10)

edge_labels = nx.get_edge_attributes(G, 'label')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=9)

plt.axis('off')

plt.tight_layout()

plt.savefig('event_graph.png', dpi=300, bbox_inches='tight')
plt.show()
