from functools import reduce

import pandas as pd
from django.contrib.auth.models import Permission

from ..models import Dog, User


def jaccard_index(set1, set2):
    set1 = set(set1)
    set2 = set(set2)
    intrsct = float(len(set1.intersection(set2)))
    union = float(len(set1.union(set2)))
    jaccard_index = intrsct / union
    return round(jaccard_index, 3)


def get_top_N_similar(username, preferences, N):
    # user_preference = preferences[username]
    user_preference = preferences[preferences["user_id"] == username].liked_dogs.to_numpy()[0].split(" ")
    # similar = [(jaccard_index(user_preference, preference), other_user) for other_user, preference in
    #            preferences.iteritems() if other_user != username]
    similar = []
    for other_user, preference in preferences.iterrows():
        if preference.user_id != username:
            similar_koef = jaccard_index(user_preference, preference.liked_dogs.split(" "))
            if similar_koef:
                similar.append((similar_koef, preference.user_id))
    similar.sort(reverse=True, key=lambda t: t[0])
    return similar[:N]


def occurs_in(post_id, preferences, users):
    count = 0
    # for user in users:
    #     preference = preferences[preferences["username"] == user].list_of_favs.to_numpy()[0].split(" ")
    #     if post_id in preference:
    #         count += 1
    user_frame = preferences[preferences.user_id.isin(users)]
    occurs = user_frame[user_frame.liked_dogs.str.contains(post_id)]
    return len(occurs.index)


def give_recommendations(username, preferences):
    N = 15  # neigbourhood of the input-user
    # preference = preferences[username]  # set of favourite posts for input-user
    preference = preferences[preferences["user_id"] == username].liked_dogs.to_numpy()[0].split(" ")
    top_similar = get_top_N_similar(username, preferences, N)  # top similar users + their similarity
    similar_users = [user for similarity, user in top_similar]  # only similar usernames
    rank = {}
    for similarity, other_user in top_similar:
        other_preferences = preferences[preferences["user_id"] == other_user].liked_dogs.to_numpy()[0].split(" ")
        for post_id in other_preferences:
            if post_id not in preference:
                rank.setdefault(post_id, 0)
                rank[post_id] += similarity

    recommendations = []
    for post_id, similarity in rank.items():
        occurs = occurs_in(post_id, preferences, similar_users)
        recommendations.append((similarity / occurs, post_id))
    recommendations.sort(reverse=True, key=lambda tuple: tuple[0])
    M = 20  # overall number of recommendations
    # WITH_TITLE = 3  # articles with titles
    recommendation_topM = recommendations[:M]
    recommendation_ids = [int(post_id) for similarity, post_id in recommendation_topM]
    # return (recommendation_topM, recommendation_ids)
    return recommendation_ids


def recommend_dogs(pk):
    user = User.objects.get(pk=pk)
    if user.dog_set.count() == 0:
        return
    perm = Permission.objects.get(codename='like_dog')
    all_user = list(perm.user_set.all())

    df = form_dictionary(all_user)
    result = give_recommendations(pk, df)
    return result


def form_dictionary(users):
    user_ids = []
    liked_dogs = []

    for user in users:
        user_liked_dogs = list(user.dog_set.values('pk').all())
        dog_likes_str = ''
        if len(user_liked_dogs) > 0:
            # dog_likes_str = reduce((lambda x, y: str(x['pk']) + ' ' + str(y['pk'])), user_liked_dogs)
            for i in user_liked_dogs:
                dog_likes_str = dog_likes_str + str(i['pk']) + ' '
            user_ids.append(user.pk)
            liked_dogs.append(dog_likes_str)

    return pd.DataFrame({'user_id' : user_ids, 'liked_dogs': liked_dogs})
# def give_recommendations(username, preferences, weights):
#     # preference = preferences[username]
#     preference = user_preferences[user_preferences["username"] == username].list_of_favs.to_numpy()[0].split(" ")
#     rank = {}
#     for user_other, preference_other in preferences.iterrows():
#         if username != preference_other.username:
#             similarity = jaccard_index(preference, preference_other.list_of_favs.split(" "))
#             if not similarity:
#                 continue
#             for post in preference_other.list_of_favs.split(" "):
#                 if post not in preference:
#                     rank.setdefault(post, 0)
#                     rank[post] += similarity
#     # normalize and convert to
#     post_list = [(similarity / weights[post], post) for post, similarity in rank.items()]
#     post_list.sort(reverse=True)

#
# user_preferences = pd.read_csv("user_favorites.csv")
# user_name = "vostokoved"
#
# give_recommendations(user_name, user_preferences)
