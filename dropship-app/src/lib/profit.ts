export interface Economics {
  salePrice: number;
  cost: number;
  platformFeePct: number;
}

export interface Profit {
  fee: number;
  profit: number;
  /** רווח כאחוז ממחיר המכירה; 0 אם אין מחיר מכירה */
  marginPct: number;
}

const round2 = (n: number) => Math.round(n * 100) / 100;

/** מחשב עמלה, רווח נקי ואחוז רווח. כל הסכומים באותה מטבע (₪). */
export function calculateProfit({ salePrice, cost, platformFeePct }: Economics): Profit {
  const fee = round2((salePrice * platformFeePct) / 100);
  const profit = round2(salePrice - cost - fee);
  const marginPct = salePrice > 0 ? round2((profit / salePrice) * 100) : 0;
  return { fee, profit, marginPct };
}

/** מחזיר מספר תקין או 0 (למשל לשדות טופס ריקים או לא חוקיים). */
export function toNumber(value: string): number {
  const n = Number(value.replace(",", "."));
  return Number.isFinite(n) && n >= 0 ? n : 0;
}
