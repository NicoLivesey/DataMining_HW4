# DataMining_HW4
4th homework of the ADM2017 at Sapienza

A. TableBuild:

First, I wanted to change my JSON documents into relational database tables-like so I tried pandas dataframes but I realized very quickly that these objects are to slow to browse so I builded numpy ndarrays. I created 6 "tables":

- authors (id, name): referencing all the authors
- authorpub(author, publication): referencing all the exisiting connexions between each publication and each author
- authorconf(author, conference): referencing all the exisiting connexions between each conference and each author
- publications(id, title, conference): referencing all the publications with their corresponding conference
- conferences(id, name): referencing all the conferences
- collaboration(author_1, author_2): referencing all the unique collaborations between each author

- indexer(): browse the JSON file to extract informations into list and build numpy ndarrays upon those lists
- uniqueRows(): remove duplicates in the ndarrays by changing them into contiguous arrays in order to store the array in an unbroken block of memory and access the next row faster.

B. GraphBuild:

- nodeBuild(): add all the authors to the graph as nodes with a list comprehension based on the "authors" table
- edgeBuild(): add all the edges one by one based on the "collaborations" table by calculing the weight with the jaccardSimilarity() function
- jaccardSimilarity(): return the intersection divided by the union of two lists builded by the function getPapersList()
- getPapersList(): based on the "authorpub" table, aggregate all the publications by author in a dictionnary in order to get the set of publications for each author


C. ConfQuery:

Here we want to get a subgraph all the authors who have participate to a conference taken as a parameter.

- findAuthors(): check if name or id, based on the "authorconf" table add the authors matching the conference to a list.
- query(): build the subgraph from the list of authors


D. NeighborQuery:

The aim is to build a subgraph from the K-order neighbors of a certain author taken as parameter.

- query(): check if name or id, for an integer parameter d, iterate through each node by appending all its neighbors to a list neighbors and repeat this for all the current level of neighbors. Finally, build the subgraph.

   


