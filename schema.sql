--
-- PostgreSQL database dump
--

-- Dumped from database version 14.3 (Debian 14.3-1.pgdg110+1)
-- Dumped by pg_dump version 14.3 (Ubuntu 14.3-0ubuntu0.22.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: cr; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cr (
    id integer NOT NULL,
    creation_day date,
    set_code character varying(5),
    set_name character varying(50),
    data jsonb,
    file_name text
);


--
-- Name: cr_diffs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cr_diffs (
    id integer NOT NULL,
    creation_day date NOT NULL,
    changes jsonb,
    source_id integer NOT NULL,
    dest_id integer NOT NULL,
    bulletin_url text
);


--
-- Name: cr_diffs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.cr_diffs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cr_diffs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.cr_diffs_id_seq OWNED BY public.cr_diffs.id;


--
-- Name: cr_diffs_pending; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cr_diffs_pending (
    id integer NOT NULL,
    creation_day date,
    source_id integer NOT NULL,
    dest_id integer NOT NULL,
    changes jsonb
);


--
-- Name: cr_diffs_pending_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.cr_diffs_pending_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cr_diffs_pending_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.cr_diffs_pending_id_seq OWNED BY public.cr_diffs_pending.id;


--
-- Name: cr_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.cr_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cr_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.cr_id_seq OWNED BY public.cr.id;


--
-- Name: cr_pending; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cr_pending (
    id integer NOT NULL,
    creation_day date,
    data jsonb,
    file_name text
);


--
-- Name: cr_pending_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.cr_pending_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cr_pending_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.cr_pending_id_seq OWNED BY public.cr_pending.id;


--
-- Name: ipg; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ipg (
    id integer NOT NULL,
    creation_day date,
    file_name text
);


--
-- Name: mtr; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.mtr (
    id integer NOT NULL,
    file_name text,
    creation_day date
);


--
-- Name: mtr_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.mtr_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: mtr_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.mtr_id_seq OWNED BY public.mtr.id;


--
-- Name: redirects; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.redirects (
    resource text NOT NULL,
    link text NOT NULL
);


--
-- Name: redirects_pending; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.redirects_pending (
    resource text NOT NULL,
    link text NOT NULL
);


--
-- Name: table_name_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.table_name_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: table_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.table_name_id_seq OWNED BY public.ipg.id;


--
-- Name: cr id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cr ALTER COLUMN id SET DEFAULT nextval('public.cr_id_seq'::regclass);


--
-- Name: cr_diffs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cr_diffs ALTER COLUMN id SET DEFAULT nextval('public.cr_diffs_id_seq'::regclass);


--
-- Name: cr_diffs_pending id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cr_diffs_pending ALTER COLUMN id SET DEFAULT nextval('public.cr_diffs_pending_id_seq'::regclass);


--
-- Name: cr_pending id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cr_pending ALTER COLUMN id SET DEFAULT nextval('public.cr_pending_id_seq'::regclass);


--
-- Name: ipg id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ipg ALTER COLUMN id SET DEFAULT nextval('public.table_name_id_seq'::regclass);


--
-- Name: mtr id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mtr ALTER COLUMN id SET DEFAULT nextval('public.mtr_id_seq'::regclass);


--
-- Name: cr_diffs_pending cr_diffs_pending_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cr_diffs_pending
    ADD CONSTRAINT cr_diffs_pending_pk PRIMARY KEY (id);


--
-- Name: cr_diffs cr_diffs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cr_diffs
    ADD CONSTRAINT cr_diffs_pkey PRIMARY KEY (id);


--
-- Name: cr_pending cr_pending_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cr_pending
    ADD CONSTRAINT cr_pending_pk PRIMARY KEY (id);


--
-- Name: cr cr_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cr
    ADD CONSTRAINT cr_pkey PRIMARY KEY (id);


--
-- Name: mtr mtr_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mtr
    ADD CONSTRAINT mtr_pk PRIMARY KEY (id);


--
-- Name: redirects_pending redirects_pending_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.redirects_pending
    ADD CONSTRAINT redirects_pending_pkey PRIMARY KEY (resource);


--
-- Name: redirects redirects_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.redirects
    ADD CONSTRAINT redirects_pkey PRIMARY KEY (resource);


--
-- Name: ipg table_name_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ipg
    ADD CONSTRAINT table_name_pk PRIMARY KEY (id);


--
-- Name: mtr_created_day_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX mtr_created_day_index ON public.mtr USING btree (creation_day DESC);


--
-- Name: table_name_creation_day_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX table_name_creation_day_index ON public.ipg USING btree (creation_day DESC);


--
-- Name: cr_diffs cr_diffs_cr_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cr_diffs
    ADD CONSTRAINT cr_diffs_cr_id_fk FOREIGN KEY (source_id) REFERENCES public.cr(id);


--
-- Name: cr_diffs cr_diffs_cr_id_fk_2; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cr_diffs
    ADD CONSTRAINT cr_diffs_cr_id_fk_2 FOREIGN KEY (dest_id) REFERENCES public.cr(id);


--
-- Name: cr_diffs_pending cr_diffs_pending_cr_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cr_diffs_pending
    ADD CONSTRAINT cr_diffs_pending_cr_id_fk FOREIGN KEY (source_id) REFERENCES public.cr(id);


--
-- Name: cr_diffs_pending cr_diffs_pending_cr_pending_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cr_diffs_pending
    ADD CONSTRAINT cr_diffs_pending_cr_pending_id_fk FOREIGN KEY (dest_id) REFERENCES public.cr_pending(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

