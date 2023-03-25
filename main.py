from neo4j import GraphDatabase
import pandas as pd
import numpy as np


# creates all nodes in the db, uses all fields from spotify csv.
def create_track(tx, track):
    tx.run(
        "MERGE (p:Track {track_id: $track.track_id, artists: $track.artists,album_name: $track.album_name,track_name: $track.track_name,popularity: $track.popularity,duration_ms: $track.duration_ms,explicit: $track.explicit,danceability: $track.danceability,energy: $track.energy,key: $track.key,loudness: $track.loudness,mode: $track.mode,speechiness: $track.speechiness,acousticness: $track.acousticness,instrumentalness: $track.instrumentalness,liveness: $track.liveness,valence: $track.valence,tempo: $track.tempo,time_signature: $track.time_signature,track_genre: $track.track_genre})",
        track=track)


# creates similarity relationship between two nodes based on unique track_id
def update_relations(tx, start, end):
    tx.run("""
        MATCH (t:Track {track_id: $ST.track_id})
        MERGE (end:Track {track_id: $ET.track_id})
        MERGE (t)-[:SIMILAR]->(end)
        """, ST=start, ET=end
           )


# similarity metric of choice for this assignment
def euclidean(x, y):
    return np.sqrt(sum((x - y) ** 2))


# function to initialize and populate the db
def creation(ses, df):
    # size between 2500~2503, varies based on if sample selected a Regina Spektor track at random.
    sampled = df.sample(n=2500)
    sampled = sampled[sampled['artists'] != 'Regina Spektor']
    to_append = df[df['artists'] == 'Regina Spektor']
    sampled = sampled.append(to_append)
    # insert all sampled tracks into db
    for track in sampled.iterrows():
        ses.execute_write(create_track, track[1].to_dict())
    # data manipulation for euclidean distance
    sampled['explicit'].replace({True: 1, False: 0}, inplace=True)
    chosen_fields = ['popularity', 'explicit', 'danceability', 'energy', 'loudness', 'speechiness', 'acousticness',
                     'instrumentalness', 'liveness', 'valence']
    # min/max normalization
    for z in chosen_fields:
        sampled[[z]] = sampled[[z]].apply(lambda x: (x - x.min()) / (x.max() - x.min()))
    # calculate euclidean distance between all songs in the dataframe.
    for i in range(len(sampled)):
        roe = []
        for j in range(len(sampled)):
            roe.append((euclidean(sampled[chosen_fields].iloc[i], sampled[chosen_fields].iloc[j]), j))
        # create relationships between the top 10 (excluding self) most similar tracks to euclidean distance
        for sim in sorted(roe)[1:11]:
            ses.execute_write(update_relations, start=sampled.iloc[i].to_dict(), end=sampled.iloc[sim[1]].to_dict())
        print(f'{i + 1}/{len(sampled)}')


# returns tracks with a relationship to 1 individual track provided
def individual_track_fetch(tx, track):
    result = tx.run("""
            MATCH (t:Track {track_id: $Z.track_id})
            MATCH (t)-[:SIMILAR]->(ret)
            RETURN ret
            """, Z=track
                    )
    return list(result.data())


# returns similar tracks to selection of tracks provided.
def get_similar(ses, selections):
    # for excluding provided tracks from results
    ids = [x['track_id'] for x in selections]
    # get all related tracks from all tracks in selection
    returns = [item for sl in [ses.execute_write(individual_track_fetch, x) for x in selections] for item in sl]
    # to be used when calculating euclidean distance, already normalized by spotify
    second_filter = ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness',
                     'liveness']
    # average all song metrics in the selections to create an 'average' song.
    average_by_sel = {}
    for x in second_filter:
        average_by_sel[x] = 0
    for x in selections:
        for y in second_filter:
            average_by_sel[y] += x[y] / len(selections)

    scores = []
    keys = []
    for y in returns:
        # prevent duplicates and selected tracks from being included
        if y['ret']['track_id'] not in ids and y['ret']['track_id'] not in keys:
            keys.append(y['ret']['track_id'])
            # euclidean distance between the average song and all returned similar songs
            scores.append((euclidean(pd.Series(list(average_by_sel.values())), pd.Series([y['ret'][t] for t in second_filter])), y['ret']))

    # top 5 songs
    return [x[1] for x in sorted(scores)[:5]]


# uri and login creds
URI = "neo4j://localhost"
AUTH = ("neo4j", "neo4j123")

# connect to db
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    with driver.session(database="neo4j") as session:
        tracks = pd.read_csv('./spotify.csv', index_col=0)
        creation(session, tracks)
        songs = [x[1].to_dict() for x in tracks[tracks['artists'] == 'Regina Spektor'].iterrows()]
        results = get_similar(session, songs)
        for x in results:
            print(x)
