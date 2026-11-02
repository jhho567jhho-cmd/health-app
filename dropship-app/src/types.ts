export const PRODUCT_STATUSES = ["idea", "checking", "listed", "sold", "dropped"] as const;
export type ProductStatus = (typeof PRODUCT_STATUSES)[number];

export const ORDER_STATUSES = ["ordered", "shipped", "delivered", "returned", "cancelled"] as const;
export type OrderStatus = (typeof ORDER_STATUSES)[number];

export const PRODUCT_STATUS_LABELS: Record<ProductStatus, string> = {
  idea: "רעיון",
  checking: "בבדיקה",
  listed: "באתר",
  sold: "נמכר",
  dropped: "נזנח",
};

export const ORDER_STATUS_LABELS: Record<OrderStatus, string> = {
  ordered: "הוזמן מהספק",
  shipped: "בדרך",
  delivered: "נמסר",
  returned: "הוחזר",
  cancelled: "בוטל",
};

export interface Product {
  id: string;
  name: string;
  source_url: string | null;
  supplier: string | null;
  cost: number;
  sale_price: number;
  platform_fee_pct: number;
  status: ProductStatus;
  notes: string | null;
  created_at: string;
}

export interface Order {
  id: string;
  product_id: string | null;
  product_name: string;
  sale_price: number;
  cost: number;
  platform_fee_pct: number;
  status: OrderStatus;
  supplier_order_id: string | null;
  tracking_number: string | null;
  ordered_at: string;
  notes: string | null;
  created_at: string;
}
