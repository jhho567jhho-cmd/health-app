import { useEffect, useState, type FormEvent } from "react";
import { supabase } from "./supabase";
import { calculateProfit, toNumber } from "./lib/profit";
import { ORDER_STATUSES, ORDER_STATUS_LABELS, type Order, type OrderStatus } from "./types";

const money = (n: number) => `₪${n.toFixed(2)}`;
const today = () => new Date().toISOString().slice(0, 10);

const emptyForm = {
  product_name: "",
  sale_price: "",
  cost: "",
  platform_fee_pct: "",
  status: "ordered" as OrderStatus,
  supplier_order_id: "",
  tracking_number: "",
  ordered_at: today(),
  notes: "",
};

export function OrdersView() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    const { data, error } = await supabase!
      .from("orders")
      .select("*")
      .order("ordered_at", { ascending: false });
    if (error) setError(error.message);
    else setOrders((data ?? []) as Order[]);
  }

  useEffect(() => {
    load();
  }, []);

  async function addOrder(e: FormEvent) {
    e.preventDefault();
    setError(null);
    const { error } = await supabase!.from("orders").insert({
      product_name: form.product_name.trim(),
      sale_price: toNumber(form.sale_price),
      cost: toNumber(form.cost),
      platform_fee_pct: toNumber(form.platform_fee_pct),
      status: form.status,
      supplier_order_id: form.supplier_order_id.trim() || null,
      tracking_number: form.tracking_number.trim() || null,
      ordered_at: form.ordered_at,
      notes: form.notes.trim() || null,
    });
    if (error) {
      setError(error.message);
      return;
    }
    setForm(emptyForm);
    load();
  }

  async function updateStatus(id: string, status: OrderStatus) {
    const { error } = await supabase!.from("orders").update({ status }).eq("id", id);
    if (error) setError(error.message);
    else load();
  }

  async function remove(id: string) {
    if (!confirm("למחוק את ההזמנה?")) return;
    const { error } = await supabase!.from("orders").delete().eq("id", id);
    if (error) setError(error.message);
    else load();
  }

  const set = (key: keyof typeof emptyForm) => (value: string) =>
    setForm((f) => ({ ...f, [key]: value }));

  // סיכום: מסופרות רק הזמנות שלא בוטלו או הוחזרו
  const counted = orders.filter((o) => o.status !== "cancelled" && o.status !== "returned");
  const totals = counted.reduce(
    (acc, o) => {
      const r = calculateProfit({ salePrice: o.sale_price, cost: o.cost, platformFeePct: o.platform_fee_pct });
      acc.revenue += o.sale_price;
      acc.profit += r.profit;
      return acc;
    },
    { revenue: 0, profit: 0 },
  );

  return (
    <div>
      <div className="card summary">
        <div>
          הזמנות פעילות: <strong>{counted.length}</strong>
        </div>
        <div>
          הכנסות: <strong>{money(totals.revenue)}</strong>
        </div>
        <div>
          רווח נקי: <strong className={totals.profit >= 0 ? "good" : "bad"}>{money(totals.profit)}</strong>
        </div>
      </div>

      <form className="card grid" onSubmit={addOrder}>
        <h2>הזמנה חדשה</h2>
        <label className="wide">
          שם המוצר
          <input value={form.product_name} onChange={(e) => set("product_name")(e.target.value)} required />
        </label>
        <label>
          מחיר שהלקוח שילם (₪)
          <input inputMode="decimal" value={form.sale_price} onChange={(e) => set("sale_price")(e.target.value)} />
        </label>
        <label>
          מה שילמנו לספק (₪)
          <input inputMode="decimal" value={form.cost} onChange={(e) => set("cost")(e.target.value)} />
        </label>
        <label>
          עמלת פלטפורמה (%)
          <input inputMode="decimal" value={form.platform_fee_pct} onChange={(e) => set("platform_fee_pct")(e.target.value)} />
        </label>
        <label>
          תאריך
          <input type="date" value={form.ordered_at} onChange={(e) => set("ordered_at")(e.target.value)} />
        </label>
        <label>
          מספר הזמנה אצל הספק
          <input value={form.supplier_order_id} onChange={(e) => set("supplier_order_id")(e.target.value)} />
        </label>
        <label>
          מספר מעקב
          <input value={form.tracking_number} onChange={(e) => set("tracking_number")(e.target.value)} />
        </label>
        <label>
          סטטוס
          <select value={form.status} onChange={(e) => set("status")(e.target.value)}>
            {ORDER_STATUSES.map((s) => (
              <option key={s} value={s}>
                {ORDER_STATUS_LABELS[s]}
              </option>
            ))}
          </select>
        </label>
        <label className="wide">
          הערות
          <textarea value={form.notes} onChange={(e) => set("notes")(e.target.value)} />
        </label>
        {error && <p className="error wide">{error}</p>}
        <button type="submit" className="wide">
          הוספה
        </button>
      </form>

      <h2>הזמנות ({orders.length})</h2>
      {orders.length === 0 && <p className="muted">עדיין אין הזמנות.</p>}
      {orders.map((o) => {
        const r = calculateProfit({ salePrice: o.sale_price, cost: o.cost, platformFeePct: o.platform_fee_pct });
        return (
          <div className="card product" key={o.id}>
            <div className="row">
              <strong>{o.product_name}</strong>
              <select value={o.status} onChange={(e) => updateStatus(o.id, e.target.value as OrderStatus)}>
                {ORDER_STATUSES.map((s) => (
                  <option key={s} value={s}>
                    {ORDER_STATUS_LABELS[s]}
                  </option>
                ))}
              </select>
            </div>
            <div className="muted">
              {o.ordered_at} · מכירה {money(o.sale_price)} · עלות {money(o.cost)} · עמלה {money(r.fee)} ·{" "}
              <strong className={r.profit >= 0 ? "good" : "bad"}>רווח {money(r.profit)}</strong>
            </div>
            {o.tracking_number && <div className="muted">מעקב: {o.tracking_number}</div>}
            {o.supplier_order_id && <div className="muted">הזמנה אצל הספק: {o.supplier_order_id}</div>}
            {o.notes && <p>{o.notes}</p>}
            <div className="row">
              <button className="link danger" onClick={() => remove(o.id)}>
                מחיקה
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
