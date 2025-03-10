import hashlib
import json
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_ollama import ChatOllama 
import datetime
from arango import ArangoClient
from langchain_community.graphs import ArangoGraph
from langchain_community.chains.graph_qa.arangodb import ArangoGraphQAChain
import networkx as nx
import nx_arangodb as nxadb
import re
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

ollama_llm = ChatOllama(model="llama3.1:latest", temperature=5)
chatgpt_llm = ChatOpenAI(
    model= "gpt-4o-mini",
    # model="gpt-4o",
    api_key=os.getenv("OPENAI_KEY")
)

app = Flask(__name__)
CORS(app)  


ARANGO_URL = "http://localhost:8529"
DB_NAME = "news_db"
USERNAME = "root"
PASSWORD = "123"

client = ArangoClient(hosts=ARANGO_URL)
db = client.db("news", username=USERNAME, password=PASSWORD)
scheduling_db = client.db("scheduling", username=USERNAME, password=PASSWORD)
if not scheduling_db.has_collection("scheduling_contents"):
    scheduling_db.create_collection("scheduling_contents")
arango_graph = ArangoGraph(db)

G_adb = nxadb.MultiGraph(name="news_graph", db=db)

aql_results = None
def delete_key_recursively(d, key_to_delete):
    if isinstance(d, dict):
        if key_to_delete in d:
            del d[key_to_delete]
        for key in list(d.keys()):
            delete_key_recursively(d[key], key_to_delete)
    elif isinstance(d, list):
        for item in d:
            delete_key_recursively(item, key_to_delete)
    return d

graph_schema = delete_key_recursively(arango_graph.schema, "example_document")
graph_schema = delete_key_recursively(graph_schema, "example_edge")

import re
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain.prompts import PromptTemplate

@tool
def text_to_aql_to_text(query: str):
    """This tool is available to invoke the
    ArangoGraphQAChain object, which enables you to
    translate a Natural Language Query into AQL, execute
    the query, and translate the result back into Natural Language.
    """
    global aql_results
    base_prompt = PromptTemplate(
        template="Do not use OUTBOUND"
    )

    chain = ArangoGraphQAChain.from_llm(
    	llm=chatgpt_llm,
    	graph=arango_graph,
    	verbose=True,
        allow_dangerous_requests=True,
        base_prompt=base_prompt
    )

    chain.top_k = 5
    chain.return_aql_query = True
    chain.return_aql_result = True
    chain.max_aql_generation_attempts = 5
    chain.aql_examples = """
    ## **important** Dont ever try to return the embedding fields and _id ever.

    # Ihow many nodes and edges are there in graph?
    WITH authors, categories, characters, countries, sources, summaries, edges
    RETURN { 
    nodeCount: COUNT(FOR vertex IN summaries RETURN vertex), 
    edgeCount: COUNT(FOR edge IN edges RETURN edge) 
    }

    """
    result = chain.invoke(query)
    aql_results = result
    return str(result["result"])
@tool
def text_to_nx_algorithm_to_text(query):
    """This tool is available to invoke a NetworkX Algorithm on
    the ArangoDB Graph. You are responsible for accepting the
    Natural Language Query, establishing which algorithm needs to
    be executed, executing the algorithm, and translating the results back
    to Natural Language, with respect to the original query.

    If the query (e.g traversals, shortest path, etc.) can be solved using the Arango Query Language, then do not use
    this tool.
    """


    ######################
    print("1) Generating NetworkX code")

    text_to_nx = chatgpt_llm.invoke(f"""
    I have a NetworkX Graph called `G_adb`. It has the following schema: {graph_schema}

    I have the following graph analysis query: {query}.

    Generate the Python Code required to answer the query using the `G_adb` object.

    Be very precise on the NetworkX algorithm you select to answer this query. Think step by step.

    Only assume that networkx is installed, and other base python dependencies.

    Always set the last variable as `FINAL_RESULT`, which represents the answer to the original query.

    Only provide python code that I can directly execute via `exec()`. Do not provide any instructions.

    Make sure that `FINAL_RESULT` stores a short & consice answer. Avoid setting this variable to a long sequence.
    If asked for visualization image, Always store the image as graph.png in current dir
    Your code:
    """).content

    text_to_nx_cleaned = re.sub(r"^```python\n|```$", "", text_to_nx, flags=re.MULTILINE).strip()

    print('-'*10)
    print(text_to_nx_cleaned)
    print('-'*10)

    ######################

    print("\n2) Executing NetworkX code")
    global_vars = {"G_adb": G_adb, "nx": nx}
    local_vars = {}

    try:
        exec(text_to_nx_cleaned, global_vars, local_vars)
        text_to_nx_final = text_to_nx
    except Exception as e:
        print(f"EXEC ERROR: {e}")
        return f"EXEC ERROR: {e}"


    print('-'*10)
    FINAL_RESULT = local_vars["FINAL_RESULT"]
    print(f"FINAL_RESULT: {FINAL_RESULT}")
    print('-'*10)

    print("3) Formulating final answer")

    nx_to_text = chatgpt_llm.invoke(f"""
        I have a NetworkX Graph called `G_adb`. It has the following schema: {graph_schema}

        I have the following graph analysis query: {query}.

        I have executed the following python code to help me answer my query:

        ---
        {text_to_nx_final}
        ---

        The `FINAL_RESULT` variable is set to the following: {FINAL_RESULT}.

        Based on my original Query and FINAL_RESULT, generate a short and concise response to
        answer my query.

        Your response:
    """).content

    return nx_to_text

@tool
def text_to_graph_visualization(query):
    """This tool is available to invoke a NetworkX Algorithm on
    the ArangoDB Graph. You are responsible for accepting the
    Natural Language Query, establishing which algorithm needs to
    be executed, executing the algorithm, and translating the results back
    to Natural Language, with respect to the original query.

    If the query (e.g traversals, shortest path, etc.) can be solved using the Arango Query Language, then do not use
    this tool.
    """


    ######################
    print("1) Generating NetworkX code")

    text_to_nx = chatgpt_llm.invoke(f"""
    I have a NetworkX Graph called `G_adb`. It has the following schema: {graph_schema}

    I have the following graph analysis query: {query}.

    Generate the Python Code required to answer the query using the `G_adb` object.

    Be very precise on the NetworkX algorithm you select to answer this query and matplotlib for graph visualization. Think step by step.

    Only assume that networkx is installed, and other base python dependencies.

    Always set the last variable as `IMAGE`, which represents the answer to the original query.

    Only provide python code that I can directly execute via `exec()`. Do not provide any instructions.

    Make sure that `IMAGE` stores a generated image, i will convert that into base64 later. Avoid setting this variable to a long sequence.

    Always store the image as graph.png in current dir
    
    NO need to store the subgraph technique, if subgraph needed, look for another workaround to generate graph
    Your code:
    """).content

    text_to_nx_cleaned = re.sub(r"^```python\n|```$", "", text_to_nx, flags=re.MULTILINE).strip()

    print('-'*10)
    print(text_to_nx_cleaned)
    print('-'*10)

    ######################

    print("\n2) Executing NetworkX code")
    global_vars = {"G_adb": G_adb, "nx": nx}
    local_vars = {}

    try:
        exec(text_to_nx_cleaned, global_vars, local_vars)
        text_to_nx_final = text_to_nx
    except Exception as e:
        print(f"EXEC ERROR: {e}")
        return f"EXEC ERROR: {e}"


    IMAGE = local_vars["IMAGE"]
    
tools = [text_to_aql_to_text, text_to_nx_algorithm_to_text, text_to_graph_visualization]

def query_graph(query):
    app = create_react_agent(chatgpt_llm, tools=tools)

    final_state = app.invoke({"messages": [{"role": "user", "content": query}]})
    return final_state["messages"][-1].content
llm = ChatOllama(
    model="qwen2.5:7b",
    temperature=0,
)
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_prompt = data.get("prompt", "")
    graph_file = "graph.png"
    if os.path.exists(graph_file):
        print("file found")
        os.remove(graph_file)
    global aql_results
    aql_results = None
    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

   

    res = query_graph(user_prompt)
    if aql_results:
        return jsonify(aql_results)
    else:
        if os.path.exists(graph_file):
            return jsonify({"graph": os.path.abspath(graph_file), "result": res})
        else: 
            return jsonify({"result" : res})

@app.route('/scheduled-message', methods=['GET'])
def get_response():
    collection = scheduling_db.collection("scheduling_contents")
    cursor = collection.all()
    
    try:
        doc = next(cursor)
        collection.delete(doc)
        return jsonify({"message": doc["content"]})
    
    except StopIteration:
        return jsonify({"message": ""}), 200

@app.route('/generate-synthetic-news', methods=['GET'])
def get_synthetic_message():
    current_date = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")

    prompt = f"""
            You are an AI designed to generate synthetic news articles for the current date: {current_date}. The news should be **realistic but entirely fictional**, based on plausible events. The tone should match real-world journalism.

            ### Instructions:
            - Generate a **realistic but fictional news article**.
            - The story should be **believable** but **not real**.
            - Ensure the article has a **clear theme** (e.g., politics, sports, technology).
            - Provide a **valid source name** and an **author name** (fictional or common journalist names).
            - Include a **title** and a **brief description**.
            - Generate a **valid URL** and **image URL** (fictional, but correctly formatted).
            - Set the **published_at** field to **today's date** in `YYYY-MM-DD` format.
            - Include a **full content version** (200-300 words) and a **summarized version** (100-150 words).
            - Identify **characters** (public figures, fictional names).
            - Identify **countries** involved.
            - Classify the article into **categories** (e.g., ["Politics", "Economy"]).

            ### Output Format:
            Return a **valid JSON** response with this exact structure:
            ```json
            {{
                "source_name": "Name of the fictional news source",
                "author": "Fictional journalist name",
                "title": "Title of the news article",
                "description": "Brief 1-2 sentence summary of the article",
                "url": "https://fictionalnews.com/article/unique-id",
                "url_to_image": "https://fictionalnews.com/images/article-thumbnail.jpg",
                "published_at": "{current_date}",
                "full_content": "A 200-300 word realistic but fictional article",
                "summarized_content": "A 100-150 word summary of the article",
                "category": ["Category1", "Category2"] or [],
                "characters": ["Person1", "Person2", "Person3"] or [],
                "country": ["Identified country"] or []
            }}"""

    
    for attempt in range(3):
        try:
            ai_msg = llm.invoke(prompt)
            response_data = ai_msg.content.strip()

            match = re.search(r"```(?:json)?\n(.*?)\n```", response_data, re.DOTALL)
            json_str = match.group(1) if match else response_data.strip()

            response_data = json.loads(json_str)
            return jsonify({"message" : response_data})  # Successfully parsed JSON

        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            datetime.time.sleep(1)  # Small delay before retrying


    return jsonify({"message" : {}})

@app.route('/store-news-in-arangodb', methods=['POST'])
def store_news_in_arangodb():
    
    data = request.json
    print(data)
    def generate_key(value):
        return hashlib.md5((str(value) + str(datetime.datetime.now().time())).encode()).hexdigest()

    categories, characters, countries = set(), set(), set()
    source_keys, author_keys, category_keys, character_keys, country_keys = {}, {}, {}, {}, {}
    edges, summaries = [], {}

    source, author = data['source_name'], data['author']
    char_list = [char.strip() for char in str(data['characters']).split(",") if char.strip()]
    category_list = [cat.strip() for cat in str(data['category']).split(",") if cat.strip()]
    country_list = [country.strip() for country in str(data['country']).split(",") if country.strip()]
        
    summary_text, title = data['summarized_content'], data['title']
   
    summary_id = generate_key((summary_text))
        # summary_embedding = generate_embedding(summary_text)

        # Store summary
    summaries[summary_id] = {
            "_key": summary_id,
            "summary_content": summary_text,
            "published_at": data["published_at"],
            "url": data["url"],
            "url_to_image": data["url_to_image"],
            # "title": title,
            # "source": str(source),
            # "author":  str(author)
            # "embeddings" : summary_embedding
        }

    for country in country_list:
        if country not in country_keys:
            country_keys[country] = generate_key(country)
            countries.add(country)

    for char in char_list:
        if char not in character_keys:
            character_keys[char] = generate_key(char)
            characters.add(char)

    for cat in category_list:
        if cat not in category_keys:
            category_keys[cat] = generate_key(cat)
            categories.add(cat)


    for cat in category_list:
        edges.append({"_from": f"categories/{category_keys[cat]}", "_to": f"summaries/{summary_id}"})

    for char in char_list:
        edges.append({"_from": f"characters/{character_keys[char]}", "_to": f"summaries/{summary_id}"})
        for cat in category_list:
            edges.append({"_from": f"categories/{category_keys[cat]}", "_to": f"characters/{character_keys[char]}"})

    for country in country_list:
        edges.append({"_from": f"countries/{country_keys[country]}", "_to": f"summaries/{summary_id}"})

        for cat in category_list:
            edges.append({"_from": f"categories/{category_keys[cat]}", "_to": f"countries/{country_keys[country]}"})

        for char in char_list:
            edges.append({"_from": f"characters/{character_keys[char]}", "_to": f"countries/{country_keys[country]}"})
    

    # Bulk Insert
    db.collection("categories").import_bulk([{"_key": category_keys[c], "name": c} for c in categories])
    db.collection("characters").import_bulk([{"_key": character_keys[ch], "name": ch} for ch in characters])
    db.collection("countries").import_bulk([{"_key": country_keys[co], "name": co} for co in countries])
    db.collection("summaries").import_bulk(list(summaries.values()))

   
    graph = db.graph("news_graph")
    for collection in ["categories", "characters", "countries", "summaries"]:
        if not graph.has_vertex_collection(collection):
            graph.create_vertex_collection(collection)

    if not graph.has_edge_definition("edges"):
        graph.create_edge_definition(
            edge_collection="edges",
            from_vertex_collections=["categories", "characters", "countries"],
            to_vertex_collections=["summaries"],
        )
    return jsonify({"message" : "OK"})

@app.route('/schdule-news', methods=['POST'])
def schedule_messages():
    data = request.json
    
    if "data" in data:
        scheduling_db.collection("scheduling_contents").insert({"content": data["data"]})
        return jsonify({"message": "OK"})
    return jsonify({"error": "Invalid data"}), 400
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)





@tool
def text_to_aql_to_text(query: str):
    """This tool is available to invoke the
    ArangoGraphQAChain object, which enables you to
    translate a Natural Language Query into AQL, execute
    the query, and translate the result back into Natural Language.
    """


    chain = ArangoGraphQAChain.from_llm(
    	llm=chatgpt_llm,
    	graph=arango_graph,
    	verbose=True,
        allow_dangerous_requests=True,
        base_prompt=base_prompt
    )

    chain.top_k = 5
    chain.return_aql_query = True
    chain.return_aql_result = True
    chain.max_aql_generation_attempts = 5
    chain.aql_examples = """
    ## **important** Dont ever try to return the embedding fields and _id ever.

    # Ihow many nodes and edges are there in graph??
    WITH authors, categories, characters, countries, sources, summaries, edges
    RETURN { 
    nodeCount: COUNT(FOR vertex IN summaries RETURN vertex), 
    edgeCount: COUNT(FOR edge IN edges RETURN edge) 
    }

    """
    result = chain.invoke(query)

    return str(result["result"])

