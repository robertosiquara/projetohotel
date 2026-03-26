from database.conexao import conectar
from mysql.connector import Error

class GerenciadorDeReservas:
    def __init__(self):
        self.conn = conectar()
        if not self.conn:
            raise Exception("Erro ao conectar ao banco de dados.")
        self.cursor = self.conn.cursor(dictionary=True)

    # =========================
    # QUARTOS
    # =========================
    def listar_quartos(self):
        """
        Lista todos os quartos e busca o checkout formatado caso esteja ocupado HOJE.
        """
        try:
            self.cursor.execute("""
                SELECT 
                    q.*, 
                    DATE_FORMAT(r.checkout, '%d/%m/%Y') AS checkout 
                FROM quartos q
                LEFT JOIN reservas r ON q.numero = r.quarto_numero 
                    AND r.status = 'ativa' 
                    AND CURDATE() BETWEEN r.checkin AND r.checkout
            """)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Erro ao listar quartos: {e}")
            return []

    def listar_quartos_disponiveis(self):
        """
        Retorna apenas quartos livres HOJE.
        """
        try:
            self.cursor.execute("""
                SELECT * FROM quartos q
                WHERE NOT EXISTS (
                    SELECT 1 FROM reservas r
                    WHERE r.quarto_numero = q.numero
                    AND r.status = 'ativa'
                    AND r.checkin <= CURDATE()
                    AND r.checkout >= CURDATE()
                )
            """)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Erro ao listar quartos disponíveis: {e}")
            return []

    def verificar_disponibilidade(self, numero_quarto):
        """
        Verifica se o quarto está livre HOJE.
        """
        try:
            self.cursor.execute("""
                SELECT 1 FROM reservas
                WHERE quarto_numero = %s
                AND status = 'ativa'
                AND checkin <= CURDATE()
                AND checkout >= CURDATE()
            """, (numero_quarto,))

            reserva = self.cursor.fetchone()
            return False if reserva else True
        except Error as e:
            print(f"Erro ao verificar disponibilidade: {e}")
            return False

    # =========================
    # RESERVAS
    # =========================
    def criar_reserva(self, cliente_id, numero_quarto, checkin, checkout):
        """
        Cria reserva verificando conflito de datas.
        """
        try:
            # Verifica sobreposição de datas
            self.cursor.execute("""
                SELECT 1 FROM reservas
                WHERE quarto_numero = %s
                AND status = 'ativa'
                AND (checkin <= %s AND checkout >= %s)
            """, (numero_quarto, checkout, checkin))

            conflito = self.cursor.fetchone()

            if conflito:
                print("❌ Quarto já reservado nesse período!")
                return False

            self.cursor.execute("""
                INSERT INTO reservas 
                (cliente_id, quarto_numero, checkin, checkout, status)
                VALUES (%s, %s, %s, %s, 'ativa')
            """, (cliente_id, numero_quarto, checkin, checkout))

            self.conn.commit()
            print("✅ Reserva criada com sucesso!")
            return True
        except Error as e:
            print(f"Erro ao criar reserva: {e}")
            return False

    def cancelar_reserva(self, reserva_id):
        try:
            self.cursor.execute("""
                UPDATE reservas
                SET status = 'cancelada'
                WHERE id = %s
            """, (reserva_id,))
            self.conn.commit()
            print("✅ Reserva cancelada!")
            return True
        except Error as e:
            print(f"Erro ao cancelar reserva: {e}")
            return False

    def listar_reservas(self):
        """
        Lista reservas com datas formatadas em PT-BR e ordenadas pela data de entrada.
        """
        try:
            self.cursor.execute("""
                SELECT 
                    r.id,
                    c.nome AS cliente,
                    q.numero,
                    q.tipo,
                    DATE_FORMAT(r.checkin, '%d/%m/%Y') AS checkin,
                    DATE_FORMAT(r.checkout, '%d/%m/%Y') AS checkout,
                    r.status,
                    CASE
                        WHEN CURDATE() BETWEEN r.checkin AND r.checkout THEN 'Hospedado'
                        WHEN CURDATE() < r.checkin THEN 'Futura'
                        ELSE 'Finalizada'
                    END AS situacao
                FROM reservas r
                JOIN clientes c ON r.cliente_id = c.id
                JOIN quartos q ON r.quarto_numero = q.numero
                ORDER BY r.checkin ASC
            """)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Erro ao listar reservas: {e}")
            return []

    # =========================
    # CLIENTES
    # =========================
    def listar_clientes(self):
        try:
            self.cursor.execute("SELECT * FROM clientes")
            return self.cursor.fetchall()
        except Error as e:
            print(f"Erro ao listar clientes: {e}")
            return []

    def adicionar_cliente(self, nome, telefone, email):
        try:
            self.cursor.execute("""
                INSERT INTO clientes (nome, telefone, email)
                VALUES (%s, %s, %s)
            """, (nome, telefone, email))
            self.conn.commit()
            print("✅ Cliente adicionado!")
            return True
        except Error as e:
            print(f"Erro ao adicionar cliente: {e}")
            return False

    def buscar_datas_ocupadas(self, numero_quarto):
        """
        Retorna as datas ocupadas para bloqueio no calendário.
        """
        try:
            self.cursor.execute("""
                SELECT 
                    DATE_FORMAT(checkin, '%d/%m/%Y') as checkin, 
                    DATE_FORMAT(checkout, '%d/%m/%Y') as checkout
                FROM reservas
                WHERE quarto_numero = %s
                AND status = 'ativa'
            """, (numero_quarto,))
            return self.cursor.fetchall()
        except Error as e:
            print(f"Erro ao buscar datas ocupadas: {e}")
            return []