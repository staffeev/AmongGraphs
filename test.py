from csv import DictWriter

data = {
    ('A', 'B'): (10, 0),
    ('B', 'C'): (15, 1),
    ('C', 'D'): (1, 1),
    ('D', 'E'): (5, 0),
    ('E', 'F'): (9, 1),
    ('F', 'D'): (24, 0)
}

with open('test_list.csv', 'w', newline='') as f:
    writer = DictWriter(f, delimiter=',',
                        fieldnames=['start', 'end', 'weight', 'is_directed'])
    writer.writeheader()
    for i in data:
        arg = dict()
        arg['start'] = i[0]
        arg['end'] = i[1]
        arg['weight'] = data[i][0]
        arg['is_directed'] = data[i][1]
        writer.writerow(arg)

