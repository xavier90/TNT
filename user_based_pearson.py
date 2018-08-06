import numpy as np
from scipy.stats import pearsonr
import math


def similarity_user(data, users):
    print "calculate similarity matrix"
    user_similarity_pearson = np.zeros((users, users))
    for user1 in range(users):
        if user1 % 10 == 0: print user1
        for user2 in range(users):
            if np.count_nonzero(data[user1]) and np.count_nonzero(data[user2]):
                try:
                    if not math.isnan(pearsonr(data[user1], data[user2])[0]):
                        user_similarity_pearson[user1][user2] = pearsonr(data[user1], data[user2])[0]
                    else:
                        user_similarity_pearson[user1][user2] = 0
                except:
                    user_similarity_pearson[user1][user2] = 0

    print "similarity matrix done"
    return user_similarity_pearson


def generate_matrix(input_file, users, items):
    print "prepare rating matrix"
    matrix = np.zeros((users, items))

    with open(input_file) as file:
        data = file.readlines()
        for line in data:
            user_id, item_id, rating, timestamp = line.split('\t')
            matrix[int(user_id) - 1][int(item_id) - 1] = float(rating)

    print "rating matrix done"

    return matrix


def main(input_file, output_file, users, items):
    rating_matrix = generate_matrix(input_file, users, items)
    pearson_matrix = similarity_user(rating_matrix, users)

    fw = open(output_file, 'w')
    print "rank matrix start"
    for user_id in range(users):
        if user_id % 10 == 0: print user_id
        user_rank_for_id = []
        idx = 0
        for ele in pearson_matrix[user_id]:
            user_rank_for_id.append([ele, idx + 1])
            idx += 1
        user_rank_for_id = sorted(user_rank_for_id, key=lambda x: x[0], reverse=True)
        user_rank = [e[1] for e in user_rank_for_id]
        fw.write(str(user_rank)[1:-1] + '\n')

    fw.close()
    print "done"


# for movielens dataset, there are 943 users and 1682 items
input_file = "ml-100k/u.data"
output_file = "rank_matrix_pearson.csv"
users = 943
items = 1682
main(input_file, output_file, users, items)
