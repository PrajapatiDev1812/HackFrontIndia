import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# pyrefly: ignore[missing-import]
from pyvis.network import Network
from backend.neo4j_client import get_neo4j_driver

def generate_graph_html() -> str:
    driver = get_neo4j_driver()
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="#333333", directed=True)
    
    # Color mapping
    colors = {
        "Decision": "#00C853",  # Green
        "PR": "#2196F3",        # Blue
        "Developer": "#FFC107", # Amber
        "File": "#9C27B0"       # Purple
    }
    
    shapes = {
        "Decision": "diamond",
        "PR": "circle",
        "Developer": "square",
        "File": "triangle"
    }

    with driver.session() as session:
        # Fetch a subgraph of recent decisions and their PRs
        result = session.run("""
            MATCH (d:Decision)<-[:EXTRACTS]-(p:PR)-[:MODIFIES]->(f:File)
            OPTIONAL MATCH (dev:Developer)-[:AUTHORED]->(p)
            RETURN d, p, f, dev
            LIMIT 30
        """)
        
        nodes_added = set()
        
        for record in result:
            # Add Decision Node
            dec = record["d"]
            dec_id = f"dec_{dec['id']}"
            if dec_id not in nodes_added:
                net.add_node(dec_id, label=f"Decision\n{dec['summary'][:30]}...", 
                             color=colors["Decision"], shape=shapes["Decision"], title=dec['rationale'])
                nodes_added.add(dec_id)
                
            # Add PR Node
            pr = record["p"]
            pr_id = f"pr_{pr['id']}"
            if pr_id not in nodes_added:
                net.add_node(pr_id, label=f"PR #{pr['number']}\n{pr['title'][:20]}...", 
                             color=colors["PR"], shape=shapes["PR"], title=pr['title'])
                nodes_added.add(pr_id)
                
            # Add File Node
            file = record["f"]
            file_id = f"file_{file['path']}"
            if file_id not in nodes_added:
                net.add_node(file_id, label=file['path'].split('/')[-1], 
                             color=colors["File"], shape=shapes["File"])
                nodes_added.add(file_id)
                
            # Add Developer Node
            dev = record["dev"]
            if dev:
                dev_id = f"dev_{dev['login']}"
                if dev_id not in nodes_added:
                    net.add_node(dev_id, label=dev['login'], 
                                 color=colors["Developer"], shape=shapes["Developer"])
                    nodes_added.add(dev_id)
                net.add_edge(dev_id, pr_id, label="AUTHORED")
                
            # Add Edges
            net.add_edge(pr_id, dec_id, label="EXTRACTS")
            net.add_edge(pr_id, file_id, label="MODIFIES")

    net.set_options("""
    var options = {
      "physics": {"enabled": true, "stabilization": {"iterations": 100}},
      "nodes": {"font": {"size": 14}},
      "edges": {"color": {"color": "#888888", "highlight": "#2196F3"}, "smooth": {"type": "continuous"}}
    }
    """)
    
    return net.generate_html()
