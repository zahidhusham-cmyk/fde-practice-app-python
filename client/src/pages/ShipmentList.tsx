import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { fetchDrivers, fetchShipments } from "../api";
import { ServiceBadge } from "../components/ServiceBadge";
import { StatusBadge } from "../components/StatusBadge";
import type { Driver, ShipmentListResponse } from "../types";

const PAGE_SIZE = 10;

function formatPromisedOn(value: string) {
  const [year, month, day] = value.split("-").map(Number);
  return new Date(year, month - 1, day).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
}

function driverName(drivers: Driver[], driverId: string | null) {
  if (!driverId) return "Unassigned";
  return drivers.find((driver) => driver.id === driverId)?.name ?? driverId;
}

function resultSummary(total: number, searching: boolean) {
  const noun = total === 1 ? "shipment" : "shipments";
  if (!searching) return `${total} ${noun} on the board`;
  return total === 1 ? "1 shipment matches" : `${total} shipments match`;
}

function routeLabel(
  originCity: string,
  originState: string,
  destinationCity: string,
  destinationState: string,
) {
  return `${originCity}, ${originState} → ${destinationCity}, ${destinationState}`;
}

export function ShipmentList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const page = Math.max(1, Number(searchParams.get("page")) || 1);
  const query = searchParams.get("q") ?? "";
  const [data, setData] = useState<ShipmentListResponse | null>(null);
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.all([fetchShipments(page, PAGE_SIZE, query), fetchDrivers()])
      .then(([shipmentPage, driverList]) => {
        if (cancelled) return;
        setData(shipmentPage);
        setDrivers(driverList);
        setError(null);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [page, query]);

  function listParams(nextPage: number, nextQuery: string) {
    const params: Record<string, string> = { page: String(nextPage) };
    if (nextQuery) params.q = nextQuery;
    return params;
  }

  function goToPage(next: number) {
    setSearchParams(listParams(next, query));
  }

  function onSearch(nextQuery: string) {
    setSearchParams(listParams(1, nextQuery));
  }

  return (
    <section>
      <div className="page-header">
        <div>
          <h1>Shipments</h1>
          <p className="muted">
            {data
              ? resultSummary(data.pagination.total, Boolean(query.trim()))
              : "Active freight for Harborline Dispatch"}
          </p>
        </div>
        <div className="header-actions">
          <Link to="/shipments/new" className="button">
            Book shipment
          </Link>
          <label className="search-field">
            Search
            <input
              type="search"
              value={query}
              placeholder="Customer, city, or ID"
              onChange={(event) => onSearch(event.target.value)}
            />
          </label>
        </div>
      </div>

      {error && <p className="banner error">{error}</p>}
      {loading && !data && <p className="muted">Loading shipments…</p>}

      {data && (
        <>
          <div className="table-wrap">
            <table className="shipment-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Customer</th>
                  <th>Route</th>
                  <th>Status</th>
                  <th>Service</th>
                  <th>Promised</th>
                  <th>Driver</th>
                </tr>
              </thead>
              <tbody>
                {data.shipments.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="empty">
                      {query.trim()
                        ? `No shipments match “${query.trim()}”.`
                        : "No shipments on this page."}
                    </td>
                  </tr>
                ) : (
                  data.shipments.map((shipment) => (
                    <tr key={shipment.id}>
                      <td className="mono">
                        <Link to={`/shipments/${shipment.id}`}>{shipment.id}</Link>
                      </td>
                      <td>
                        <Link to={`/shipments/${shipment.id}`}>{shipment.customer}</Link>
                      </td>
                      <td>
                        {routeLabel(
                          shipment.origin_city,
                          shipment.origin_state,
                          shipment.destination_city,
                          shipment.destination_state,
                        )}
                      </td>
                      <td>
                        <StatusBadge status={shipment.status} />
                      </td>
                      <td>
                        <ServiceBadge service={shipment.service_level} />
                      </td>
                      <td className="muted">{formatPromisedOn(shipment.promised_on)}</td>
                      <td>{driverName(drivers, shipment.driver_id)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <div className="pagination">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => goToPage(page - 1)}
            >
              Previous
            </button>
            <span className="muted">
              Page {data.pagination.page} of {data.pagination.total_pages}
            </span>
            <button
              type="button"
              disabled={page >= data.pagination.total_pages}
              onClick={() => goToPage(page + 1)}
            >
              Next
            </button>
          </div>
        </>
      )}
    </section>
  );
}
