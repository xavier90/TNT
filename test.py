import math
def success_rate_limit(ref_set, user_set, r, ksi):

    # ref_set should be {user1:p1, user2:p2}
    # user_set should be [user1, user2]
    def helper(ref_set, user_set, r, ksi, res_set, cur_set, start):
        if len(cur_set) == r:
            tmp_p = 1.0

            for user in cur_set:
                tmp_p *= (1 - ref_set[user])

            if tmp_p > ksi:
                return cur_set


        res = []
        for i in range(start, len(user_set)):
            cur_set.append(user_set[i])
            tmp = helper(ref_set, user_set, r, ksi, res_set, cur_set, start+1)
            res = list(set(tmp + res))
            cur_set.pop()

        return res

    return helper(ref_set, user_set, r, ksi, [], [], 0)


ref_set = {'1': 0.5, '2' : 0.7, '3': 0.5, '4':0.6}
user_set = ['1','2','3','4']

# print success_rate_limit(ref_set, user_set, 1, 0.1)


print math.log(10, 2)
