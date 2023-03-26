# ds4300hw4
# A. How we sampled the data:
We sampled the data by first pulling all 114,000 songs into a Pandas DataFrame. Then, using the DataFrame.sample() function, we took a random sample of 2500 songs. Next, we removed any of the Regina Spektor songs if they were present in our sample, and finally we added all three Regina Spektor songs to our sample. Based on this methodology, anywhere between 2500-2503 songs could be present in our final sample, depending on if any Regina Spektor songs happened to be initially selected. Given that each song has approximately a 2.2% chance of being included in the sample, there is approximately a 93.6% chance that none of the Regina Spektor songs are initially selected, meaning that there is a 93.6% chance of there being 2503 songs in the final sample.

# B. Description of our graph model:
Our graph data model consists of a node for each song included in the sample, and they are represented as a “Track”. The graph data model is thus likely to have 2503 Tracks. Each of these Tracks contains information about their genre, loudness, liveliness, tempo, valence, instrumentalness, danceability, speechiness, mode, explicitness, duration, artists, album name, track id, acousticness, popularity, key, energy, track name, and time signature. We have one potential relationship between nodes called “SIMILAR”. This relationship is added when a Track is sufficiently similar to another Track. Each Track points to the 10 most similar tracks with this “SIMILAR” relationship. Thus, if the graph data model has 2503 nodes, then the model will have 25,030 edges.

# C. Explanation of our recommendation algorithm:
After creating the nodes for each Track in our sample, we then needed to determine the similarity between the Tracks. In order to do this, we first picked the 10 categories that we figured were the most impactful: 'popularity', 'explicit', 'danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', and 'valence'. Next, we min-max normalized the data for each of these variables, setting the minimum value to 0 and the maximum value to 1. Then, we iterated through each track and calculated the euclidean distance between this track and every other track in the database based on the aforementioned variables. This is an O(n2) operation and thus required 6,265,009 computations. After calculating the euclidean distances for each track, we then found the 10 lowest euclidean distances for each track (the 10 most similar tracks) and added a relationship pointing from this track to each of the 10 most similar tracks. This completed our graph model with 2503 nodes and 25030 edges. 

Next, we had to find the 5 best recommended songs for a fan of Regina Spektor. First, we got all of the Tracks that were connected to the nodes representing the Regina Spektor tracks. Next, we picked the variables that we thought are the most crucial: 'danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', and 'liveness'. Then, we computed the average for each category for the Regina Spektor songs. We then iterated through the list of the similar tracks (there could be up to 10x the number of Regina Spektor songs, barring any duplicates), and found the euclidean distance between that and the average of the Regina Spektor song. We took the songs (excluding duplicates) with the 5 lowest euclidean distances, and those were our final 5 recommended songs.
