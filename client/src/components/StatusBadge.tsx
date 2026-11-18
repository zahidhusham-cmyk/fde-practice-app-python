import type { Status } from "../types";

const LABELS: Record<Status, string> = {
  booked: "Booked",
  at_origin: "At origin",
  in_transit: "In transit",
  at_hub: "At hub",
  out_for_delivery: "Out for delivery",
  delivered: "Delivered",
  delayed: "Delayed",
  cancelled: "Cancelled",
};

export function StatusBadge({ status }: { status: Status }) {
  return <span className={`badge status-${status}`}>{LABELS[status]}</span>;
}
