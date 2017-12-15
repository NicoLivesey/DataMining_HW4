import json
import pprint
import networkx as nx
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from math import*


class TableBuild:

    def __init__(self, data):
        self.authors, self.authorpub, self.publications, self.conferences, self.collaborations = self.indexer(data)

    def indexer(self, data):
        author_name = []
        author_id = []

        authorpub_author = []
        authorpub_pub = []

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
            
            pub_id.append(str(paper['id_publication_int']))
            pub_title.append(str(paper['title']))
            pub_conf.append(str(paper['id_conference_int']))

            conf_id.append(str(paper['id_conference_int']))
            conf_name.append(str(paper['id_conference']))

        # authors = pd.DataFrame({'id': author_id, 'name': author_name}).drop_duplicates('id')
        # authorpub = pd.DataFrame({'author': authorpub_author, 'publication': authorpub_pub})
        # publications = pd.DataFrame({'id': pub_id, 'title': pub_title, 'conference': pub_conf})
        # conferences = pd.DataFrame({'id': conf_id, 'name': conf_name}).drop_duplicates()
        # collaborations = pd.DataFrame({'author1': collab1, 'author2': collab2})

        # collaborations['concat'] = collaborations.apply(lambda row: ''.join(sorted([row['author1'], row['author2']])), axis=1)
        # collaborations = collaborations.drop_duplicates('concat')
        # collaborations = collaborations.drop(columns='concat')

        authors = self.unique_rows(np.column_stack((author_id, author_name)))
        authorpub = np.column_stack((authorpub_author, authorpub_pub))
        publications = np.column_stack((pub_id, pub_title, pub_conf))
        conferences = self.unique_rows(np.column_stack((conf_id, conf_name)))
        collaborations = self.unique_rows(np.column_stack((collab1, collab2)))

        return authors, authorpub, publications, conferences, collaborations

    def unique_rows(self, a):
        a = np.ascontiguousarray(a)
        unique_a = np.unique(a.view([('', a.dtype)]*a.shape[1]))

        return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))


class GraphBuild:

    def __init__(self, data):
        self.G = nx.Graph()
        self.db = TableBuild(data)
        print(" %s seconds to build db" % (time.time() - start_time))
        self.set = self.getPapersList(self.db)
        print(" %s seconds to index biblio" % (time.time() - start_time))
        self.nodeBuild()
        print(" %s seconds to add nodes" % (time.time() - start_time))
        self.edgeBuild()
        print(" %s seconds to add edges" % (time.time() - start_time))

    def nodeBuild(self):
        self.G.add_nodes_from([item[0] for item in self.db.authors])

    def edgeBuild(self):
        for item in self.db.collaborations:
            weight = 1 - self.jaccard_similarity(self.set[item[0]], self.set[item[1]])
            self.G.add_edge(item[0], item[1], weight = weight)

    def jaccard_similarity(self, x, y):
        intersection = len(set.intersection(*[set(x), set(y)]))
        union = len(set.union(*[set(x), set(y)]))
        
        return intersection/float(union)

    def getPapersList(self, db):
        d = {}

        for row in self.db.authorpub:
            if row[0] in d:
                d[row[0]].append(row[1])
            else:
                d[row[0]] = [row[1]]

        return d


class ConfQuery:
    
    def __init__(self, G, conf):
        self.G = G
        self.conf = conf




start_time = time.time()
pp = pprint.PrettyPrinter(indent=3)

json_data = open("reduced_dblp.json").read()

data = json.loads(json_data)
print(" %s seconds to load data" % (time.time() - start_time))

graph = GraphBuild(data)
print(" %s seconds to execute full code" % (time.time() - start_time))