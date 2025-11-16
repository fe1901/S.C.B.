import time
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

conec_data = os.getenv('DATABASE_URL')

with psycopg.connect(conec_data) as conec:
    with conec.cursor() as db:

        def salvar_cadastro_prof(arduino, nome):
            arduino.reset_input_buffer()
            arduino.reset_output_buffer()
            arduino.write("i".encode())
            time.sleep(3)

            while True:
                if arduino.in_waiting > 0:
                    linha = arduino.readline().decode('utf-8').strip()
                    print(f"Recebido do Arduino: '{linha}'")
                    try:
                        idArduino = int(linha)
                        if idArduino:
                            try:
                                db.execute('''INSERT INTO professores (id, nome) VALUES (%s, %s)''', (idArduino, nome))
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

        def salvar_cadastro_aluno(arduino, nome, serie,sala):

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
                                db.execute('''INSERT INTO alunos (id, nome, sala, serie) VALUES (%s, %s, %s, %s)''',
                                               (idArduino, nome, sala, serie))

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


        def salvar_prof(arduino, nome):

            arduino.reset_input_buffer()
            arduino.reset_output_buffer()
            arduino.write("l".encode())
            time.sleep(1)

            arduino.reset_input_buffer()
            arduino.reset_output_buffer()
            salvar_cadastro_prof(arduino, nome)

        def salvar_aluno(arduino, nome, serie, sala):
            arduino.reset_input_buffer()
            arduino.reset_output_buffer()
            arduino.write("l".encode())
            time.sleep(1)

            arduino.reset_input_buffer()
            arduino.reset_output_buffer()
            salvar_cadastro_aluno(arduino, nome, serie, sala)

        def deletar(arduino, id):

            id_valido = int(id)
            arduino.reset_input_buffer()
            arduino.reset_output_buffer()
            try:
                db.execute('DELETE FROM alunos WHERE id = %s', (id_valido,))
                conec.commit()
                if db.rowcount == 0:
                    db.execute('DELETE FROM professores WHERE id = %s', (id_valido,))
                    arduino.write("k".encode())
                    time.sleep(0.2)
                    arduino.write(id.encode())
                    conec.commit()
                    return None
                else:
                    arduino.write("k".encode())
                    time.sleep(0.2)
                    arduino.write(id.encode())
                    return None
            except psycopg.Error as e:
                print(f"Erro ao deletar o id: {e}")
                return None


