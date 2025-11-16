"""init_legal_schema

Révision de base pour la structure juridique de Konan.
Compatible PostgreSQL 16 (sans pgvector).
"""

from alembic import op
import sqlalchemy as sa

# Révisions Alembic
revision = "3de4f71ad3b0"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS pg_trgm;
    -- Extension pgvector désactivée (non installée sous Windows)
    -- CREATE EXTENSION IF NOT EXISTS vector;

    CREATE TABLE IF NOT EXISTS ref_language (
        code TEXT PRIMARY KEY,
        name TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS ref_doc_type (
        code TEXT PRIMARY KEY,
        label TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS institution (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name TEXT NOT NULL,
        kind TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS jort_issue (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        series TEXT NOT NULL,
        number INTEGER NOT NULL,
        publication_date DATE NOT NULL,
        pdf_url TEXT NOT NULL,
        page_start INTEGER,
        page_end INTEGER,
        sha256 BYTEA,
        source_url TEXT NOT NULL,
        UNIQUE (series, number, publication_date)
    );

    CREATE TABLE IF NOT EXISTS legal_document (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        doc_type TEXT NOT NULL REFERENCES ref_doc_type(code),
        official_number TEXT,
        title TEXT NOT NULL,
        promulgation_date DATE,
        issuer UUID REFERENCES institution(id),
        jort_issue_id UUID REFERENCES jort_issue(id),
        jort_page_start INTEGER,
        jort_page_end INTEGER,
        status TEXT NOT NULL CHECK (
            status IN ('en_vigueur','abroge','modifie','caduc','transitoire')
        ),
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now()
    );

    CREATE TABLE IF NOT EXISTS article (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        document_id UUID NOT NULL REFERENCES legal_document(id) ON DELETE CASCADE,
        number TEXT NOT NULL,
        position INTEGER NOT NULL,
        UNIQUE (document_id, number)
    );

    CREATE TABLE IF NOT EXISTS article_version (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        article_id UUID NOT NULL REFERENCES article(id) ON DELETE CASCADE,
        lang TEXT NOT NULL REFERENCES ref_language(code),
        text_plain TEXT NOT NULL,
        text_html TEXT,
        effective_from DATE NOT NULL,
        effective_to DATE,
        change_type TEXT NOT NULL CHECK (
            change_type IN ('creation','modification','abrogation')
        ),
        source_act UUID REFERENCES legal_document(id),
        jort_issue_id UUID REFERENCES jort_issue(id),
        sha256 BYTEA,
        is_current BOOLEAN GENERATED ALWAYS AS (effective_to IS NULL) STORED,
        -- Substitution temporaire du champ vectoriel
        embedding BYTEA
    );

    CREATE TABLE IF NOT EXISTS act_relation (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        from_act UUID NOT NULL REFERENCES legal_document(id) ON DELETE CASCADE,
        to_act UUID NOT NULL REFERENCES legal_document(id) ON DELETE CASCADE,
        relation TEXT NOT NULL CHECK (
            relation IN ('modifie','abroge','complete','remplace')
        ),
        note TEXT
    );

    CREATE TABLE IF NOT EXISTS cross_reference (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        from_article UUID NOT NULL REFERENCES article(id) ON DELETE CASCADE,
        to_document UUID REFERENCES legal_document(id),
        to_article UUID REFERENCES article(id),
        anchor_text TEXT NOT NULL,
        norm_target TEXT
    );

    CREATE TABLE IF NOT EXISTS case_law (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        court TEXT NOT NULL,
        chamber TEXT,
        case_number TEXT,
        decision_date DATE NOT NULL,
        title TEXT,
        jort_issue_id UUID REFERENCES jort_issue(id),
        pdf_url TEXT,
        sha256 BYTEA
    );

    CREATE INDEX IF NOT EXISTS idx_av_current ON article_version (is_current);
    CREATE INDEX IF NOT EXISTS idx_av_trgm ON article_version USING gin (text_plain gin_trgm_ops);
    CREATE INDEX IF NOT EXISTS idx_av_doc ON article_version (article_id);
    -- Index vectoriel désactivé
    -- CREATE INDEX IF NOT EXISTS idx_av_vec ON article_version USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

    CREATE OR REPLACE VIEW current_articles_v AS
    SELECT av.id AS article_version_id, a.id AS article_id, ld.id AS document_id,
           ld.title, a.number AS article_number, av.lang, av.text_plain,
           ji.number AS jort_number, ji.publication_date AS jort_date,
           ld.doc_type, ld.status
    FROM article_version av
    JOIN article a ON a.id = av.article_id
    JOIN legal_document ld ON ld.id = a.document_id
    LEFT JOIN jort_issue ji ON ji.id = av.jort_issue_id
    WHERE av.is_current = true;

    INSERT INTO ref_language(code, name) VALUES
      ('ar','Arabe'), ('fr','Français')
    ON CONFLICT (code) DO NOTHING;

    INSERT INTO ref_doc_type(code, label) VALUES
      ('constitution','Constitution'),
      ('loi','Loi'),
      ('loi_organique','Loi organique'),
      ('decret','Décret'),
      ('decret_loi','Décret-loi'),
      ('arrete','Arrêté'),
      ('circulaire','Circulaire'),
      ('code','Code'),
      ('jurisprudence','Jurisprudence')
    ON CONFLICT (code) DO NOTHING;
    """)


def downgrade():
    op.execute("""
    DROP VIEW IF EXISTS current_articles_v;
    DROP TABLE IF EXISTS case_law, cross_reference, act_relation,
        article_version, article, legal_document, jort_issue,
        institution, ref_doc_type, ref_language CASCADE;
    """)
