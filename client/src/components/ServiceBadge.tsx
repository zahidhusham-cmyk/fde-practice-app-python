import type { ServiceLevel } from "../types";

const LABELS: Record<ServiceLevel, string> = {
  standard: "Standard",
  expedited: "Expedited",
  overnight: "Overnight",
};

export function ServiceBadge({ service }: { service: ServiceLevel }) {
  return (
    <span className={`badge service-${service}`}>{LABELS[service]}</span>
  );
}
