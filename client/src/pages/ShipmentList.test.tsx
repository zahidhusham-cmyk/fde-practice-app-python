import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, it, vi } from "vitest";
import type { Shipment, ShipmentListResponse } from "../types";
import { ShipmentList } from "./ShipmentList";

const DRIVERS = {
  drivers: [
    {
      id: "drv-maya",
      name: "Maya Chen",
      email: "maya@example.com",
      region: "East",
      vehicle: "Van",
    },
  ],
};

const MAPLE: Shipment = {
  id: "HL-4401",
  customer: "Maple & Co",
  origin_city: "Boston",
  origin_state: "MA",
  destination_city: "Portland",
  destination_state: "ME",
  status: "booked",
  service_level: "standard",
  promised_on: "2026-11-20",
  weight_lb: 100,
  pieces: 1,
  driver_id: null,
  created_at: "2026-11-01T00:00:00Z",
  updated_at: "2026-11-01T00:00:00Z",
};

function page(shipments: Shipment[], total = shipments.length): ShipmentListResponse {
  return {
    shipments,
    pagination: { page: 1, limit: 10, total, total_pages: 1 },
  };
}

function installFetch(onShipments: (query: string | null) => ShipmentListResponse) {
  const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
    const url = new URL(String(input), "http://localhost");
    const body = url.pathname === "/api/drivers" ? DRIVERS : onShipments(url.searchParams.get("q"));
    return new Response(JSON.stringify(body), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function renderList(path = "/") {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <ShipmentList />
    </MemoryRouter>,
  );
}

function shipmentRequests(fetchMock: ReturnType<typeof installFetch>) {
  return fetchMock.mock.calls
    .map(([input]) => String(input))
    .filter((url) => url.startsWith("/api/shipments"));
}

afterEach(() => {
  vi.unstubAllGlobals();
});

it("shows an empty result when the search matches nothing", async () => {
  const user = userEvent.setup();
  installFetch((query) => (query ? page([]) : page([MAPLE], 28)));
  renderList();

  expect(await screen.findByRole("link", { name: "Maple & Co" })).toBeTruthy();

  await user.type(screen.getByRole("searchbox", { name: "Search" }), "no-such-customer");

  expect(await screen.findByText("No shipments match “no-such-customer”.")).toBeTruthy();
  expect(screen.queryByRole("link", { name: "Maple & Co" })).toBeNull();
  expect(screen.getByText("0 shipments match")).toBeTruthy();
});

it("sends a SQL-looking search as a query parameter and does not show the full board", async () => {
  const user = userEvent.setup();
  const payload = "' OR 1=1; DROP TABLE shipments; --";
  const fetchMock = installFetch((query) => (query ? page([]) : page([MAPLE], 28)));
  renderList("/?page=2");

  await screen.findByRole("link", { name: "Maple & Co" });
  await user.type(screen.getByRole("searchbox", { name: "Search" }), payload);

  expect(await screen.findByText(`No shipments match “${payload}”.`)).toBeTruthy();
  expect(screen.queryByRole("link", { name: "Maple & Co" })).toBeNull();

  await waitFor(() => {
    const requests = shipmentRequests(fetchMock);
    const last = requests[requests.length - 1];
    expect(last).toBeTruthy();
    const params = new URL(last ?? "", "http://localhost").searchParams;
    expect(params.get("page")).toBe("1");
    expect(params.get("q")).toBe(payload);
  });
});
