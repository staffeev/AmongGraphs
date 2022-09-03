from csv import DictWriter, writer

data_list = {
    ('A', 'B'): (10, 0),
    ('B', 'C'): (15, 1),
    ('C', 'D'): (1, 1),
    ('D', 'E'): (5, 0),
    ('E', 'F'): (9, 1),
    ('F', 'D'): (24, 0)
}

data_matrix = [
    ['', 'A', 'B', 'C', 'D', 'E', 'F'],
    ['A', '', '10.0', '', '', '', ''],
    ['B', '10.0', '', '15.0', '', '', ''],
    ['C', '', '', '', '1.0', '', ''],
    ['D', '', '', '', '', '5.0', '24.0'],
    ['E', '', '', '', '5.0', '', '9.0'],
    ['F', '', '', '', '24.0', '', '']
]

# with open('test_list.csv', 'w', newline='') as f:
#     writer = DictWriter(f, delimiter=',',
#                         fieldnames=['start', 'end', 'weight', 'is_directed'])
#     writer.writeheader()
#     for i in data_list:
#         arg = dict()
#         arg['start'] = i[0]
#         arg['end'] = i[1]
#         arg['weight'] = data_list[i][0]
#         arg['is_directed'] = data_list[i][1]
#         writer.writerow(arg)

# with open('test_matrix.csv', 'w', newline='') as f:
#     wr = writer(f, delimiter=';')
#     wr.writerows(data_matrix)

print(float(10.0))