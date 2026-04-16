--
-- PostgreSQL database dump
--

\restrict 3P4ko7kuv2RwyGPo7rRmsL86bRmGEXQg9jufcKvzpYK8rIeyEyQE70emqElW7fV

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

-- Started on 2026-01-05 11:06:47

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
-- SET transaction_timeout = 0;
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
-- TOC entry 219 (class 1259 OID 25555)
-- Name: app_user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.app_user (
    id uuid NOT NULL,
    restaurant_id uuid,
    email character varying NOT NULL,
    password_hash character varying NOT NULL,
    display_name character varying,
    phone character varying,
    role character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    fcm_token text
);


ALTER TABLE public.app_user OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 25646)
-- Name: guest_session; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.guest_session (
    id uuid NOT NULL,
    qr_id uuid NOT NULL,
    session_token character varying NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone
);


ALTER TABLE public.guest_session OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 25569)
-- Name: menu_category; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.menu_category (
    id uuid NOT NULL,
    restaurant_id uuid NOT NULL,
    name character varying NOT NULL,
    icon character varying
);


ALTER TABLE public.menu_category OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 25579)
-- Name: menu_item; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.menu_item (
    id uuid NOT NULL,
    restaurant_id uuid NOT NULL,
    category_id uuid NOT NULL,
    name character varying NOT NULL,
    description character varying,
    price numeric NOT NULL,
    is_available boolean,
    image_url character varying,
    meta jsonb
);


ALTER TABLE public.menu_item OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 25695)
-- Name: menu_item_review; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.menu_item_review (
    id uuid NOT NULL,
    restaurant_id uuid NOT NULL,
    order_id uuid NOT NULL,
    order_line_id uuid NOT NULL,
    menu_item_id uuid NOT NULL,
    rating integer NOT NULL,
    comment text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.menu_item_review OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 25676)
-- Name: order_line; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_line (
    id uuid NOT NULL,
    order_id uuid NOT NULL,
    menu_item_id uuid NOT NULL,
    item_name text NOT NULL,
    qty integer NOT NULL,
    unit_price numeric NOT NULL,
    note text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.order_line OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 25748)
-- Name: order_status_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_status_history (
    id uuid NOT NULL,
    order_id uuid,
    old_status character varying,
    new_status character varying,
    changed_by uuid,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.order_status_history OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 25664)
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    id uuid NOT NULL,
    restaurant_id uuid NOT NULL,
    table_id uuid NOT NULL,
    qr_id uuid NOT NULL,
    user_id uuid,
    status character varying,
    total_amount numeric,
    currency character varying,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 25721)
-- Name: point_transaction; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.point_transaction (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    order_id uuid,
    points integer NOT NULL,
    reason character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.point_transaction OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 25623)
-- Name: qr_code; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.qr_code (
    id uuid NOT NULL,
    restaurant_id uuid NOT NULL,
    table_id uuid NOT NULL,
    code character varying NOT NULL,
    type character varying,
    status character varying,
    image_path character varying,
    created_at timestamp with time zone
);


ALTER TABLE public.qr_code OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 25607)
-- Name: restaurant_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.restaurant_table (
    id uuid NOT NULL,
    restaurant_id uuid NOT NULL,
    name text NOT NULL,
    seats integer NOT NULL,
    status text,
    created_at timestamp with time zone
);


ALTER TABLE public.restaurant_table OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 25591)
-- Name: restaurants; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.restaurants (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description character varying,
    owner_id uuid NOT NULL,
    image_preview character varying,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.restaurants OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 25741)
-- Name: tenant; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenant (
    id uuid NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE public.tenant OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 25711)
-- Name: user_point; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_point (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    total_points integer,
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.user_point OWNER TO postgres;

--
-- TOC entry 5006 (class 0 OID 25555)
-- Dependencies: 219
-- Data for Name: app_user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.app_user (id, restaurant_id, email, password_hash, display_name, phone, role, created_at, fcm_token) FROM stdin;
d94960a8-e7d9-4135-a34b-39236a20dff0	\N	customer@gmail.com	$2b$04$cZHLzhaR0k.a1KRfjjAz0e5qK5A01iZ/CwpEJ.NXeHtcMohXYwct2	custmer	\N	customer	2026-01-02 11:19:48.187131+07	\N
a185a53b-da72-422d-9884-ba00367d0445	\N	owner@gmail.com	$2b$04$P82cRlM91fdxVsy7oS2rNODNlnrm3SLH2lSXPYr0XXTYvWWyj4Ra.	owner	\N	owner	2026-01-02 11:17:32.839164+07	\N
1f1db9d2-9fce-4edf-b588-0440ff112508	f3c7bc32-5565-4b32-ae42-20577d54a2de	staff@gmail.com	$2b$04$Zl4W1Y9Al.Xq2Hzvm/P9sudrxqsF3qXgrJYK3XrPKELDzuGsn7LCa	staff	\N	staff	2026-01-02 11:19:35.802377+07	\N
6d306b14-6feb-4039-9117-2631de6f593e	\N	protected@test.com	$2b$04$DifXDDdcL8cSOeSM7Qa8oujVl/A2K5uFRAlC55my6IC6CU3huPwy6	\N	\N	customer	2026-01-02 11:33:22.942771+07	\N
3ac3663f-568b-4068-8e07-249b8798020d	\N	48bade3f-6a7e-442d-a8f4-ec9393dcde23@test.com	$2b$04$puf0H7cFJ3qvypXAr8H4AuAw71NQKfiGJoz1RcZ2qwzawiNYrcc2q	\N	\N	customer	2026-01-02 11:33:22.972343+07	\N
be38975e-c05c-43af-836a-2b22cc37108e	\N	9f01645b-b114-4bc5-86eb-d34a6eda6563@test.com	$2b$04$gV.3yB4/kw48lKE3lz6R/eVJrWl19Kq5ocRbWRmOCRfrDBxjmkCqq	\N	\N	customer	2026-01-02 11:33:22.981729+07	\N
163cbe3c-403a-4a29-88e8-9c1a9e6ccd3a	\N	988cbea5-ad35-40d0-b6cf-2bf9076873f3@test.com	$2b$04$b1vC7IW7AlqApIhJw8HJSepdZ06gJ0WR1YVe3KvA6pQqsN6ONWfTO	\N	\N	customer	2026-01-02 11:33:35.154556+07	\N
be88c143-e97b-4f8a-ab13-77065fd2f76d	\N	0d1df8e0-7db4-4d94-a1fd-018cc49810a1@test.com	$2b$04$wvfRH46rnqZlrDypwVQ8veERf.2Rt7g7ic8BBBFEEW0EhsIXQWgqK	\N	\N	customer	2026-01-02 11:33:35.165253+07	\N
e8fd98ff-8675-4743-9419-4abb32c14dfb	\N	27a15721-71af-46fe-98b9-47dece1f329e@test.com	$2b$04$3uVF7C8B7n1y3NY3OSA2reHBggCRtSpqALnnKhWnCUaP1CB8W0R9a	\N	\N	customer	2026-01-02 11:33:35.185606+07	\N
cbffeaca-9a3f-4cd6-800d-7326497fe49f	\N	505eeaa1-e88a-4b4c-9a2b-05789df9f5bc@test.com	$2b$04$OLp4Goub7Hs9BKaqHNuJOuNpoGKLKpC.zrWiMtk.N8S7va1QJqDgq	\N	\N	customer	2026-01-03 17:50:52.644728+07	\N
c653cd42-4781-4d28-a280-1e392055f8f4	\N	8c4b11c4-6334-4c87-839f-0e831ac653b9@test.com	$2b$04$WatH6IyXaEpnzSVwrKHmQOtc5potnqTeBLx7I0y62.h0xgxbbGcf6	\N	\N	customer	2026-01-03 17:50:52.655949+07	\N
3dd4cd27-ffb1-4fe3-91b6-798ced68ecfe	\N	1c3f1368-bb41-4546-8c94-71acfa745869@test.com	$2b$04$vgqC0jYoCJ1mXBeE0kGKaedVZBDOmSk1NGcBfB406nLx1sa7tGddu	\N	\N	customer	2026-01-03 17:51:21.446146+07	\N
391a8c6f-8671-4b47-b313-631222bec8e9	\N	6697e775-f49d-4dc3-af1f-386c57f2bbf1@test.com	$2b$04$Ik9iOn3wS3VgQrUQ6i/m8OjbJqKRfmRORCPagXTNH.m7j8avw86HK	\N	\N	customer	2026-01-03 17:51:21.455697+07	\N
88ab5b6c-89d6-4faa-9eb1-9d96a713229e	\N	42fc52ea-48ff-4d01-b7f0-29650c139718@test.com	$2b$04$3gEj7JLqKBirRPBn64gqJ.8X/suEnRZPOFPXIgljOe.mx2mfUywuW	\N	\N	customer	2026-01-03 17:51:21.469354+07	\N
30c9cb1c-d100-41f7-bf13-e98175449026	\N	ba26a3f8-723b-40bb-bf0e-a3d3c1e9030a@test.com	$2b$04$J2P.B3kc8GbN0jRmy/5iZuDUgpSw.Zb3p23OrBBFnIFIrCCWWKRPy	\N	\N	customer	2026-01-03 17:51:38.068257+07	\N
c79f2b43-bac1-4340-be11-f6853dc7b3fb	\N	9dc710d0-debd-4876-86ee-afa0022131a4@test.com	$2b$04$CaguLPIIO0WIR9LNS/ouu.CkcCj/BRl9AFS2pTERBMwcM0Bq2B/3y	\N	\N	customer	2026-01-03 17:51:38.079358+07	\N
07e468a6-c6ed-455d-8fd0-ccb9dde72e6e	\N	8ef78bf2-4c22-47e5-ac72-ab03e819db89@test.com	$2b$04$tpIbU.Hy9YcIa.pK7xk/1.gEFvqQW8hBFYGOrISt6jCAjB/T/yX1a	\N	\N	customer	2026-01-03 17:51:38.09386+07	\N
de282ad6-ad6d-4b17-a79a-ae7c4cf2ef3d	\N	a1b2ac57-8114-400f-aa26-66032abd3ac4@test.com	$2b$04$NYS1LwWJFd92fHcShL59GuX1V23OZupWNub1Rslm4n/tgJTGZ/Biy	\N	\N	customer	2026-01-03 17:51:49.098351+07	\N
152df546-2449-4615-b9cd-0fe83a1978c6	\N	dda0d8f5-0b9c-4689-bf31-213167d08537@test.com	$2b$04$dBfZ8CcIRQZrUZMKtOBMF.NJ4argaGdO8PYzXAM8Qcr.3d7qalkN.	\N	\N	customer	2026-01-03 17:51:49.107132+07	\N
8d4c0aa6-9804-49e5-8b20-89f83f113db9	\N	39c105c0-1ff2-4cf8-b4f8-f44a84b12643@test.com	$2b$04$zDuJypZ1x3u.NT25198HeusZR3DPc5Nxmd1PDWFQ9wE6029t3rAXm	\N	\N	customer	2026-01-03 17:51:49.121213+07	\N
\.


--
-- TOC entry 5012 (class 0 OID 25646)
-- Dependencies: 225
-- Data for Name: guest_session; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.guest_session (id, qr_id, session_token, expires_at, created_at) FROM stdin;
731015ee-fd37-4481-9853-8f8be18685fd	40207684-fea5-43d2-a142-9da9fbdf6aeb	8qzHXdfr3Oi6xDXiIQWP96zuZ9Zd6c7JKwEPb-hLq_M	2026-01-02 11:50:54.466959+07	2026-01-02 07:50:54.467958+07
1b3d10c4-ee05-4236-ae40-ef08599cc9be	40207684-fea5-43d2-a142-9da9fbdf6aeb	gYTvu9YNFzsn5sqkFp85CBu1UGl03bIEQmK0CQhJuwQ	2026-01-02 12:09:03.821166+07	2026-01-02 08:09:03.822167+07
e0d3f071-cfa4-47cc-a53b-7232b72f32d0	40207684-fea5-43d2-a142-9da9fbdf6aeb	-snlR2UqKo4GofR-rDDn72mlrye4oa9ZAGa4lT3AHbc	2026-01-02 14:18:53.695107+07	2026-01-02 10:18:53.696108+07
350e969f-e3cc-425f-a19a-b4dd53cdb160	40207684-fea5-43d2-a142-9da9fbdf6aeb	ZPArEGCPYy6mT3pa-CCf3Xln3itRoouSmpXA-EWCnD0	2026-01-02 14:18:53.747549+07	2026-01-02 10:18:53.74855+07
bda43781-5925-4bc3-8571-ab3bbb852c76	40207684-fea5-43d2-a142-9da9fbdf6aeb	1SIIWanQO4Sq1iN8cC2TDMz1HgQGTc209P5nhN2D9ss	2026-01-02 16:32:21.738209+07	2026-01-02 12:32:21.739212+07
64323aea-bc4f-4e3a-ad57-4c65e5bd6625	40207684-fea5-43d2-a142-9da9fbdf6aeb	6YJIBW3DE0sbKU4bqLTSi_voZRwWTfhtyvwNGagrNeI	2026-01-02 18:09:50.249984+07	2026-01-02 14:09:50.250958+07
b9996c44-8d9d-4f3d-9c97-7c7712287217	c93ae799-abe2-4a81-8de1-efbc9f697075	CxUQKZ0C5ICu-6xuJsNcmua47m_S_X6Ht4D48-ryrWY	2026-01-02 18:14:48.499239+07	2026-01-02 14:14:48.499239+07
f2c4c857-99a5-4afd-9dac-bc575d4e0233	c93ae799-abe2-4a81-8de1-efbc9f697075	rn5jQYMz22rj_NxVJq5RFd6CDfH1bWQhZ2WGpQ3kBtU	2026-01-03 13:00:43.234521+07	2026-01-03 09:00:43.236559+07
f22e0275-e257-4d91-886f-f003e39adf89	dde28676-ccdc-4c2a-b18a-601cd9aad167	J9xn9LRS8_vakcogz-oyQN1TyAJChleUmPPZgvCShg8	2026-01-03 13:07:04.443241+07	2026-01-03 09:07:04.444279+07
01d198b8-4612-468b-9271-ab29891d2df6	dde28676-ccdc-4c2a-b18a-601cd9aad167	I7GKVpaQ1rMJyj9EftkyCsPC-BTrEl-ueQ_2vmB1-kM	2026-01-03 13:27:52.022423+07	2026-01-03 09:27:52.023388+07
b5723ce2-d645-4553-b77f-5709e5a5f6a9	dde28676-ccdc-4c2a-b18a-601cd9aad167	Oo506TmC9NJgrhYd7SnuduetB-mRlDdlOw9ORLfGUY0	2026-01-03 19:09:19.381573+07	2026-01-03 15:09:19.383094+07
a3f6ae2e-645c-4da7-bdc5-25eba9aca21f	dde28676-ccdc-4c2a-b18a-601cd9aad167	-d4h2hpOap7R1zTmxzmLDhyyEKQUFDZT-W4lJS5fuJg	2026-01-04 07:14:19.107879+07	2026-01-04 03:14:19.108879+07
\.


--
-- TOC entry 5007 (class 0 OID 25569)
-- Dependencies: 220
-- Data for Name: menu_category; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.menu_category (id, restaurant_id, name, icon) FROM stdin;
243d503c-cd0d-4728-a696-4a0ce0537c42	f3c7bc32-5565-4b32-ae42-20577d54a2de	Cà phê	☕
324dcfbe-ce85-479c-b753-f99f314e8d9a	f3c7bc32-5565-4b32-ae42-20577d54a2de	Trà	🍵
bc5967b5-d384-4cab-a146-c18fe5385d3e	f3c7bc32-5565-4b32-ae42-20577d54a2de	Nước ép	🧃
a0e2a1b1-1bdc-47c6-adcc-8beb51374e33	f3c7bc32-5565-4b32-ae42-20577d54a2de	Sinh tố	🥤
8fbb2fb7-b8f9-4cba-8160-9a9530596a70	f3c7bc32-5565-4b32-ae42-20577d54a2de	Bánh ngọt	🍰
42127311-2d4f-46da-9955-a40d97276f53	f3c7bc32-5565-4b32-ae42-20577d54a2de	Ăn vặt	🍟
\.


--
-- TOC entry 5008 (class 0 OID 25579)
-- Dependencies: 221
-- Data for Name: menu_item; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.menu_item (id, restaurant_id, category_id, name, description, price, is_available, image_url, meta) FROM stdin;
0645a2ac-6af0-4558-a105-f02293707b36	f3c7bc32-5565-4b32-ae42-20577d54a2de	8fbb2fb7-b8f9-4cba-8160-9a9530596a70	Bánh brownie	Bánh chocolate đậm vị	40000	t	/media/menus/chocolate_cake.png	{"size": ["M", "L"]}
0cc71d51-a746-4d8b-9d77-a52f3060cc50	f3c7bc32-5565-4b32-ae42-20577d54a2de	bc5967b5-d384-4cab-a146-c18fe5385d3e	Nước ép ổi	Nước ép ổi tươi	30000	t	/media/menus/epoi.png	{"ice": ["ít", "vừa", "nhiều"], "size": ["M", "L"], "sugar": ["ít", "vừa", "nhiều"]}
14251912-52e8-49af-bdb4-8e1b81b98cca	f3c7bc32-5565-4b32-ae42-20577d54a2de	42127311-2d4f-46da-9955-a40d97276f53	Bánh tráng trộn	Bánh tráng trộn sa tế	40000	t	/media/menus/bantrangtron.png	{"size": ["M", "L"], "spicy": ["ít", "vừa", "nhiều"]}
2052af57-7ac6-4dd8-ab63-dd8d961a1b84	f3c7bc32-5565-4b32-ae42-20577d54a2de	243d503c-cd0d-4728-a696-4a0ce0537c42	Cà phê sữa đá	Cà phê pha phin, sữa đặc	30000	t	/media/menus/cf_suada.png	{"ice": ["ít", "vừa", "nhiều"], "size": ["S", "M", "L"]}
28db50ad-9fbd-4d15-81cb-a3a64e8ab683	f3c7bc32-5565-4b32-ae42-20577d54a2de	a0e2a1b1-1bdc-47c6-adcc-8beb51374e33	Sinh tố bơ	Sinh tố bơ sánh mịn	40000	t	/media/menus/st_bo.png	{"ice": ["ít", "vừa", "nhiều"], "size": ["M", "L"]}
330fe3a8-04cc-4927-8bf7-aec68f50481c	f3c7bc32-5565-4b32-ae42-20577d54a2de	a0e2a1b1-1bdc-47c6-adcc-8beb51374e33	Sinh tố dâu	Sinh tố dâu tươi	40000	t	/media/menus/st_dau.png	{"ice": ["ít", "vừa", "nhiều"], "size": ["M", "L"]}
3eff801d-4222-49db-b3f1-a618ac85264a	f3c7bc32-5565-4b32-ae42-20577d54a2de	42127311-2d4f-46da-9955-a40d97276f53	Khoai tây chiên	Khoai tây chiên giòn	30000	t	/media/menus/khoaitaychien.png	{"size": ["S", "M", "L"]}
453436ba-4fd9-41c5-8bc6-7e674a605b68	f3c7bc32-5565-4b32-ae42-20577d54a2de	324dcfbe-ce85-479c-b753-f99f314e8d9a	Trà tắc	Trà tắc chua nhẹ	30000	t	/media/menus/tratac.png	{"ice": ["ít", "vừa", "nhiều"], "size": ["M", "L"]}
490e7344-86c3-4725-8b59-2eb0dff77b13	f3c7bc32-5565-4b32-ae42-20577d54a2de	a0e2a1b1-1bdc-47c6-adcc-8beb51374e33	Sinh tố mãng cầu	Sinh tố mãng cầu thơm béo	42000	t	/media/menus/st_mangcau.png	{"ice": ["ít", "vừa", "nhiều"], "size": ["M", "L"]}
5083b9c6-37e5-4b26-a2a7-344a1dde0cbf	f3c7bc32-5565-4b32-ae42-20577d54a2de	42127311-2d4f-46da-9955-a40d97276f53	Cá viên chiên	Cá viên chiên giòn	30000	t	/media/menus/cavienchien.png	{"size": ["S", "M", "L"]}
54834848-7dfc-47c5-9fbb-dfc826cd5daa	f3c7bc32-5565-4b32-ae42-20577d54a2de	42127311-2d4f-46da-9955-a40d97276f53	Xúc xích chiên	Xúc xích chiên nóng	25000	t	/media/menus/xucxich.png	{"size": ["S", "M", "L"]}
5b2a7074-4e9f-4113-a701-b9ad8179965f	f3c7bc32-5565-4b32-ae42-20577d54a2de	324dcfbe-ce85-479c-b753-f99f314e8d9a	Trà vải	Trà vải thanh mát	35000	t	/media/menus/travai.png	{"ice": ["ít", "vừa", "nhiều"], "size": ["M", "L"]}
66afa25a-f0a4-4186-a324-c9d1014b415c	f3c7bc32-5565-4b32-ae42-20577d54a2de	bc5967b5-d384-4cab-a146-c18fe5385d3e	Nước ép cam	Nước ép cam tươi	35000	t	/media/menus/epcam.png	{"ice": ["ít", "vừa", "nhiều"], "size": ["M", "L"], "sugar": ["ít", "vừa", "nhiều"]}
6d7de848-befe-4ecf-b98b-07068406b4c9	f3c7bc32-5565-4b32-ae42-20577d54a2de	324dcfbe-ce85-479c-b753-f99f314e8d9a	Trà đào cam sả	Trà đào tươi, cam sả	35000	t	/media/menus/tradaocamsa.png	{"ice": ["ít", "vừa", "nhiều"], "size": ["M", "L"]}
6f2c8066-8ffd-4315-a043-0f5b88ae1c61	f3c7bc32-5565-4b32-ae42-20577d54a2de	324dcfbe-ce85-479c-b753-f99f314e8d9a	Trà chanh	Trà chanh truyền thống	25000	t	/media/menus/trachanh.png	{"ice": ["ít", "vừa", "nhiều"], "size": ["M", "L"]}
88efeb37-2c16-43ae-8bdd-35b92f42f51a	f3c7bc32-5565-4b32-ae42-20577d54a2de	8fbb2fb7-b8f9-4cba-8160-9a9530596a70	Bánh su kem	Bánh su nhân kem vani	30000	t	/media/menus/banhsukem.png	{"size": ["S", "M"]}
9a9c0ddf-4e67-497d-918e-4a5b8247cd0c	f3c7bc32-5565-4b32-ae42-20577d54a2de	8fbb2fb7-b8f9-4cba-8160-9a9530596a70	Bánh tiramisu	Bánh tiramisu mềm mịn, vị cà phê	45000	t	/media/menus/tiramisu.png	{"size": ["M", "L"]}
b35f9933-0613-48e2-8c5a-c5dcb9cc2279	f3c7bc32-5565-4b32-ae42-20577d54a2de	bc5967b5-d384-4cab-a146-c18fe5385d3e	Nước ép táo	Nước ép táo nguyên chất	35000	t	/media/menus/nceptao.png	{"ice": ["ít", "vừa", "nhiều"], "size": ["M", "L"], "sugar": ["ít", "vừa", "nhiều"]}
a2e9f010-8325-46e1-b97c-a41ab32a4277	f3c7bc32-5565-4b32-ae42-20577d54a2de	8fbb2fb7-b8f9-4cba-8160-9a9530596a70	Bánh bông lan trứng muối	Bông lan mềm, trứng muối béo	45000	t	/media/menus/bonglantrungmuoi.png	{"size": ["M", "L"]}
a933155c-18c1-448c-a0c2-c5f429181db2	f3c7bc32-5565-4b32-ae42-20577d54a2de	243d503c-cd0d-4728-a696-4a0ce0537c42	Cà phê đen đá	Cà phê pha phin	30000	t	/media/menus/cfden.png	{"ice": ["ít", "vừa", "nhiều"], "size": ["S", "M", "L"]}
aa81d2ae-e8d5-4d02-9829-63136e429d8a	f3c7bc32-5565-4b32-ae42-20577d54a2de	bc5967b5-d384-4cab-a146-c18fe5385d3e	Nước ép dứa	Nước ép dứa thơm mát	32000	t	/media/menus/ncepdua.png	{"ice": ["ít", "vừa", "nhiều"], "size": ["M", "L"], "sugar": ["ít", "vừa", "nhiều"]}
c1ee1d94-932e-4ebe-89a5-77903337fbfc	f3c7bc32-5565-4b32-ae42-20577d54a2de	bc5967b5-d384-4cab-a146-c18fe5385d3e	Nước ép cà rốt	Nước ép cà rốt bổ dưỡng	30000	t	/media/menus/ncepcarot.png	{"ice": ["ít", "vừa", "nhiều"], "size": ["M", "L"], "sugar": ["ít", "vừa", "nhiều"]}
d1688555-01d7-4da2-8e57-d5a1b9c2842d	f3c7bc32-5565-4b32-ae42-20577d54a2de	a0e2a1b1-1bdc-47c6-adcc-8beb51374e33	Sinh tố xoài	Sinh tố xoài chua ngọt	38000	t	/media/menus/st_xoai.png	{"ice": ["ít", "vừa", "nhiều"], "size": ["M", "L"]}
eb375f2d-ca38-487a-8981-c1fe1dc85ffe	f3c7bc32-5565-4b32-ae42-20577d54a2de	8fbb2fb7-b8f9-4cba-8160-9a9530596a70	Bánh cheesecake	Bánh phô mai béo mịn	50000	t	/media/menus/banhchesecake.png	{"size": ["M", "L"]}
ef17b790-c884-47a3-8e44-ebcacfeb7eb1	f3c7bc32-5565-4b32-ae42-20577d54a2de	324dcfbe-ce85-479c-b753-f99f314e8d9a	Trà sữa truyền thống	Trà đen pha sữa	40000	t	/media/menus/trasuatruyenthong.png	{"ice": ["ít", "vừa", "nhiều"], "size": ["M", "L"]}
fa8a49fc-1221-4e28-bb20-09ce5eb3fa86	f3c7bc32-5565-4b32-ae42-20577d54a2de	a0e2a1b1-1bdc-47c6-adcc-8beb51374e33	Sinh tố chuối	Sinh tố chuối sữa	35000	t	/media/menus/st_chuoi.png	{"ice": ["ít", "vừa", "nhiều"], "size": ["M", "L"]}
00a6c65d-bf36-45ad-88b0-72bede610d62	f3c7bc32-5565-4b32-ae42-20577d54a2de	42127311-2d4f-46da-9955-a40d97276f53	Gà viên chiên	Gà viên chiên giòn	35000	t	/media/menus/gavien.png	{"size": ["S", "M", "L"]}
\.


--
-- TOC entry 5015 (class 0 OID 25695)
-- Dependencies: 228
-- Data for Name: menu_item_review; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.menu_item_review (id, restaurant_id, order_id, order_line_id, menu_item_id, rating, comment, created_at) FROM stdin;
1846dd61-05e5-4a35-91ed-fef0698d6d54	f3c7bc32-5565-4b32-ae42-20577d54a2de	9aceba8f-12fe-4612-aa65-66ec3ef3c98a	2e54d9a4-a332-4f52-899e-19bdf4c13f47	2052af57-7ac6-4dd8-ab63-dd8d961a1b84	5	Test bằng DB cho nhanh	2026-01-03 10:04:26.319371+07
\.


--
-- TOC entry 5014 (class 0 OID 25676)
-- Dependencies: 227
-- Data for Name: order_line; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.order_line (id, order_id, menu_item_id, item_name, qty, unit_price, note, created_at) FROM stdin;
2e54d9a4-a332-4f52-899e-19bdf4c13f47	9aceba8f-12fe-4612-aa65-66ec3ef3c98a	2052af57-7ac6-4dd8-ab63-dd8d961a1b84	Cà phê sữa đá	3	30000	ít đá	2026-01-02 21:17:35.040485+07
bda8a13b-fa6e-43bb-a318-31ccdedd7e6c	9aceba8f-12fe-4612-aa65-66ec3ef3c98a	a933155c-18c1-448c-a0c2-c5f429181db2	Cà phê đen đá	6	30000	nóng	2026-01-02 21:17:35.040485+07
634f18fe-13b7-4312-8912-8a8187058733	69227d91-cf42-48d0-bf1b-33ae5cac2097	2052af57-7ac6-4dd8-ab63-dd8d961a1b84	Cà phê sữa đá	48	30000	\N	2026-01-03 16:02:51.636121+07
09f33ebc-3dd7-48ec-9cd6-8f69f4d4657c	c18d5275-c5bf-4a46-8467-d427304fc5c0	2052af57-7ac6-4dd8-ab63-dd8d961a1b84	Cà phê sữa đá	48	30000	\N	2026-01-03 16:08:10.687904+07
58588827-8dd4-423e-b359-5d2270edef6f	d05b6149-f9bc-4b2f-8552-7ce334a2706e	2052af57-7ac6-4dd8-ab63-dd8d961a1b84	Cà phê sữa đá	48	30000	\N	2026-01-03 16:29:04.006068+07
17cf46e5-d7e2-4d6b-9e06-946769784ce5	60c48f74-7650-45e5-9321-ae0809b71e23	2052af57-7ac6-4dd8-ab63-dd8d961a1b84	Cà phê sữa đá	48	30000	\N	2026-01-03 16:42:57.241653+07
f7604777-0353-41d3-8757-33cd7e4a11d5	8ed4502b-1d5a-4697-9433-fc0dd13eb0b9	2052af57-7ac6-4dd8-ab63-dd8d961a1b84	Cà phê sữa đá	48	30000	\N	2026-01-03 16:45:50.751305+07
24fdb7ea-7d07-4abc-b3b5-076b64615cec	0130d4a5-937e-451b-a7b8-69bbb7c51df7	2052af57-7ac6-4dd8-ab63-dd8d961a1b84	Cà phê sữa đá	1	30000	ít đá	2026-01-03 22:14:39.304792+07
56b94642-73cc-4e27-a2af-f68d3c916a3d	0130d4a5-937e-451b-a7b8-69bbb7c51df7	a933155c-18c1-448c-a0c2-c5f429181db2	Cà phê đen đá	2	30000	nóng	2026-01-03 22:14:39.304792+07
6e674396-2c26-4ff3-ba28-fec2b670cfee	3d79edf1-94af-48cf-9ee0-59279a976785	2052af57-7ac6-4dd8-ab63-dd8d961a1b84	Cà phê sữa đá	48	30000	\N	2026-01-04 10:14:43.001159+07
3319a374-3ea1-4932-b52c-5a2ff1e9dcd1	f92eb174-a936-40b1-8954-f7b60a96738b	2052af57-7ac6-4dd8-ab63-dd8d961a1b84	Cà phê sữa đá	48	30000	\N	2026-01-04 11:35:05.630099+07
26e236e5-b8bb-4732-a1e5-01adb59b54f6	0942fc6e-0f6f-4749-9bb1-59f376f6c710	2052af57-7ac6-4dd8-ab63-dd8d961a1b84	Cà phê sữa đá	48	30000	\N	2026-01-04 11:46:03.095729+07
f214aa63-7ff1-4446-acdf-8c18c0ff3bc1	1ae3f75e-0943-4a40-8bf5-c1a39a6841f9	2052af57-7ac6-4dd8-ab63-dd8d961a1b84	Cà phê sữa đá	48	30000	\N	2026-01-04 12:11:40.355331+07
d8ed41cc-e61c-4f84-83ce-037e25684d41	d23d16db-235c-4bcb-8474-535cf7733dd6	2052af57-7ac6-4dd8-ab63-dd8d961a1b84	Cà phê sữa đá	48	30000	\N	2026-01-04 12:14:55.965337+07
\.


--
-- TOC entry 5019 (class 0 OID 25748)
-- Dependencies: 232
-- Data for Name: order_status_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.order_status_history (id, order_id, old_status, new_status, changed_by, created_at) FROM stdin;
\.


--
-- TOC entry 5013 (class 0 OID 25664)
-- Dependencies: 226
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.orders (id, restaurant_id, table_id, qr_id, user_id, status, total_amount, currency, created_at) FROM stdin;
8ed4502b-1d5a-4697-9433-fc0dd13eb0b9	f3c7bc32-5565-4b32-ae42-20577d54a2de	6ab6b753-a9ad-45b2-bd5c-9df72db501cb	dde28676-ccdc-4c2a-b18a-601cd9aad167	d94960a8-e7d9-4135-a34b-39236a20dff0	served	1440000	VND	2026-01-03 16:45:50.751305+07
0130d4a5-937e-451b-a7b8-69bbb7c51df7	f3c7bc32-5565-4b32-ae42-20577d54a2de	6ab6b753-a9ad-45b2-bd5c-9df72db501cb	dde28676-ccdc-4c2a-b18a-601cd9aad167	d94960a8-e7d9-4135-a34b-39236a20dff0	served	90000	VND	2026-01-03 22:14:39.304792+07
3d79edf1-94af-48cf-9ee0-59279a976785	f3c7bc32-5565-4b32-ae42-20577d54a2de	6ab6b753-a9ad-45b2-bd5c-9df72db501cb	dde28676-ccdc-4c2a-b18a-601cd9aad167	d94960a8-e7d9-4135-a34b-39236a20dff0	served	1440000	VND	2026-01-04 10:14:43.001159+07
f92eb174-a936-40b1-8954-f7b60a96738b	f3c7bc32-5565-4b32-ae42-20577d54a2de	6ab6b753-a9ad-45b2-bd5c-9df72db501cb	dde28676-ccdc-4c2a-b18a-601cd9aad167	d94960a8-e7d9-4135-a34b-39236a20dff0	served	1440000	VND	2026-01-04 11:35:05.630099+07
0942fc6e-0f6f-4749-9bb1-59f376f6c710	f3c7bc32-5565-4b32-ae42-20577d54a2de	6ab6b753-a9ad-45b2-bd5c-9df72db501cb	dde28676-ccdc-4c2a-b18a-601cd9aad167	d94960a8-e7d9-4135-a34b-39236a20dff0	served	1440000	VND	2026-01-04 11:46:03.095729+07
69227d91-cf42-48d0-bf1b-33ae5cac2097	f3c7bc32-5565-4b32-ae42-20577d54a2de	ccf6494a-6e37-45a9-ad48-9ae4e53d048f	c93ae799-abe2-4a81-8de1-efbc9f697075	\N	served	1440000	VND	2026-01-03 16:02:51.636121+07
1ae3f75e-0943-4a40-8bf5-c1a39a6841f9	f3c7bc32-5565-4b32-ae42-20577d54a2de	6ab6b753-a9ad-45b2-bd5c-9df72db501cb	dde28676-ccdc-4c2a-b18a-601cd9aad167	d94960a8-e7d9-4135-a34b-39236a20dff0	served	1440000	VND	2026-01-04 12:11:40.355331+07
9aceba8f-12fe-4612-aa65-66ec3ef3c98a	f3c7bc32-5565-4b32-ae42-20577d54a2de	ccf6494a-6e37-45a9-ad48-9ae4e53d048f	c93ae799-abe2-4a81-8de1-efbc9f697075	d94960a8-e7d9-4135-a34b-39236a20dff0	served	270000	VND	2026-01-02 21:17:35.040485+07
c18d5275-c5bf-4a46-8467-d427304fc5c0	f3c7bc32-5565-4b32-ae42-20577d54a2de	6ab6b753-a9ad-45b2-bd5c-9df72db501cb	dde28676-ccdc-4c2a-b18a-601cd9aad167	d94960a8-e7d9-4135-a34b-39236a20dff0	served	1440000	VND	2026-01-03 16:08:10.687904+07
d23d16db-235c-4bcb-8474-535cf7733dd6	f3c7bc32-5565-4b32-ae42-20577d54a2de	6ab6b753-a9ad-45b2-bd5c-9df72db501cb	dde28676-ccdc-4c2a-b18a-601cd9aad167	d94960a8-e7d9-4135-a34b-39236a20dff0	served	1440000	VND	2026-01-04 12:14:55.965337+07
d05b6149-f9bc-4b2f-8552-7ce334a2706e	f3c7bc32-5565-4b32-ae42-20577d54a2de	6ab6b753-a9ad-45b2-bd5c-9df72db501cb	dde28676-ccdc-4c2a-b18a-601cd9aad167	d94960a8-e7d9-4135-a34b-39236a20dff0	served	1440000	VND	2026-01-03 16:29:04.006068+07
60c48f74-7650-45e5-9321-ae0809b71e23	f3c7bc32-5565-4b32-ae42-20577d54a2de	6ab6b753-a9ad-45b2-bd5c-9df72db501cb	dde28676-ccdc-4c2a-b18a-601cd9aad167	d94960a8-e7d9-4135-a34b-39236a20dff0	served	1440000	VND	2026-01-03 16:42:57.241653+07
\.


--
-- TOC entry 5017 (class 0 OID 25721)
-- Dependencies: 230
-- Data for Name: point_transaction; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.point_transaction (id, user_id, order_id, points, reason, created_at) FROM stdin;
ec90b3ae-87cf-4c77-9247-607fda0a5d88	d94960a8-e7d9-4135-a34b-39236a20dff0	8ed4502b-1d5a-4697-9433-fc0dd13eb0b9	14400	ORDER_SERVED	2026-01-03 16:46:23.284346+07
c26d1698-6255-41f0-b08d-b095c3441234	d94960a8-e7d9-4135-a34b-39236a20dff0	0130d4a5-937e-451b-a7b8-69bbb7c51df7	900	ORDER_SERVED	2026-01-03 22:16:08.681088+07
ae7aa3a4-a75c-4de1-80c3-54c6901d7e6a	d94960a8-e7d9-4135-a34b-39236a20dff0	3d79edf1-94af-48cf-9ee0-59279a976785	14400	ORDER_SERVED	2026-01-04 10:52:41.526083+07
bcc46cca-8319-46ea-bc99-d6322b5f2c4c	d94960a8-e7d9-4135-a34b-39236a20dff0	f92eb174-a936-40b1-8954-f7b60a96738b	14400	ORDER_SERVED	2026-01-04 11:37:08.672045+07
3567653c-b659-46da-9308-d743d1192f1b	d94960a8-e7d9-4135-a34b-39236a20dff0	0942fc6e-0f6f-4749-9bb1-59f376f6c710	14400	ORDER_SERVED	2026-01-04 11:46:44.605166+07
a594ec4b-0cde-46a5-aa34-3adbf47b7dab	d94960a8-e7d9-4135-a34b-39236a20dff0	1ae3f75e-0943-4a40-8bf5-c1a39a6841f9	14400	ORDER_SERVED	2026-01-04 12:12:17.797876+07
19c88c2c-a805-400a-9532-0e2940e2482a	d94960a8-e7d9-4135-a34b-39236a20dff0	d23d16db-235c-4bcb-8474-535cf7733dd6	14400	ORDER_SERVED	2026-01-04 12:15:21.699026+07
\.


--
-- TOC entry 5011 (class 0 OID 25623)
-- Dependencies: 224
-- Data for Name: qr_code; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.qr_code (id, restaurant_id, table_id, code, type, status, image_path, created_at) FROM stdin;
c93ae799-abe2-4a81-8de1-efbc9f697075	f3c7bc32-5565-4b32-ae42-20577d54a2de	ccf6494a-6e37-45a9-ad48-9ae4e53d048f	926e16b0-ab21-48ba-9572-64252ede15e7	table	active	/media/qrs/table-ccf6494a-6e37-45a9-ad48-9ae4e53d048f.png	2026-01-02 07:43:17.822332+07
40207684-fea5-43d2-a142-9da9fbdf6aeb	f3c7bc32-5565-4b32-ae42-20577d54a2de	d825f6e1-d3c9-44da-9640-335e0a5cb41c	d8ac01f4-101e-4c38-bea8-459603ae9adf	table	active	/media/qrs/table-d825f6e1-d3c9-44da-9640-335e0a5cb41c.png	2026-01-02 07:43:22.292403+07
b683f163-9ae6-422d-a53a-5a84461c1ae5	f3c7bc32-5565-4b32-ae42-20577d54a2de	516a34df-7696-42e3-9d48-74c0e1913d79	bcd36aaa-7d5e-4d1f-901a-074bc51b7137	table	active	/media/qrs/table-516a34df-7696-42e3-9d48-74c0e1913d79.png	2026-01-03 09:06:15.012762+07
e737d271-bee0-4bd1-b742-3e4baacab471	f3c7bc32-5565-4b32-ae42-20577d54a2de	1a63fcf9-cb68-45d4-bc20-6248b9dbaab3	3a174f5d-07bd-41e8-aa94-5861d646c811	table	active	/media/qrs/table-1a63fcf9-cb68-45d4-bc20-6248b9dbaab3.png	2026-01-03 09:06:16.641781+07
dde28676-ccdc-4c2a-b18a-601cd9aad167	f3c7bc32-5565-4b32-ae42-20577d54a2de	6ab6b753-a9ad-45b2-bd5c-9df72db501cb	ff899946-52f7-46bd-9e97-e2280e511c28	table	active	/media/qrs/table-6ab6b753-a9ad-45b2-bd5c-9df72db501cb.png	2026-01-03 09:06:17.988682+07
\.


--
-- TOC entry 5010 (class 0 OID 25607)
-- Dependencies: 223
-- Data for Name: restaurant_table; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.restaurant_table (id, restaurant_id, name, seats, status, created_at) FROM stdin;
ccf6494a-6e37-45a9-ad48-9ae4e53d048f	f3c7bc32-5565-4b32-ae42-20577d54a2de	string	5	available	2026-01-02 07:43:17.811299+07
d825f6e1-d3c9-44da-9640-335e0a5cb41c	f3c7bc32-5565-4b32-ae42-20577d54a2de	string	5	available	2026-01-02 07:43:22.286591+07
516a34df-7696-42e3-9d48-74c0e1913d79	f3c7bc32-5565-4b32-ae42-20577d54a2de	string	5	available	2026-01-03 09:06:15.007389+07
1a63fcf9-cb68-45d4-bc20-6248b9dbaab3	f3c7bc32-5565-4b32-ae42-20577d54a2de	string	5	available	2026-01-03 09:06:16.639269+07
6ab6b753-a9ad-45b2-bd5c-9df72db501cb	f3c7bc32-5565-4b32-ae42-20577d54a2de	string	5	available	2026-01-03 09:06:17.985447+07
\.


--
-- TOC entry 5009 (class 0 OID 25591)
-- Dependencies: 222
-- Data for Name: restaurants; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.restaurants (id, name, description, owner_id, image_preview, created_at) FROM stdin;
f3c7bc32-5565-4b32-ae42-20577d54a2de	S2O Coffee	Chi nhánh Nguyễn Huệ	a185a53b-da72-422d-9884-ba00367d0445	\N	2026-01-02 11:23:44.251758+07
\.


--
-- TOC entry 5018 (class 0 OID 25741)
-- Dependencies: 231
-- Data for Name: tenant; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant (id, name) FROM stdin;
\.


--
-- TOC entry 5016 (class 0 OID 25711)
-- Dependencies: 229
-- Data for Name: user_point; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_point (id, user_id, total_points, updated_at) FROM stdin;
7f5518a2-1e66-4ac5-8193-b47f2da8a602	d94960a8-e7d9-4135-a34b-39236a20dff0	87300	2026-01-04 12:15:21.699026+07
\.


--
-- TOC entry 4815 (class 2606 OID 25568)
-- Name: app_user app_user_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT app_user_email_key UNIQUE (email);


--
-- TOC entry 4817 (class 2606 OID 25566)
-- Name: app_user app_user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT app_user_pkey PRIMARY KEY (id);


--
-- TOC entry 4831 (class 2606 OID 25656)
-- Name: guest_session guest_session_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guest_session
    ADD CONSTRAINT guest_session_pkey PRIMARY KEY (id);


--
-- TOC entry 4833 (class 2606 OID 25658)
-- Name: guest_session guest_session_session_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guest_session
    ADD CONSTRAINT guest_session_session_token_key UNIQUE (session_token);


--
-- TOC entry 4819 (class 2606 OID 25578)
-- Name: menu_category menu_category_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_category
    ADD CONSTRAINT menu_category_pkey PRIMARY KEY (id);


--
-- TOC entry 4821 (class 2606 OID 25590)
-- Name: menu_item menu_item_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_item
    ADD CONSTRAINT menu_item_pkey PRIMARY KEY (id);


--
-- TOC entry 4839 (class 2606 OID 25710)
-- Name: menu_item_review menu_item_review_order_line_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_item_review
    ADD CONSTRAINT menu_item_review_order_line_id_key UNIQUE (order_line_id);


--
-- TOC entry 4841 (class 2606 OID 25708)
-- Name: menu_item_review menu_item_review_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_item_review
    ADD CONSTRAINT menu_item_review_pkey PRIMARY KEY (id);


--
-- TOC entry 4837 (class 2606 OID 25689)
-- Name: order_line order_line_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_line
    ADD CONSTRAINT order_line_pkey PRIMARY KEY (id);


--
-- TOC entry 4851 (class 2606 OID 25756)
-- Name: order_status_history order_status_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_status_history
    ADD CONSTRAINT order_status_history_pkey PRIMARY KEY (id);


--
-- TOC entry 4835 (class 2606 OID 25675)
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- TOC entry 4847 (class 2606 OID 25732)
-- Name: point_transaction point_transaction_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.point_transaction
    ADD CONSTRAINT point_transaction_pkey PRIMARY KEY (id);


--
-- TOC entry 4827 (class 2606 OID 25635)
-- Name: qr_code qr_code_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qr_code
    ADD CONSTRAINT qr_code_code_key UNIQUE (code);


--
-- TOC entry 4829 (class 2606 OID 25633)
-- Name: qr_code qr_code_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qr_code
    ADD CONSTRAINT qr_code_pkey PRIMARY KEY (id);


--
-- TOC entry 4825 (class 2606 OID 25617)
-- Name: restaurant_table restaurant_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.restaurant_table
    ADD CONSTRAINT restaurant_table_pkey PRIMARY KEY (id);


--
-- TOC entry 4823 (class 2606 OID 25601)
-- Name: restaurants restaurants_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.restaurants
    ADD CONSTRAINT restaurants_pkey PRIMARY KEY (id);


--
-- TOC entry 4849 (class 2606 OID 25747)
-- Name: tenant tenant_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant
    ADD CONSTRAINT tenant_pkey PRIMARY KEY (id);


--
-- TOC entry 4843 (class 2606 OID 25718)
-- Name: user_point user_point_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_point
    ADD CONSTRAINT user_point_pkey PRIMARY KEY (id);


--
-- TOC entry 4845 (class 2606 OID 25720)
-- Name: user_point user_point_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_point
    ADD CONSTRAINT user_point_user_id_key UNIQUE (user_id);


--
-- TOC entry 4856 (class 2606 OID 25659)
-- Name: guest_session guest_session_qr_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guest_session
    ADD CONSTRAINT guest_session_qr_id_fkey FOREIGN KEY (qr_id) REFERENCES public.qr_code(id);


--
-- TOC entry 4857 (class 2606 OID 25690)
-- Name: order_line order_line_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_line
    ADD CONSTRAINT order_line_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id);


--
-- TOC entry 4858 (class 2606 OID 25757)
-- Name: order_status_history order_status_history_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_status_history
    ADD CONSTRAINT order_status_history_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id);


--
-- TOC entry 4854 (class 2606 OID 25636)
-- Name: qr_code qr_code_restaurant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qr_code
    ADD CONSTRAINT qr_code_restaurant_id_fkey FOREIGN KEY (restaurant_id) REFERENCES public.restaurants(id);


--
-- TOC entry 4855 (class 2606 OID 25641)
-- Name: qr_code qr_code_table_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qr_code
    ADD CONSTRAINT qr_code_table_id_fkey FOREIGN KEY (table_id) REFERENCES public.restaurant_table(id);


--
-- TOC entry 4853 (class 2606 OID 25618)
-- Name: restaurant_table restaurant_table_restaurant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.restaurant_table
    ADD CONSTRAINT restaurant_table_restaurant_id_fkey FOREIGN KEY (restaurant_id) REFERENCES public.restaurants(id);


--
-- TOC entry 4852 (class 2606 OID 25602)
-- Name: restaurants restaurants_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.restaurants
    ADD CONSTRAINT restaurants_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.app_user(id);


-- Completed on 2026-01-05 11:06:48

--
-- PostgreSQL database dump complete
--

\unrestrict 3P4ko7kuv2RwyGPo7rRmsL86bRmGEXQg9jufcKvzpYK8rIeyEyQE70emqElW7fV
