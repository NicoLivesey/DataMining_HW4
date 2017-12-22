import json
import pprint
import networkx as nx
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from pqdict import minpq
from math import*


class TableBuild:

    def __init__(self, data):
        self.authors, self.authorpub, self.authorconf, self.publications, self.conferences, self.collaborations = self.indexer(data)

    def indexer(self, data):
        author_name = []
        author_id = []

        authorpub_author = []
        authorpub_pub = []

        authorconf_author = []
        authorconf_conf = []

        pub_id = []
        pub_title = []
        pub_conf = []

        conf_id = []
        conf_name = []

        collab1 = []
        collab2 = []

        for paper in data:
            for author in paper['authors']:
                for author2 in paper['authors']:
                    if author['author_id'] != author2['author_id']:
                        collab1.append(str(author['author_id']))
                        collab2.append(str(author2['author_id']))
                    else: continue
                author_id.append(str(author['author_id']))
                author_name.append(str(author['author']))

                authorpub_author.append(str(author['author_id']))
                authorpub_pub.append(str(paper['id_publication_int']))

                authorconf_author.append(str(author['author_id']))
                authorconf_conf.append(str(paper['id_conference_int']))
            
            pub_id.append(str(paper['id_publication_int']))
            pub_title.append(str(paper['title']))
            pub_conf.append(str(paper['id_conference_int']))

            conf_id.append(str(paper['id_conference_int']))
            conf_name.append(str(paper['id_conference']))

        authors = self.uniqueRows(np.column_stack((author_id, author_name)))
        authorpub = np.column_stack((authorpub_author, authorpub_pub))
        authorconf = self.uniqueRows(np.column_stack((authorconf_author, authorconf_conf)))
        publications = np.column_stack((pub_id, pub_title, pub_conf))
        conferences = self.uniqueRows(np.column_stack((conf_id, conf_name)))
        collaborations = self.uniqueRows(np.column_stack((collab1, collab2)))

        return authors, authorpub, authorconf, publications, conferences, collaborations

    def uniqueRows(self, a):
        a = np.ascontiguousarray(a)
        unique_a = np.unique(a.view([('', a.dtype)]*a.shape[1]))

        return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))


class GraphBuild:

    def __init__(self, data):
        self.G = nx.Graph()
        self.db = TableBuild(data)
        self.set = self.getPapersList()
        self.nodeBuild()
        self.edgeBuild()

    def nodeBuild(self):
        self.G.add_nodes_from([item[0] for item in self.db.authors])

    def edgeBuild(self):
        for item in self.db.collaborations:
            weight = 1 - self.jaccardSimilarity(self.set[item[0]], self.set[item[1]])
            self.G.add_edge(item[0], item[1], weight = weight)

    def jaccardSimilarity(self, x, y):
        intersection = len(set.intersection(*[set(x), set(y)]))
        union = len(set.union(*[set(x), set(y)]))
        
        return intersection/float(union)

    def getPapersList(self):
        d = {}

        for row in self.db.authorpub:
            if row[0] in d:
                d[row[0]].append(row[1])
            else:
                d[row[0]] = [row[1]]

        return d


class ConfQuery:
    
    def __init__(self, data, conf, name = False):
        self.graph = GraphBuild(data)
        self.conf = conf
        self.name = name
        self.authors = []
        self.G = nx.Graph()
        self.query()

    def findAuthors(self):
        if self.name == False:
            for item in self.graph.db.authorconf:
                if item[1] == self.conf:
                    self.authors.append(item[0])
        else:
            _id = [item[0] for item in self.graph.db.conferences if item[1] == self.conf]
            _id = _id[0]
            for item in self.graph.db.authorconf:
                if item[1] == _id:
                    self.authors.append(item[0])

    def query(self):
        self.findAuthors()
        self.G = self.graph.G.subgraph(self.authors)


class NeighborQuery:

    def __init__(self, data, author, d, name = False):
        self.graph = GraphBuild(data)
        self.author = author
        self.d = d
        self.neighbors = []
        self.name = name
        self.G = nx.Graph()
        self.query()

    def query(self):
        if self.name == True:
            _id = [item[0] for item in self.graph.db.authors if item[1] == self.author]
            self.author = _id[0]

        current_nodes = [self.author]
        new_nodes = []
        self.neighbors.append(self.author)
        for i in range(self.d):
            for j in range(len(current_nodes)):
                self.neighbors.extend(self.graph.G.neighbors(current_nodes[j]))
                new_nodes.extend(self.graph.G.neighbors(current_nodes[j]))
            current_nodes = new_nodes
            new_nodes = []

        self.neighbors = list(set(self.neighbors))
        self.G = self.graph.G.subgraph(self.neighbors)


class ArisQuery:

    def __init__(self, data, author):
        self.graph = GraphBuild(data)
        self.author = author
        self.weight = 0
        self.shortestPath()


    def shortestPath(self):

        if nx.has_path(self.graph.G, self.author, '256176'):
            self.weight = self.distanceCalcul()
        else: self.weight = -1
            

    def distanceCalcul(self):
        length = {} 
        end = '256176'   

        pq = minpq()
        for node in nx.node_connected_component(self.graph.G, self.author):
            if node == self.author:
                pq[node] = 0
            else:
                pq[node] = float('inf')
                

        for node, min_dist in pq.popitems():
            length[node] = min_dist
            if node == end:
                break

            for neighbor in self.graph.G.neighbors(node):
                if neighbor in pq:
                    new_length = length[node] + self.graph.G[node][neighbor]['weight']
                    if new_length < pq[neighbor]:
                        pq[neighbor] = new_length

        return length[end]


start_time = time.time()
json_data = open("reduced_dblp.json").read()
data = json.loads(json_data)

typeofquery = input("Hi, welcome the DBLP dataset explorer.\n What kind of query do you want to execute ?\n - Write 'conf' for a Conference Query\n - Write 'neighbor' for a Neighbor Query\n - Write 'aris' for an Aris Query\n")

if typeofquery == 'conf':
    q = input("Which conference are you looking for ?")
    n = input("Did you write the id or the name ? (id or name)")
    if n == 'name':
        confquery = ConfQuery(data, q, name = True)
        nx.draw(confquery.G)
        plt.show()
    elif n == 'id':
        confquery = ConfQuery(data, q)
        nx.draw(confquery.G)
        plt.show()

elif typeofquery == 'neighbor':
    q = input("Which author are you looking for ? (the center of your graph)")
    d = int(input("How deep should I search ? (number of edges)"))
    n = input("Did you write the id or the name ? (id or name)")
    if n == 'name':
        neighquery = NeighborQuery(data, q, d, name = True)
        nx.draw(neighquery.G)
        plt.show()
    if n == 'id':
        neighquery = NeighborQuery(data, q, d)
        nx.draw(neighquery.G)
        plt.show()

elif typeofquery == 'aris':
    q = input("Which author are you looking for ? (connected to Aris Anagnostopoulos)(you have to give the id)")
    a = ArisQuery(data, q)
    if a.weight == 0:
        print("You just asked for Aris Anagnostopoulos himself, it does not make sense to me")
    elif a.weight == -1:
        print("Sorry but this author is not connected to Aris Anagnostopoulos at all")
    else:
        print("The distance of their connection is " + str(a.weight))

else: print("This query is not valid.")