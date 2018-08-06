import math
import random
import sys
import heapq


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

    # assign position to base, cellular use, request user and others
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


def get_closest_points(position_list, num_of_request):
    base_point = position_list[0]
    celluar_user = position_list[1]
    request_user = position_list[2]

    p_r = request_user[1]
    others = position_list[3:]

    map_id_to_position = {}
    for e in others:
        map_id_to_position[e[0]] = e[1]

    neighbors = []
    for e in others:
        dist = get_distance(e[1], p_r)
        heapq.heappush(neighbors, (dist, e[0]))


    closest_neighbors = heapq.nsmallest(num_of_request, neighbors)
    closest_neighbors = [(e[1], map_id_to_position[e[1]]) for e in closest_neighbors]

    return closest_neighbors



def main():
    print 'This is experiment 2'
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


    # get random position of points recommended from social layer(device_position_list_target) and all points
    device_position_list_target, device_position_list_all = get_random_position(radius, num_of_points, [])  # format is (id, (x,y))
    # print 'Generate position for all points'
    # print device_position_list_all

    # find n closest neighbors for request user
    top_n_closest_points = get_closest_points(device_position_list_all, num_of_requests)
    print 'Closest users are '
    print top_n_closest_points
    print '**********************'

    # calculate the transmission rate for those neighbors
    final_group = device_position_list_all[:3] + top_n_closest_points
    group_poisson = {}
    for e in top_n_closest_points:
        group_poisson[e[0]] = 1.0/num_of_requests

    T_d = transmission_success_rate(p_j_d, p_i_c, sigma_2, gamma_g, gamma_h, unit_func, group_poisson, final_group)
    print 'transmission rate is'
    print T_d


if __name__ == '__main__':
    main()
