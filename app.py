# File: app.py (Virtual Lab Uniform Cost Search - Single File Version)

import streamlit as st
import pandas as pd
import time
import heapq # Modul untuk Priority Queue
import matplotlib.pyplot as plt
import networkx as nx # Digunakan untuk visualisasi Graf
import random

# List global untuk menyimpan riwayat langkah
HISTORY = []

# =================================================================
# --- FUNGSI ALGORITMA UNIFORM COST SEARCH (UCS) ---
# =================================================================

def uniform_cost_search(graph, start_node, goal_node):
    """
    Mengimplementasikan Uniform Cost Search (UCS) dan mencatat langkah.
    Graph harus berbentuk dictionary: {simpul: {neighbor: cost, ...}, ...}
    """
    global HISTORY
    HISTORY = []

    # Priority Queue: (biaya_total, simpul, jalur)
    # Heapq selalu memprioritaskan elemen pertama (biaya_total)
    priority_queue = [(0, start_node, [start_node])]
    
    # Dictionary untuk menyimpan biaya terendah yang ditemukan sejauh ini ke setiap simpul
    min_cost = {start_node: 0}
    
    # Catat status awal
    HISTORY.append({
        'action': f"Mulai UCS dari '{start_node}' ke '{goal_node}'.",
        'queue': list(priority_queue),
        'min_cost': min_cost.copy(),
        'expanded': None,
        'status': 'Mulai'
    })

    while priority_queue:
        # Ambil simpul dengan biaya terendah dari antrian
        current_cost, current_node, current_path = heapq.heappop(priority_queue)

        # Catat simpul yang sedang diekspansi
        HISTORY.append({
            'action': f"Ekspansi simpul '{current_node}' dengan biaya {current_cost}.",
            'queue': list(priority_queue),
            'min_cost': min_cost.copy(),
            'expanded': current_node,
            'path': current_path,
            'status': 'Ekspansi'
        })
        
        # Jika simpul saat ini adalah simpul tujuan
        if current_node == goal_node:
            HISTORY.append({
                'action': f"Tujuan '{goal_node}' DITEMUKAN dengan biaya total {current_cost}.",
                'queue': list(priority_queue),
                'min_cost': min_cost.copy(),
                'expanded': current_node,
                'path': current_path,
                'cost': current_cost,
                'status': 'Ditemukan'
            })
            return current_path, current_cost, HISTORY

        # Jelajahi tetangga
        if current_node in graph:
            for neighbor, cost in graph[current_node].items():
                new_cost = current_cost + cost
                new_path = current_path + [neighbor]

                # Periksa apakah jalur baru lebih baik (biaya lebih rendah)
                if neighbor not in min_cost or new_cost < min_cost[neighbor]:
                    min_cost[neighbor] = new_cost
                    
                    # Tambahkan ke antrian prioritas
                    heapq.heappush(priority_queue, (new_cost, neighbor, new_path))
                    
                    HISTORY.append({
                        'action': f"Memperbarui jalur ke '{neighbor}'. Biaya baru: {new_cost}.",
                        'queue': list(priority_queue),
                        'min_cost': min_cost.copy(),
                        'expanded': current_node,
                        'path': new_path,
                        'status': 'Update'
                    })

    # Jika antrian kosong dan tujuan tidak ditemukan
    HISTORY.append({
        'action': f"Antrian kosong. Tujuan '{goal_node}' tidak terjangkau dari '{start_node}'.",
        'queue': list(priority_queue),
        'min_cost': min_cost.copy(),
        'expanded': None,
        'status': 'Gagal'
    })
    return None, 0, HISTORY

# =================================================================
# --- KONFIGURASI DAN STREAMLIT APP ---
# =================================================================

st.set_page_config(
    page_title="Virtual Lab: Uniform Cost Search",
    layout="wide"
)

st.title("🛣️ Virtual Lab: Uniform Cost Search (UCS) Interaktif")
st.markdown("### Menemukan Jalur dengan Biaya Terendah pada Graf")

# 

st.sidebar.header("Konfigurasi Graf dan Pencarian")

default_graph_str = """
A: B=1, C=5
B: D=3, E=6
C: F=4, G=2
D: H=1
E: G=2
F: H=3
G: H=1
"""
input_graph_str = st.sidebar.text_area(
    "Definisi Graf (Format: Simpul: Tetangga=Biaya,...)", 
    default_graph_str, height=200
)

# Parsing Graf
try:
    graph_data = {}
    nodes = set()
    edges = set()
    
    for line in input_graph_str.strip().split('\n'):
        if ':' in line:
            parent, neighbors_str = line.split(':', 1)
            parent = parent.strip()
            nodes.add(parent)
            graph_data[parent] = {}
            
            for neighbor_cost in neighbors_str.split(','):
                parts = neighbor_cost.strip().split('=')
                if len(parts) == 2:
                    neighbor = parts[0].strip()
                    cost = int(parts[1].strip())
                    nodes.add(neighbor)
                    graph_data[parent][neighbor] = cost
                    edges.add((parent, neighbor, cost))

    all_nodes = sorted(list(nodes))
    if not all_nodes:
        st.error("Graf tidak valid atau kosong.")
        st.stop()
        
    # Ambil simpul awal dan tujuan
    default_start = all_nodes[0]
    default_goal = all_nodes[-1]
    
    start_node = st.sidebar.selectbox("Simpul Awal (Start):", all_nodes, index=all_nodes.index(default_start) if default_start in all_nodes else 0)
    goal_node = st.sidebar.selectbox("Simpul Tujuan (Goal):", all_nodes, index=all_nodes.index(default_goal) if default_goal in all_nodes else (len(all_nodes)-1))

    speed = st.sidebar.slider("Kecepatan Simulasi (detik)", 0.1, 2.0, 0.5)

except Exception as e:
    st.error(f"Kesalahan parsing graf: {e}")
    st.stop()


# --- Fungsi Plot Graf (NetworkX + Matplotlib) ---
def plot_graph(graph_edges, all_nodes_list, path_found=None, expanded_node=None, min_cost_dict=None):
    
    G = nx.DiGraph()
    G.add_nodes_from(all_nodes_list)
    G.add_weighted_edges_from(graph_edges)
    
    # Layout untuk posisi node
    try:
        pos = nx.spring_layout(G, seed=random.randint(0, 100))
    except:
        pos = nx.random_layout(G)
        
    fig, ax = plt.subplots(figsize=(10, 6))

    # Warna Node Default: Abu-abu Muda
    node_colors = ['#cccccc'] * len(all_nodes_list)
    node_map = {node: idx for idx, node in enumerate(all_nodes_list)}
    
    # Warna Edge Default: Abu-abu
    edge_colors = ['#888888'] * len(G.edges())
    
    # 1. Menandai Simpul yang Diekspansi
    if expanded_node and expanded_node in node_map:
        node_colors[node_map[expanded_node]] = '#FF9900' # Orange
    
    # 2. Menandai Jalur yang Ditemukan (Hijau)
    if path_found and len(path_found) > 1:
        path_edges = list(zip(path_found, path_found[1:]))
        
        # Warnai Simpul di Jalur
        for node in path_found:
             if node in node_map:
                 node_colors[node_map[node]] = '#6AA84F' # Hijau
                 
        # Warnai Tepi (Edges) di Jalur
        for i, edge in enumerate(G.edges()):
            if (edge[0], edge[1]) in path_edges:
                edge_colors[i] = '#6AA84F'

    # 3. Menandai Start dan Goal
    if start_node in node_map:
        node_colors[node_map[start_node]] = '#4A86E8' # Biru (Start)
    if goal_node in node_map:
        node_colors[node_map[goal_node]] = '#8E44AD' # Ungu (Goal)
        
    # --- Gambar Graf ---
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1500, alpha=0.9, ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2, arrows=True, arrowsize=20, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=ax)

    # Label Biaya (Weight)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', ax=ax)

    # Label Biaya Minimum (Min Cost) di bawah Node
    if min_cost_dict:
        cost_labels = {node: f"C:{min_cost_dict.get(node, '∞')}" for node in G.nodes()}
        # Geser posisi label biaya ke bawah sedikit
        cost_pos = {k: [v[0], v[1] - 0.05] for k, v in pos.items()}
        nx.draw_networkx_labels(G, cost_pos, labels=cost_labels, font_size=8, font_color='blue', ax=ax)

    ax.set_title("Uniform Cost Search Traversal", fontsize=14)
    ax.axis('off')
    
    plt.close(fig) 
    return fig


# --- Visualisasi Utama ---
st.markdown("---")
st.subheader("Visualisasi UCS")
st.write(f"Mencari jalur dari **{start_node}** ke **{goal_node}**.")

# Konversi edges dari dict graf ke list (untuk NetworkX)
graph_edges_list = [(u, v, d) for u, neighbors in graph_data.items() for v, d in neighbors.items()]

if st.button("Mulai Simulasi Uniform Cost Search"):
    
    path, cost, history = uniform_cost_search(graph_data, start_node, goal_node)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        vis_placeholder = st.empty()
        status_placeholder = st.empty() 
    with col2:
        table_placeholder = st.empty()
    
    final_path = None
    final_cost = 0
    
    # --- Loop Simulasi ---
    for step, state in enumerate(history):
        status = state['status']
        action = state['action']
        
        expanded_node = state.get('expanded')
        min_cost = state.get('min_cost')
        current_path = state.get('path')
        
        if status == 'Ditemukan':
            final_path = state.get('path')
            final_cost = state.get('cost')
        
        # --- Tampilkan Grafik (Matplotlib/NetworkX) ---
        # Jika ditemukan, warnai final_path. Jika tidak, warnai current_path.
        path_to_plot = final_path if final_path else current_path
        
        fig_mpl = plot_graph(
            graph_edges_list, 
            all_nodes, 
            path_found=path_to_plot, 
            expanded_node=expanded_node,
            min_cost_dict=min_cost
        )

        with vis_placeholder.container():
            st.pyplot(fig_mpl, clear_figure=True)
        
        # --- TABEL DATA PENDUKUNG ---
        with table_placeholder.container():
             st.markdown("##### Antrian Prioritas dan Biaya Minimum")
             
             # Format Priority Queue
             pq_data = state['queue']
             pq_df = pd.DataFrame(pq_data, columns=['Biaya', 'Simpul', 'Jalur'])
             st.dataframe(pq_df, hide_index=True)
             
             # Format Min Cost
             mc_df = pd.DataFrame(min_cost.items(), columns=['Simpul', 'Min Cost'])
             st.dataframe(mc_df, hide_index=True)


        with status_placeholder.container():
            if status == 'Ditemukan':
                st.success(f"**Langkah ke-{step+1}** | **Status:** {status}")
            elif status == 'Gagal':
                st.error(f"**Langkah ke-{step+1}** | **Status:** {status}")
            else:
                 st.info(f"**Langkah ke-{step+1}** | **Status:** {status}")
            st.caption(action)

        time.sleep(speed)

    # --- Hasil Akhir Final ---
    st.markdown("---")
    if final_path:
        st.balloons()
        st.success(f"**Pencarian Tuntas!**")
        st.write(f"Jalur Biaya Terendah DITEMUKAN: **{' -> '.join(final_path)}**")
        st.write(f"Total Biaya: **{final_cost}**")
    else:
        st.error(f"**Pencarian Tuntas!**")
        st.write("Simpul Tujuan tidak dapat dijangkau.")
    
    st.info(f"Algoritma Uniform Cost Search selesai dalam **{len(history)}** langkah.")
