import type { Driver, Shipment, ShipmentListResponse } from "./types";

function errorMessage(data: unknown, status: number): string {
  if (data && typeof data === "object" && "detail" in data) {
    const detail = (data as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      const messages = detail.flatMap((item) => {
        if (item && typeof item === "object" && "msg" in item) {
          const message = (item as { msg: unknown }).msg;
          return typeof message === "string" ? [message] : [];
        }
        return [];
      });
      if (messages.length > 0) return messages.join(" ");
    }
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

export function fetchShipments(
  page = 1,
  limit = 10,
  query = "",
): Promise<ShipmentListResponse> {
  const params = new URLSearchParams({
    page: String(page),
    limit: String(limit),
  });
  const trimmed = query.trim();
  if (trimmed) params.set("q", trimmed);
  return request<ShipmentListResponse>(`/api/shipments?${params.toString()}`);
}

export interface NewShipment {
  customer: string;
  origin_city: string;
  origin_state: string;
  destination_city: string;
  destination_state: string;
  service_level: Shipment["service_level"];
  promised_on: string;
  weight_lb: number;
  pieces: number;
  driver_id?: string | null;
  notes?: string;
}

export function createShipment(body: NewShipment): Promise<Shipment> {
  return request<Shipment>("/api/shipments", {
    method: "POST",
    body: JSON.stringify(body),
  });
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
