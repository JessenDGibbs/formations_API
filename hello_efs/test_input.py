# Load Data
import networkx as nx

test_input_graph_data = {
    "userData": {
        "userID": "user00000",
        "constraints": {
            "1": {
                "room1": {
                    "min_width": 5,
                    "max_width": 10,
                    "min_area": 30,
                    "max_area": 60,
                    "adj_ref": 1,
                    "type": "bedroom",
                    "label": "master bed"
                },
                "room2": {
                    "min_width": 7,
                    "max_width": 10,
                    "min_area": 40,
                    "max_area": 60,
                    "adj_ref": 2,
                    "type": "bedroom",
                    "label": "second bed"
                },
                "room3": {
                    "min_width": 3,
                    "max_width": 5,
                    "min_area": 10,
                    "max_area": 30,
                    "adj_ref": 3,
                    "type": "bathroom",
                    "label": "primary bath"
                },
                "room4": {
                    "min_width": 5,
                    "max_width": 10,
                    "min_area": 40,
                    "max_area": 100,
                    "adj_ref": 4,
                    "type": "bathroom",
                    "label": "second bath"
                },
                "room5": {
                    "min_width": 6,
                    "max_width": 12,
                    "min_area": 30,
                    "max_area": 70,
                    "adj_ref": 5,
                    "type": "kitchen",
                    "label": "kitchen"
                },
                "room6": {
                    "min_width": 4,
                    "max_width": 8,
                    "min_area": 10,
                    "max_area": 40,
                    "adj_ref": 6,
                    "type": "living-room",
                    "label": "living"
                },
                "room7": {
                    "min_width": 2,
                    "max_width": 5,
                    "min_area": 10,
                    "max_area": 30,
                    "adj_ref": 7,
                    "type": "dining-room",
                    "label": "dining"
                },
                "room8": {
                    "min_width": 4,
                    "max_width": 7,
                    "min_area": 10,
                    "max_area": 40,
                    "adj_ref": 8,
                    "type": "bedroom",
                    "label": "guest bed"
                },
                "adjs": [
                    [
                        1,
                        2
                    ],
                    [
                        1,
                        3
                    ],
                    [
                        1,
                        4
                    ],
                    [
                        2,
                        3
                    ],
                    [
                        2,
                        4
                    ],
                    [
                        3,
                        4
                    ],
                    [
                        3,
                        5
                    ],
                    [
                        5,
                        6
                    ],
                    [
                        6,
                        7
                    ],
                    [
                        6,
                        8
                    ],
                    [
                        7,
                        8
                    ]
                ],
                "land": [
                    [1.3499493,4.394949],
                    [3.5949393,4.6952020]
                ],
                "envelope": [
                    [2.3499493,7.394949],
                    [5.5949393,1.6952020]
                ]
            },
            "2":{}
        }
    }
}
#Define input graph
