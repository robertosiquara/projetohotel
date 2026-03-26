from database.conexao import conectar

try:
    conexao = conectar()
    print("Conexão com o banco realizada com sucesso!")
    conexao.close()
except Exception as e:
    print("Erro ao conectar:", e)