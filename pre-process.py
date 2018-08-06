input_file = "ml-100k/u.data"
output_file = "ml-100k/u_new.data"

rating_dic = {}
with open(input_file) as file:
    data = file.readlines()
    for line in data:
        user_id, item_id, rating, timestamp = line.split('\t')
        rating_dic.setdefault(user_id, [])
        rating_dic[user_id].append(line)


fw = open(output_file, 'w')
for user_id in range(1, 944):
    for line in rating_dic[str(user_id)]:
        fw.write(line)

fw.close()


