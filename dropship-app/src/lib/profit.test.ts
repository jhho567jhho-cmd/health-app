import { describe, expect, it } from "vitest";
import { calculateProfit, toNumber } from "./profit";

describe("calculateProfit", () => {
  it("מחשב רווח נקי אחרי עלות ועמלה", () => {
    const r = calculateProfit({ salePrice: 200, cost: 80, platformFeePct: 10 });
    expect(r).toEqual({ fee: 20, profit: 100, marginPct: 50 });
  });

  it("רווח שלילי כשההוצאות גבוהות מההכנסה", () => {
    const r = calculateProfit({ salePrice: 100, cost: 120, platformFeePct: 0 });
    expect(r.profit).toBe(-20);
    expect(r.marginPct).toBe(-20);
  });

  it("לא מחלק באפס כשאין מחיר מכירה", () => {
    const r = calculateProfit({ salePrice: 0, cost: 50, platformFeePct: 10 });
    expect(r.marginPct).toBe(0);
    expect(r.profit).toBe(-50);
  });

  it("מעגל לשתי ספרות אחרי הנקודה", () => {
    const r = calculateProfit({ salePrice: 33.33, cost: 10, platformFeePct: 7.5 });
    expect(r.fee).toBe(2.5);
    expect(r.profit).toBe(20.83);
  });
});

describe("toNumber", () => {
  it("ממיר פסיק עשרוני", () => {
    expect(toNumber("12,5")).toBe(12.5);
  });
  it("מחזיר 0 לקלט לא חוקי או שלילי", () => {
    expect(toNumber("")).toBe(0);
    expect(toNumber("abc")).toBe(0);
    expect(toNumber("-5")).toBe(0);
  });
});
