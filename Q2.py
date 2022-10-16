from utilities.operations import Operations
from Input.parameters import Parameters

csv_data = Operations.get_csv_file(Parameters.filename, 5)
graph_nodes = Operations.get_nodes(csv_data)
Operations.add_successors_with_relationships(csv_data, graph_nodes)
Operations.update_relationships(csv_data, graph_nodes)
Operations.create_start_and_end_nodes_with_relationships(csv_data, graph_nodes)
start_node = graph_nodes['START']
Operations.compute_level_with_relationships(start_node)
Operations.front_pass_with_relationships(graph_nodes)
Operations.back_pass_with_relationships(graph_nodes)
Operations.compute_float_with_relationships(graph_nodes)
print("Project duration is: " + str(graph_nodes['FINISH'].early_finish))
print("The critical path(s) are - ")
Operations.critical_path_with_relationships(start_node, "")
Operations.print_output(graph_nodes)