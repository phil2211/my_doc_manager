import { NavLink, Route, Routes } from "react-router-dom";
import AppLogo from "./components/AppLogo";
import DocumentDetail from "./pages/DocumentDetail";
import Search from "./pages/Search";
import Settings from "./pages/Settings";
import Upload from "./pages/Upload";

export default function App() {
  return (
    <div className="app-shell">
      <header>
        <h1 className="app-title">
          <AppLogo />
          <span>PDF Scan Metadata Manager</span>
        </h1>
        <nav>
          <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : "")}>
            Upload
          </NavLink>
          <NavLink to="/search" className={({ isActive }) => (isActive ? "active" : "")}>
            Search
          </NavLink>
          <NavLink to="/settings" className={({ isActive }) => (isActive ? "active" : "")}>
            Settings
          </NavLink>
        </nav>
      </header>
      <Routes>
        <Route path="/" element={<Upload />} />
        <Route path="/search" element={<Search />} />
        <Route path="/documents/:id" element={<DocumentDetail />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </div>
  );
}
