-- =========================
-- SCHEMA ONLY (NO DATA)
-- =========================

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

-- =========================
-- TABLES
-- =========================

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);

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

CREATE TABLE public.guest_session (
    id uuid NOT NULL,
    qr_id uuid NOT NULL,
    session_token character varying NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone
);

CREATE TABLE public.menu_category (
    id uuid NOT NULL,
    restaurant_id uuid NOT NULL,
    name character varying NOT NULL,
    icon character varying
);

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

CREATE TABLE public.order_status_history (
    id uuid NOT NULL,
    order_id uuid,
    old_status character varying,
    new_status character varying,
    changed_by uuid,
    created_at timestamp with time zone DEFAULT now()
);

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

CREATE TABLE public.point_transaction (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    order_id uuid,
    points integer NOT NULL,
    reason character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);

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

CREATE TABLE public.restaurant_table (
    id uuid NOT NULL,
    restaurant_id uuid NOT NULL,
    name text NOT NULL,
    seats integer NOT NULL,
    status text,
    created_at timestamp with time zone
);

CREATE TABLE public.restaurants (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description character varying,
    owner_id uuid NOT NULL,
    image_preview character varying,
    created_at timestamp with time zone DEFAULT now()
);

CREATE TABLE public.tenant (
    id uuid NOT NULL,
    name character varying(255) NOT NULL
);

CREATE TABLE public.user_point (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    total_points integer,
    updated_at timestamp with time zone DEFAULT now()
);

-- =========================
-- PRIMARY KEYS
-- =========================

ALTER TABLE ONLY public.alembic_version ADD PRIMARY KEY (version_num);
ALTER TABLE ONLY public.app_user ADD PRIMARY KEY (id);
ALTER TABLE ONLY public.guest_session ADD PRIMARY KEY (id);
ALTER TABLE ONLY public.menu_category ADD PRIMARY KEY (id);
ALTER TABLE ONLY public.menu_item ADD PRIMARY KEY (id);
ALTER TABLE ONLY public.menu_item_review ADD PRIMARY KEY (id);
ALTER TABLE ONLY public.order_line ADD PRIMARY KEY (id);
ALTER TABLE ONLY public.order_status_history ADD PRIMARY KEY (id);
ALTER TABLE ONLY public.orders ADD PRIMARY KEY (id);
ALTER TABLE ONLY public.point_transaction ADD PRIMARY KEY (id);
ALTER TABLE ONLY public.qr_code ADD PRIMARY KEY (id);
ALTER TABLE ONLY public.restaurant_table ADD PRIMARY KEY (id);
ALTER TABLE ONLY public.restaurants ADD PRIMARY KEY (id);
ALTER TABLE ONLY public.tenant ADD PRIMARY KEY (id);
ALTER TABLE ONLY public.user_point ADD PRIMARY KEY (id);

-- =========================
-- UNIQUE
-- =========================

ALTER TABLE ONLY public.app_user ADD UNIQUE (email);
ALTER TABLE ONLY public.guest_session ADD UNIQUE (session_token);
ALTER TABLE ONLY public.menu_item_review ADD UNIQUE (order_line_id);
ALTER TABLE ONLY public.qr_code ADD UNIQUE (code);
ALTER TABLE ONLY public.user_point ADD UNIQUE (user_id);

-- =========================
-- FOREIGN KEYS
-- =========================

ALTER TABLE public.guest_session
    ADD FOREIGN KEY (qr_id) REFERENCES public.qr_code(id);

ALTER TABLE public.order_line
    ADD FOREIGN KEY (order_id) REFERENCES public.orders(id);

ALTER TABLE public.order_status_history
    ADD FOREIGN KEY (order_id) REFERENCES public.orders(id);

ALTER TABLE public.qr_code
    ADD FOREIGN KEY (restaurant_id) REFERENCES public.restaurants(id);

ALTER TABLE public.qr_code
    ADD FOREIGN KEY (table_id) REFERENCES public.restaurant_table(id);

ALTER TABLE public.restaurant_table
    ADD FOREIGN KEY (restaurant_id) REFERENCES public.restaurants(id);

ALTER TABLE public.restaurants
    ADD FOREIGN KEY (owner_id) REFERENCES public.app_user(id);