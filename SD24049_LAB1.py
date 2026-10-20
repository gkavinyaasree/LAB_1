import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

# Directed graph from the question figure (11 edges).
GRAPH = {
    'A': ['B', 'D'],
    'B': ['C', 'E', 'G'],
    'C': ['A'],
    'D': ['C'],
    'E': ['H'],
    'F': [],
    'G': ['F'],
    'H': ['F', 'G'],
}

# Node positions copied from the figure (used for the default graph only)
POS = {'A': (4.4, 6.3), 'E': (5.6, 6.3), 'D': (3.25, 5.7), 'H': (6.7, 5.9),
       'B': (4.7, 5.2), 'C': (3.8, 4.8), 'G': (5.7, 4.6), 'F': (6.7, 4.8)}


def normalize(graph):
    """Upper-case names, remove duplicates, sort neighbours alphabetically."""
    result = {str(k).strip().upper(): sorted(set(str(v).strip().upper() for v in vs))
              for k, vs in graph.items()}
    for vs in list(result.values()):
        for v in vs:
            result.setdefault(v, [])
    return dict(sorted(result.items()))


def search(graph, start, goal=None, method='BFS'):
    graph = normalize(graph)
    start = start.upper().strip()
    goal = goal.upper().strip() if goal else None
    if start not in graph or (goal and goal not in graph):
        raise ValueError('Start and goal must exist in the graph.')
    if method not in ('BFS', 'DFS'):
        raise ValueError('Method must be BFS or DFS.')

    parent, depth, order, trace = {}, {}, [], []

    if method == 'BFS':
        # BFS: FIFO queue, a node is marked DISCOVERED when it is enqueued
        frontier = deque([start])
        discovered = {start}
        parent[start], depth[start] = None, 0
        while frontier:
            node = frontier.popleft()
            order.append(node)
            if node != goal:
                for nb in graph[node]:                  # alphabetical order
                    if nb not in discovered:
                        discovered.add(nb)
                        parent[nb], depth[nb] = node, depth[node] + 1
                        frontier.append(nb)
            trace.append({'step': len(order), 'current': node, 'visited': order.copy(),
                          'frontier': list(frontier), 'depth': depth[node],
                          'parent': parent[node]})
            if node == goal:
                break
    else:
        # DFS marks a node VISITED when it is POPPED (true DFS).
        frontier = [(start, None, 0)]                   # (node, parent, depth)
        visited = set()
        while frontier:
            node, par, d = frontier.pop()               # LIFO
            if node in visited:
                continue
            visited.add(node)
            parent[node], depth[node] = par, d
            order.append(node)
            if node != goal:
                for nb in reversed(graph[node]):        # reverse -> smallest popped first
                    if nb not in visited:
                        frontier.append((nb, node, d + 1))
            trace.append({'step': len(order), 'current': node, 'visited': order.copy(),
                          'frontier': [f[0] for f in frontier], 'depth': d, 'parent': par})
            if node == goal:
                break

    path = []
    if goal is not None and goal in order:
        cursor = goal
        while cursor is not None:
            path.append(cursor)
            cursor = parent[cursor]
        path.reverse()

    return {'method': method, 'order': order, 'path': path,
            'found': bool(path) if goal else None, 'trace': trace,
            'depths': depth, 'parents': parent, 'explored': len(order),
            'max_frontier': max([1] + [len(t['frontier']) for t in trace])}


def edges_from_text(text):
    """One directed edge per line: 'A B' or 'A,B'; an isolated node: 'A'."""
    graph = {}
    for line in text.splitlines():
        line = line.split('#', 1)[0].strip().replace(',', ' ')
        if not line:
            continue
        tokens = line.upper().split()
        if len(tokens) not in (1, 2):
            raise ValueError(f'Invalid line: {line}')
        graph.setdefault(tokens[0], [])
        if len(tokens) == 2:
            graph[tokens[0]].append(tokens[1])
            graph.setdefault(tokens[1], [])
    if not graph:
        raise ValueError('Graph cannot be empty.')
    if len(graph) > 100:
        raise ValueError('Maximum 100 nodes.')
    return normalize(graph)


def graph_to_text(g):
    lines = []
    for u, vs in g.items():
        lines += [f'{u} {v}' for v in vs] if vs else [u]
    return '\n'.join(lines)


DEFAULT_EDGES = graph_to_text(normalize(GRAPH))

st.set_page_config(page_title='BSD3513 | BFS & DFS Lab#1', page_icon='🔍', layout='wide')
st.title('BFS & DFS | Interactive Uninformed Search Algorithms')
st.caption('BSD3513 Introduction to AI · Lab Report 1 · SD24049 (Section 01G) · '
           'Alphabetical tie-breaking · UMPSA')

with st.expander('Learning guide & complexity', expanded=False):
    st.markdown(
        '**BFS** explores level by level using a FIFO queue; **DFS** goes as deep as '
        'possible using a LIFO stack and then backtracks.\n\n'
        '| | BFS | DFS |\n|---|---|---|\n'
        '| Time | O(V + E) | O(V + E) |\n'
        '| Space | O(V) | O(V) |\n'
        '| Shortest path (unweighted) | Yes | No |\n\n'
        'V = number of vertices, E = number of edges.')

with st.sidebar:
    st.header('Graph editor')
    edge_text = st.text_area('Directed edges (one per line: A B)', DEFAULT_EDGES, height=260)
    st.caption('A line with only a node = isolated node. Edges are directed. '
               'The default graph is the one from Question 2.')

try:
    graph = edges_from_text(edge_text)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

nodes = list(graph)
a, b, c = st.columns(3)
start = a.selectbox('Starting node', nodes)
goal = b.selectbox('Goal node (optional)', ['No goal'] + nodes)
method = c.selectbox('Algorithm', ['Both', 'BFS', 'DFS'])
goal = None if goal == 'No goal' else goal

results = {m: search(graph, start, goal, m)
           for m in (['BFS', 'DFS'] if method == 'Both' else [method])}


def draw_graph(result, step):
    g = nx.DiGraph()
    for node, neighbors in graph.items():
        g.add_node(node)
        for nb in neighbors:
            g.add_edge(node, nb)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    # Use the layout from the question for the default graph, otherwise auto-layout
    pos = POS if set(POS) == set(g.nodes) else nx.spring_layout(g, seed=12)

    trace = result['trace'][step - 1]
    current, seen, path = trace['current'], trace['visited'], result['path']

    colors = []
    for node in g.nodes:
        if node == current:
            colors.append('#10b981')            # current: green
        elif path and node == path[-1]:
            colors.append('#f59e0b')            # goal: orange
        elif node in seen:
            colors.append('#93c5fd')            # visited: blue
        else:
            colors.append('#e5e7eb')            # unvisited: grey

    path_edges = set(zip(path, path[1:]))
    edge_colors = ['#f59e0b' if (u, v) in path_edges else '#64748b' for u, v in g.edges()]

    nx.draw_networkx(g, pos, ax=ax, with_labels=True, node_color=colors, node_size=950,
                     font_weight='bold', arrows=True, arrowsize=19,
                     edge_color=edge_colors, width=2)
    ax.axis('off')
    fig.tight_layout()
    return fig


for m, r in results.items():
    st.subheader(f'{m} search')
    st.write('**Expansion order:** ' + ' → '.join(r['order']))

    # Level (BFS) / depth (DFS tree) of every node - required by the question
    label = 'Levels' if m == 'BFS' else 'Depths (DFS tree)'
    by_depth = {}
    for n in r['order']:
        by_depth.setdefault(r['depths'][n], []).append(n)
    st.write(f'**{label}:** ' + ' | '.join(f'{k}: {", ".join(v)}' for k, v in sorted(by_depth.items())))

    if goal:
        if r['found']:
            st.write('**Goal path:** ' + ' → '.join(r['path']))
            st.write(f"**Path length:** {len(r['path']) - 1} edges ({len(r['path'])} nodes)")
        else:
            st.write('**Goal path:** Not reachable')

    x, y, z = st.columns(3)
    x.metric('Expanded nodes', r['explored'])
    y.metric('Max recorded frontier size', r['max_frontier'])
    z.metric('Goal path edges', len(r['path']) - 1 if r['found'] else '—')

    step = st.slider(f'{m}: inspect expansion step', 1, len(r['trace']), len(r['trace']), key=m)
    left, right = st.columns([1.2, 1])
    with left:
        fig = draw_graph(r, step)
        st.pyplot(fig)
        plt.close(fig)
        st.caption('Green: current | Blue: visited | Orange: goal and goal-path edges | Grey: unvisited')
    with right:
        st.write('**Step trace**')
        st.dataframe(pd.DataFrame(r['trace']), hide_index=True)
        st.info('Current frontier: ' + str(r['trace'][step - 1]['frontier']))

st.divider()
