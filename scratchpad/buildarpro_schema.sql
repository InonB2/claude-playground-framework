-- ============================================================
-- BuildARPro — 5-Table Schema Migration
-- Source: buildarpro_architecture_research.md Q9
-- Prepared by: Silas (Database Agent)
-- Date: 2026-05-02
-- Target: New Supabase project (see buildarpro_schema_done.md for deployment notes)
-- ============================================================

-- ----------------------------------------------------------------
-- TABLE 1: users
-- Extension of Supabase Auth (auth.users). Stores profile data.
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.users (
  id          uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email       text NOT NULL,
  full_name   text,
  created_at  timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Users can read and update only their own profile
CREATE POLICY "users_select_own" ON public.users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "users_update_own" ON public.users
  FOR UPDATE USING (auth.uid() = id);

-- Auto-insert user profile on signup (triggered by auth.users insert)
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER SET search_path = public
AS $$
BEGIN
  INSERT INTO public.users (id, email, full_name)
  VALUES (
    NEW.id,
    NEW.email,
    NEW.raw_user_meta_data->>'full_name'
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ----------------------------------------------------------------
-- TABLE 2: guides
-- Core product catalog — one row per AR guide.
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.guides (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id            uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  title               text NOT NULL,
  description         text,
  product_sku         text,
  vuforia_target_id   text,
  steps               jsonb,
  is_published        boolean NOT NULL DEFAULT false,
  created_at          timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS guides_owner_id_idx ON public.guides(owner_id);
CREATE INDEX IF NOT EXISTS guides_is_published_idx ON public.guides(is_published);
CREATE INDEX IF NOT EXISTS guides_product_sku_idx ON public.guides(product_sku);

ALTER TABLE public.guides ENABLE ROW LEVEL SECURITY;

-- Guide owners can do full CRUD on their own guides
CREATE POLICY "guides_owner_all" ON public.guides
  FOR ALL USING (auth.uid() = owner_id);

-- Any authenticated user can read published guides
CREATE POLICY "guides_published_read" ON public.guides
  FOR SELECT USING (is_published = true AND auth.role() = 'authenticated');

-- ----------------------------------------------------------------
-- TABLE 3: image_targets
-- Vuforia target registry — links physical targets to guides.
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.image_targets (
  id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  guide_id              uuid NOT NULL REFERENCES public.guides(id) ON DELETE CASCADE,
  vuforia_target_name   text NOT NULL,
  target_type           text NOT NULL CHECK (target_type IN ('image', 'model')),
  rating                int CHECK (rating >= 0 AND rating <= 5),
  metadata_json         jsonb,
  uploaded_at           timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS image_targets_guide_id_idx ON public.image_targets(guide_id);

ALTER TABLE public.image_targets ENABLE ROW LEVEL SECURITY;

-- Only guide owners can manage their targets
CREATE POLICY "image_targets_owner_all" ON public.image_targets
  FOR ALL USING (
    auth.uid() = (SELECT owner_id FROM public.guides WHERE id = guide_id)
  );

-- Authenticated users can read targets for published guides
CREATE POLICY "image_targets_published_read" ON public.image_targets
  FOR SELECT USING (
    (SELECT is_published FROM public.guides WHERE id = guide_id) = true
    AND auth.role() = 'authenticated'
  );

-- ----------------------------------------------------------------
-- TABLE 4: subscriptions
-- Mirrors Stripe subscription state per user.
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.subscriptions (
  id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id               uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  stripe_customer_id    text,
  stripe_sub_id         text,
  plan_tier             text NOT NULL DEFAULT 'free'
                          CHECK (plan_tier IN ('free', 'pro', 'team', 'enterprise')),
  status                text NOT NULL DEFAULT 'active'
                          CHECK (status IN ('active', 'past_due', 'canceled', 'trialing')),
  guides_limit          int NOT NULL DEFAULT 1,  -- 1 for free, -1 for unlimited
  current_period_end    timestamptz,
  created_at            timestamptz NOT NULL DEFAULT now(),
  UNIQUE (user_id)  -- one active subscription per user
);

CREATE INDEX IF NOT EXISTS subscriptions_user_id_idx ON public.subscriptions(user_id);
CREATE INDEX IF NOT EXISTS subscriptions_stripe_customer_id_idx ON public.subscriptions(stripe_customer_id);

ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

-- Users can only read their own subscription
CREATE POLICY "subscriptions_select_own" ON public.subscriptions
  FOR SELECT USING (auth.uid() = user_id);

-- Only service role (Stripe webhook Edge Function) can insert/update subscriptions
CREATE POLICY "subscriptions_service_write" ON public.subscriptions
  FOR ALL USING (auth.role() = 'service_role');

-- ----------------------------------------------------------------
-- TABLE 5: guide_views
-- Usage analytics — one row per view event.
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.guide_views (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  guide_id    uuid NOT NULL REFERENCES public.guides(id) ON DELETE CASCADE,
  user_id     uuid REFERENCES public.users(id) ON DELETE SET NULL,  -- nullable for anonymous
  viewed_at   timestamptz NOT NULL DEFAULT now(),
  device_os   text
);

CREATE INDEX IF NOT EXISTS guide_views_guide_id_idx ON public.guide_views(guide_id);
CREATE INDEX IF NOT EXISTS guide_views_user_id_idx ON public.guide_views(user_id);
CREATE INDEX IF NOT EXISTS guide_views_viewed_at_idx ON public.guide_views(viewed_at);

ALTER TABLE public.guide_views ENABLE ROW LEVEL SECURITY;

-- Guide owners can read view analytics for their guides
CREATE POLICY "guide_views_owner_read" ON public.guide_views
  FOR SELECT USING (
    auth.uid() = (SELECT owner_id FROM public.guides WHERE id = guide_id)
  );

-- Any authenticated user (or anonymous via service role) can insert a view
CREATE POLICY "guide_views_insert_authenticated" ON public.guide_views
  FOR INSERT WITH CHECK (auth.role() IN ('authenticated', 'service_role', 'anon'));

-- ============================================================
-- END OF MIGRATION
-- Tables: users, guides, image_targets, subscriptions, guide_views
-- RLS: ENABLED on all 5 tables
-- ============================================================
