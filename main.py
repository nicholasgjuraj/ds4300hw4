from neo4j import GraphDatabase
import pandas as pd
import numpy as np


def create_track(tx, track):
    tx.run(
        "MERGE (p:Track {track_id: $track.track_id, artists: $track.artists,album_name: $track.album_name,track_name: $track.track_name,popularity: $track.popularity,duration_ms: $track.duration_ms,explicit: $track.explicit,danceability: $track.danceability,energy: $track.energy,key: $track.key,loudness: $track.loudness,mode: $track.mode,speechiness: $track.speechiness,acousticness: $track.acousticness,instrumentalness: $track.instrumentalness,liveness: $track.liveness,valence: $track.valence,tempo: $track.tempo,time_signature: $track.time_signature,track_genre: $track.track_genre})",
        track=track)


def update_relations(tx, start, end):
    tx.run("""
        MATCH (t:Track {track_id: $ST.track_id})
        MERGE (end:Track {track_id: $ET.track_id})
        MERGE (t)-[:SIMILAR]->(end)
        """, ST=start, ET=end
           )


def euclidean(x, y):
    return np.sqrt(sum((x - y) ** 2))


URI = "neo4j://localhost"
AUTH = ("neo4j", "neo4j123")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    df = pd.read_csv('./spotify.csv', index_col=0)
    sampled = df.sample(n=2500)
    sampled = sampled[sampled['artists'] != 'Regina Spektor']
    to_append = df[df['artists'] == 'Regina Spektor']
    sampled = sampled.append(to_append)
    with driver.session(database="neo4j") as session:
        for track in sampled.iterrows():
            session.execute_write(create_track, track[1].to_dict())
        sampled['explicit'].replace({True: 1, False: 0}, inplace=True)
        chosen_fields = ['popularity', 'explicit', 'danceability', 'energy', 'loudness', 'speechiness', 'acousticness',
                         'instrumentalness', 'liveness', 'valence']
        for z in chosen_fields:
            sampled[[z]] = sampled[[z]].apply(lambda x: (x - x.min()) / (x.max() - x.min()))
        for i in range(len(sampled)):
            roe = []
            for j in range(len(sampled)):
                roe.append((euclidean(sampled[chosen_fields].iloc[i], sampled[chosen_fields].iloc[j]), j))
            for sim in sorted(roe)[1:11]:
                session.execute_write(update_relations, start=sampled.iloc[i].to_dict(), end=sampled.iloc[sim[1]].to_dict())
            print(f'{i+1}/{len(sampled)}')
