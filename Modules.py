import json
import pprint
import networkx
import pandas as pd
import numpy as np
import time

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
        self.author, self.authorpub, self.publications, self.conferences = self.indexer(data)

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

        for paper in data:
            for author in paper['authors']:
                author_id.append(author['author_id'])
                author_name.append(author['author'])

                authorpub_author.append(author['author_id'])
                authorpub_pub.append(paper['id_publication_int'])
            
            pub_id.append(paper['id_publication_int'])
            pub_title.append(paper['title'])
            pub_conf.append(paper['id_conference_int'])

            conf_id.append(paper['id_conference_int'])
            conf_name.append(paper['id_conference'])

        authors = pd.DataFrame({'id': author_id, 'name': author_name}).drop_duplicates()
        authorpub = pd.DataFrame({'author': authorpub_author, 'publication': authorpub_pub})
        publications = pd.DataFrame({'id': pub_id, 'title': pub_title, 'conference': pub_conf})
        conferences = pd.DataFrame({'id': conf_id, 'name': conf_name}).drop_duplicates()

        return authors, authorpub, publications, conferences


start_time = time.time()
json_data = open("reduced_dblp.json").read()

data = json.loads(json_data)
print(" %s seconds to load data" % (time.time() - start_time))

db = TableBuild(data)
print(" %s seconds to execute full code" % (time.time() - start_time))

# pp = pprint.PrettyPrinter(indent=3)
# pp.pprint(data[0:3])