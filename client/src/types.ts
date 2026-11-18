export const STATUSES = [
  "booked",
  "at_origin",
  "in_transit",
  "at_hub",
  "out_for_delivery",
  "delivered",
  "delayed",
  "cancelled",
] as const;

export const SERVICE_LEVELS = ["standard", "expedited", "overnight"] as const;

export type Status = (typeof STATUSES)[number];
export type ServiceLevel = (typeof SERVICE_LEVELS)[number];

export interface Driver {
  id: string;
  name: string;
  email: string;
  region: string;
  vehicle: string;
}

export interface ShipmentEvent {
  id: number;
  timestamp: string;
  location: string | null;
  message: string;
}

export interface Shipment {
  id: string;
  customer: string;
  origin_city: string;
  origin_state: string;
  destination_city: string;
  destination_state: string;
  status: Status;
  service_level: ServiceLevel;
  promised_on: string;
  weight_lb: number;
  pieces: number;
  driver_id: string | null;
  created_at: string;
  updated_at: string;
  notes?: string;
  events?: ShipmentEvent[];
}

export interface Pagination {
  page: number;
  limit: number;
  total: number;
  total_pages: number;
}

export interface ShipmentListResponse {
  shipments: Shipment[];
  pagination: Pagination;
}
