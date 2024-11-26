import networkx as nx
import matplotlib.pyplot as plt

def main():
    G = nx.DiGraph()

    nodes = {
        'Start': {'pos': (0, 8)},
        'Customer Arrives': {'pos': (0, 7)},
        'Assign Request Type': {'pos': (0, 6)},
        'Attempt AI Resolution': {'pos': (0, 5)},
        'Resolved by AI': {'pos': (2, 5)},
        'Queued for Level 1 Support': {'pos': (-2, 5)},
        'Level 1 Support Started': {'pos': (-2, 4)},
        'Level 1 Resolution': {'pos': (-2, 3)},
        'Escalation Needed?': {'pos': (-2, 2)},
        'Resolved by Level 1': {'pos': (-4, 2)},
        'Escalated to Level 2': {'pos': (-2, 1)},
        'Queued for Level 2 Support': {'pos': (-2, 0)},
        'Level 2 Support Started': {'pos': (-2, -1)},
        'Level 2 Resolution': {'pos': (-2, -2)},
        'Resolved by Level 2': {'pos': (-4, -2)},
        'End': {'pos': (0, -3)},
    }

    for node, data in nodes.items():
        G.add_node(node, pos=data['pos'])

    edges = [
        ('Start', 'Customer Arrives'),
        ('Customer Arrives', 'Assign Request Type'),
        ('Assign Request Type', 'Attempt AI Resolution'),
        ('Attempt AI Resolution', 'Resolved by AI'),
        ('Attempt AI Resolution', 'Queued for Level 1 Support'),
        ('Resolved by AI', 'End'),
        ('Queued for Level 1 Support', 'Level 1 Support Started'),
        ('Level 1 Support Started', 'Level 1 Resolution'),
        ('Level 1 Resolution', 'Escalation Needed?'),
        ('Escalation Needed?', 'Resolved by Level 1'),
        ('Escalation Needed?', 'Escalated to Level 2'),
        ('Resolved by Level 1', 'End'),
        ('Escalated to Level 2', 'Queued for Level 2 Support'),
        ('Queued for Level 2 Support', 'Level 2 Support Started'),
        ('Level 2 Support Started', 'Level 2 Resolution'),
        ('Level 2 Resolution', 'Resolved by Level 2'),
        ('Resolved by Level 2', 'End'),
    ]

    G.add_edges_from(edges)

    edge_labels = {
        ('Attempt AI Resolution', 'Resolved by AI'): 'Yes',
        ('Attempt AI Resolution', 'Queued for Level 1 Support'): 'No',
        ('Escalation Needed?', 'Resolved by Level 1'): 'No',
        ('Escalation Needed?', 'Escalated to Level 2'): 'Yes',
    }

    pos = nx.get_node_attributes(G, 'pos')

    node_colors = []
    for node in G.nodes():
        if node in ['Start', 'End']:
            node_colors.append('lightblue')
        elif node in ['Attempt AI Resolution', 'Escalation Needed?']:
            node_colors.append('lightgreen')
        else:
            node_colors.append('white')

    nx.draw_networkx_nodes(G, pos, node_size=3000, node_color=node_colors, edgecolors='black')

    nx.draw_networkx_labels(G, pos, font_size=8)

    nx.draw_networkx_edges(G, pos, arrows=True)

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=8)

    plt.axis('off')

    plt.tight_layout()

    plt.savefig('customer_support_flowchart.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()