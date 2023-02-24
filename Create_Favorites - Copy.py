import numpy as np
import spotipy

client_id='your client_id'
client_secret='your client_secret'   
redirect_url='http://localhost:9000'
'''
#you can get your username this way
scope = "user-library-read"
from spotipy.oauth2 import SpotifyOAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = client_id, client_secret = client_secret, redirect_uri = redirect_url, scope=scope))
sp_user = sp.current_user()
user_name = sp_user['uri'].split(":")[2]
print(user_name)
'''
user_name = 'your user_name'

scope = 'user-library-read'
token = spotipy.util.prompt_for_user_token(user_name,scope = scope,client_id = client_id,client_secret = client_secret,redirect_uri=redirect_url) 
sp = spotipy.Spotify(auth=token)

#get the IDs of currently saved songs = favourites
n = 10000
offsets = np.linspace(0,n,int(n/20)+1)

trackids = []
for offset in offsets:
    results = sp.current_user_saved_tracks(offset=int(offset))
    if not(bool(results['items'])):
        break
    for item in results['items']:
        track = item['track']
        #print(track)
        trackids.append(track['id'])

#create a public playlist to copy the favourites into
playlist_name = 'Lieblingssongs'  

#check if playlist already exists:
limit = 50
exists = False
for osets  in np.linspace(0,10000,int(10000/50)+1):
    results = sp.current_user_playlists(limit=limit,offset=int(osets))
    if len(results) == 0:
        break
    elif len(results)>0:
        for x in range(len(results['items'])):
            if results['items'][x]['name'] == playlist_name:
                playlist_id = results['items'][x]['id']
                exists = True
                break
    elif exists == True:
        break

scope = 'playlist-modify-public'
token = spotipy.util.prompt_for_user_token(user_name,scope = scope,client_id = client_id,client_secret = client_secret,redirect_uri=redirect_url) 
sp = spotipy.Spotify(auth=token)
        
if exists:
    print('update existing playlist')
    #get the existing tracks of the playlist
    ptrackids = []
    for offset in offsets:
        results = sp.user_playlist_tracks(playlist_id = playlist_id,offset=int(offset))
        if not(bool(results['items'])):
            break
        for item in results['items']:
            track = item['track']
            ptrackids.append(track['id'])
    
    #get the tracks that need to be added
    new_tracks = list(set(trackids)-set(ptrackids))
    if len(new_tracks)>0:
        #add the songs to the new playlist
        URIs = ['spotify:track:' + str(sp_id) for sp_id in new_tracks]
        #partition tracks into batches of 100 to add to playlist
        #find highest value between 0 and len(URIs) divisible by 100
        if len(URIs)<=100:
            indices = [0,len(URIs)]
        else:
            if len(URIs)%100 == 0:
                regular = np.linspace(0,len(URIs),int(len(URIs)/100)+1)
                indices = [int(x) for x in regular]
            else:
                h_value = len(URIs) - len(URIs)%100
                regular = np.linspace(0,h_value,int(len(URIs)/100)+1)
                indices = [int(x) for x in regular]
                indices.append(len(URIs))
        
        for i in range(len(indices)-1):
            tracks = URIs[int(indices[i]):int(indices[i+1])]
            sp.playlist_add_items(playlist_id, tracks, position=indices[i])
            print('added',len(tracks),'songs')
    else:
        print('no tracks added')
    #delete tracks that are no longer part of favourite tracks
    delete_tracks = list(set(ptrackids)-set(trackids))
    if len(delete_tracks)>0:
        URIs = ['spotify:track:' + str(sp_id) for sp_id in delete_tracks]
        if len(URIs)<=100:
            indices = [0,len(URIs)]
        else:
            if len(URIs)%100 == 0:
                regular = np.linspace(0,len(URIs),int(len(URIs)/100)+1)
                indices = [int(x) for x in regular]
            else:
                h_value = len(URIs) - len(URIs)%100
                regular = np.linspace(0,h_value,int(len(URIs)/100)+1)
                indices = [int(x) for x in regular]
                indices.append(len(URIs))
        
        for i in range(len(indices)-1):
            tracks = URIs[indices[i]:indices[i+1]]
            sp.user_playlist_remove_all_occurrences_of_tracks(user_name, playlist_id, tracks)
            print('deleted',len(tracks),'songs')

#There exists no playlist with the above definde name playlist_name
else:
    print('new playlist generated')
    #create new playlist
    sp.user_playlist_create(user = user_name, name=playlist_name, public=True)
    
    #get the playlist ID of the newly created playlist
    exists = False
    for osets  in np.linspace(0,10000,int(10000/50)+1):
        results = sp.current_user_playlists(limit=limit,offset=int(osets))
        if len(results) == 0:
            break
        elif len(results)>0:
            for x in range(len(results['items'])):
                if results['items'][x]['name'] == playlist_name:
                    playlist_id = results['items'][x]['id']
                    exists = True
                    break
        elif exists == True:
            break

    #add the songs to the new playlist
    URIs = ['spotify:track:' + str(sp_id) for sp_id in trackids]
    #partition tracks into batches of 100 to add to playlist
    #find highest value between 0 and len(URIs) divisible by 100
    if len(URIs)<=100:
        indices = [0,len(URIs)]
    else:
        if len(URIs)%100 == 0:
            regular = np.linspace(0,len(URIs),int(len(URIs)/100)+1)
            indices = [int(x) for x in regular]
        else:
            h_value = len(URIs) - len(URIs)%100
            regular = np.linspace(0,h_value,int(len(URIs)/100)+1)
            indices = [int(x) for x in regular]
            indices.append(len(URIs))
    
    for i in range(len(indices)-1):
        tracks = URIs[int(indices[i]):int(indices[i+1])]
        sp.playlist_add_items(playlist_id, tracks)
        print('added',len(tracks),'songs')