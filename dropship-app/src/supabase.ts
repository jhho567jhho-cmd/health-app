import { createClient } from "@supabase/supabase-js";

const url = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;

export const isConfigured = Boolean(url && anonKey);

// כשחסרה תצורה לא יוצרים לקוח, והאפליקציה מציגה הודעה מתאימה במקום לקרוס.
export const supabase = isConfigured ? createClient(url!, anonKey!) : null;
