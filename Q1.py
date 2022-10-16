from utilities.operations import Operations
from Input.parameters import Parameters

csv_data = Operations.get_csv_file(Parameters.filename, 3)
graph_nodes = Operations.get_nodes(csv_data)
Operations.add_successors(csv_data, graph_nodes)
Operations.create_start_and_end_nodes(csv_data, graph_nodes)
start_node = graph_nodes['START']
Operations.compute_level(start_node)
Operations.front_pass(graph_nodes)
Operations.back_pass(graph_nodes)
Operations.compute_float(graph_nodes)
print("Project duration is: " + str(graph_nodes['FINISH'].early_finish))
print("The critical path(s) are - ")
Operations.critical_path(start_node, "")
Operations.print_output(graph_nodes)

# print(graph_nodes['A'].successors[0])
