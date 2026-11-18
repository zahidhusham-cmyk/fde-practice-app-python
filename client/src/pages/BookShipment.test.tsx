import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes, useParams } from "react-router-dom";
import { afterEach, expect, it, vi } from "vitest";
import { BookShipment } from "./BookShipment";

function OpenedShipment() {
  const { id } = useParams();
  return <p>Opened {id}</p>;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

it("books a shipment and opens its detail page", async () => {
  const user = userEvent.setup();
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    if (url === "/api/drivers") {
      return new Response(JSON.stringify({ drivers: [] }), { status: 200 });
    }
    const body = JSON.parse(String(init?.body));
    return new Response(
      JSON.stringify({
        id: "HL-4429",
        customer: body.customer,
        origin_city: body.origin_city,
        origin_state: "MA",
        destination_city: body.destination_city,
        destination_state: "NY",
        status: "booked",
        service_level: body.service_level,
        promised_on: body.promised_on,
        weight_lb: body.weight_lb,
        pieces: body.pieces,
        driver_id: null,
        created_at: "2026-11-18T15:00:00Z",
        updated_at: "2026-11-18T15:00:00Z",
        notes: body.notes,
        events: [],
      }),
      { status: 201 },
    );
  });
  vi.stubGlobal("fetch", fetchMock);

  render(
    <MemoryRouter initialEntries={["/shipments/new"]}>
      <Routes>
        <Route path="/shipments/new" element={<BookShipment />} />
        <Route path="/shipments/:id" element={<OpenedShipment />} />
      </Routes>
    </MemoryRouter>,
  );

  await user.type(screen.getByRole("textbox", { name: "Customer" }), "Northwind Provisions");
  await user.type(screen.getByRole("textbox", { name: "Origin city" }), "Boston");
  await user.type(screen.getByRole("textbox", { name: "Origin state" }), "MA");
  await user.type(screen.getByRole("textbox", { name: "Destination city" }), "Albany");
  await user.type(screen.getByRole("textbox", { name: "Destination state" }), "NY");
  await user.type(screen.getByLabelText("Promised on"), "2026-11-25");
  await user.type(screen.getByRole("spinbutton", { name: "Weight (lb)" }), "300");
  await user.type(screen.getByRole("spinbutton", { name: "Pieces" }), "4");
  await user.click(screen.getByRole("button", { name: "Book shipment" }));

  expect(await screen.findByText("Opened HL-4429")).toBeTruthy();
  const post = fetchMock.mock.calls.find(([, init]) => init?.method === "POST");
  expect(post?.[0]).toBe("/api/shipments");
  expect(JSON.parse(String(post?.[1]?.body))).toMatchObject({
    customer: "Northwind Provisions",
    origin_city: "Boston",
    service_level: "standard",
    weight_lb: 300,
    pieces: 4,
    driver_id: null,
  });
});
