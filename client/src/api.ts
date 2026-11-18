import type { Driver, Shipment, ShipmentListResponse } from "./types";

function errorMessage(data: unknown, status: number): string {
  if (data && typeof data === "object" && "detail" in data) {
    const detail = (data as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
  }
  return `Request failed (${status})`;
}

async function request<T>(input: string, init?: RequestInit): Promise<T> {
  const res = await fetch(input, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(errorMessage(data, res.status));
  }
  return data as T;
}

export function fetchShipments(page = 1, limit = 10): Promise<ShipmentListResponse> {
  const params = new URLSearchParams({
    page: String(page),
    limit: String(limit),
  });
  return request<ShipmentListResponse>(`/api/shipments?${params.toString()}`);
}

export function fetchShipment(id: string): Promise<Shipment> {
  return request<Shipment>(`/api/shipments/${id}`);
}

export function updateShipment(
  id: string,
  body: { status?: Shipment["status"]; driver_id?: string | null },
): Promise<Shipment> {
  return request<Shipment>(`/api/shipments/${id}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export function fetchDrivers(): Promise<Driver[]> {
  return request<{ drivers: Driver[] }>("/api/drivers").then((data) => data.drivers);
}
