import csv
from queue import PriorityQueue
from utilities.Relationships import Relationship
from utilities.Activity import Activity


class Operations:
    @staticmethod
    def get_csv_file(filename, no_of_columns):
        with open(filename) as csvfile:
            tablereader = csv.reader(csvfile, delimiter=',')
            data = list(tablereader)

        temp_data_set = data[::2]
        data_set = temp_data_set[1:]
        for row in range(0, len(data_set)):
            if no_of_columns == 3:
                first_three_columns = data_set[row][:3]
                data_set[row] = first_three_columns
            else:
                first_five_columns = data_set[row][:5]
                data_set[row] = first_five_columns

        return data_set

    @staticmethod
    def get_nodes(csv_data):
        graph_nodes = {}
        for row in csv_data:
            label = row[0]
            duration = row[1]
            activity = Activity(label, int(duration))
            graph_nodes[label] = activity
        return graph_nodes

    @staticmethod
    def add_successors(csv_data, graph_nodes):
        for row in csv_data:
            label = row[0]
            if row[2] != '---':
                predecessors = row[2].split(",")  # ['B', 'C' , etc.,]
                activity = graph_nodes[label]
                for parent_label in predecessors:
                    parent_node = graph_nodes[parent_label]
                    parent_node.successors.append(activity)

    @staticmethod
    def add_successors_with_relationships(csv_data, graph_nodes):
        for row in csv_data:
            label = row[0]
            if row[2] != '---':
                predecessors = row[2].split(",")  # ['B', 'C' , etc.,]
                activity = graph_nodes[label]
                for parent_label in predecessors:
                    parent_node = graph_nodes[parent_label]
                    parent_node.successors.append(Relationship(parent_node, activity, 'FS', 0))

    @staticmethod
    def update_relationships(csv_data, graph_nodes):
        print(csv_data)
        for row in csv_data:
            relationship_string = row[3]
            lag_string = row[4]
            if relationship_string != '':
                lag = int(lag_string) if lag_string != '' else 0
                type = relationship_string[:2]
                from_label = relationship_string[3:4]
                to_label = relationship_string[5:6]
                from_node = graph_nodes[from_label]
                to_node = graph_nodes[to_label]
                found = False
                for successor_relationship in from_node.successors:
                    if successor_relationship.to_node.label == to_label:
                        successor_relationship.r_type = type
                        successor_relationship.lag = lag
                        found = True
                if found == False:
                    from_node.successors.append(Relationship(from_node, to_node, type, lag))

    @staticmethod
    def create_start_and_end_nodes(csv_data, graph_nodes):
        """creating start node"""
        start_node = Activity('START', 0)
        start_node.early_start = 0
        start_node.early_finish = 0
        start_node.level = 1

        """creating end node"""
        end_node = Activity('FINISH', 0)

        """finding successors of start nodes"""
        no_predecessor_node_labels = []
        for row in csv_data:
            label = row[0]
            if row[2] == '---':
                no_predecessor_node_labels.append(label)

        """adding start nodes to successor"""
        for label in no_predecessor_node_labels:
            activity = graph_nodes[label]
            start_node.successors.append(activity)

        """finding finish node's predecessors"""
        for label in graph_nodes.keys():
            activity = graph_nodes[label]
            if len(activity.successors) == 0:
                activity.successors.append(end_node)

        """adding start and end notes to the graph"""
        graph_nodes['START'] = start_node
        graph_nodes['FINISH'] = end_node

    @staticmethod
    def create_start_and_end_nodes_with_relationships(csv_data, graph_nodes):
        start_node = Activity('START', 0)
        start_node.early_start = 0
        start_node.early_finish = 0
        start_node.level = 1
        end_node = Activity('FINISH', 0)
        no_predecessor_node_labels = []
        for row in csv_data:
            label = row[0]
            if row[2] == '---':
                no_predecessor_node_labels.append(label)

        for label in no_predecessor_node_labels:
            activity = graph_nodes[label]
            start_node.successors.append(Relationship(start_node, activity, 'FS', 0))

        for label in graph_nodes.keys():
            activity = graph_nodes[label]
            if len(activity.successors) == 0:
                activity.successors.append(Relationship(activity, end_node, 'FS', 0))

        graph_nodes['START'] = start_node
        graph_nodes['FINISH'] = end_node

    @staticmethod
    def compute_level(current_node):
        """excluding iterations when the current node is FINISH node"""
        if current_node.label == 'FINISH':
            return
        if current_node.level is not None:
            """iteratively updating successor level"""
            for successor in current_node.successors:
                if successor.level is None:
                    successor.level = current_node.level + 1
                else:
                    successor.level = max(successor.level, current_node.level + 1)
                Operations.compute_level(successor)
        return

    @staticmethod
    def compute_level_with_relationships(current_node):
        if current_node.label == 'FINISH':
            return
        if current_node.level is not None:
            for successor_relationship in current_node.successors:
                successor = successor_relationship.to_node
                if successor.level is None:
                    successor.level = current_node.level + 1
                else:
                    successor.level = max(successor.level, current_node.level + 1)
                Operations.compute_level_with_relationships(successor)
        return

    @staticmethod
    def front_pass(graph_nodes):
        """Using priority queue to pop elements with the highest priority"""

        queue = PriorityQueue()
        # add all nodes in graph to queue
        for label in graph_nodes.keys():
            node = graph_nodes[label]
            queue.put((node.level, node.label))

        while queue.qsize() > 0:
            popped = queue.get()
            current_node_label = popped[1]
            current_node = graph_nodes[current_node_label]
            for successor in current_node.successors:
                if successor.early_start is None:
                    successor.early_start = current_node.early_finish
                    successor.early_finish = successor.early_start + successor.duration
                else:
                    new_early_start = current_node.early_finish
                    successor.early_start = max(successor.early_start, new_early_start)
                    successor.early_finish = successor.early_start + successor.duration

    @staticmethod
    def front_pass_with_relationships(graph_nodes):
        queue = PriorityQueue()
        for label in graph_nodes.keys():
            node = graph_nodes[label]
            queue.put((node.level, node.label))

        while queue.qsize() > 0:
            popped = queue.get()
            current_node_label = popped[1]
            current_node = graph_nodes[current_node_label]
            for successor_relationship in current_node.successors:
                type = successor_relationship.r_type
                to_node = successor_relationship.to_node
                lag = successor_relationship.lag
                if type == 'FS':
                    new_early_start = current_node.early_finish + lag
                if type == 'SS':
                    new_early_start = current_node.early_start + lag
                if type == 'FF':
                    new_early_start = current_node.early_finish + lag - to_node.duration
                if type == 'SF':
                    new_early_start = current_node.early_start + lag - to_node.duration
                if to_node.early_start is None:
                    to_node.early_start = new_early_start
                    to_node.early_finish = to_node.early_start + to_node.duration
                else:
                    to_node.early_start = max(to_node.early_start, new_early_start)
                    to_node.early_finish = to_node.early_start + to_node.duration

    @staticmethod
    def back_pass(graph_nodes):
        finish_node = graph_nodes['FINISH']
        finish_node.late_finish = finish_node.early_finish
        finish_node.late_start = finish_node.late_finish - finish_node.duration
        queue = PriorityQueue()
        for label in graph_nodes.keys():
            node = graph_nodes[label]
            queue.put((-node.level, node.label))

        while queue.qsize() > 0:
            popped = queue.get()
            current_node_label = popped[1]
            current_node = graph_nodes[current_node_label]
            for successor in current_node.successors:
                if current_node.late_finish is None:
                    current_node.late_finish = successor.late_start
                    current_node.late_start = current_node.late_finish - current_node.duration
                else:
                    new_late_finish = successor.late_start
                    current_node.late_finish = min(current_node.late_finish, new_late_finish)
                    current_node.late_start = current_node.late_finish - current_node.duration

    @staticmethod
    def back_pass_with_relationships(graph_nodes):
        finish_node = graph_nodes['FINISH']
        finish_node.late_finish = finish_node.early_finish
        finish_node.late_start = finish_node.late_finish - finish_node.duration
        queue = PriorityQueue()
        for label in graph_nodes.keys():
            node = graph_nodes[label]
            queue.put((-node.level, node.label))

        while queue.qsize() > 0:
            popped = queue.get()
            current_node_label = popped[1]
            current_node = graph_nodes[current_node_label]
            for successor_relationship in current_node.successors:
                type = successor_relationship.r_type
                to_node = successor_relationship.to_node
                from_node = successor_relationship.from_node
                lag = successor_relationship.lag
                if type == 'FS':
                    new_late_finish = to_node.late_start - lag
                if type == 'SS':
                    new_late_finish = to_node.late_start - lag + current_node.duration
                if type == 'FF':
                    new_late_finish = to_node.late_finish - lag
                if type == 'SF':
                    new_late_finish = to_node.late_finish - lag + current_node.duration
                if current_node.late_finish is None:
                    current_node.late_finish = new_late_finish
                    current_node.late_start = current_node.late_finish - current_node.duration
                else:
                    current_node.late_finish = min(current_node.late_finish, new_late_finish)
                    current_node.late_start = current_node.late_finish - current_node.duration

    @staticmethod
    def compute_float(graph_nodes):
        for label in graph_nodes.keys():
            current_node = graph_nodes[label]
            current_node.total_float = current_node.late_finish - current_node.early_finish
            for successor in current_node.successors:
                if successor.label == 'FINISH':
                    current_node.free_float = 'NA'
                else:
                    if current_node.free_float is None:
                        current_node.free_float = successor.early_start - current_node.early_finish
                    else:
                        new_free_float = successor.early_start - current_node.early_finish
                        current_node.free_float = min(current_node.free_float, new_free_float)

    @staticmethod
    def compute_float_with_relationships(graph_nodes):
        for label in graph_nodes.keys():
            current_node = graph_nodes[label]
            current_node.total_float = current_node.late_finish - current_node.early_finish
            for successor_relationship in current_node.successors:
                type = successor_relationship.r_type
                to_node = successor_relationship.to_node
                from_node = successor_relationship.from_node
                lag = successor_relationship.lag
                if to_node.label == 'FINISH':
                    current_node.free_float = 'NA'
                else:
                    if type == 'FS':
                        new_free_float = to_node.early_start - lag - current_node.early_finish
                    if type == 'SS':
                        new_free_float = to_node.early_start - lag - current_node.early_start
                    if type == 'FF':
                        new_free_float = to_node.early_finish - lag - current_node.early_finish
                    if type == 'SF':
                        new_free_float = to_node.early_finish - lag - current_node.early_start
                    if current_node.free_float is None:
                        current_node.free_float = new_free_float
                    else:
                        current_node.free_float = min(current_node.free_float, new_free_float)

    @staticmethod
    def print_output(graph_nodes):
        data_format = "{:>15}"
        print(
            data_format.format("Activity") + data_format.format("Duration") + data_format.format(
                "ES") + data_format.format("EF")
            + data_format.format("LS") + data_format.format("LF") + data_format.format("TF") + data_format.format(
                "FF") + data_format.format("Critical Path"))
        for label in graph_nodes.keys():
            if (label != 'START') and label != 'FINISH':
                current_node = graph_nodes[label]
                is_critical_path = 'Yes' if current_node.total_float == 0 else 'No'
                print(data_format.format(current_node.label) + data_format.format(current_node.duration) +
                      data_format.format(current_node.early_start) + data_format.format(current_node.early_finish) +
                      data_format.format(current_node.late_start) + data_format.format(current_node.late_finish) +
                      data_format.format(current_node.total_float) + data_format.format(
                    current_node.free_float) + data_format.format(is_critical_path))

    @staticmethod
    def critical_path(current_node, path_so_far):
        if current_node.label == 'FINISH':
            print(path_so_far[1:])
            return
        if current_node.total_float == 0:
            for successor in current_node.successors:
                new_path = path_so_far + '-' + current_node.label if current_node.label != 'START' else path_so_far
                Operations.critical_path(successor, new_path)
        return

    @staticmethod
    def critical_path_with_relationships(current_node, path_so_far):
        if current_node.label == 'FINISH':
            print(path_so_far[1:])
            return
        if current_node.total_float == 0:
            for successor_relationship in current_node.successors:
                successor = successor_relationship.to_node
                new_path = path_so_far + '-' + current_node.label if current_node.label != 'START' else path_so_far
                Operations.critical_path_with_relationships(successor, new_path)
        return

    @staticmethod
    def print_graph(graph_nodes):
        for label in graph_nodes.keys():
            activity = graph_nodes[label]
            print('Activity name: ' + label + ', Activity values: ' + str(activity))

