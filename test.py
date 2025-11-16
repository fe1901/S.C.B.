import psycopg

try:
    with psycopg.connect("postgresql://neondb_owner:npg_fp3TCl1XSEPv@ep-sparkling-feather-ac7juqtl-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require") as conec:
            with conec.cursor() as db:
                db.execute("INSERT INTO professores (id, nome) VALUES (%s, %s)", (2,"teste",))
                print("Dados inseridos com sucesso")
except Exception as e:
    print("Erro na conexão ou execução:", e)
