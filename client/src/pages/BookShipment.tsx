import { useEffect, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createShipment, fetchDrivers } from "../api";
import { SERVICE_LEVELS, type Driver, type ServiceLevel } from "../types";

export function BookShipment() {
  const navigate = useNavigate();
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [customer, setCustomer] = useState("");
  const [originCity, setOriginCity] = useState("");
  const [originState, setOriginState] = useState("");
  const [destinationCity, setDestinationCity] = useState("");
  const [destinationState, setDestinationState] = useState("");
  const [serviceLevel, setServiceLevel] = useState<ServiceLevel>("standard");
  const [promisedOn, setPromisedOn] = useState("");
  const [weightLb, setWeightLb] = useState("");
  const [pieces, setPieces] = useState("");
  const [driverId, setDriverId] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetchDrivers()
      .then((driverList) => {
        if (!cancelled) setDrivers(driverList);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const created = await createShipment({
        customer,
        origin_city: originCity,
        origin_state: originState,
        destination_city: destinationCity,
        destination_state: destinationState,
        service_level: serviceLevel,
        promised_on: promisedOn,
        weight_lb: Number(weightLb),
        pieces: Number(pieces),
        driver_id: driverId === "" ? null : driverId,
        notes,
      });
      navigate(`/shipments/${created.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not book shipment");
      setSaving(false);
    }
  }

  return (
    <section>
      <p className="crumb">
        <Link to="/">Shipments</Link>
        <span aria-hidden="true"> / </span>
        <span>Book shipment</span>
      </p>
      <div className="page-header">
        <div>
          <h1>Book shipment</h1>
          <p className="muted">New freight starts as booked.</p>
        </div>
      </div>

      {error && <p className="banner error">{error}</p>}

      <form className="card book-form" onSubmit={onSubmit}>
        <label className="span-2">
          Customer
          <input value={customer} onChange={(event) => setCustomer(event.target.value)} required />
        </label>
        <label>
          Origin city
          <input
            value={originCity}
            onChange={(event) => setOriginCity(event.target.value)}
            required
          />
        </label>
        <label>
          Origin state
          <input
            value={originState}
            onChange={(event) => setOriginState(event.target.value)}
            maxLength={2}
            required
          />
        </label>
        <label>
          Destination city
          <input
            value={destinationCity}
            onChange={(event) => setDestinationCity(event.target.value)}
            required
          />
        </label>
        <label>
          Destination state
          <input
            value={destinationState}
            onChange={(event) => setDestinationState(event.target.value)}
            maxLength={2}
            required
          />
        </label>
        <label>
          Service
          <select
            value={serviceLevel}
            onChange={(event) => setServiceLevel(event.target.value as ServiceLevel)}
          >
            {SERVICE_LEVELS.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <label>
          Promised on
          <input
            type="date"
            value={promisedOn}
            onChange={(event) => setPromisedOn(event.target.value)}
            required
          />
        </label>
        <label>
          Weight (lb)
          <input
            type="number"
            min={1}
            value={weightLb}
            onChange={(event) => setWeightLb(event.target.value)}
            required
          />
        </label>
        <label>
          Pieces
          <input
            type="number"
            min={1}
            value={pieces}
            onChange={(event) => setPieces(event.target.value)}
            required
          />
        </label>
        <label className="span-2">
          Driver
          <select value={driverId} onChange={(event) => setDriverId(event.target.value)}>
            <option value="">Unassigned</option>
            {drivers.map((driver) => (
              <option key={driver.id} value={driver.id}>
                {driver.name} ({driver.region})
              </option>
            ))}
          </select>
        </label>
        <label className="span-2">
          Notes
          <textarea value={notes} onChange={(event) => setNotes(event.target.value)} rows={3} />
        </label>
        <div className="span-2">
          <button type="submit" disabled={saving}>
            {saving ? "Booking…" : "Book shipment"}
          </button>
        </div>
      </form>
    </section>
  );
}
