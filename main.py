from datetime import datetime, time
import customtkinter as ctk
import serial as sr
from serial.serialutil import SerialException
import os
import psycopg
from dotenv import load_dotenv

import func as fn

load_dotenv()

conec_data = os.getenv('DATABASE_URL')

conec = psycopg.connect(conec_data)
db = conec.cursor()

class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        def erro_mensagem(mensagem):
            self.erro = ctk.CTkToplevel(self)
            self.erro.geometry("300x300")
            self.erro.title("Erro")
            self.erro.configure(fg_color="#A1CDF4")
            self.erro.resizable(False, False)

            self.msg_erro = ctk.CTkLabel(self.erro, font=("Arial", 18), text_color="#000000",
                                         text=f"Erro, {mensagem}")
            self.destroy_erro = ctk.CTkButton(self.erro, text="Fechar", command=self.erro.destroy, width=300,
                                              height=50, fg_color="#4e0da0", border_width=2,
                                              border_color="#000000")

            self.msg_erro.pack(side="top", padx=30, pady=30)
            self.destroy_erro.pack(side="bottom", padx=30, pady=30)
            return None

        def sincronizar():

            def registrar():

                tempo_2 = datetime.now().time()

                inicio_1 = time(7, 30)
                atraso = time(7, 45)
                fim_1 = time(9, 10)
                fim_2 = time(11, 5)
                fim_3 = time(12, 45)

                if not inicio_1 <= tempo_2 <= fim_3:
                    arduino.write(b'n')
                    arduino.flush()

                if inicio_1 <= tempo_2 <= fim_3:
                    arduino.write(b'p')
                    arduino.flush()

                if arduino.in_waiting > 0:
                    linha = arduino.readline().decode('utf-8').strip()
                    if linha == "Did not find fingerprint sensor :(":
                       erro_mensagem("o sensor não está funcinando")
                       return
                    try:
                        id_arduino = int(linha)
                        tempo = datetime.now()
                        tempo = tempo.strftime('%Y-%m-%d %H:%M')


                        if id_arduino:
                            try:
                                presenca_1 =db.execute('''SELECT estado FROM primeira_aula WHERE id = %s''', (id_arduino,))
                                presenca_aula_1 = presenca_1.fetchone()

                                em_sala_1 = db.execute('''SELECT em_sala FROM primeira_aula WHERE id = %s''', (id_arduino,))
                                em_sala_aula_1 = em_sala_1.fetchone()

                                presenca_2 = db.execute('''SELECT estado FROM segunda_aula WHERE id = %s''', (id_arduino,))
                                presenca_aula_2 = presenca_2.fetchone()

                                em_sala_2 = db.execute('''SELECT em_sala FROM segunda_aula WHERE id = %s''', (id_arduino,))
                                em_sala_aula_2 = em_sala_2.fetchone()

                                presenca_3 = db.execute('''SELECT estado FROM terceira_aula WHERE id = %s''', (id_arduino,))
                                presenca_aula_3 = presenca_3.fetchone()

                                em_sala_3 = db.execute('''SELECT em_sala FROM terceira_aula WHERE id = %s''', (id_arduino,))
                                em_sala_aula_3 = em_sala_3.fetchone()

                                conec.commit()

                                db.execute('SELECT nome FROM alunos WHERE id= %s', (id_arduino,))
                                result = db.fetchone()

                                if result[0]:
                                    nome = result[0]
                                    db.execute('''INSERT INTO registros (id, nome, horario) VALUES (%s,%s,%s)''',
                                               (id_arduino, nome, tempo))
                                    conec.commit()
                                    if inicio_1 <= tempo_2 <= fim_3:
                                        if result[0] and presenca_aula_1[0] == "ausente" and presenca_aula_2[0] == "ausente" and presenca_aula_3[0] == "ausente":
                                            if inicio_1 <= tempo_2 <= fim_1:
                                                if inicio_1 <= tempo_2 <= atraso:
                                                    db.execute('''UPDATE primeira_aula SET estado = %s, em_sala = %s,atrasado = %s, horario = %s WHERE id = %s''',
                                                               ("Presente", "Presente","Não", tempo, id_arduino))
                                                else:
                                                    db.execute('''UPDATE primeira_aula SET estado   = %s,em_sala  = %s,atrasado = %s,horario  = %s WHERE id = %s''',
                                                               ("Presente", "Presente", "Sim", tempo, id_arduino))

                                                db.execute('''UPDATE segunda_aula SET estado   = %s,em_sala  = %s,atrasado = %s,horario  = %s WHERE id = %s''',
                                                           ("Presente", "Presente", "Sim", tempo, id_arduino))

                                                db.execute('''UPDATE terceira_aula SET estado   = %s,em_sala  = %s,atrasado = %s,horario  = %s WHERE id = %s''',
                                                           ("Presente", "Presente", "Sim", tempo, id_arduino))

                                                conec.commit()
                                            elif fim_1 <= tempo_2 <= fim_2:
                                                db.execute('''UPDATE segunda_aula SET estado   = %s,em_sala  = %s,atrasado = %s,horario  = %s WHERE id = %s''',
                                                           ("Presente", "Presente", "Sim", tempo, id_arduino))

                                                db.execute('''UPDATE terceira_aula SET estado   = %s,em_sala  = %s,atrasado = %s,horario  = %s WHERE id = %s''',
                                                           ("Presente", "Presente", "Sim", tempo, id_arduino))

                                                conec.commit()
                                            elif fim_2 <= tempo_2 <= fim_3:
                                                db.execute('''UPDATE terceira_aula SET estado   = %s,em_sala  = %s,atrasado = %s,horario  = %s WHERE id = %s''',
                                                    ("Presente", "Presente", "Sim", tempo, id_arduino))

                                                conec.commit()
                                        elif result[0] and presenca_aula_1[0] == "Presente" and em_sala_aula_1[0] == "Presente":
                                            db.execute('''UPDATE primeira_aula SET em_sala  = %s WHERE id = %s''',
                                                       ("ausente", id_arduino))
                                            conec.commit()
                                        elif result[0] and presenca_aula_1[0] == "Presente" and em_sala_aula_1[0] == "ausente":
                                            db.execute('''UPDATE primeira_aula SET em_sala  = %s WHERE id = %s''',
                                                       ("Presente", id_arduino))
                                            conec.commit()
                                        elif result[0] and presenca_aula_2[0] == "Presente" and em_sala_aula_2[0] == "Presente":
                                            db.execute('''UPDATE segunda_aula SET em_sala  = %s WHERE id = %s''',
                                                       ("ausente", id_arduino))
                                            conec.commit()
                                        elif result[0] and presenca_aula_2[0] == "Presente" and em_sala_aula_2[0] == "ausente":
                                            db.execute('''UPDATE segunda_aula SET em_sala  = %s WHERE id = %s''',
                                                       ("Presente", id_arduino))
                                            conec.commit()
                                        elif result[0] and presenca_aula_3[0] == "Presente" and em_sala_aula_3[0] == "Presente":
                                            db.execute('''UPDATE terceira_aula SET em_sala  = %s WHERE id = %s''',
                                                       ("ausente", id_arduino))
                                            conec.commit()
                                        elif result[0] and presenca_aula_3[0] == "Presente" and em_sala_aula_3[0] == "ausente":
                                            db.execute('''UPDATE terceira_aula SET em_sala  = %s WHERE id = %s''',
                                                       ("Presente", id_arduino))
                                            conec.commit()
                                    else:
                                        print("Fora do horario de aula")

                                else:
                                    db.execute('SELECT nome FROM professores WHERE id = %s', (id_arduino,))
                                    result = db.fetchone()
                                    if result is None:
                                        print("ID not found in alunos or professores")
                                    else:
                                        nome = result[0]
                                        db.execute('INSERT INTO registros_profs (id, nome, horario) VALUES (%s, %s, %s)',
                                                   (id_arduino, nome, tempo))
                                        conec.commit()
                                        print("mandou")

                            except psycopg.IntegrityError as e:
                                print(f"Erro de integridade no banco de dados: {e}")
                            except Exception as e:
                                print(f"Erro ao inserir no banco de dados: {e}")

                    except Exception:
                        print(f"erro, por ser uma string")

                self.after(1000, registrar)
            try:
                arduino = sr.Serial('/dev/ttyUSB0', 9600, timeout=2)
                if arduino:
                    self.sincronia.configure(fg_color="#188c2e")
                    self.arduino_sincronia.configure(text="On")
                    registrar()
                    return arduino

            except SerialException:
                erro_mensagem("na conexão do arduino")

        def salvar_cadastro():

            def enviar(arduino, tipo):

                if tipo == "professor":
                    nome = self.entry_nome_prof.get()
                    fn.salvar_prof(arduino, nome)
                    self.form.destroy()
                elif tipo == "aluno":
                    nome = self.entry_nome_aluno.get()
                    serie = self.entry_serie_aluno.get()
                    sala = self.entry_sala_aluno.get()
                    fn.salvar_aluno(arduino, nome, serie, sala)
                    self.form.destroy()

            arduino = sincronizar()
            if not arduino:
                return None
            self.verificacao_prof = ctk.CTkInputDialog(fg_color="#02135A", title="Verificacao", text="Salvar Professor")
            verificacao = self.verificacao_prof.get_input()
            if verificacao == "sim" or verificacao == "s":
                self.form = ctk.CTkToplevel(self)
                self.form.geometry("300x300")
                self.form.title("Formulario")
                self.form.configure(fg_color="#A1CDF4")
                self.form.columnconfigure(1, weight=1)
                self.form.rowconfigure(5, weight=1)
                self.form.resizable(False, False)

                self.label_nome_prof = ctk.CTkLabel(self.form, font=("Arial", 20), text_color="#000000", text="Coloque o nome:")
                self.entry_nome_prof = ctk.CTkEntry(self.form, font=("Arial", 15), text_color="#ffffff",width= 180, height= 30)
                self.enviar = ctk.CTkButton(self.form, width=200, height=30, text="Enviar", fg_color="#4e0da0",text_color="#ffffff", border_width=2, border_color="#000000", command=lambda: enviar(arduino, "professor"))
                self.enviar.grid(row=5, column=1, padx=30, pady=30)

                self.label_nome_prof.grid(row=2, column=1, padx=30, pady=30)
                self.entry_nome_prof.grid(row=4, column=1, padx=30, pady=30)


                return None
            elif verificacao != "sim" or  verificacao != "s":
                self.form = ctk.CTkToplevel(self)
                self.form.geometry("500x700")
                self.form.title("Formulario")
                self.form.configure(fg_color="#A1CDF4")
                self.form.columnconfigure(1, weight=1)
                self.form.rowconfigure(8, weight=1)
                self.form.resizable(False, False)

                self.label_nome_aluno = ctk.CTkLabel(self.form, font=("Arial", 20), text_color="#000000",text="Coloque o nome:")
                self.entry_nome_aluno = ctk.CTkEntry(self.form, font=("Arial", 15), text_color="#ffffff", width=180, height=30)

                self.label_serie_aluno = ctk.CTkLabel(self.form, font=("Arial", 20), text_color="#000000",text="Coloque a serie:")
                self.entry_serie_aluno = ctk.CTkEntry(self.form, font=("Arial", 15), text_color="#ffffff", width=180,height=30)

                self.label_sala_aluno = ctk.CTkLabel(self.form, font=("Arial", 20), text_color="#000000",text="Coloque a sala:")
                self.entry_sala_aluno = ctk.CTkEntry(self.form, font=("Arial", 15), text_color="#ffffff", width=180,height=30)

                self.enviar_aluno = ctk.CTkButton(self.form, width=200, height=30, text="Enviar", fg_color="#4e0da0",text_color="#ffffff", border_width=2, border_color="#000000", command=lambda: enviar(arduino, "aluno"))
                self.enviar_aluno.grid(row=8, column=1, padx=30, pady=30)

                self.label_nome_aluno.grid(row=1, column=1, padx=30, pady=30)
                self.entry_nome_aluno.grid(row=2, column=1, padx=30, pady=30)
                self.label_serie_aluno.grid(row=3, column=1, padx=30, pady=30)
                self.entry_serie_aluno.grid(row=4, column=1, padx=30, pady=30)
                self.label_sala_aluno.grid(row=5, column=1, padx=30, pady=30)
                self.entry_sala_aluno.grid(row=6, column=1, padx=30, pady=30)

                return None
            else:
                erro_mensagem("na verificacao")

        def deletar():
            arduino = sincronizar()
            if not arduino:
                return None
            else:
                self.pegar_id = ctk.CTkInputDialog(fg_color="#02135A", title="Pegar id", text="Qual id quer apagar")
                id = self.pegar_id.get_input()
                fn.deletar(arduino, id)
                return None

        def visualizar_aluno():

            self.tabela = ctk.CTkToplevel(self)
            self.tabela.geometry("1200x600")
            self.tabela.title("Tabela: Alunos")
            self.tabela.configure(fg_color="#A1CDF4")
            self.tabela.columnconfigure(0, weight=1)
            self.tabela.rowconfigure(1, weight=1)
            self.tabela.resizable(False, False)

            self.tabela_aluno = ctk.CTkTextbox(self.tabela, width=1100, height=420, font=("Arial", 30), text_color="#000000", fg_color="#B5B5B5", border_width=3, border_color="#000000")

            self.destroy_tabela = ctk.CTkButton(self.tabela, width=350, height=60, text="Voltar", fg_color="#4e0da0", border_width=3, border_color="#000000", command=self.tabela.destroy)

            db.execute('SELECT * FROM alunos')
            valores_alunos = db.fetchall()

            self.tabela_aluno.configure(state="normal")
            texto_formatado = ""
            for aluno in valores_alunos:
                linha = "         |   ".join(str(campo) for campo in aluno) + "\n"
                texto_formatado += linha
            self.tabela_aluno.insert("end", texto_formatado)
            self.tabela_aluno.configure(state="disabled")

            self.tabela_aluno.grid(row=1, column=0, padx=30, pady=30)

            self.destroy_tabela.grid(row=3, column=0, padx=30, pady=30)

            return None

        def visualizar_prof():

            self.tabela = ctk.CTkToplevel(self)
            self.tabela.geometry("1200x600")
            self.tabela.title("Tabela: Professores")
            self.tabela.configure(fg_color="#A1CDF4")
            self.tabela.columnconfigure(0, weight=1)
            self.tabela.rowconfigure(1, weight=1)
            self.tabela.resizable(False, False)

            self.tabela_prof = ctk.CTkTextbox(self.tabela, width=1100, height=420, font=("Arial", 30),text_color="#000000", fg_color="#B5B5B5", border_width=3,border_color="#000000")

            self.destroy_tabela = ctk.CTkButton(self.tabela, width=350, height=60, text="Voltar", fg_color="#4e0da0",border_width=3, border_color="#000000", command=self.tabela.destroy)

            db.execute('SELECT * FROM professores')
            valores_profs = db.fetchall()

            self.tabela_prof.configure(state="normal")
            texto_formatado = ""
            for aluno in valores_profs:
                linha = "         |   ".join(str(campo) for campo in aluno) + "\n"
                texto_formatado += linha
            self.tabela_prof.insert("end", texto_formatado)
            self.tabela_prof.configure(state="disabled")

            self.tabela_prof.grid(row=1, column=0, padx=30, pady=30)

            self.destroy_tabela.grid(row=3, column=0, padx=30, pady=30)

            return None

        def visualizar_presenca():
            self.tabela = ctk.CTkToplevel(self)
            self.tabela.geometry("1200x600")
            self.tabela.title("Tabela: Registros")
            self.tabela.configure(fg_color="#A1CDF4")
            self.tabela.columnconfigure(0, weight=1)
            self.tabela.rowconfigure(1, weight=1)
            self.tabela.resizable(False, False)

            self.tabela_registro = ctk.CTkTextbox(self.tabela, width=1100, height=420, font=("Arial", 30),
                                              text_color="#000000", fg_color="#B5B5B5", border_width=3,
                                              border_color="#000000")

            self.destroy_tabela = ctk.CTkButton(self.tabela, width=350, height=60, text="Voltar", fg_color="#4e0da0",
                                                border_width=3, border_color="#000000", command=self.tabela.destroy)

            db.execute('SELECT * FROM registros_alunos')
            valores_registro = db.fetchall()

            self.tabela_registro.configure(state="normal")
            texto_formatado = ""
            for aluno in valores_registro:
                linha = "         |   ".join(str(campo) for campo in aluno) + "\n"
                texto_formatado += linha
            self.tabela_registro.insert("end", texto_formatado)
            self.tabela_registro.configure(state="disabled")

            self.tabela_registro.grid(row=1, column=0, padx=30, pady=30)

            self.destroy_tabela.grid(row=3, column=0, padx=30, pady=30)

            return None

        def visualizar_presenca_profs():
            self.tabela = ctk.CTkToplevel(self)
            self.tabela.geometry("1200x600")
            self.tabela.title("Tabela: Registros")
            self.tabela.configure(fg_color="#A1CDF4")
            self.tabela.columnconfigure(0, weight=1)
            self.tabela.rowconfigure(1, weight=1)
            self.tabela.resizable(False, False)

            self.tabela_registro = ctk.CTkTextbox(self.tabela, width=1100, height=420, font=("Arial", 30),
                                                  text_color="#000000", fg_color="#B5B5B5", border_width=3,
                                                  border_color="#000000")

            self.destroy_tabela = ctk.CTkButton(self.tabela, width=350, height=60, text="Voltar", fg_color="#4e0da0",
                                                border_width=3, border_color="#000000", command=self.tabela.destroy)

            db.execute('SELECT * FROM registros_professores')
            valores_registro = db.fetchall()

            self.tabela_registro.configure(state="normal")
            texto_formatado = ""
            for aluno in valores_registro:
                linha = "         |   ".join(str(campo) for campo in aluno) + "\n"
                texto_formatado += linha
            self.tabela_registro.insert("end", texto_formatado)
            self.tabela_registro.configure(state="disabled")

            self.tabela_registro.grid(row=1, column=0, padx=30, pady=30)

            self.destroy_tabela.grid(row=3, column=0, padx=30, pady=30)

            return None

        def atualizar():

            def form_att(tipo):

                def salvar_aluno(id):

                    nome = self.entry_nome_aluno_att.get()
                    serie = self.entry_serie_aluno_att.get()
                    sala = self.entry_sala_aluno_att.get()
                    self.att_form.destroy()

                    if nome == "":
                        erro_mensagem("coloque um nome")

                    elif serie == "":
                        erro_mensagem(" coloque uma serie")

                    elif sala == "":
                       erro_mensagem("coloque uma sala")
                    else:
                        try:
                            db.execute('''UPDATE alunos SET nome = %s, serie = %s, sala = %s WHERE id = %s''', (nome, serie, sala, id))
                            conec.commit()

                            self.msg_confir = ctk.CTkToplevel(self)
                            self.msg_confir.geometry("300x300")
                            self.msg_confir.title("Confirmação")
                            self.msg_confir.configure(fg_color="#A1CDF4")
                            self.msg_confir.resizable(False, False)

                            self.msg = ctk.CTkLabel(self.msg_confir, font=("Arial", 17), text_color="#000000",text="Edição foi um sucesso")
                            self.destroy = ctk.CTkButton(self.msg_confir, text="Fechar",command=self.msg_confir.destroy, width=300, height=50,fg_color="#4e0da0", border_width=2, border_color="#000000")

                            self.msg.pack(side="top", padx=30, pady=30)
                            self.destroy.pack(side="bottom", padx=30, pady=30)
                            self.tabview_tabelas.destroy()
                            atualizar()
                            return None
                        except psycopg.Error:
                            erro_mensagem("houve algo na atualização")

                def salvar_prof(id):

                    nome = self.entry_nome_prof_att.get()
                    self.att_form.destroy()

                    if nome == "":
                        erro_mensagem("coloque um nome")

                    else:

                        try:
                            db.execute('''UPDATE professores SET nome = %s WHERE id = %s''', (nome, id))
                            conec.commit()

                            self.msg_confir = ctk.CTkToplevel(self)
                            self.msg_confir.geometry("300x300")
                            self.msg_confir.title("Confirmação")
                            self.msg_confir.configure(fg_color="#A1CDF4")
                            self.msg_confir.resizable(False, False)

                            self.msg = ctk.CTkLabel(self.msg_confir, font=("Arial", 17), text_color="#000000",
                                                    text="Edição foi um sucesso")
                            self.destroy = ctk.CTkButton(self.msg_confir, text="Fechar",
                                                         command=self.msg_confir.destroy, width=300, height=50,
                                                         fg_color="#4e0da0", border_width=2, border_color="#000000")

                            self.msg.pack(side="top", padx=30, pady=30)
                            self.destroy.pack(side="bottom", padx=30, pady=30)
                            self.tabview_tabelas.destroy()
                            atualizar()
                            return None
                        except psycopg.Error:
                            erro_mensagem("houve algo na atualização")


                if tipo == "professor":
                    self.verificacao_prof_id = ctk.CTkInputDialog(fg_color="#02135A", title="Verificacao",text="Id para atualização")
                    id = int(self.verificacao_prof_id.get_input())

                    if not id:
                        return None

                    try:
                        db.execute('SELECT nome FROM professores WHERE id = %s', (id,))

                        verificao_tabela = db.fetchone()

                        if verificao_tabela is None:
                           erro_mensagem("id não está na tabela")
                           return None
                        else:
                            pass
                    except psycopg.Error as e:
                        print(f"Erro ao achar o id: {e}")
                        return None


                    self.att_form = ctk.CTkToplevel(self)
                    self.att_form.geometry("500x400")
                    self.att_form.title("Atualização")
                    self.att_form.configure(fg_color="#A1CDF4")
                    self.att_form.columnconfigure(1, weight=1)
                    self.att_form.rowconfigure(5, weight=1)
                    self.att_form.resizable(False, False)

                    self.label_nome_prof_att = ctk.CTkLabel(self.att_form, font=("Arial", 20), text_color="#000000",text="Coloque o nome:")
                    self.entry_nome_prof_att = ctk.CTkEntry(self.att_form, font=("Arial", 15), text_color="#ffffff", width=180,height=30)

                    self.label_nome_prof_att.grid(row=2, column=1, padx=30, pady=30)
                    self.entry_nome_prof_att.grid(row=4, column=1, padx=30, pady=30)

                    self.enviar_att = ctk.CTkButton(self.att_form, width=200, height=30, text="Enviar", fg_color="#4e0da0",text_color="#ffffff", border_width=2, border_color="#000000",command=lambda: salvar_prof( id))
                    self.enviar_att.grid(row=5, column=1, padx=30, pady=30)



                elif tipo == "aluno":
                    self.verificacao_prof_id = ctk.CTkInputDialog(fg_color="#02135A", title="Verificacao",text="Id para atualização")
                    id = int(self.verificacao_prof_id.get_input())
                    try:
                        db.execute('SELECT nome FROM alunos WHERE id = %s', (id,))
                        verificao_tabela = db.fetchone()
                        if verificao_tabela is None:
                            erro_mensagem("id não está na tabela")
                            return None
                        else:
                            pass
                    except psycopg.Error as e:
                        print(f"Erro ao achar o id: {e}")
                        return None
                    self.att_form = ctk.CTkToplevel(self)
                    self.att_form.geometry("500x700")
                    self.att_form.title("Atualização")
                    self.att_form.configure(fg_color="#A1CDF4")
                    self.att_form.columnconfigure(1, weight=1)
                    self.att_form.rowconfigure(7, weight=1)
                    self.att_form.resizable(False, False)

                    self.label_nome_aluno_att = ctk.CTkLabel(self.att_form, font=("Arial", 20), text_color="#000000",text="Coloque o nome:")
                    self.entry_nome_aluno_att = ctk.CTkEntry(self.att_form, font=("Arial", 15), text_color="#ffffff", width=180,height=30)

                    self.label_serie_aluno_att = ctk.CTkLabel(self.att_form, font=("Arial", 20), text_color="#000000",text="Coloque a serie:")
                    self.entry_serie_aluno_att = ctk.CTkEntry(self.att_form, font=("Arial", 15), text_color="#ffffff",width=180, height=30)

                    self.label_sala_aluno_att = ctk.CTkLabel(self.att_form, font=("Arial", 20), text_color="#000000",text="Coloque a sala:")
                    self.entry_sala_aluno_att = ctk.CTkEntry(self.att_form, font=("Arial", 15), text_color="#ffffff", width=180,height=30)

                    self.enviar_aluno_att = ctk.CTkButton(self.att_form, width=200, height=30, text="Enviar",fg_color="#4e0da0", text_color="#ffffff", border_width=2,  border_color="#000000", command=lambda : salvar_aluno(id))
                    self.enviar_aluno_att.grid(row=8, column=1, padx=30, pady=30)

                    self.label_nome_aluno_att.grid(row=1, column=1, padx=30, pady=30)
                    self.entry_nome_aluno_att.grid(row=2, column=1, padx=30, pady=30)
                    self.label_serie_aluno_att.grid(row=3, column=1, padx=30, pady=30)
                    self.entry_serie_aluno_att.grid(row=4, column=1, padx=30, pady=30)
                    self.label_sala_aluno_att.grid(row=5, column=1, padx=30, pady=30)
                    self.entry_sala_aluno_att.grid(row=6, column=1, padx=30, pady=30)
                return None

            self.tabview_tabelas = ctk.CTkToplevel(self)
            self.tabview_tabelas.geometry("1368x768")
            self.tabview_tabelas.title("Atualização")
            self.tabview_tabelas.configure(fg_color="#A1CDF4")
            self.tabview_tabelas.columnconfigure(0, weight=1)
            self.tabview_tabelas.rowconfigure(1, weight=1)
            self.tabview_tabelas.resizable(False, False)

            self.tabelas = ctk.CTkTabview(self.tabview_tabelas,width=1368, height=768, fg_color="#A1CDF4" )
            self.tabela1 = self.tabelas.add("Tab_aluno")
            self.tabela2 = self.tabelas.add("Tab_prof")
            self.tabelas.grid(row = 1, column=1, sticky="nsew")


            #Tab 1
            self.tabela_aluno = ctk.CTkTextbox(self.tabelas.tab("Tab_aluno"), width=1100, height=420, font=("Arial", 30), text_color="#000000", fg_color="#B5B5B5", border_width=3,border_color="#000000")

            self.destroy_tabela = ctk.CTkButton(self.tabelas.tab("Tab_aluno"), width=350, height=60, text="Voltar", fg_color="#4e0da0",border_width=3, border_color="#000000", command=self.tabview_tabelas.destroy)

            self.atualizar = ctk.CTkButton(self.tabelas.tab("Tab_aluno"), width=350, height=60, text="Atualizar", fg_color="#4e0da0",border_width=3, border_color="#000000", command= lambda :form_att("aluno"))


            db.execute('SELECT * FROM alunos')
            valores_alunos = db.fetchall()

            self.tabela_aluno.configure(state="normal")
            texto_formatado = ""
            for aluno in valores_alunos:
                linha = "         |   ".join(str(campo) for campo in aluno) + "\n"
                texto_formatado += linha
            self.tabela_aluno.insert("end", texto_formatado)
            self.tabela_aluno.configure(state="disabled")

            self.tabela_aluno.pack(side="top", padx=30, pady=30)

            self.atualizar.pack(side="bottom", padx=30, pady=30)

            self.destroy_tabela.pack(side="bottom", padx=30, pady=30)


            #Tab 2
            self.tabela_prof = ctk.CTkTextbox(self.tabelas.tab("Tab_prof"), width=1100, height=420, font=("Arial", 30),text_color="#000000", fg_color="#B5B5B5", border_width=3,border_color="#000000")

            self.atualizar = ctk.CTkButton(self.tabelas.tab("Tab_prof"), width=350, height=60, text="Atualizar", fg_color="#4e0da0",border_width=3, border_color="#000000", command= lambda : form_att("professor"))


            self.destroy_tabela = ctk.CTkButton(self.tabelas.tab("Tab_prof"), width=350, height=60, text="Voltar", fg_color="#4e0da0", border_width=3, border_color="#000000", command=self.tabview_tabelas.destroy)

            db.execute('SELECT * FROM professores')
            valores_profs = db.fetchall()

            self.tabela_prof.configure(state="normal")
            texto_formatado = ""
            for aluno in valores_profs:
                linha = "         |   ".join(str(campo) for campo in aluno) + "\n"
                texto_formatado += linha
            self.tabela_prof.insert("end", texto_formatado)
            self.tabela_prof.configure(state="disabled")

            self.tabela_prof.pack(side= "top", padx=30, pady=30)

            self.atualizar.pack(side="bottom", padx=30, pady=30)

            self.destroy_tabela.pack(side= "bottom", padx=30, pady=30)


        self.geometry("1368x768")
        self.title("S.C.B")
        self.grid_anchor("center")
        self.grid_rowconfigure((1,2,3,4,5,6), weight=2)
        self.grid_columnconfigure((1,2,3,4,5,6), weight=2)
        self.configure(fg_color = "#A1CDF4")


        #Menu
        self.menu = ctk.CTkFrame(self, fg_color="#4A5899", height=768, corner_radius=0, border_color="#000000")
        self.borda_menu = ctk.CTkFrame(self, fg_color="#000000", width=5, height= 768, corner_radius=0)

        self.menu_bnt1 = ctk.CTkButton(self.menu, width=200, height=30, text="Alunos", fg_color="#B5B5B5", text_color="#000000", border_width=2, border_color="#000000", command=visualizar_aluno)
        self.menu_bnt2 = ctk.CTkButton(self.menu, width=200, height=30, text="Professores",fg_color="#B5B5B5", text_color="#000000",border_width=2, border_color="#000000", command=visualizar_prof)
        self.menu_bnt3 = ctk.CTkButton(self.menu, width=200, height=50, text="Presenças dos alunos", fg_color="#B5B5B5", text_color="#000000",border_width=2, border_color="#000000", command=visualizar_presenca)
        self.menu_bnt4 = ctk.CTkButton(self.menu, width=200, height=50, text="Presenças dos professores", fg_color="#B5B5B5", text_color="#000000",border_width=2, border_color="#000000", command=visualizar_presenca_profs)

        #Header
        self.header = ctk.CTkFrame(self, fg_color="#02135A", width=1368, height=80, corner_radius=0)
        self.borda_header = ctk.CTkFrame(self, fg_color="#000000", width=1074, height= 5, corner_radius=0)

        self.sincronia = ctk.CTkFrame(self.header, fg_color="#aa1e09", width=50, height=50, corner_radius=5, border_width=2, border_color="#000000")
        self.titulo = ctk.CTkLabel(self.header, font=("Arial", 60), text_color="#B5B5B5", text="S.C.B." )
        self.arduino_sincronia = ctk.CTkLabel(self.sincronia, font=("Arial", 20), text_color="#B5B5B5", text="Off")


        #Body
        self.princ_btn1 = ctk.CTkButton(self, width=350, height=60, text="Salvar", fg_color="#4e0da0", border_width=3, border_color="#000000", command=salvar_cadastro)
        self.princ_btn2 = ctk.CTkButton(self, width=350, height=60, text="Deletar", fg_color="#4e0da0", border_width=3, border_color="#000000", command=deletar)
        self.princ_btn3 = ctk.CTkButton(self, width=350, height=60, text="Sincronizar", fg_color="#4e0da0", border_width=3, border_color="#000000", command=sincronizar)
        self.princ_btn4 = ctk.CTkButton(self, width=350, height=60, text="Atualizar", fg_color="#4e0da0", border_width=3, border_color="#000000", command=atualizar)

        #Frames
        self.menu.grid(row=1, column= 1, columnspan= 2 ,rowspan=6 ,sticky="nws", pady=(80,0))
        self.borda_menu.grid(row=1,rowspan=6, column=2, sticky="ns", padx=(8,0))
        self.header.grid(row=1, column=1, columnspan=6, sticky="new" )
        self.borda_header.grid(row=1, column=1, columnspan=6, sticky="e", pady=(15,0))
        self.sincronia.pack(side="right", padx= 20, pady= 20)

        #Buttons
        self.menu_bnt1.pack(side="top", padx=46, pady=(30, 20))
        self.menu_bnt2.pack(side="top", padx=46, pady=(30, 20))
        self.menu_bnt3.pack(side="top", padx=46, pady=(30, 20))
        self.menu_bnt4.pack(side="top", padx=46, pady=(30, 20))


        self.princ_btn1.grid(row= 3, column=3, padx=20, pady=20)
        self.princ_btn2.grid(row= 3, column=5, padx=20, pady=20)
        self.princ_btn3.grid(row=5, column=3, padx=20, pady=20)
        self.princ_btn4.grid(row=5, column=5, padx=20, pady=20)

        #Labels
        self.titulo.pack(side="left", padx=10, pady=10)
        self.arduino_sincronia.pack(padx= 10, pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()