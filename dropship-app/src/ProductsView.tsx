import { useEffect, useState, type FormEvent } from "react";
import { supabase } from "./supabase";
import { calculateProfit, toNumber } from "./lib/profit";
import {
  PRODUCT_STATUSES,
  PRODUCT_STATUS_LABELS,
  type Product,
  type ProductStatus,
} from "./types";

const money = (n: number) => `₪${n.toFixed(2)}`;

const emptyForm = {
  name: "",
  source_url: "",
  supplier: "AliExpress",
  cost: "",
  sale_price: "",
  platform_fee_pct: "",
  status: "idea" as ProductStatus,
  notes: "",
};

export function ProductsView() {
  const [products, setProducts] = useState<Product[]>([]);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    const { data, error } = await supabase!
      .from("products")
      .select("*")
      .order("created_at", { ascending: false });
    if (error) setError(error.message);
    else setProducts((data ?? []) as Product[]);
  }

  useEffect(() => {
    load();
  }, []);

  async function addProduct(e: FormEvent) {
    e.preventDefault();
    setError(null);
    const { error } = await supabase!.from("products").insert({
      name: form.name.trim(),
      source_url: form.source_url.trim() || null,
      supplier: form.supplier.trim() || null,
      cost: toNumber(form.cost),
      sale_price: toNumber(form.sale_price),
      platform_fee_pct: toNumber(form.platform_fee_pct),
      status: form.status,
      notes: form.notes.trim() || null,
    });
    if (error) {
      setError(error.message);
      return;
    }
    setForm(emptyForm);
    load();
  }

  async function updateStatus(id: string, status: ProductStatus) {
    const { error } = await supabase!
      .from("products")
      .update({ status, updated_at: new Date().toISOString() })
      .eq("id", id);
    if (error) setError(error.message);
    else load();
  }

  async function remove(id: string) {
    if (!confirm("למחוק את המוצר?")) return;
    const { error } = await supabase!.from("products").delete().eq("id", id);
    if (error) setError(error.message);
    else load();
  }

  const set = (key: keyof typeof emptyForm) => (value: string) =>
    setForm((f) => ({ ...f, [key]: value }));

  const preview = calculateProfit({
    salePrice: toNumber(form.sale_price),
    cost: toNumber(form.cost),
    platformFeePct: toNumber(form.platform_fee_pct),
  });

  return (
    <div>
      <form className="card grid" onSubmit={addProduct}>
        <h2>מוצר חדש</h2>
        <label className="wide">
          שם המוצר
          <input value={form.name} onChange={(e) => set("name")(e.target.value)} required />
        </label>
        <label className="wide">
          קישור למקור (AliExpress / eBay)
          <input type="url" value={form.source_url} onChange={(e) => set("source_url")(e.target.value)} />
        </label>
        <label>
          ספק
          <input value={form.supplier} onChange={(e) => set("supplier")(e.target.value)} />
        </label>
        <label>
          סטטוס
          <select value={form.status} onChange={(e) => set("status")(e.target.value)}>
            {PRODUCT_STATUSES.map((s) => (
              <option key={s} value={s}>
                {PRODUCT_STATUS_LABELS[s]}
              </option>
            ))}
          </select>
        </label>
        <label>
          עלות כוללת מהספק (₪)
          <input inputMode="decimal" value={form.cost} onChange={(e) => set("cost")(e.target.value)} />
        </label>
        <label>
          מחיר מכירה (₪)
          <input inputMode="decimal" value={form.sale_price} onChange={(e) => set("sale_price")(e.target.value)} />
        </label>
        <label>
          עמלת פלטפורמה (%)
          <input inputMode="decimal" value={form.platform_fee_pct} onChange={(e) => set("platform_fee_pct")(e.target.value)} />
        </label>
        <div className="preview">
          רווח משוער: <strong>{money(preview.profit)}</strong> ({preview.marginPct}%)
        </div>
        <label className="wide">
          הערות
          <textarea value={form.notes} onChange={(e) => set("notes")(e.target.value)} />
        </label>
        {error && <p className="error wide">{error}</p>}
        <button type="submit" className="wide">
          הוספה
        </button>
      </form>

      <h2>רשימת מוצרים ({products.length})</h2>
      {products.length === 0 && <p className="muted">עדיין אין מוצרים. מוסיפים את הראשון למעלה.</p>}
      {products.map((p) => {
        const r = calculateProfit({ salePrice: p.sale_price, cost: p.cost, platformFeePct: p.platform_fee_pct });
        return (
          <div className="card product" key={p.id}>
            <div className="row">
              <strong>{p.name}</strong>
              <select value={p.status} onChange={(e) => updateStatus(p.id, e.target.value as ProductStatus)}>
                {PRODUCT_STATUSES.map((s) => (
                  <option key={s} value={s}>
                    {PRODUCT_STATUS_LABELS[s]}
                  </option>
                ))}
              </select>
            </div>
            <div className="muted">
              {p.supplier && <>{p.supplier} · </>}
              עלות {money(p.cost)} · מכירה {money(p.sale_price)} · עמלה {money(r.fee)} ·{" "}
              <strong className={r.profit >= 0 ? "good" : "bad"}>
                רווח {money(r.profit)} ({r.marginPct}%)
              </strong>
            </div>
            {p.notes && <p>{p.notes}</p>}
            <div className="row">
              {p.source_url && (
                <a href={p.source_url} target="_blank" rel="noreferrer">
                  לקישור המקור
                </a>
              )}
              <button className="link danger" onClick={() => remove(p.id)}>
                מחיקה
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
