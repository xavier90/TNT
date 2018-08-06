import math
import random
import sys

def get_rating_item_dic():
    input_file = "ml-100k/u.data"

    rating_dic = {}
    item_dic = {}
    with open(input_file) as file:
        data = file.readlines()
        for line in data:
            user_id, item_id, rating, timestamp = line.strip().split('\t')
            rating_dic.setdefault(user_id, [])
            item_dic.setdefault(item_id, [])
            rating_dic[user_id].append((item_id, rating, timestamp))
            item_dic[item_id].append(user_id)

    return rating_dic, item_dic


def select_user(item_dic, rating_dic, item_j):
    # item_sorted = sorted(item_dic, key=lambda k : len(item_dic[k]), reverse=True)
    user_sorted = sorted(rating_dic, key=lambda k: len(rating_dic[k]), reverse=True)

    # item_top_10 = item_sorted[:10]
    user_set = []


    # select 258 from top 10 items
    for user in user_sorted:
        for t in rating_dic[user]:
            if item_j in t:
                user_set.append(user)
                break

        if len(user_set) == 10:
            break

    return user_set


def poisson_rank(test_set, lmd=5):

    # test_set should be [(user1, rate1), (user2, rate2)]

    def poisson(r, lmd):
        return 1.0 * (pow(math.e,(-1*lmd)) * pow(lmd, r))/math.factorial(r)

    set_sorted = sorted(test_set, key=lambda k: poisson(int(k[1]), lmd), reverse=True)

    user_poisson = {}
    for e in set_sorted:
        user_poisson[e[0]] = poisson(int(e[1]),lmd)

    user_set = [e[0] for e in set_sorted]

    return set_sorted, user_poisson, user_set

def success_rate_limit(ref_set, user_set, num_of_requests, ksi):

    # ref_set should be {user1:p1, user2:p2}
    # user_set should be [user1, user2]

    request_combinations = get_group_candidate(user_set, num_of_requests)

    final_user_set = []
    final_group_list = []
    for group in request_combinations:
        tmp_p = 1.0
        for user in group:
            tmp_p *= (1 - ref_set[user])
        if tmp_p <= ksi:
            final_user_set += group
            final_group_list.append(group)

    return list(set(final_user_set)), final_group_list


def get_random_position(radius, num_of_points, user_set_after_success_rate):
    # generate random position for one base station, one cellular use, n target uses and other users
    # in total will be N users
    # output will be id and position, castration is a circle


    # generate random position list, base, cellular, device
    xy_range = [-1*radius, radius]
    positions = [(0, 0)]

    for i in range(num_of_points-1):
        x = 2 * radius
        y = radius
        while x**2 + y**2 > radius**2:
            x = random.randint(xy_range[0], xy_range[1])
            y = random.randint(xy_range[0], xy_range[1])

        positions.append((x, y))

    # assign position to base, cellular use, target user and other users
    target_users = sorted([int(e) for e in user_set_after_success_rate])
    #base id is 90000, other device id will be 90001, 90002
    base_id = 90000
    device_position_list_target = [(base_id, (0, 0))]
    device_position_list_all = [(base_id, (0, 0))]

    idx = 1
    for user in target_users:
        device_position_list_all.append((user, (positions[idx])))
        device_position_list_target.append((user, (positions[idx])))
        idx += 1

    while idx < len(positions):
        base_id += 1
        device_position_list_all.append((base_id, (positions[idx])))
        idx += 1

    return device_position_list_target, device_position_list_all

def get_distance(p_a, p_b):
    return math.sqrt((p_a[0]-p_b[0])**2 + (p_a[1]-p_b[1])**2)

def get_group_candidate(users, k):
    # return all combination of subset of users, there are k users in each subset

    def helper(users, res_set, cur_set, start, k):
        if len(cur_set) == k:
            res_set.append(list(cur_set))
            return

        for i in range(start, len(users)):
            cur_set.append(users[i])
            helper(users, res_set, cur_set, i+1, k)
            cur_set.pop()

    candidate_set = []
    helper(users, candidate_set, [], 0, k)
    return candidate_set

def group_after_transmission_rate_limit(p_s_c, p_t_d, gamma_g, gamma_h, sigma_2, epsilon, device_position_list, group_candidate, unit_func):
    # use formula on paper to select the group, remove group which cannot meet the limit
    # p_s_c, p_t_d, sigma_2 are constant variables
    # epsilon is the constraint value
    # Gaussian distribution ~ (mu, sigma)
    # h_i_j is cellular user i to device j, calculate by formula in another paper. gamma_g equals Mu

    base_point = device_position_list[0]
    celluar_point = device_position_list[1]

    p_base = base_point[1]
    p_c = celluar_point[1]
    dist_cb = get_distance(p_base, p_c)
    hcb = (1.0/gamma_h) * math.exp(-1.0 * dist_cb/gamma_h) * unit_func

    map_id_to_position = {}
    for e in device_position_list:
        map_id_to_position[e[0]] = e[1]

    final_candidate = []
    for group in group_candidate:

        min_hij = sys.maxsize
        for i in range(len(group)):
            p_i = map_id_to_position[int(group[i])]
            dist = get_distance(p_i, p_c)
            hij = (1.0/gamma_h) * math.exp(-1.0 * dist/gamma_h) * unit_func
            min_hij = min(min_hij, hij)

        tmp = 1 + (p_s_c * hcb)/(p_t_d * min_hij + sigma_2)

        T_c = math.log(tmp, 2)

        if  T_c >= epsilon:
            final_candidate.append(group)

    return final_candidate


def transmission_success_rate(p_j_d, p_i_c, sigma_2, gamma_g, gamma_h, unit_func, group_poisson, device_position_list):
    # in each group
    # for each device, calculate transmission success rate
    # return a list

    # for g_i
    # in each group, sort the user_id by rating value from high to low
    # g_1 means device 1 to 2, g_2 means device 2 to 3, for g_last, use the previous g

    # input will be transmission rate of each device, and possibility calculate by poisson distribution
    # output will be the transmission rate,

    celluar_point = device_position_list[1]
    request_point = device_position_list[2]

    p_c = celluar_point[1]
    p_r = request_point[1]

    map_id_to_position = {}
    for e in device_position_list:
        map_id_to_position[e[0]] = e[1]

    #format of group_poisson is {id1:p1, id2:p2}
    group = sorted(group_poisson.items(), key=lambda x:x[1], reverse=True)
    #format of group is [(id1:p1), (id2:p2)]

    g_j_list = []
    for i in range(len(group)):
        p_i = map_id_to_position[int(group[i][0])]
        dist = get_distance(p_i, p_r)
        g_j = (1.0/gamma_g) * math.exp(-1.0 * dist/gamma_g) * unit_func
        g_j_list.append(g_j)

    # calculate T_d
    T_d = 0
    for i in range(len(group)):

        res_poisson = 1
        for j in range(i-1, -1, -1):
            res_poisson *= (1 - group[j][1])

        p_i = map_id_to_position[int(group[i][0])]
        dist = get_distance(p_i, p_c)
        hij = (1.0/gamma_h) * math.exp(-1.0 * dist/gamma_h) * unit_func

        tmp = 1 + (p_j_d * g_j_list[i])/(p_i_c * hij + sigma_2)
        T_i = math.log(tmp, 2)

        T_d += res_poisson * T_i

    return T_d


def transmission_rank_result(p_j_d, p_i_c, sigma_2, gamma_g, gamma_h, unit_func, user_poisson, group_candidates, device_position_list):
    # sort transmission success rate for each group and return a list

    transmission_rate_dict = {}
    for group in group_candidates:
        group_poisson = {}
        for e in group:
            group_poisson[e] = user_poisson[e]
        success_rate = transmission_success_rate(p_j_d, p_i_c, sigma_2, gamma_g, gamma_h, unit_func, group_poisson, device_position_list)
        transmission_rate_dict[success_rate] = group

    return sorted(transmission_rate_dict.items(), key=lambda x: x[0], reverse=True)


def main():
    print 'This is experiment 3'
    print '**********************'

    ############################################################
    item_j = '258'
    num_of_points = 20
    num_of_requests = 4
    radius = 20
    p_s_c = 1000
    p_t_d = 1
    p_j_d = 1
    p_i_c = 1
    mu = 40
    sigma_2 = 1
    ksi = 0.57
    epsilon = 0.5
    unit_func = 1
    gamma_g = mu
    gamma_h = mu
    ############################################################


    rating_dic, item_dic = get_rating_item_dic()

    user_selected = select_user(item_dic, rating_dic, item_j)


    user_rate_test_set = []

    for user in user_selected:
        for t in rating_dic[user]: #tuple = (item_id, rating, time)
            if t[0] == item_j:
                user_rate_test_set.append((user, t[1]))

    poisson_rank_res, user_poisson, user_set = poisson_rank(user_rate_test_set)
    print 'User id and probability'
    print user_poisson
    print '**********************'



    # generate coordinate for all users, in the list_all, will be base, celluar_user, request_user
    device_position_list_target, device_position_list_all = get_random_position(radius, num_of_points, [poisson_rank_res[0][0]])  # format is (id, (x,y))


    base = device_position_list_all[0]
    target = device_position_list_all[1]
    celluar = device_position_list_all[2]
    request = device_position_list_all[3]

    device_position_list_target = [base, celluar, request, target]

    # we set the user with highest poisson value as the target user, format of target_poisson is {id:p}


    # first put target user into position, then simulate its position change randomly
    target_poisson = {int(poisson_rank_res[0][0]): user_poisson[poisson_rank_res[0][0]]}
    for i in range(num_of_requests-1):
        target_poisson[device_position_list_all[4+i][0]] = user_poisson[poisson_rank_res[0][0]]
        device_position_list_target.append(device_position_list_all[4+i])


    print 'target and its poisson is'
    print target_poisson
    print '**********************'

    # calculate transmission rate
    T_d = transmission_success_rate(p_j_d, p_i_c, sigma_2, gamma_g, gamma_h, unit_func, target_poisson, device_position_list_target)
    print 'transmisson rate is'
    print T_d

if __name__ == '__main__':
    main()