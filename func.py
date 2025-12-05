import time
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

conec_data = os.getenv('DATABASE_URL')

conec = psycopg.connect(conec_data)
db = conec.cursor()



def salvar_cadastro_prof(arduino, nome, login, senha):
            arduino.reset_input_buffer()
            arduino.reset_output_buffer()
            arduino.write("i".encode())
            time.sleep(3)
            estado = "ausente"
            atrasado = "Fora de aula"

            while True:
                if arduino.in_waiting > 0:
                    linha = arduino.readline().decode('utf-8').strip()
                    print(f"Recebido do Arduino: '{linha}'")
                    try:
                        idArduino = int(linha)
                        if idArduino:
                            try:
                                db.execute('''INSERT INTO professores (id, nome, login, senha, estado, atraso) VALUES (%s, %s, %s, %s, %s, %s)''', (idArduino, nome, login, senha, estado, atrasado))
                                print("Cadastro feito com sucesso!")
                                arduino.reset_input_buffer()
                                arduino.reset_output_buffer()
                                arduino.write(b'u')
                                conec.commit()
                                break
                            except psycopg.IntegrityError as e:
                                print(f"Erro de integridade no banco de dados: {e}")
                            except Exception as e:
                                print(f"Erro ao inserir no banco de dados: {e}")

                    except ValueError:
                        print("Leitura inválida do Arduino.")
            time.sleep(0.1)

            return print("cadastro feito!!")

def salvar_cadastro_aluno(arduino, nome, serie,sala, login, senha):

            arduino.reset_input_buffer()
            arduino.reset_output_buffer()
            arduino.write("i".encode())
            time.sleep(0.5)

            estado = "ausente"
            em_sala = "ausente"
            atrasado = "sim"
            horario = "None"

            while True:
                if arduino.in_waiting > 0:
                    linha = arduino.readline().decode('utf-8').strip()
                    print(f"Recebido do Arduino: '{linha}'")
                    try:
                        idArduino = int(linha)
                        if idArduino:
                            try:
                                db.execute('''INSERT INTO alunos (id, nome, sala, serie,login,senha) VALUES (%s, %s, %s, %s,%s,%s)''',
                                               (idArduino, nome, sala, serie,login,senha))

                                db.execute('''INSERT INTO primeira_aula (id, nome, sala, estado, em_sala, atrasado, horario) VALUES (%s,%s,%s,%s,%s,%s,%s)''',
                                           (idArduino, nome, sala, estado, em_sala, atrasado, horario))

                                db.execute('''INSERT INTO segunda_aula (id, nome, sala, estado, em_sala, atrasado, horario) VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                                           (idArduino, nome, sala, estado, em_sala, atrasado, horario))

                                db.execute('''INSERT INTO terceira_aula (id, nome, sala, estado, em_sala, atrasado, horario) VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                                           (idArduino, nome, sala, estado, em_sala, atrasado, horario))

                                conec.commit()
                                print("Cadastro feito com sucesso!")
                                arduino.reset_input_buffer()
                                arduino.reset_output_buffer()
                                arduino.write(b'u')
                                break
                            except psycopg.IntegrityError as e:
                                print(f"Erro de integridade no banco de dados: {e}")
                            except Exception as e:
                                print(f"Erro ao inserir no banco de dados: {e}")
                                break
                    except ValueError:
                        print("Leitura inválida do Arduino.")
            time.sleep(0.1)


def salvar_prof(arduino, nome , login , senha):

            arduino.reset_input_buffer()
            arduino.reset_output_buffer()
            arduino.write("l".encode())
            time.sleep(1)

            arduino.reset_input_buffer()
            arduino.reset_output_buffer()
            salvar_cadastro_prof(arduino, nome, login , senha)

def salvar_aluno(arduino, nome, serie, sala, login, senha):
            arduino.reset_input_buffer()
            arduino.reset_output_buffer()
            arduino.write("l".encode())
            time.sleep(1)

            arduino.reset_input_buffer()
            arduino.reset_output_buffer()
            salvar_cadastro_aluno(arduino, nome, serie, sala, login, senha)

def deletar(arduino, id):
    id_valido = int(id)  # Garante que 'id_valido' é um inteiro
    arduino.reset_input_buffer()
    arduino.reset_output_buffer()

    try:
        db.execute('DELETE FROM alunos WHERE id = %s', (id_valido,))
        conec.commit()

        if db.rowcount == 0:
            db.execute('DELETE FROM professores WHERE id = %s', (id_valido,))
            conec.commit()
            arduino.write("k".encode())
            time.sleep(0.2)
            arduino.write(bytes([id_valido]))

            return None
        elif db.rowcount > 0:
            db.execute('DELETE FROM primeira_aula WHERE id = %s', (id_valido,))
            conec.commit()
            db.execute('DELETE FROM segunda_aula WHERE id = %s', (id_valido,))
            conec.commit()
            db.execute('DELETE FROM terceira_aula WHERE id = %s', (id_valido,))
            conec.commit()
            arduino.write("k".encode())
            time.sleep(0.2)
            arduino.write(bytes([id_valido]))

            return None
        else:
            arduino.write("k".encode())
            time.sleep(0.2)
            arduino.write(bytes([id_valido]))
            return None

    except psycopg.Error as e:
        print(f"Erro ao deletar o id no banco: {e}")
        return None

