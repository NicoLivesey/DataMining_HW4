import json
import pprint
import networkx as nx
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from math import*

# class Paper:

#     def __init__(self, id, title, conf, authors):
#         self.title = title     #data['title']
#         self.id = id           #data['id_publication_int']
#         self.conf = conf       #data['id_conference_int']
#         self.authors = authors #[x[''author_id''] for x in data['authors']]

# class Author:

#     def __init__(self, id, name):
#         self.id = id
#         self.name = name
#         self.papers = []

# class Conference:

#     def __init__(self, id, name):
#         self.id = id
#         self.name = name
#         self.authors = []


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

        authors = pd.DataFrame({'id': author_id, 'name': author_name}).drop_duplicates('id')
        authorpub = pd.DataFrame({'author': authorpub_author, 'publication': authorpub_pub})
        publications = pd.DataFrame({'id': pub_id, 'title': pub_title, 'conference': pub_conf})
        conferences = pd.DataFrame({'id': conf_id, 'name': conf_name}).drop_duplicates()
        collaborations = pd.DataFrame({'author1': collab1, 'author2': collab2})

        collaborations['concat'] = collaborations.apply(lambda row: ''.join(sorted([row['author1'], row['author2']])), axis=1)
        collaborations = collaborations.drop_duplicates('concat')
        collaborations = collaborations.drop(columns='concat')

        return authors, authorpub, publications, conferences, collaborations


class GraphBuild:

    def __init__(self, data):
        self.G = nx.Graph()
        self.db = TableBuild(data)
        self.set = self.getPapersList(self.db)
        self.nodeBuild()
        self.edgeBuild()

    def nodeBuild(self):
        self.G.add_nodes_from(self.db.authors['id'].tolist())

    def edgeBuild(self):
        for index, row in enumerate(self.db.collaborations.values):
            weight = 1 - self.jaccard_similarity(self.set[row[0]], self.set[row[1]])
            self.G.add_edge(row[0], row[1], weight = weight)

    def jaccard_similarity(self, x, y):
        intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
        union_cardinality = len(set.union(*[set(x), set(y)]))
        
        return intersection_cardinality/float(union_cardinality)

    def getPapersList(self, db):
        d = {}
        for index, row in enumerate(db.authors.values):
            d[row[0]] = []
            for index2, row2 in enumerate(db.authorpub[db.authorpub['author'] == row[0]].values):
                d[row[0]].append(row2[1])

        return d





start_time = time.time()
pp = pprint.PrettyPrinter(indent=3)

json_data = open("reduced_dblp.json").read()

data = json.loads(json_data)
print(" %s seconds to load data" % (time.time() - start_time))

graph = GraphBuild(data)

print(" %s seconds to execute full code" % (time.time() - start_time))


# pp.pprint(data[0:3])