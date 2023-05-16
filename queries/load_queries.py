from flask import g


def load_queries(file_path):
    with open(file_path, "r") as file:
        queries = file.read()
    return queries

# Cargar consultas desde el archivo
queries = load_queries("queries/sparql_queries.txt")

# Ejecutar una consulta SPARQL utilizando la librería RDFlib
results = g.query(queries)

# Procesar los resultados de la consulta
for row in results:
    # Realizar operaciones con los resultados
    print(row)
