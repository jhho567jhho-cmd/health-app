import { useEffect, useState, type FormEvent } from "react";
import type { Session } from "@supabase/supabase-js";
import { isConfigured, supabase } from "./supabase";
import { ProductsView } from "./ProductsView";
import { OrdersView } from "./OrdersView";

type Tab = "products" | "orders";

export default function App() {
  if (!isConfigured || !supabase) {
    return (
      <div className="center-page">
        <div className="card">
          <h1>חסרה הגדרה</h1>
          <p>
            צריך ליצור קובץ <code>.env.local</code> עם <code>VITE_SUPABASE_URL</code> ו-
            <code>VITE_SUPABASE_ANON_KEY</code>. ראו את <code>README.md</code>.
          </p>
        </div>
      </div>
    );
  }
  return <Gate />;
}

function Gate() {
  const [session, setSession] = useState<Session | null | undefined>(undefined);

  useEffect(() => {
    supabase!.auth.getSession().then(({ data }) => setSession(data.session));
    const { data } = supabase!.auth.onAuthStateChange((_event, s) => setSession(s));
    return () => data.subscription.unsubscribe();
  }, []);

  if (session === undefined) return <div className="center-page">טוען...</div>;
  if (!session) return <LoginForm />;
  return <Shell email={session.user.email ?? ""} />;
}

function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    const { error } = await supabase!.auth.signInWithPassword({ email, password });
    if (error) setError("ההתחברות נכשלה. בדקו אימייל וסיסמה.");
    setBusy(false);
  }

  return (
    <div className="center-page">
      <form className="card login" onSubmit={onSubmit}>
        <h1>דרופשיפינג משותף</h1>
        <label>
          אימייל
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          סיסמה
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={busy}>
          {busy ? "מתחבר..." : "כניסה"}
        </button>
      </form>
    </div>
  );
}

function Shell({ email }: { email: string }) {
  const [tab, setTab] = useState<Tab>("products");

  return (
    <div className="app">
      <header className="topbar">
        <strong>דרופשיפינג משותף</strong>
        <span className="who">
          {email}{" "}
          <button className="link" onClick={() => supabase!.auth.signOut()}>
            יציאה
          </button>
        </span>
      </header>
      <nav className="tabs">
        <button className={tab === "products" ? "active" : ""} onClick={() => setTab("products")}>
          מוצרים
        </button>
        <button className={tab === "orders" ? "active" : ""} onClick={() => setTab("orders")}>
          הזמנות
        </button>
      </nav>
      <main>{tab === "products" ? <ProductsView /> : <OrdersView />}</main>
    </div>
  );
}
