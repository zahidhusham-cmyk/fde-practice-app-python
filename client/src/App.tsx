import { BrowserRouter, NavLink, Route, Routes } from "react-router-dom";
import { BookShipment } from "./pages/BookShipment";
import { ShipmentDetail } from "./pages/ShipmentDetail";
import { ShipmentList } from "./pages/ShipmentList";

export function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <header className="topbar">
          <NavLink to="/" className="brand">
            <span className="brand-mark">H</span>
            Harborline Dispatch
          </NavLink>
          <span className="topbar-meta">Freight operations · Internal</span>
        </header>
        <main className="main">
          <Routes>
            <Route path="/" element={<ShipmentList />} />
            <Route path="/shipments/new" element={<BookShipment />} />
            <Route path="/shipments/:id" element={<ShipmentDetail />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
