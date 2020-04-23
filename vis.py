from pyvis.network import Network
import networkx as nx
import pandas as pd
import pickle
import sys

def get_description(profile):
    return f"{profile['dest_title']} @ {profile['dest_company']}"

def create_graph(net, df):
    c_list= []
    for i in range(len(df)):
        p = df.loc[i,:]
        dg = int(p["graph_degree"])
        n_id = p["dest_id"]
        d = {"n_id": n_id, "label":p["dest_name"], "image": p["dest_pic"], "shape":"circularImage", \
            "title":get_description(p), "color": colors[dg], "borderWidth": 5-dg}
        net.add_node(**d)

        if not pd.isna(p["dest_connected"]):
            cn = p["dest_connected"].split(",")
            l = [(n_id, c) for c in cn]
            c_list.append(l)
            
    for c in c_list:
        net.add_edges(c)

# with open('graph_options.data', 'rb') as f:
#     graph_options = pickle.load(f)
# graph = Network(height ="100%", width = "100%", bgcolor = "#222222", font_color= "white")
# graph.barnes_hut()
# plot_graph(graph, df)
# graph.set_options(graph_options)
# graph.show("ap_graph.html")


def create_tree(net, df):
    c_list = []
    for i in range(len(df)):
        p = df.loc[i,:]
        n_id = p["dest_id"]
        dg = p["tree_degree"]
        d = {"n_id": n_id, "label":p["dest_name"], "image": p["dest_pic"], \
             "shape":"circularImage", "title":get_description(p), "level":dg, "color":colors[dg]}
        net.add_node(**d)
        
        if i != 0:
            c_list.append((p["source_id"], p["dest_id"]))
    net.add_edges(c_list)

# with open('tree_options.data', 'rb') as f:
#     tree_options = pickle.load(f)
# tree = Network(height ="100%", width = "100%", directed = True,  bgcolor = "#222222", font_color= "white")
# plot_tree(tree, df)
# tree.set_options(tree_options)
# tree.show("ap_tree.html")

# tree = Network(height ="100%", width = "100%", directed = True,  bgcolor = "#222222", font_color= "white")
# plot_tree(tree, df)
# tree.set_options(tree_options)
# tree.show("ap_tree.html")

def plot_tree(df_path, tree_name = None, tree_options = "tree_options.data"):
    df = pd.read_csv(df_path)

    if tree_name is None:
        tree_name = df_path[:df_path.find(".csv")] + "_tree"
    with open(tree_options, 'rb') as f:
        tree_options = pickle.load(f)
    tree = Network(height ="100%", width = "100%", directed = True,  bgcolor = "#222222", font_color= "white")
    create_tree(tree, df)
    tree.set_options(tree_options)
    tree.show(tree_name + ".html")

def plot_graph(df_path, graph_name = None, graph_options = "graph_options.data"):
    df = pd.read_csv(df_path)
    if graph_name is None:
        graph_name = df_path[:df_path.find(".csv")] + "_graph"
    with open(graph_options, 'rb') as f:
        graph_options = pickle.load(f)
    graph = Network(height ="100%", width = "100%", bgcolor = "#222222", font_color= "white")
    graph.barnes_hut()
    create_graph(graph, df)
    graph.set_options(graph_options)
    graph.show(graph_name + ".html")

#python vis.py andrew_palmer_profiles.csv graph ap_graph 

if __name__ == "__main__":
    df_path, which, name = sys.argv[1:4]
    colors =  {0:"red", 1:"orange", 2:"yellow", 3:"green", 4:"blue", 5:"purple"}

    if which == "graph":
        plot_graph(df_path, name)
    elif which == "tree":
        plot_tree(df_path, name)
    else:
        print("invalid argument")



