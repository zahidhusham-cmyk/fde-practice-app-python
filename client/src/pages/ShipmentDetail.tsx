import { useEffect, useMemo, useState, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchDrivers, fetchShipment, updateShipment } from "../api";
import { ServiceBadge } from "../components/ServiceBadge";
import { StatusBadge } from "../components/StatusBadge";
import { STATUSES, type Driver, type Shipment, type Status } from "../types";

function formatPromisedOn(value: string) {
  const [year, month, day] = value.split("-").map(Number);
  return new Date(year, month - 1, day).toLocaleDateString(undefined, {
    dateStyle: "medium",
  });
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function statusLabel(status: Status) {
  return status.replace(/_/g, " ");
}

export function ShipmentDetail() {
  const { id } = useParams();
  const [shipment, setShipment] = useState<Shipment | null>(null);
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [status, setStatus] = useState<Status>("booked");
  const [driverId, setDriverId] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setLoading(true);
    Promise.all([fetchShipment(id), fetchDrivers()])
      .then(([nextShipment, driverList]) => {
        if (cancelled) return;
        setShipment(nextShipment);
        setStatus(nextShipment.status);
        setDriverId(nextShipment.driver_id ?? "");
        setDrivers(driverList);
        setError(null);
      })
      .catch((err: Error) => {
        if (!cancelled) {
          setShipment(null);
          setError(err.message);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  const assignedName = useMemo(() => {
    if (!shipment?.driver_id) return "Unassigned";
    return (
      drivers.find((driver) => driver.id === shipment.driver_id)?.name ??
      shipment.driver_id
    );
  }, [drivers, shipment]);

  async function onSave(event: FormEvent) {
    event.preventDefault();
    if (!shipment) return;
    setSaving(true);
    setNotice(null);
    setError(null);
    try {
      const updated = await updateShipment(shipment.id, {
        status,
        driver_id: driverId === "" ? null : driverId,
      });
      setShipment(updated);
      setStatus(updated.status);
      setDriverId(updated.driver_id ?? "");
      setNotice("Shipment updated.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update shipment");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <p className="muted">Loading shipment…</p>;
  }

  if (!shipment) {
    return (
      <section>
        <p className="banner error">{error ?? "Shipment not found"}</p>
        <Link to="/">Back to shipments</Link>
      </section>
    );
  }

  const events = shipment.events ?? [];

  return (
    <section>
      <p className="crumb">
        <Link to="/">Shipments</Link>
        <span aria-hidden="true"> / </span>
        <span className="mono">{shipment.id}</span>
      </p>

      <div className="page-header">
        <div>
          <h1>{shipment.customer}</h1>
          <p className="muted">
            {shipment.origin_city}, {shipment.origin_state} → {shipment.destination_city},{" "}
            {shipment.destination_state}
          </p>
        </div>
        <div className="badge-row">
          <StatusBadge status={shipment.status} />
          <ServiceBadge service={shipment.service_level} />
        </div>
      </div>

      {error && <p className="banner error">{error}</p>}
      {notice && <p className="banner ok">{notice}</p>}

      <div className="detail-grid">
        <article className="card">
          <h2>Notes</h2>
          <p className="body-text">{shipment.notes || "No notes."}</p>

          <h2>Tracking events</h2>
          {events.length === 0 ? (
            <p className="muted">No tracking events yet.</p>
          ) : (
            <ul className="event-list">
              {events.map((event) => (
                <li key={event.id}>
                  <div className="event-meta">
                    <strong>{event.location ?? "Update"}</strong>
                    <span className="muted">{formatDateTime(event.timestamp)}</span>
                  </div>
                  <p>{event.message}</p>
                </li>
              ))}
            </ul>
          )}
        </article>

        <aside className="card">
          <h2>Details</h2>
          <dl className="meta-list">
            <div>
              <dt>Promised on</dt>
              <dd>{formatPromisedOn(shipment.promised_on)}</dd>
            </div>
            <div>
              <dt>Weight</dt>
              <dd>
                {shipment.weight_lb.toLocaleString()} lb · {shipment.pieces}{" "}
                {shipment.pieces === 1 ? "piece" : "pieces"}
              </dd>
            </div>
            <div>
              <dt>Driver</dt>
              <dd>{assignedName}</dd>
            </div>
            <div>
              <dt>Last updated</dt>
              <dd>{formatDateTime(shipment.updated_at)}</dd>
            </div>
          </dl>

          <form className="update-form" onSubmit={onSave}>
            <label>
              Status
              <select
                value={status}
                onChange={(event) => setStatus(event.target.value as Status)}
              >
                {STATUSES.map((value) => (
                  <option key={value} value={value}>
                    {statusLabel(value)}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Driver
              <select
                value={driverId}
                onChange={(event) => setDriverId(event.target.value)}
              >
                <option value="">Unassigned</option>
                {drivers.map((driver) => (
                  <option key={driver.id} value={driver.id}>
                    {driver.name} ({driver.region})
                  </option>
                ))}
              </select>
            </label>
            <button type="submit" disabled={saving}>
              {saving ? "Saving…" : "Save changes"}
            </button>
          </form>
        </aside>
      </div>
    </section>
  );
}
