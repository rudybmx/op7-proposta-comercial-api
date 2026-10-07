# op7-proposta-comercial-api

Landing page OP7 exportada da VPS cypher em 07/10/2026.

- **Domínio:** (sem domínio próprio; usada pela proposta comercial)
- **Como roda:** Python 3.12 + uvicorn (Dockerfile), porta 8080
- **Subir:** `docker build -t op7-proposta-comercial-api .` e `docker run -d -p <porta>:<porta da linha acima> op7-proposta-comercial-api`
- **Atenção:** Precisa da variável DATABASE_URL apontando pra um Postgres. Os dados das propostas estão hoje no banco 'nucleo' da cypher: peça um dump ao Rudy se for migrar.
