import os
from datetime import date
from decimal import Decimal
from typing import Any

import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

DATABASE_URL = os.environ["DATABASE_URL"]

app = FastAPI(title="Proposta Comercial API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://propostacomercial.op7franquia.com.br"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)


class ProposalIn(BaseModel):
    unidade: str = Field(min_length=1, max_length=255)
    cidade_estado: str | None = Field(default=None, max_length=255)
    link_plano_acao: HttpUrl | None = None
    link_lista: HttpUrl | None = None
    link_criativos: HttpUrl | None = None
    data_reuniao: date | None = None
    nichos: str | None = Field(default=None, max_length=1000)
    investimento_trafego: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    roteiros: bool = False
    outbound: bool = False
    criativos: bool = False
    videos: bool = False
    start_acoes: bool = False
    conversas: int = Field(default=0, ge=0)
    fechados_mes: int = Field(default=0, ge=0)
    status: str = Field(default="ativo", pattern="^(ativo|em-ativacao|pendente)$")


class Proposal(ProposalIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: Any
    updated_at: Any


def connect():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def row_to_dict(row):
    return dict(row)


@app.get("/health")
def health():
    with connect() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok"}


@app.get("/api/propostas", response_model=list[Proposal])
def list_proposals():
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM public.propostacomercial ORDER BY id"
        ).fetchall()
    return [row_to_dict(row) for row in rows]


@app.post("/api/propostas", response_model=Proposal, status_code=201)
def create_proposal(payload: ProposalIn):
    data = payload.model_dump(mode="json")
    with connect() as conn:
        row = conn.execute(
            """
            INSERT INTO public.propostacomercial (
                unidade, cidade_estado, link_plano_acao, link_lista, link_criativos,
                data_reuniao, nichos,
                investimento_trafego, roteiros, outbound, criativos, videos,
                start_acoes, conversas, fechados_mes, status
            ) VALUES (
                %(unidade)s, %(cidade_estado)s, %(link_plano_acao)s, %(link_lista)s,
                %(link_criativos)s, %(data_reuniao)s,
                %(nichos)s, %(investimento_trafego)s, %(roteiros)s, %(outbound)s,
                %(criativos)s, %(videos)s, %(start_acoes)s, %(conversas)s,
                %(fechados_mes)s, %(status)s
            ) RETURNING *
            """,
            data,
        ).fetchone()
        conn.commit()
    return row_to_dict(row)


@app.put("/api/propostas/{proposal_id}", response_model=Proposal)
def update_proposal(proposal_id: int, payload: ProposalIn):
    data = payload.model_dump(mode="json")
    data["id"] = proposal_id
    with connect() as conn:
        row = conn.execute(
            """
            UPDATE public.propostacomercial SET
                unidade = %(unidade)s,
                cidade_estado = %(cidade_estado)s,
                link_plano_acao = %(link_plano_acao)s,
                link_lista = %(link_lista)s,
                link_criativos = %(link_criativos)s,
                data_reuniao = %(data_reuniao)s,
                nichos = %(nichos)s,
                investimento_trafego = %(investimento_trafego)s,
                roteiros = %(roteiros)s,
                outbound = %(outbound)s,
                criativos = %(criativos)s,
                videos = %(videos)s,
                start_acoes = %(start_acoes)s,
                conversas = %(conversas)s,
                fechados_mes = %(fechados_mes)s,
                status = %(status)s
            WHERE id = %(id)s
            RETURNING *
            """,
            data,
        ).fetchone()
        conn.commit()
    if row is None:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")
    return row_to_dict(row)


@app.delete("/api/propostas/{proposal_id}", status_code=204)
def delete_proposal(proposal_id: int):
    with connect() as conn:
        result = conn.execute(
            "DELETE FROM public.propostacomercial WHERE id = %s", (proposal_id,)
        )
        conn.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")
